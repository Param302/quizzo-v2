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

        # Get quiz to check if it's scheduled
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        parser = reqparse.RequestParser()
        parser.add_argument('answers', type=list, location='json', required=True,
                            help='List of answers in format [{"question_id": 1, "answer": [0]}, ...]')
        args = parser.parse_args()

        # Check if user has already submitted this quiz (only for scheduled quizzes)
        existing_submission = None
        if quiz.is_scheduled:
            existing_submission = Submission.query.filter_by(
                user_id=user.id,
                quiz_id=quiz_id
            ).first()

            if existing_submission:
                return {'message': 'Quiz already submitted'}, 400

        # For non-scheduled quizzes, handle existing submissions by updating them
        existing_submissions_dict = {}
        if not quiz.is_scheduled:
            existing_submissions = Submission.query.filter_by(
                user_id=user.id,
                quiz_id=quiz_id
            ).all()
            existing_submissions_dict = {
                sub.question_id: sub for sub in existing_submissions}

        submissions_to_add = []
        submissions_to_update = []

        for answer_data in args['answers']:
            question_id = answer_data.get('question_id')
            answer = answer_data.get('answer')

            question = Question.query.get(question_id)
            if not question or question.quiz_id != quiz_id:
                continue

            is_correct = answer == question.correct_answer

            # For non-scheduled quizzes, update existing submissions or create new ones
            if not quiz.is_scheduled and question_id in existing_submissions_dict:
                existing_sub = existing_submissions_dict[question_id]
                existing_sub.answer = answer
                existing_sub.is_correct = is_correct
                existing_sub.timestamp = datetime.now()
                submissions_to_update.append(existing_sub)
            else:
                submission = Submission(
                    user_id=user.id,
                    quiz_id=quiz_id,
                    question_id=question_id,
                    answer=answer,
                    is_correct=is_correct,
                    timestamp=datetime.now()
                )
                submissions_to_add.append(submission)

        # Save all submissions
        if submissions_to_add:
            db.session.add_all(submissions_to_add)
        db.session.commit()

        invalidate_user_cache(user.id)
        score = calculate_quiz_score(quiz_id, user.id)

        total_submissions = len(submissions_to_add) + \
            len(submissions_to_update)
        return {
            'message': 'Quiz submitted successfully',
            'score': score,
            'total_questions': total_submissions
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


class UserDataExportResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """Export user data as CSV"""
        from flask import make_response
        import csv
        import io

        user = get_current_user()

        try:
            # Prepare CSV data
            output = io.StringIO()
            writer = csv.writer(output)

            # Write user info header
            writer.writerow(['User Information'])
            writer.writerow(['Username', 'Email', 'Role', 'Created At'])
            writer.writerow([user.username, user.email, user.role,
                            user.created_at.strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])  # Empty row

            # Get user submissions
            submissions = db.session.query(
                Submission, Quiz, Chapter, Course
            ).join(
                Quiz, Submission.quiz_id == Quiz.id
            ).join(
                Chapter, Quiz.chapter_id == Chapter.id
            ).join(
                Course, Chapter.course_id == Course.id
            ).filter(
                Submission.user_id == user.id
            ).order_by(Submission.timestamp.desc()).all()

            # Group submissions by quiz to get unique quiz attempts
            quiz_submissions = {}
            for submission, quiz, chapter, course in submissions:
                if quiz.id not in quiz_submissions:
                    quiz_submissions[quiz.id] = {
                        'quiz': quiz,
                        'chapter': chapter,
                        'course': course,
                        'first_submission': submission.timestamp,
                        'last_submission': submission.timestamp
                    }
                else:
                    # Update the time range for this quiz
                    if submission.timestamp < quiz_submissions[quiz.id]['first_submission']:
                        quiz_submissions[quiz.id]['first_submission'] = submission.timestamp
                    if submission.timestamp > quiz_submissions[quiz.id]['last_submission']:
                        quiz_submissions[quiz.id]['last_submission'] = submission.timestamp

            # Write submissions header
            writer.writerow(['Quiz Submissions'])
            writer.writerow([
                'Quiz Title', 'Course', 'Chapter', 'Score', 'Correct Answers',
                'Total Questions', 'Percentage', 'Time Taken', 'Attempted On'
            ])

            for quiz_id, quiz_info in quiz_submissions.items():
                score_data = calculate_quiz_score(quiz_id, user.id)

                # Calculate time taken (difference between first and last submission for this quiz)
                time_diff = quiz_info['last_submission'] - \
                    quiz_info['first_submission']
                time_taken_minutes = int(time_diff.total_seconds() / 60)
                time_taken = f"{time_taken_minutes} minutes" if time_taken_minutes > 0 else "< 1 minute"

                writer.writerow([
                    quiz_info['quiz'].title,
                    quiz_info['course'].name,
                    quiz_info['chapter'].name,
                    f"{score_data['obtained_marks']}/{score_data['total_marks']}",
                    score_data['obtained_marks'],
                    score_data['total_marks'],
                    f"{score_data['percentage']:.1f}%",
                    time_taken,
                    quiz_info['last_submission'].strftime('%Y-%m-%d %H:%M:%S')
                ])

            writer.writerow([])  # Empty row

            # Get user subscriptions
            subscriptions = db.session.query(
                Subscription, Chapter, Course
            ).join(
                Chapter, Subscription.chapter_id == Chapter.id
            ).join(
                Course, Chapter.course_id == Course.id
            ).filter(
                Subscription.user_id == user.id,
                Subscription.is_active == True
            ).all()

            # Write subscriptions header
            writer.writerow(['Active Subscriptions'])
            writer.writerow(['Course', 'Chapter', 'Subscribed On'])

            for subscription, chapter, course in subscriptions:
                writer.writerow([
                    course.name,
                    chapter.name,
                    subscription.subscribed_on.strftime('%Y-%m-%d %H:%M:%S')
                ])

            # Get user statistics
            stats = get_user_quiz_stats(user.id)

            writer.writerow([])  # Empty row
            writer.writerow(['Statistics'])
            writer.writerow(['Metric', 'Value'])
            writer.writerow(
                ['Total Quizzes Taken', stats.get('total_quizzes_taken', 0)])
            writer.writerow(
                ['Overall Accuracy', f"{stats.get('overall_accuracy', 0):.1f}%"])
            writer.writerow(
                ['Average Score', f"{stats.get('average_score', 0):.1f}%"])
            writer.writerow(['Total Time Spent (minutes)',
                            stats.get('total_time_spent', 0)])

            # Create response
            output.seek(0)
            csv_data = output.getvalue()
            output.close()

            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers[
                'Content-Disposition'] = f'attachment; filename=user_data_{user.username}_{datetime.now().strftime("%Y%m%d")}.csv'

            return response

        except Exception as e:
            current_app.logger.error(f"Error exporting user data: {str(e)}")
            return {'message': 'Failed to export user data'}, 500


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

        # Get all quizzes from subscribed chapters that are scheduled
        all_quizzes = Quiz.query.filter(
            Quiz.chapter_id.in_(chapter_ids),
            Quiz.is_scheduled == True
        ).join(Chapter).join(Course).order_by(Quiz.date_of_quiz).all()

        quiz_list = []
        for quiz in all_quizzes:
            try:
                # Parse the quiz start time
                quiz_start = quiz.date_of_quiz

                # Parse duration and calculate end time
                if quiz.time_duration:
                    try:
                        duration_parts = quiz.time_duration.split(':')
                        if len(duration_parts) >= 2:
                            duration_minutes = int(
                                duration_parts[0]) * 60 + int(duration_parts[1])
                        else:
                            # If duration is just a number, assume it's minutes
                            duration_minutes = int(quiz.time_duration)
                        quiz_end = quiz_start + \
                            timedelta(minutes=duration_minutes)
                    except (ValueError, IndexError):
                        # Default 60 minutes if duration parsing fails
                        quiz_end = quiz_start + timedelta(minutes=60)
                        print(
                            f"Warning: Could not parse duration '{quiz.time_duration}' for quiz {quiz.id}, using 60 minutes default")
                else:
                    # Default 60 minutes if no duration specified
                    quiz_end = quiz_start + timedelta(minutes=60)

                # Debug logging
                print(
                    f"Quiz {quiz.id} ({quiz.title}): Start={quiz_start}, End={quiz_end}, Now={now}, Include={quiz_end > now}")

                # Only include quizzes that haven't ended yet
                if quiz_end > now:
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
            except Exception as e:
                print(f"Error processing quiz {quiz.id}: {e}")
                continue

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


class QuizSubmissionDetailResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get detailed submission for a specific quiz with question-wise breakdown"""
        user = get_current_user()

        # Check if user has submitted this quiz
        submissions = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).all()

        if not submissions:
            return {'message': 'No submission found for this quiz'}, 404

        # Get quiz and questions
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        submissions_dict = {sub.question_id: sub for sub in submissions}

        # Calculate total score
        total_marks = sum(q.marks for q in questions)
        obtained_marks = sum(
            q.marks for q in questions
            if q.id in submissions_dict and submissions_dict[q.id].is_correct
        )
        percentage = (obtained_marks / total_marks *
                      100) if total_marks > 0 else 0

        # Prepare question details
        question_details = []
        for question in questions:
            submission = submissions_dict.get(question.id)

            question_data = {
                'question_id': question.id,
                'question_statement': question.question_statement,
                'question_type': question.question_type,
                'marks': question.marks,
                'correct_answer': question.correct_answer,
                'options': question.options if question.question_type in ['MCQ', 'MSQ'] else None,
                'user_answer': submission.answer if submission else None,
                'is_correct': submission.is_correct if submission else False,
                'is_answered': submission is not None,
                'marks_obtained': question.marks if (submission and submission.is_correct) else 0
            }
            question_details.append(question_data)

        result = {
            'quiz_id': quiz.id,
            'quiz_title': quiz.title,
            'chapter': quiz.chapter.name,
            'course': quiz.chapter.course.name,
            'total_questions': len(questions),
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'percentage': round(percentage, 2),
            'correct_answers': len([s for s in submissions if s.is_correct]),
            'incorrect_answers': len([s for s in submissions if not s.is_correct]),
            'unanswered': len(questions) - len(submissions),
            'submission_time': max(s.timestamp for s in submissions).isoformat() if submissions else None,
            'questions': question_details
        }

        return result


class QuizCertificateResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Download certificate for a completed quiz"""
        from flask import send_file, make_response
        import io

        user = get_current_user()

        # Check if user has submitted this quiz
        submission_exists = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).first()

        if not submission_exists:
            return {'message': 'Quiz not submitted yet'}, 400

        # Get certificate generator
        cert_generator = get_certificate_generator()
        if not cert_generator:
            return {'message': 'Certificate service unavailable'}, 503

        # Check if certificate can be generated
        can_generate, message = cert_generator.can_generate_certificate(
            user.id, quiz_id)
        if not can_generate:
            return {'message': message}, 400

        try:
            # Generate certificate PDF
            certificate_pdf = cert_generator.generate_certificate_pdf(
                user.id, quiz_id)

            # Create response with PDF
            response = make_response(certificate_pdf)
            response.headers['Content-Type'] = 'application/pdf'
            response.headers[
                'Content-Disposition'] = f'attachment; filename="quiz_{quiz_id}_certificate.pdf"'

            return response

        except Exception as e:
            current_app.logger.error(f"Error generating certificate: {str(e)}")
            return {'message': 'Failed to generate certificate'}, 500


def register_user_api(api):
    api.add_resource(DashboardResource, '/user/dashboard')
    api.add_resource(QuizMetadataResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(QuizSubmissionResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(QuizSubmissionDetailResource,
                     '/user/quiz/<int:quiz_id>/submission')
    api.add_resource(QuizCertificateResource,
                     '/user/quiz/<int:quiz_id>/certificate')
    api.add_resource(SubscriptionsResource, '/user/subscriptions',
                     '/user/subscriptions/<int:chapter_id>')
    api.add_resource(CourseSubscriptionResource, '/user/course-subscription')
    api.add_resource(UserDataExportResource, '/user/export-data')
    api.add_resource(UserExportResource, '/user/export/csv')
    api.add_resource(UserStatsResource, '/user/stats')
    api.add_resource(UserUpcomingQuizzesResource, '/user/upcoming-quizzes')
    api.add_resource(UserAnalyticsResource, '/user/analytics')
    api.add_resource(UserSubmissionsResource, '/user/submissions')
    api.add_resource(UnsubscribeResource,
                     '/user/unsubscribe/<int:subscription_id>')
    api.add_resource(UserProfileResource, '/user/profile',
                     '/user/profile/<string:username>')
