from flask import current_app, request
from flask_restful import Resource
from datetime import datetime
from app.utils import get_user_quiz_stats
from app.models import User, Submission, Quiz, Question, Course, Chapter, db


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


class PublicCoursesResource(Resource):
    def get(self):
        """List all courses with chapters for public access"""
        cache_key_name = 'public_courses_list'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get search query if provided
        search_query = request.args.get('search', '').lower()

        courses = Course.query.all()

        result_courses = []
        for course in courses:
            # Filter by search if provided
            if search_query and search_query not in course.name.lower():
                continue

            course_data = {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'chapters': []
            }

            for chapter in course.chapters:
                # Get quiz counts by type
                all_quizzes = chapter.quizzes
                live_quizzes = [
                    q for q in all_quizzes if q.is_scheduled and q.date_of_quiz <= datetime.now()]
                upcoming_quizzes = [
                    q for q in all_quizzes if q.is_scheduled and q.date_of_quiz > datetime.now()]
                general_quizzes = [
                    q for q in all_quizzes if not q.is_scheduled]

                # Get next upcoming quiz
                next_quiz = None
                if upcoming_quizzes:
                    next_quiz_obj = min(
                        upcoming_quizzes, key=lambda x: x.date_of_quiz)
                    next_quiz = {
                        'date': next_quiz_obj.date_of_quiz.isoformat(),
                        'title': next_quiz_obj.title
                    }

                chapter_data = {
                    'id': chapter.id,
                    'name': chapter.name,
                    'description': chapter.description,
                    'quiz_counts': {
                        'total': len(all_quizzes),
                        'live': len(live_quizzes),
                        'upcoming': len(upcoming_quizzes),
                        'general': len(general_quizzes)
                    },
                    'next_upcoming_quiz': next_quiz
                }
                course_data['chapters'].append(chapter_data)

            result_courses.append(course_data)

        result = {'courses': result_courses}

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class PublicChapterQuizzesResource(Resource):
    def get(self, course_id, chapter_id):
        """Get quizzes for a specific chapter"""
        cache_key_name = f'public_chapter_{chapter_id}_quizzes'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        chapter = Chapter.query.filter_by(
            id=chapter_id, course_id=course_id).first()
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        now = datetime.now()

        categorized_quizzes = {
            'live': [],
            'upcoming': [],
            'general': [],
            'ended': []
        }

        for quiz in quizzes:
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'question_count': len(quiz.questions),
                'total_marks': sum(q.marks for q in quiz.questions)
            }

            if not quiz.is_scheduled:
                categorized_quizzes['general'].append(quiz_data)
            elif quiz.date_of_quiz > now:
                categorized_quizzes['upcoming'].append(quiz_data)
            elif quiz.date_of_quiz <= now:
                # Check if it's still "live" (within reasonable time window)
                time_diff = (
                    now - quiz.date_of_quiz).total_seconds() / 3600  # hours
                if time_diff <= 24:  # Consider live for 24 hours
                    categorized_quizzes['live'].append(quiz_data)
                else:
                    categorized_quizzes['ended'].append(quiz_data)

        result = {
            'course': {
                'id': chapter.course.id,
                'name': chapter.course.name,
                'description': chapter.course.description
            },
            'chapter': {
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description
            },
            'quizzes': categorized_quizzes
        }

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


def register_public_api(api):
    api.add_resource(PublicProfileResource, '/public/u/@<string:username>')
    api.add_resource(PublicCoursesResource, '/public/courses')
    api.add_resource(PublicChapterQuizzesResource,
                     '/public/courses/<int:course_id>/chapters/<int:chapter_id>/quizzes')
