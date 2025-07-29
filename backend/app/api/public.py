from flask import current_app
from flask_restful import Resource
from app.utils import get_user_quiz_stats
from app.models import User, Submission, Quiz, Question, db


class PublicProfileResource(Resource):
    def get(self, username):
        """Public stats & quiz performance"""
        # Remove @ from username if present
        if username.startswith('@'):
            username = username[1:]

        cache_key_name = f'public_profile_{username}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Find user by username
        user = User.query.filter_by(username=username).first()
        if not user:
            return {'message': 'User not found'}, 404

        # Get public stats (only basic information)
        stats = get_user_quiz_stats(user.id)

        # Get top quiz performances (best scores)
        quiz_scores = stats.get('quiz_scores', [])
        top_performances = sorted(
            quiz_scores,
            key=lambda x: x['score']['percentage'],
            reverse=True
        )[:5]  # Top 5 performances

        # Calculate some aggregate stats
        total_marks_obtained = sum(
            score['score']['obtained_marks'] for score in quiz_scores)
        total_marks_possible = sum(
            score['score']['total_marks'] for score in quiz_scores)

        result = {
            'user': {
                'username': user.username,
                'name': user.name
            },
            'public_stats': {
                'total_quizzes_taken': stats['total_quizzes'],
                'total_questions_answered': stats['total_questions'],
                'overall_accuracy': stats['overall_accuracy'],
                'total_marks_obtained': total_marks_obtained,
                'total_marks_possible': total_marks_possible
            },
            'top_performances': [
                {
                    'quiz_title': perf['quiz_title'],
                    'percentage': perf['score']['percentage'],
                    'obtained_marks': perf['score']['obtained_marks'],
                    'total_marks': perf['score']['total_marks']
                }
                for perf in top_performances
            ]
        }

        # Cache for 1 hour
        current_app.cache.set(cache_key_name, result, timeout=3600)
        return result


def register_public_api(api):
    api.add_resource(PublicProfileResource, '/public/u/@<string:username>')
