from flask import current_app
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.cache import invalidate_user_cache, invalidate_quiz_cache
from app.models import Quiz, Question, Submission, Subscription, Chapter, Course, db
from app.utils import user_required, get_current_user, validate_quiz_access, format_quiz_result


class UpcomingQuizzesResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """List upcoming/scheduled quizzes"""
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
            return {'upcoming_quizzes': []}

        # Get upcoming scheduled quizzes
        upcoming_quizzes = Quiz.query.filter(
            Quiz.chapter_id.in_(chapter_ids),
            Quiz.is_scheduled == True,
            Quiz.date_of_quiz > datetime.now()
        ).join(Chapter).join(Course).order_by(Quiz.date_of_quiz).all()

        result = {
            'upcoming_quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'course': quiz.chapter.course.name,
                    'date_of_quiz': quiz.date_of_quiz.isoformat(),
                    'time_duration': quiz.time_duration,
                    'remarks': quiz.remarks,
                    'question_count': len(quiz.questions)
                }
                for quiz in upcoming_quizzes
            ]
        }

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class OpenQuizzesResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """List available quizzes now"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_open_quizzes'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get user's subscribed chapters
        subscriptions = Subscription.query.filter_by(
            user_id=user.id, is_active=True).all()
        chapter_ids = [sub.chapter_id for sub in subscriptions]

        if not chapter_ids:
            return {'open_quizzes': []}

        # Get quizzes that are either not scheduled or scheduled for now/past
        open_quizzes = Quiz.query.filter(
            Quiz.chapter_id.in_(chapter_ids),
            db.or_(
                Quiz.is_scheduled == False,
                db.and_(
                    Quiz.is_scheduled == True,
                    Quiz.date_of_quiz <= datetime.now()
                )
            )
        ).join(Chapter).join(Course).all()

        # Filter out already submitted quizzes
        submitted_quiz_ids = db.session.query(Submission.quiz_id).filter_by(
            user_id=user.id
        ).distinct().all()
        submitted_quiz_ids = {q[0] for q in submitted_quiz_ids}

        available_quizzes = [
            quiz for quiz in open_quizzes if quiz.id not in submitted_quiz_ids]

        result = {
            'open_quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'course': quiz.chapter.course.name,
                    'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                    'time_duration': quiz.time_duration,
                    'remarks': quiz.remarks,
                    'question_count': len(quiz.questions),
                    'total_marks': sum(q.marks for q in quiz.questions)
                }
                for quiz in available_quizzes
            ]
        }

        # Cache for 3 minutes
        current_app.cache.set(cache_key_name, result, timeout=180)
        return result


class QuizQuestionsResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get questions with metadata"""
        user = get_current_user()

        # Validate access
        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        # Check if already submitted
        existing_submission = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).first()

        if existing_submission:
            return {'message': 'Quiz already submitted'}, 400

        cache_key_name = f'quiz_{quiz_id}_questions_user'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(
            quiz_id=quiz_id).order_by(Question.id).all()

        result = {
            'quiz': {
                'id': quiz.id,
                'title': quiz.title,
                'chapter': quiz.chapter.name,
                'course': quiz.chapter.course.name,
                'time_duration': quiz.time_duration,
                'total_questions': len(questions),
                'total_marks': sum(q.marks for q in questions),
                'instructions': quiz.remarks
            },
            'questions': [
                {
                    'id': question.id,
                    'question_number': idx + 1,
                    'question_statement': question.question_statement,
                    'question_type': question.question_type,
                    'options': question.options,
                    'marks': question.marks
                }
                for idx, question in enumerate(questions)
            ]
        }

        # Cache for 15 minutes
        current_app.cache.set(cache_key_name, result, timeout=900)
        return result


