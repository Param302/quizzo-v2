from flask import current_app, send_file, make_response, Blueprint
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from app.utils import user_required, admin_required, get_current_user
import io


class ExportStatusResource(Resource):
    @jwt_required()
    def get(self, job_id):
        """Poll job completion status"""
        # TODO: Implement with Celery to check actual job status
        # For now, returning mock data

        cache_key_name = f'job_status_{job_id}'
        cached_status = current_app.cache.get(cache_key_name)

        if cached_status:
            return cached_status

        # Mock implementation - in real scenario, check Celery job status
        if 'admin' in job_id:
            status = {
                'job_id': job_id,
                'status': 'completed',  # pending, running, completed, failed
                'progress': 100,
                'message': 'Admin export completed successfully',
                'download_url': f'/downloads/admin_export_{job_id}.csv',
                'created_at': '2025-07-29T10:00:00Z',
                'completed_at': '2025-07-29T10:05:00Z'
            }
        else:
            status = {
                'job_id': job_id,
                'status': 'completed',
                'progress': 100,
                'message': 'User export completed successfully',
                'download_url': f'/downloads/user_export_{job_id}.csv',
                'created_at': '2025-07-29T10:00:00Z',
                'completed_at': '2025-07-29T10:03:00Z'
            }

        # Cache for 1 minute
        current_app.cache.set(cache_key_name, status, timeout=60)
        return status


# Create Blueprint for certificate routes
certificate_bp = Blueprint('certificate', __name__)


@certificate_bp.route('/certificate/<int:quiz_id>/download')
@jwt_required()
@user_required
def download_certificate(quiz_id):
    """Download certificate as PDF file"""
    user = get_current_user()

    try:
        from app.certificate_generator import get_certificate_generator
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


class DailyReminderResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Trigger daily email reminders"""
        # TODO: Implement with Celery
        return {
            'message': 'Daily reminder job started',
            'job_id': 'daily_reminder_123',
            'status': 'pending'
        }


class MonthlyReportResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Trigger monthly report for all users"""
        # TODO: Implement with Celery
        return {
            'message': 'Monthly report job started',
            'job_id': 'monthly_report_123',
            'status': 'pending'
        }


def register_export_api(api):
    api.add_resource(ExportStatusResource, '/export/status/<string:job_id>')
    api.add_resource(DailyReminderResource, '/reminders/send/daily')
    api.add_resource(MonthlyReportResource, '/reports/send/monthly')


def register_certificate_routes(app):
    app.register_blueprint(certificate_bp)
