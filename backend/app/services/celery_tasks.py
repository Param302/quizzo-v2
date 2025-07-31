from celery import current_app as celery_app
from app.models import User, db
from app.services.email_service import EmailService
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_app_context():
    from run import app
    return app


@celery_app.task(bind=True)
def send_daily_reminders_task(self):
    app = get_app_context()
    with app.app_context():
        try:
            logger.info("Starting daily reminders task...")

            email_service = EmailService()
            result = email_service.send_bulk_daily_reminders()

            logger.info(f"Daily reminders task completed. Result: {result}")
            return {
                'status': 'success',
                'message': 'Daily reminders sent successfully',
                'result': result
            }

        except Exception as e:
            logger.error(f"Daily reminders task failed: {str(e)}")
            # Retry the task with exponential backoff
            raise self.retry(countdown=60, max_retries=3, exc=e)


@celery_app.task(bind=True)
def send_monthly_reports_task(self):
    app = get_app_context()
    with app.app_context():
        try:
            logger.info("Starting monthly reports task...")

            email_service = EmailService()
            result = email_service.send_bulk_monthly_reports()

            logger.info(f"Monthly reports task completed. Result: {result}")
            return {
                'status': 'success',
                'message': 'Monthly reports sent successfully',
                'result': result
            }

        except Exception as e:
            logger.error(f"Monthly reports task failed: {str(e)}")
            # Retry the task with exponential backoff
            raise self.retry(countdown=300, max_retries=3, exc=e)


@celery_app.task(bind=True)
def schedule_user_emails_task(self, user_id):
    app = get_app_context()
    with app.app_context():
        try:
            logger.info(f"Scheduling email tasks for user {user_id}...")

            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return {'status': 'error', 'message': 'User not found'}

            # Send welcome email with information about upcoming features
            email_service = EmailService()

            # Note: The user will automatically be included in the bulk daily reminders
            # and monthly reports that run on schedule. No need to create individual schedules.

            logger.info(f"User {user_id} ({user.email}) will receive:")
            logger.info("- Daily reminder emails (when subscribed to courses)")
            logger.info("- Monthly progress reports")

            return {
                'status': 'success',
                'message': f'Email scheduling completed for user {user_id}',
                'user_email': user.email
            }

        except Exception as e:
            logger.error(
                f"User email scheduling task failed for user {user_id}: {str(e)}")
            raise self.retry(countdown=60, max_retries=3, exc=e)


@celery_app.task(bind=True)
def send_individual_daily_reminder_task(self, user_id):
    app = get_app_context()
    with app.app_context():
        try:
            logger.info(f"Sending daily reminder to user {user_id}...")

            email_service = EmailService()
            success = email_service.send_daily_reminder_email(user_id)

            if success:
                logger.info(
                    f"Daily reminder sent successfully to user {user_id}")
                return {
                    'status': 'success',
                    'message': f'Daily reminder sent to user {user_id}'
                }
            else:
                logger.warning(
                    f"Failed to send daily reminder to user {user_id}")
                return {
                    'status': 'failed',
                    'message': f'Failed to send daily reminder to user {user_id}'
                }

        except Exception as e:
            logger.error(
                f"Individual daily reminder task failed for user {user_id}: {str(e)}")
            raise self.retry(countdown=60, max_retries=3, exc=e)


@celery_app.task(bind=True)
def send_individual_monthly_report_task(self, user_id):
    app = get_app_context()
    with app.app_context():
        try:
            logger.info(f"Sending monthly report to user {user_id}...")

            email_service = EmailService()
            success = email_service.send_monthly_report_email(user_id)

            if success:
                logger.info(
                    f"Monthly report sent successfully to user {user_id}")
                return {
                    'status': 'success',
                    'message': f'Monthly report sent to user {user_id}'
                }
            else:
                logger.warning(
                    f"Failed to send monthly report to user {user_id}")
                return {
                    'status': 'failed',
                    'message': f'Failed to send monthly report to user {user_id}'
                }

        except Exception as e:
            logger.error(
                f"Individual monthly report task failed for user {user_id}: {str(e)}")
            raise self.retry(countdown=300, max_retries=3, exc=e)
