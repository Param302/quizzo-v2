from flask import current_app
from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required
from app.utils import user_required, admin_required, get_current_user


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


class CertificateResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get dynamically generated certificate"""
        user = get_current_user()
        
        # Check if user completed the quiz
        from app.models import Submission, Quiz
        
        submissions = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).all()
        
        if not submissions:
            return {'message': 'Quiz not completed'}, 400
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        # Calculate score
        from app.utils import calculate_quiz_score
        score = calculate_quiz_score(quiz_id, user.id)
        
        # Check if user passed (assuming 60% is passing)
        if score['percentage'] < 60:
            return {'message': 'Certificate not available. Minimum 60% score required.'}, 400
        
        # TODO: Generate actual certificate PDF
        # For now, return certificate data
        certificate_data = {
            'certificate_id': f'CERT_{user.id}_{quiz_id}',
            'user_name': user.name,
            'quiz_title': quiz.title,
            'chapter': quiz.chapter.name,
            'course': quiz.chapter.course.name,
            'score': score,
            'completion_date': max([s.timestamp for s in submissions]).isoformat(),
            'certificate_url': f'/certificates/CERT_{user.id}_{quiz_id}.pdf'
        }
        
        return certificate_data


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
    api.add_resource(CertificateResource, '/quiz/<int:quiz_id>/certificate')
    api.add_resource(DailyReminderResource, '/reminders/send/daily')
    api.add_resource(MonthlyReportResource, '/reports/send/monthly')
