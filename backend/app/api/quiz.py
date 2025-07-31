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

        # Filter out already submitted quizzes (only for scheduled quizzes)
        submitted_quiz_ids = db.session.query(Submission.quiz_id).filter_by(
            user_id=user.id
        ).distinct().all()
        submitted_quiz_ids = {q[0] for q in submitted_quiz_ids}

        # For scheduled quizzes, exclude if already submitted
        # For non-scheduled quizzes, always include (allow multiple submissions)
        available_quizzes = []
        for quiz in open_quizzes:
            if quiz.is_scheduled and quiz.id in submitted_quiz_ids:
                continue  # Skip scheduled quizzes that are already submitted
            available_quizzes.append(quiz)

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

        # Get quiz to check if it's scheduled
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        # Check if already submitted (only for scheduled quizzes)
        if quiz.is_scheduled:
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
        """Submit quiz answers (handles both new submissions and updates to existing ones)"""
        user = get_current_user()

        # Validate access
        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('answers', type=list, location='json', required=True,
                            help='List of answers: [{"question_id": 1, "answer": [0]}, ...]')
        args = parser.parse_args()

        # Get all questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        question_dict = {q.id: q for q in questions}

        # Get existing submissions for this user and quiz
        existing_submissions = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).all()
        existing_by_question = {
            sub.question_id: sub for sub in existing_submissions}

        # Process answers
        submissions_to_add = []
        submissions_to_update = []

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

            # Update existing submission or create new one
            if question_id in existing_by_question:
                submission = existing_by_question[question_id]
                submission.answer = answer
                submission.is_correct = is_correct
                submission.timestamp = datetime.now()
                submissions_to_update.append(submission)
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

        # Clear relevant caches
        invalidate_user_cache(user.id)
        invalidate_quiz_cache(quiz_id)

        # Always generate certificate and send completion email
        certificate_info = None
        try:
            from app.services.certificate_generator import get_certificate_generator
            cert_generator = get_certificate_generator()

            if cert_generator:
                # Always generate certificate data
                certificate_data = cert_generator.get_certificate_data(
                    user.id, quiz_id)
                certificate_info = {
                    'certificate_available': True,
                    'certificate_id': certificate_data['certificate_id'],
                    'download_url': f'/certificate/{quiz_id}/download'
                }

                # Always send completion email with certificate attachment
                try:
                    from app.services.email_service import get_email_service
                    email_service = get_email_service()

                    # Send email in background with application context
                    import threading
                    from flask import current_app

                    # Capture the Flask app instance before threading
                    app = current_app._get_current_object()

                    def send_completion_email_with_context():
                        with app.app_context():
                            email_service.send_certificate_email(
                                user.id, quiz_id)

                    email_thread = threading.Thread(
                        target=send_completion_email_with_context)
                    email_thread.daemon = True
                    email_thread.start()

                    current_app.logger.info(
                        f"Quiz completion email with certificate queued for user {user.id}, quiz {quiz_id}")

                except Exception as e:
                    current_app.logger.error(
                        f"Failed to queue completion email: {e}")
            else:
                current_app.logger.warning(
                    "Certificate generator not available")

        except ImportError:
            current_app.logger.info(
                "Certificate generator not available - WeasyPrint not installed")
        except Exception as e:
            current_app.logger.error(
                f"Certificate generation failed: {e}")

        total_submissions = len(submissions_to_add) + \
            len(submissions_to_update)
        response_data = {
            'message': 'Quiz submitted successfully',
            'quiz_id': quiz_id,
            'submitted_answers': total_submissions,
            'total_questions': len(questions)
        }

        # Add certificate info if available
        if certificate_info:
            response_data.update(certificate_info)

        return response_data