class QuizSubmitResource(Resource):
    @jwt_required()
    @user_required
    def post(self, quiz_id):
        """Submit quiz answers"""
        user = get_current_user()

        # Validate access
        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        # Check if already submitted
        existing_submission = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).first()

        if existing_submission:
            return {'message': 'Quiz already submitted'}, 400

        parser = reqparse.RequestParser()
        parser.add_argument('answers', type=list, location='json', required=True,
                            help='List of answers: [{"question_id": 1, "answer": [0]}, ...]')
        args = parser.parse_args()

        # Get all questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        question_dict = {q.id: q for q in questions}

        # Process answers
        submissions = []
        for answer_data in args['answers']:
            question_id = answer_data.get('question_id')
            answer = answer_data.get('answer')

            if question_id not in question_dict:
                continue

            question = question_dict[question_id]

            # Validate answer format based on question type
            if question.question_type in ['MCQ', 'MSQ']:
                if not isinstance(answer, list):
                    return {'message': f'Answer for question {question_id} must be a list'}, 400
            elif question.question_type == 'NAT':
                if not isinstance(answer, (list, int, float, str)):
                    return {'message': f'Invalid answer format for question {question_id}'}, 400
                if not isinstance(answer, list):
                    answer = [answer]  # Convert to list for consistency

            # Check if answer is correct
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

        # Save all submissions
        db.session.add_all(submissions)
        db.session.commit()

        # Clear relevant caches
        invalidate_user_cache(user.id)
        invalidate_quiz_cache(quiz_id)

        # Try to generate certificate information (but don't fail if it doesn't work)
        certificate_info = None
        try:
            from app.services.certificate_generator import get_certificate_generator
            cert_generator = get_certificate_generator()

            can_generate, _ = cert_generator.can_generate_certificate(
                user.id, quiz_id)
            if can_generate:
                certificate_data = cert_generator.get_certificate_data(
                    user.id, quiz_id)
                certificate_info = {
                    'certificate_available': True,
                    'certificate_id': certificate_data['certificate_id'],
                    'download_url': f'/certificate/{quiz_id}/download'
                }

                # Try to send certificate email asynchronously
                try:
                    from app.services.email_service import get_email_service
                    email_service = get_email_service()

                    # Send email in background (don't wait for completion)
                    import threading
                    email_thread = threading.Thread(
                        target=email_service.send_certificate_email,
                        args=(user.id, quiz_id)
                    )
                    email_thread.daemon = True
                    email_thread.start()

                    current_app.logger.info(
                        f"Certificate email queued for user {user.id}, quiz {quiz_id}")

                except Exception as e:
                    current_app.logger.error(
                        f"Failed to queue certificate email: {e}")

        except ImportError:
            current_app.logger.info(
                "Certificate generator not available - WeasyPrint not installed")
        except Exception as e:
            current_app.logger.error(
                f"Certificate generation check failed: {e}")

        response_data = {
            'message': 'Quiz submitted successfully',
            'quiz_id': quiz_id,
            'submitted_answers': len(submissions),
            'total_questions': len(questions)
        }

        # Add certificate info if available
        if certificate_info:
            response_data.update(certificate_info)

        return response_data


class QuizResultResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get result + analytics"""
        user = get_current_user()

        # Check if user has submitted this quiz
        submission_exists = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).first()

        if not submission_exists:
            return {'message': 'Quiz not submitted yet'}, 400

        cache_key_name = f'quiz_{quiz_id}_result_{user.id}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        result = format_quiz_result(quiz_id, user.id)

        # Cache for 30 minutes
        current_app.cache.set(cache_key_name, result, timeout=1800)
        return result


class ChapterQuizzesResource(Resource):
    @jwt_required()
    @user_required
    def get(self, course_id, chapter_id):
        """Get categorized quizzes for a chapter with user submission status"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_chapter_{chapter_id}_quizzes'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        chapter = Chapter.query.filter_by(
            id=chapter_id, course_id=course_id).first()
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()

        # Get user submissions for this chapter
        quiz_ids = [q.id for q in quizzes]
        user_submissions = db.session.query(Submission.quiz_id).filter(
            Submission.user_id == user.id,
            Submission.quiz_id.in_(quiz_ids)
        ).distinct().all()
        submitted_quiz_ids = {s[0] for s in user_submissions}

        # Use the proper categorization logic from utils
        from app.utils import categorize_quizzes
        categorized = categorize_quizzes(quizzes)

        # Build the response data
        categorized_quizzes = {
            'live': [],
            'upcoming': [],
            'general': [],
            'ended': [],
            'completed': []
        }

        for category, quiz_list in categorized.items():
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

                # Add submission status and score if completed
                if quiz.id in submitted_quiz_ids:
                    from app.utils import calculate_quiz_score
                    score = calculate_quiz_score(quiz.id, user.id)
                    quiz_data['user_score'] = score
                    quiz_data['is_completed'] = True
                    categorized_quizzes['completed'].append(quiz_data.copy())
                else:
                    quiz_data['is_completed'] = False

                # Add additional time information for specific categories
                if category == 'upcoming' and quiz.date_of_quiz:
                    from datetime import datetime
                    now = datetime.now()
                    days_until = (quiz.date_of_quiz - now).days
                    quiz_data['days_until'] = days_until
                elif category == 'ended' and quiz.date_of_quiz:
                    from datetime import datetime
                    now = datetime.now()
                    days_past = (now - quiz.date_of_quiz).days
                    quiz_data['days_past'] = days_past

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


