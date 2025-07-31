from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.utils import admin_required
from app.services.celery_tasks import (
    send_daily_reminders_task,
    send_monthly_reports_task,
    send_individual_daily_reminder_task,
    send_individual_monthly_report_task
)
from app.models import User


class EmailTasksResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('task_type', type=str, required=True,
                            choices=['daily_reminders', 'monthly_reports',
                                     'test_daily', 'test_monthly'],
                            help='Task type is required')
        parser.add_argument('user_id', type=int,
                            help='User ID for individual tasks')
        args = parser.parse_args()

        try:
            if args['task_type'] == 'daily_reminders':
                # Trigger bulk daily reminders
                task = send_daily_reminders_task.delay()
                return {
                    'message': 'Daily reminders task started',
                    'task_id': task.id,
                    'status': 'queued'
                }, 202

            elif args['task_type'] == 'monthly_reports':
                # Trigger bulk monthly reports
                task = send_monthly_reports_task.delay()
                return {
                    'message': 'Monthly reports task started',
                    'task_id': task.id,
                    'status': 'queued'
                }, 202

            elif args['task_type'] == 'test_daily':
                # Send test daily reminder to specific user or first user
                user_id = args.get('user_id')
                if not user_id:
                    user = User.query.filter_by(role='user').first()
                    if not user:
                        return {'message': 'No users found for testing'}, 404
                    user_id = user.id

                task = send_individual_daily_reminder_task.delay(user_id)
                return {
                    'message': f'Test daily reminder sent to user {user_id}',
                    'task_id': task.id,
                    'user_id': user_id,
                    'status': 'queued'
                }, 202

            elif args['task_type'] == 'test_monthly':
                # Send test monthly report to specific user or first user
                user_id = args.get('user_id')
                if not user_id:
                    user = User.query.filter_by(role='user').first()
                    if not user:
                        return {'message': 'No users found for testing'}, 404
                    user_id = user.id

                task = send_individual_monthly_report_task.delay(user_id)
                return {
                    'message': f'Test monthly report sent to user {user_id}',
                    'task_id': task.id,
                    'user_id': user_id,
                    'status': 'queued'
                }, 202

        except Exception as e:
            current_app.logger.error(f"Failed to trigger email task: {str(e)}")
            return {
                'message': f'Failed to trigger task: {str(e)}'
            }, 500


class CeleryStatusResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        try:
            from app import create_app
            app = create_app()
            celery = app.celery

            inspect = celery.control.inspect()
            active_tasks = inspect.active()
            scheduled_tasks = inspect.scheduled()
            stats = inspect.stats()

            return {
                'celery_status': 'connected',
                'active_tasks': active_tasks or {},
                'scheduled_tasks': scheduled_tasks or {},
                'worker_stats': stats or {},
                'beat_schedule': {
                    'daily_reminders': '9:00 AM UTC daily',
                    'monthly_reports': '1st of month at 10:00 AM UTC'
                }
            }

        except Exception as e:
            current_app.logger.error(f"Failed to get Celery status: {str(e)}")
            return {
                'celery_status': 'error',
                'error': str(e),
                'message': 'Make sure Celery worker is running'
            }, 500


def register_email_tasks_api(api):
    api.add_resource(EmailTasksResource, '/admin/email-tasks')
    api.add_resource(CeleryStatusResource, '/admin/celery-status')