class QuizQuestionSubmitResource(Resource):
    @jwt_required()
    @user_required
    def post(self, quiz_id):
        """Submit individual question answer"""
        user = get_current_user()

        # Validate access
        can_access, message = validate_quiz_access(quiz_id, user.id)
        if not can_access:
            return {'message': message}, 403

        parser = reqparse.RequestParser()
        parser.add_argument('question_id', type=int, required=True,
                            help='Question ID is required')
        parser.add_argument('answer', type=list, location='json', required=True,
                            help='Answer is required')
        args = parser.parse_args()

        question_id = args['question_id']
        answer = args['answer']

        # Check if question belongs to this quiz
        question = Question.query.filter_by(
            id=question_id, quiz_id=quiz_id).first()
        if not question:
            return {'message': 'Question not found'}, 404

        # Validate answer format based on question type
        if question.question_type in ['MCQ', 'MSQ']:
            if not isinstance(answer, list):
                return {'message': 'Answer must be a list for MCQ/MSQ'}, 400
        elif question.question_type == 'NAT':
            if not isinstance(answer, list) or len(answer) != 1:
                return {'message': 'NAT answer must be a single-item list'}, 400

        # Check if answer is correct
        is_correct = answer == question.correct_answer

        # Check if submission already exists for this question
        existing_submission = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id,
            question_id=question_id
        ).first()

        if existing_submission:
            # Update existing submission
            existing_submission.answer = answer
            existing_submission.is_correct = is_correct
            existing_submission.timestamp = datetime.now()
        else:
            # Create new submission
            submission = Submission(
                user_id=user.id,
                quiz_id=quiz_id,
                question_id=question_id,
                answer=answer,
                is_correct=is_correct,
                timestamp=datetime.now()
            )
            db.session.add(submission)

        db.session.commit()

        return {
            'message': 'Answer saved successfully',
            'question_id': question_id,
            'is_correct': is_correct
        }


class QuizResultResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get detailed quiz result + analytics"""
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

        # Get quiz and questions
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        total_questions = len(questions)
        total_marks = sum(q.marks for q in questions)

        # Get user submissions for this quiz
        submissions = Submission.query.filter_by(
            user_id=user.id,
            quiz_id=quiz_id
        ).all()

        # Calculate results
        correct_answers = sum(1 for s in submissions if s.is_correct)
        incorrect_answers = len(submissions) - correct_answers
        unanswered = total_questions - len(submissions)

        obtained_marks = sum(q.marks for s in submissions if s.is_correct
                             for q in questions if q.id == s.question_id)

        percentage = (obtained_marks / total_marks *
                      100) if total_marks > 0 else 0

        result = {
            'quiz_id': quiz_id,
            'quiz_title': quiz.title,
            'chapter': quiz.chapter.name,
            'course': quiz.chapter.course.name,
            'total_questions': total_questions,
            'total_marks': total_marks,
            'obtained_marks': obtained_marks,
            'percentage': round(percentage, 2),
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'unanswered': unanswered,
            'submission_id': submissions[0].id if submissions else None,
            'submission_time': max(s.timestamp for s in submissions).isoformat() if submissions else None
        }

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

                    # ALL submitted quizzes (both scheduled and non-scheduled) go to completed section
                    categorized_quizzes['completed'].append(quiz_data.copy())

                    # For scheduled quizzes, mark as completed (prevents retaking)
                    # For non-scheduled quizzes, don't mark as completed (allows retaking)
                    quiz_data['is_completed'] = quiz.is_scheduled
                else:
                    # Add additional time information for specific categories
                    quiz_data['is_completed'] = False
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
                # Only mark scheduled quizzes as completed when submitted
                'is_completed': quiz.is_scheduled and quiz.id in submitted_quiz_ids
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
    api.add_resource(QuizQuestionSubmitResource,
                     '/quiz/<int:quiz_id>/submit-answer')
    api.add_resource(QuizSubmitResource, '/quiz/<int:quiz_id>/submit')
    api.add_resource(QuizResultResource, '/quiz/<int:quiz_id>/result')
    api.add_resource(ChapterQuizzesResource,
                     '/quiz/courses/<int:course_id>/chapters/<int:chapter_id>')
    api.add_resource(CourseQuizzesResource,
                     '/quiz/courses/<int:course_id>/quizzes')
