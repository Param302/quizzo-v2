from flask import current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from app.utils import user_required, admin_required, get_current_user
from app.models import User, Quiz, Submission, db


class SendCertificateEmailResource(Resource):
    @jwt_required()
    @user_required
    def post(self, quiz_id):
        """Send certificate email for a specific quiz"""
        user = get_current_user()

        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()

            # Send certificate email
            success = email_service.send_certificate_email(user.id, quiz_id)

            if success:
                return {
                    'message': 'Certificate email sent successfully',
                    'email': user.email
                }
            else:
                return {
                    'message': 'Failed to send certificate email. Please check your email configuration.',
                }, 500

        except ImportError:
            return {
                'message': 'Certificate generation service unavailable. Please install weasyprint.'
            }, 500
        except Exception as e:
            current_app.logger.error(f"Failed to send certificate email: {e}")
            return {
                'message': 'Failed to send certificate email'
            }, 500


class BulkCertificateEmailResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Send certificate emails to all users who completed specific quiz"""
        parser = reqparse.RequestParser()
        parser.add_argument('quiz_id', type=int,
                            required=True, help='Quiz ID is required')
        args = parser.parse_args()

        quiz_id = args['quiz_id']

        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()

            # Get all users who completed this quiz
            completed_users = db.session.query(Submission.user_id).filter_by(
                quiz_id=quiz_id
            ).distinct().all()

            user_ids = [u[0] for u in completed_users]

            if not user_ids:
                return {
                    'message': 'No users have completed this quiz'
                }, 404

            # Send emails to all users
            success_count = 0
            failed_count = 0

            for user_id in user_ids:
                try:
                    success = email_service.send_certificate_email(
                        user_id, quiz_id)
                    if success:
                        success_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    current_app.logger.error(
                        f"Failed to send email to user {user_id}: {e}")
                    failed_count += 1

            return {
                'message': f'Bulk email completed',
                'total_users': len(user_ids),
                'emails_sent': success_count,
                'failed_emails': failed_count
            }

        except ImportError:
            return {
                'message': 'Certificate generation service unavailable'
            }, 500
        except Exception as e:
            current_app.logger.error(f"Bulk email failed: {e}")
            return {
                'message': 'Bulk email operation failed'
            }, 500


class EmailTestResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Test email configuration"""
        parser = reqparse.RequestParser()
        parser.add_argument('recipient_email', type=str,
                            required=True, help='Recipient email is required')
        args = parser.parse_args()

        try:
            from app.services.email_service import get_email_service
            email_service = get_email_service()

            # Send test email
            test_subject = "Quizzo Email Configuration Test"
            test_body = """
            <html>
            <body>
                <h2>Email Configuration Test</h2>
                <p>This is a test email to verify that your Quizzo email configuration is working correctly.</p>
                <p>If you receive this email, your email settings are properly configured!</p>
                <br>
                <p>Best regards,<br>Quizzo Team</p>
            </body>
            </html>
            """

            success = email_service.send_email(
                recipient_email=args['recipient_email'],
                subject=test_subject,
                html_body=test_body
            )

            if success:
                return {
                    'message': 'Test email sent successfully',
                    'recipient': args['recipient_email']
                }
            else:
                return {
                    'message': 'Failed to send test email. Please check your email configuration.'
                }, 500

        except Exception as e:
            current_app.logger.error(f"Email test failed: {e}")
            return {
                'message': f'Email test failed: {str(e)}'
            }, 500


def register_email_api(api):
    """Register email-related API endpoints"""
    api.add_resource(SendCertificateEmailResource,
                     '/certificate/<int:quiz_id>/email')
    api.add_resource(BulkCertificateEmailResource,
                     '/admin/certificates/bulk-email')
    api.add_resource(EmailTestResource, '/admin/email/test')
