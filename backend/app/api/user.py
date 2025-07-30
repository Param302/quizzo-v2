from datetime import datetime
from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.services.report_generator import ReportGenerator
from app.services.certificate_generator import get_certificate_generator
from app.cache import invalidate_user_cache, invalidate_quiz_cache
from app.models import User, Quiz, Question, Submission, Subscription, Chapter, Course, db
from app.utils import user_required, get_current_user, get_user_quiz_stats, validate_quiz_access, calculate_quiz_score


class DashboardResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        user = get_current_user()
        cache_key_name = f'user_{user.id}_dashboard'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get user's subscribed chapters
        subscriptions = Subscription.query.filter_by(
            user_id=user.id, is_active=True).all()
        chapter_ids = [sub.chapter_id for sub in subscriptions]

        # Get upcoming quizzes from subscribed chapters
        upcoming_quizzes = Quiz.query.filter(
            Quiz.chapter_id.in_(chapter_ids),
            Quiz.is_scheduled == True,
            Quiz.date_of_quiz > datetime.now()
        ).order_by(Quiz.date_of_quiz).limit(5).all()

        # Get recent quiz history
        recent_submissions = db.session.query(Submission.quiz_id).filter_by(
            user_id=user.id
        ).distinct().order_by(Submission.timestamp.desc()).limit(5).all()

        recent_quiz_ids = [s[0] for s in recent_submissions]
        recent_quizzes = Quiz.query.filter(Quiz.id.in_(recent_quiz_ids)).all()

        # Get basic stats
        stats = get_user_quiz_stats(user.id)
        recent_quizzes_with_certificates = []
        cert_generator = get_certificate_generator()

        for quiz in recent_quizzes:
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'chapter': quiz.chapter.name,
                'course': quiz.chapter.course.name,
                'score': calculate_quiz_score(quiz.id, user.id)
            }

            can_generate, _ = cert_generator.can_generate_certificate(
                user.id, quiz.id)
            if can_generate:
                quiz_data['certificate_available'] = True
                quiz_data['download_url'] = f'/certificate/{quiz.id}/download'
            else:
                quiz_data['certificate_available'] = False

            recent_quizzes_with_certificates.append(quiz_data)

        result = {
            'user': {
                'id': user.id,
                'name': user.name,
                'username': user.username
            },
            'upcoming_quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'course': quiz.chapter.course.name,
                    'date_of_quiz': quiz.date_of_quiz.isoformat(),
                    'time_duration': quiz.time_duration
                }
                for quiz in upcoming_quizzes
            ],
            'recent_quizzes': recent_quizzes_with_certificates,
            'stats': {
                'total_quizzes_taken': stats['total_quizzes'],
                'overall_accuracy': stats['overall_accuracy']
            }
        }

        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class QuizMetadataResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        user = get_current_user()
        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        cache_key_name = f'quiz_{quiz_id}_metadata'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        result = {
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'chapter': quiz.chapter.name,
                'course': quiz.chapter.course.name,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'total_questions': len(questions),
                'total_marks': sum(q.marks for q in questions)
            },
            'questions': [
                {
                    'id': question.id,
                    'question_statement': question.question_statement,
                    'question_type': question.question_type,
                    'options': question.options,
                    'marks': question.marks
                }
                for question in questions
            ]
        }

        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result


class QuizSubmissionResource(Resource):
    @jwt_required()
    @user_required
    def post(self, quiz_id):
        """Submit quiz answers"""
        user = get_current_user()

        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('answers', type=list, location='json', required=True,
                            help='List of answers in format [{"question_id": 1, "answer": [0]}, ...]')
        args = parser.parse_args()

        # Check if user has already submitted this quiz
        existing_submission = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).first()

        if existing_submission:
            return {'message': 'Quiz already submitted'}, 400

        submissions = []
        for answer_data in args['answers']:
            question_id = answer_data.get('question_id')
            answer = answer_data.get('answer')

            question = Question.query.get(question_id)
            if not question or question.quiz_id != quiz_id:
                continue

            is_correct = answer == question.correct_answer

            submission = Submission(
                user_id=user.id,
                quiz_id=quiz_id,
                question_id=question_id,
                answer=answer,
                is_correct=is_correct,
                timestamp=datetime.now()
            )

            submissions.append(submission)

        db.session.add_all(submissions)
        db.session.commit()

        invalidate_user_cache(user.id)
        score = calculate_quiz_score(quiz_id, user.id)

        return {
            'message': 'Quiz submitted successfully',
            'score': score,
            'total_questions': len(submissions)
        }


class SubscriptionsResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        user = get_current_user()
        cache_key_name = f'user_{user.id}_subscriptions'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        subscriptions = Subscription.query.filter_by(
            user_id=user.id,
            is_active=True
        ).join(Chapter).join(Course).all()

        result = {
            'subscriptions': [
                {
                    'id': sub.id,
                    'chapter_id': sub.chapter_id,
                    'chapter_name': sub.chapter.name,
                    'course_id': sub.chapter.course.id,
                    'course_name': sub.chapter.course.name,
                    'subscribed_on': sub.subscribed_on.isoformat(),
                    'quiz_count': len(sub.chapter.quizzes)
                }
                for sub in subscriptions
            ]
        }

        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result

    @jwt_required()
    @user_required
    def post(self):
        """Subscribe to chapter"""
        user = get_current_user()

        parser = reqparse.RequestParser()
        parser.add_argument('chapter_id', type=int, required=True)
        args = parser.parse_args()

        chapter = Chapter.query.get(args['chapter_id'])
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        existing_sub = Subscription.query.filter_by(
            user_id=user.id,
            chapter_id=args['chapter_id']
        ).first()

        if existing_sub:
            if existing_sub.is_active:
                return {'message': 'Already subscribed to this chapter'}, 400
            else:
                existing_sub.is_active = True
                existing_sub.subscribed_on = datetime.now()
        else:
            subscription = Subscription(
                user_id=user.id,
                chapter_id=args['chapter_id'],
                subscribed_on=datetime.now(),
                is_active=True
            )
            db.session.add(subscription)

        db.session.commit()
        invalidate_user_cache(user.id)

        return {
            'message': 'Successfully subscribed to chapter',
            'chapter': {
                'id': chapter.id,
                'name': chapter.name,
                'course': chapter.course.name
            }
        }

    @jwt_required()
    @user_required
    def delete(self, chapter_id=None):
        """Unsubscribe from chapter - supports both URL parameter and request body"""
        user = get_current_user()

        if chapter_id is None:
            # Legacy support: chapter_id in request body
            parser = reqparse.RequestParser()
            parser.add_argument('chapter_id', type=int, required=True)
            args = parser.parse_args()
            chapter_id = args['chapter_id']

        subscription = Subscription.query.filter_by(
            user_id=user.id,
            chapter_id=chapter_id,
            is_active=True
        ).first()

        if not subscription:
            return {'message': 'Not subscribed to this chapter'}, 404

        subscription.is_active = False
        db.session.commit()
        invalidate_user_cache(user.id)

        return {'message': 'Successfully unsubscribed from chapter'}


class UserExportResource(Resource):
    @jwt_required()
    @user_required
    def post(self):
        """Trigger user quiz export (async)"""
        user = get_current_user()

        try:
            report_gen = ReportGenerator()
            job_id = report_gen.export_user_data(user.id)

            return {
                'message': 'Export job started',
                'job_id': job_id,
                'status': 'running',
                'download_url': f'/api/export/download/user/{job_id}'
            }
        except Exception as e:
            current_app.logger.error(f"User export failed: {str(e)}")
            return {'message': 'Failed to start export'}, 500


class UserStatsResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """Detailed quiz stats"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_detailed_stats'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        stats = get_user_quiz_stats(user.id)
        subscriptions = Subscription.query.filter_by(
            user_id=user.id, is_active=True).all()
        chapter_performance = []

        for sub in subscriptions:
            chapter_quizzes = Quiz.query.filter_by(
                chapter_id=sub.chapter_id).all()
            chapter_quiz_ids = [q.id for q in chapter_quizzes]
            chapter_submissions = Submission.query.filter(
                Submission.user_id == user.id,
                Submission.quiz_id.in_(chapter_quiz_ids)
            ).all()

            if chapter_submissions:
                total_questions = len(chapter_submissions)
                correct_answers = sum(
                    1 for s in chapter_submissions if s.is_correct)
                accuracy = (correct_answers / total_questions) * \
                    100 if total_questions > 0 else 0

                chapter_performance.append({
                    'chapter_id': sub.chapter_id,
                    'chapter_name': sub.chapter.name,
                    'course_name': sub.chapter.course.name,
                    'quizzes_taken': len(set(s.quiz_id for s in chapter_submissions)),
                    'total_questions': total_questions,
                    'correct_answers': correct_answers,
                    'accuracy': accuracy
                })

        result = {
            'overall_stats': stats,
            'chapter_performance': chapter_performance
        }

        # Cache for 15 minutes
        current_app.cache.set(cache_key_name, result, timeout=900)
        return result


class CourseSubscriptionResource(Resource):
    @jwt_required()
    @user_required
    def post(self):
        """Subscribe to all chapters of a course"""
        user = get_current_user()

        parser = reqparse.RequestParser()
        parser.add_argument('course_id', type=int, required=True)
        args = parser.parse_args()

        course = Course.query.get(args['course_id'])
        if not course:
            return {'message': 'Course not found'}, 404

        chapters = Chapter.query.filter_by(course_id=args['course_id']).all()
        if not chapters:
            return {'message': 'No chapters found in this course'}, 404

        subscribed_chapters = []
        already_subscribed = []

        for chapter in chapters:
            existing_sub = Subscription.query.filter_by(
                user_id=user.id,
                chapter_id=chapter.id
            ).first()

            if existing_sub:
                if existing_sub.is_active:
                    already_subscribed.append(chapter.name)
                else:
                    existing_sub.is_active = True
                    existing_sub.subscribed_on = datetime.now()
                    subscribed_chapters.append(chapter.name)
            else:
                subscription = Subscription(
                    user_id=user.id,
                    chapter_id=chapter.id,
                    subscribed_on=datetime.now(),
                    is_active=True
                )
                db.session.add(subscription)
                subscribed_chapters.append(chapter.name)

        db.session.commit()
        invalidate_user_cache(user.id)

        return {
            'message': f'Successfully subscribed to {len(subscribed_chapters)} chapters',
            'course': course.name,
            'subscribed_chapters': subscribed_chapters,
            'already_subscribed': already_subscribed
        }


class UserUpcomingQuizzesResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """Get upcoming quizzes from subscribed chapters"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_upcoming_quizzes'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get user's subscribed chapters
        subscriptions = Subscription.query.filter_by(
            user_id=user.id, is_active=True).all()
        chapter_ids = [sub.chapter_id for sub in subscriptions]

        if not chapter_ids:
            return {'quizzes': []}

        # Get upcoming quizzes from subscribed chapters
        from datetime import datetime, timedelta
        now = datetime.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # Get quizzes happening today or in the future
        upcoming_quizzes = Quiz.query.filter(
            Quiz.chapter_id.in_(chapter_ids),
            Quiz.is_scheduled == True,
            Quiz.date_of_quiz >= today_start
        ).join(Chapter).join(Course).order_by(Quiz.date_of_quiz).all()

        quiz_list = []
        for quiz in upcoming_quizzes:
            quiz_data = {
                'id': quiz.id,
                'title': quiz.title,
                'chapter': quiz.chapter.name,
                'chapter_id': quiz.chapter_id,
                'course': quiz.chapter.course.name,
                'course_id': quiz.chapter.course.id,
                'date_of_quiz': quiz.date_of_quiz.isoformat(),
                'time_duration': quiz.time_duration
            }
            quiz_list.append(quiz_data)

        result = {'quizzes': quiz_list}
        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class UserAnalyticsResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """Get user analytics data for charts"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_analytics'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        stats = get_user_quiz_stats(user.id)
        quiz_scores = stats.get('quiz_scores', [])

        # Get course attempts data
        course_attempts = {}
        for quiz_score in quiz_scores:
            quiz = Quiz.query.get(quiz_score['quiz_id'])
            if quiz and quiz.chapter and quiz.chapter.course:
                course_name = quiz.chapter.course.name
                if course_name not in course_attempts:
                    course_attempts[course_name] = 0
                course_attempts[course_name] += 1

        course_attempts_list = [
            {'course_name': course, 'attempts': count}
            for course, count in course_attempts.items()
        ]

        result = {
            'quiz_scores': quiz_scores,
            'course_attempts': course_attempts_list
        }

        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result


class UserSubmissionsResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """Get user's quiz submissions with details"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_detailed_submissions'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get all quizzes user has participated in
        quiz_ids = db.session.query(Submission.quiz_id).filter_by(
            user_id=user.id).distinct().all()
        quiz_ids = [q[0] for q in quiz_ids]

        submissions_data = []
        total_time_spent = 0

        cert_generator = get_certificate_generator()

        for quiz_id in quiz_ids:
            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                continue

            # Get submissions for this quiz
            user_submissions = Submission.query.filter_by(
                quiz_id=quiz_id,
                user_id=user.id
            ).all()

            if not user_submissions:
                continue

            # Calculate score and stats
            total_questions = len(user_submissions)
            correct_answers = sum(1 for s in user_submissions if s.is_correct)
            score = (correct_answers / total_questions) * \
                100 if total_questions > 0 else 0

            # Get the latest submission timestamp
            latest_submission = max(
                user_submissions, key=lambda s: s.timestamp)

            # Calculate time spent (duration in minutes)
            if quiz.time_duration:
                duration_parts = quiz.time_duration.split(':')
                duration_minutes = int(
                    duration_parts[0]) * 60 + int(duration_parts[1])
                total_time_spent += duration_minutes

            # Check if certificate is available
            can_generate, _ = cert_generator.can_generate_certificate(
                user.id, quiz_id)

            submission_data = {
                'quiz_id': quiz.id,
                'quiz_title': quiz.title,
                'chapter_name': quiz.chapter.name,
                'course_name': quiz.chapter.course.name,
                'total_questions': total_questions,
                'correct_answers': correct_answers,
                'score': score,
                'attempted_on': latest_submission.timestamp.isoformat(),
                'time_duration': quiz.time_duration or '00:00',
                'certificate_available': can_generate
            }
            submissions_data.append(submission_data)

        # Sort by attempted date (newest first)
        submissions_data.sort(key=lambda x: x['attempted_on'], reverse=True)

        result = {
            'submissions': submissions_data,
            'total_time_spent': total_time_spent
        }

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class UnsubscribeResource(Resource):
    @jwt_required()
    @user_required
    def delete(self, subscription_id):
        """Unsubscribe from a chapter"""
        user = get_current_user()

        try:
            # Find the subscription
            subscription = Subscription.query.filter_by(
                id=subscription_id,
                user_id=user.id
            ).first()

            if not subscription:
                return {'message': 'Subscription not found'}, 404

            # Delete the subscription
            db.session.delete(subscription)
            db.session.commit()

            # Clear cache
            cache_key_name = f'user_{user.id}_subscriptions'
            current_app.cache.delete(cache_key_name)

            return {'message': 'Successfully unsubscribed from chapter'}, 200

        except Exception as e:
            db.session.rollback()
            return {'message': f'Error unsubscribing: {str(e)}'}, 500