class CourseQuizzesResource(Resource):
    @jwt_required()
    @user_required
    def get(self, course_id):
        """Get categorized quizzes for all chapters in a course"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_course_{course_id}_quizzes'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        course = Course.query.get(course_id)
        if not course:
            return {'message': 'Course not found'}, 404

        # Get all quizzes for this course through chapters
        chapters = Chapter.query.filter_by(course_id=course_id).all()
        chapter_ids = [ch.id for ch in chapters]

        if not chapter_ids:
            return {'quizzes': {'live': [], 'upcoming': [], 'general': [], 'ended': []}}

        quizzes = Quiz.query.filter(Quiz.chapter_id.in_(chapter_ids)).all()
        now = datetime.now()

        # Get user submissions for this course
        quiz_ids = [q.id for q in quizzes]
        user_submissions = db.session.query(Submission.quiz_id).filter(
            Submission.user_id == user.id,
            Submission.quiz_id.in_(quiz_ids)
        ).distinct().all()
        submitted_quiz_ids = {s[0] for s in user_submissions}

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
                'chapter': quiz.chapter.name,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'question_count': len(quiz.questions),
                'total_marks': sum(q.marks for q in quiz.questions),
                'is_completed': quiz.id in submitted_quiz_ids
            }

            # Add submission status and score if completed
            if quiz.id in submitted_quiz_ids:
                from app.utils import calculate_quiz_score
                score = calculate_quiz_score(quiz.id, user.id)
                quiz_data['user_score'] = score

            # Categorize by schedule
            if not quiz.is_scheduled:
                categorized_quizzes['general'].append(quiz_data)
            elif quiz.date_of_quiz:
                if quiz.date_of_quiz.date() == now.date():
                    # Check if quiz is currently live
                    if quiz.time_duration:
                        # For scheduled quizzes with duration, check if within time window
                        quiz_datetime = quiz.date_of_quiz
                        duration_parts = quiz.time_duration.split(':')
                        duration_minutes = int(
                            duration_parts[0]) * 60 + int(duration_parts[1])

                        quiz_end = quiz_datetime + \
                            timedelta(minutes=duration_minutes)

                        if quiz_datetime <= now <= quiz_end:
                            categorized_quizzes['live'].append(quiz_data)
                        elif now > quiz_end:
                            categorized_quizzes['ended'].append(quiz_data)
                        else:
                            categorized_quizzes['upcoming'].append(quiz_data)
                    else:
                        categorized_quizzes['live'].append(quiz_data)
                elif quiz.date_of_quiz > now:
                    categorized_quizzes['upcoming'].append(quiz_data)
                else:
                    categorized_quizzes['ended'].append(quiz_data)

        result = {
            'quizzes': categorized_quizzes
        }

        # Cache for 3 minutes
        current_app.cache.set(cache_key_name, result, timeout=180)
        return result


def register_quiz_api(api):
    api.add_resource(UpcomingQuizzesResource, '/quiz/upcoming')
    api.add_resource(OpenQuizzesResource, '/quiz/open')
    api.add_resource(QuizQuestionsResource, '/quiz/<int:quiz_id>/questions')
    api.add_resource(QuizSubmitResource, '/quiz/<int:quiz_id>/submit')
    api.add_resource(QuizResultResource, '/quiz/<int:quiz_id>/result')
    api.add_resource(ChapterQuizzesResource,
                     '/quiz/courses/<int:course_id>/chapters/<int:chapter_id>')
    api.add_resource(CourseQuizzesResource,
                     '/quiz/courses/<int:course_id>/quizzes')
