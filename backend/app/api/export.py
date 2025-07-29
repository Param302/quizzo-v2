import io
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.services.report_generator import ReportGenerator
from app.services.certificate_generator import CertificateGenerator
from flask import current_app, send_file, make_response, Blueprint
from app.utils import user_required, admin_required, get_current_user


class ExportStatusResource(Resource):
    @jwt_required()
    def get(self, job_id):
        """Poll job completion status"""
        cache_key_name = f'job_status_{job_id}'
        cached_status = current_app.cache.get(cache_key_name)

        if cached_status:
            return cached_status

        # If not in cache, job doesn't exist
        return {
            'job_id': job_id,
            'status': 'not_found',
            'message': 'Job not found or expired'
        }, 404


# Create Blueprint for certificate routes
certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/certificate/<int:quiz_id>/download')
@jwt_required()
@user_required
def download_certificate(quiz_id):
    """Download certificate as PDF file"""
    user = get_current_user()

    try:
        from app.services.certificate_generator import get_certificate_generator
        cert_generator = get_certificate_generator()
    except ImportError as e:
        current_app.logger.error(f"Certificate generator import failed: {e}")
        return {'message': 'Certificate generation service unavailable'}, 500

    # Check if certificate can be generated
    can_generate, message = cert_generator.can_generate_certificate(
        user.id, quiz_id)
    if not can_generate:
        return {'message': message}, 400

    try:
        # Generate PDF bytes
        pdf_bytes = cert_generator.generate_certificate_pdf(user.id, quiz_id)
        certificate_data = cert_generator.get_certificate_data(
            user.id, quiz_id)

        # Create a file-like object from bytes
        pdf_buffer = io.BytesIO(pdf_bytes)
        pdf_buffer.seek(0)

        # Generate filename
        filename = f"certificate_{certificate_data['certificate_id']}.pdf"

        # Return PDF file
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )

    except Exception as e:
        current_app.logger.error(f"Certificate download failed: {e}")
        return {'message': f'Failed to download certificate: {str(e)}'}, 500


class ExportDownloadResource(Resource):
    @jwt_required()
    def get(self, export_type, job_id):
        current_user = get_current_user()

        try:
            if export_type == 'admin':
                if not current_user.is_admin:
                    return {'message': 'Admin access required'}, 403

                report_gen = ReportGenerator()
                file_content, filename = report_gen.download_admin_export(
                    job_id)

                if not file_content:
                    return {'message': 'Export file not found or expired'}, 404

                return send_file(
                    io.BytesIO(file_content),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='text/csv'
                )

            elif export_type == 'user':
                report_gen = ReportGenerator()
                file_content, filename = report_gen.download_user_export(
                    current_user.id, job_id)

                if not file_content:
                    return {'message': 'Export file not found or expired'}, 404

                return send_file(
                    io.BytesIO(file_content),
                    as_attachment=True,
                    download_name=filename,
                    mimetype='text/csv'
                )

            else:
                return {'message': 'Invalid export type'}, 400

        except Exception as e:
            current_app.logger.error(f"Download error: {str(e)}")
            return {'message': 'Download failed'}, 500


class DailyReminderResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        try:
            report_gen = ReportGenerator()
            job_id = report_gen.send_daily_reminders()

            return {
                'message': 'Daily reminder job started',
                'job_id': job_id,
                'status': 'running'
            }
        except Exception as e:
            current_app.logger.error(f"Daily reminder failed: {str(e)}")
            return {'message': 'Failed to start daily reminders'}, 500


class MonthlyReportResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        try:
            report_gen = ReportGenerator()
            job_id = report_gen.send_monthly_reports()

            return {
                'message': 'Monthly report job started',
                'job_id': job_id,
                'status': 'running'
            }
        except Exception as e:
            current_app.logger.error(f"Monthly report failed: {str(e)}")
            return {'message': 'Failed to start monthly reports'}, 500


def register_export_api(api):
    api.add_resource(ExportStatusResource, '/export/status/<string:job_id>')
    api.add_resource(ExportDownloadResource,
                     '/export/download/<string:export_type>/<string:job_id>')
    api.add_resource(DailyReminderResource, '/reminders/send/daily')
    api.add_resource(MonthlyReportResource, '/reports/send/monthly')


def register_certificate_routes(app):
    app.register_blueprint(certificate_bp)