class UserProfileResource(Resource):
    @jwt_required()
    @user_required
    def get(self, username=None):
        """Get user profile - own profile includes email, others don't"""
        current_user = get_current_user()

        # If no username provided, get current user's profile
        if not username:
            username = current_user.username

        # Remove @ from username if present
        if username.startswith('@'):
            username = username[1:]

        cache_key_name = f'user_profile_{username}_{current_user.id}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Find target user by username
        target_user = User.query.filter_by(username=username).first()
        if not target_user:
            return {'message': 'User not found'}, 404

        # Get user stats
        stats = get_user_quiz_stats(target_user.id)

        # Calculate total time spent
        submissions = Submission.query.filter_by(user_id=target_user.id).all()
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

        # Prepare user data
        user_data = {
            'username': target_user.username,
            'name': target_user.name,
            'created_at': target_user.created_at.isoformat()
        }

        # Include email only if viewing own profile
        if current_user.id == target_user.id:
            user_data['email'] = target_user.email

        result = {
            'user': user_data,
            'stats': {
                'total_quizzes_taken': stats['total_quizzes'],
                'total_questions_answered': stats['total_questions'],
                'overall_accuracy': stats['overall_accuracy'],
                'total_time_spent': total_time_spent
            },
            'is_own_profile': current_user.id == target_user.id
        }

        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result


def register_user_api(api):
    api.add_resource(DashboardResource, '/user/dashboard')
    api.add_resource(QuizMetadataResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(QuizSubmissionResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(SubscriptionsResource, '/user/subscriptions',
                     '/user/subscriptions/<int:chapter_id>')
    api.add_resource(CourseSubscriptionResource, '/user/course-subscription')
    api.add_resource(UserExportResource, '/user/export/csv')
    api.add_resource(UserStatsResource, '/user/stats')
    api.add_resource(UserUpcomingQuizzesResource, '/user/upcoming-quizzes')
    api.add_resource(UserAnalyticsResource, '/user/analytics')
    api.add_resource(UserSubmissionsResource, '/user/submissions')
    api.add_resource(UnsubscribeResource,
                     '/user/unsubscribe/<int:subscription_id>')
    api.add_resource(UserProfileResource, '/user/profile',
                     '/user/profile/<string:username>')
