from flask import current_app, request
from flask_restful import Resource
from datetime import datetime
from app.utils import get_user_quiz_stats, categorize_quizzes
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

        # Calculate total time spent
        submissions = Submission.query.filter_by(user_id=user.id).all()
        total_time_spent = 0
        for submission in submissions:
            if submission.time_duration:
                try:
                    time_parts = submission.time_duration.split(':')
                    if len(time_parts) == 3:  # HH:MM:SS format
                        hours = int(time_parts[0])
                        minutes = int(time_parts[1])
                        duration_minutes = hours * 60 + minutes
                        total_time_spent += duration_minutes
                    elif len(time_parts) == 2:  # MM:SS format
                        minutes = int(time_parts[0])
                        total_time_spent += minutes
                except (ValueError, IndexError):
                    continue

        result = {
            'user': {
                'username': user.username,
                'name': user.name,
                'created_at': user.created_at.isoformat()
            },
            'public_stats': {
                'total_quizzes_taken': stats['total_quizzes'],
                'total_questions_answered': stats['total_questions'],
                'overall_accuracy': stats['overall_accuracy'],
                'total_marks_obtained': total_marks_obtained,
                'total_marks_possible': total_marks_possible,
                'total_time_spent': total_time_spent
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
                # Get quiz counts by type using new categorization
                all_quizzes = chapter.quizzes
                categorized = categorize_quizzes(all_quizzes, datetime.now())

                live_quizzes = categorized['live']
                upcoming_quizzes = categorized['upcoming']
                general_quizzes = categorized['general']
                ended_quizzes = categorized['ended']

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

        # Use the new categorization function
        categorized_quiz_objects = categorize_quizzes(quizzes, now)

        categorized_quizzes = {
            'live': [],
            'upcoming': [],
            'general': [],
            'ended': []
        }

        # Convert quiz objects to dictionaries for each category
        for category, quiz_list in categorized_quiz_objects.items():
            for quiz in quiz_list:
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
                categorized_quizzes[category].append(quiz_data)

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
