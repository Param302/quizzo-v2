from datetime import datetime
from flask import current_app
from flask_jwt_extended import jwt_required
from flask_restful import Resource, reqparse
from app.cache import invalidate_user_cache, invalidate_quiz_cache
from app.models import User, Quiz, Question, Submission, Subscription, Chapter, Course, db
from app.utils import user_required, get_current_user, get_user_quiz_stats, validate_quiz_access, calculate_quiz_score


class DashboardResource(Resource):
    @jwt_required()
    @user_required
    def get(self):
        """User dashboard - quiz history, stats, upcoming"""
        user = get_current_user()
        cache_key_name = f'user_{user.id}_dashboard'
        cached_result = current_app.cache.get(cache_key_name)
        
        if cached_result:
            return cached_result
        
        # Get user's subscribed chapters
        subscriptions = Subscription.query.filter_by(user_id=user.id, is_active=True).all()
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
            'recent_quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'course': quiz.chapter.course.name,
                    'score': calculate_quiz_score(quiz.id, user.id)
                }
                for quiz in recent_quizzes
            ],
            'stats': {
                'total_quizzes_taken': stats['total_quizzes'],
                'overall_accuracy': stats['overall_accuracy']
            }
        }
        
        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class QuizMetadataResource(Resource):
    @jwt_required()
    @user_required
    def get(self, quiz_id):
        """Get quiz metadata & questions"""
        user = get_current_user()
        
        # Validate access
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
        
        # Validate access
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
        
        # Process each answer
        submissions = []
        for answer_data in args['answers']:
            question_id = answer_data.get('question_id')
            answer = answer_data.get('answer')
            
            question = Question.query.get(question_id)
            if not question or question.quiz_id != quiz_id:
                continue
            
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
        
        # Clear user caches
        invalidate_user_cache(user.id)
        
        # Calculate and return score
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
        """List chapter subscriptions"""
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
        
        # Check if already subscribed
        existing_sub = Subscription.query.filter_by(
            user_id=user.id,
            chapter_id=args['chapter_id']
        ).first()
        
        if existing_sub:
            if existing_sub.is_active:
                return {'message': 'Already subscribed to this chapter'}, 400
            else:
                # Reactivate subscription
                existing_sub.is_active = True
                existing_sub.subscribed_on = datetime.now()
        else:
            # Create new subscription
            subscription = Subscription(
                user_id=user.id,
                chapter_id=args['chapter_id'],
                subscribed_on=datetime.now(),
                is_active=True
            )
            db.session.add(subscription)
        
        db.session.commit()
        
        # Clear caches
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
    def delete(self):
        """Unsubscribe from chapter"""
        user = get_current_user()
        
        parser = reqparse.RequestParser()
        parser.add_argument('chapter_id', type=int, required=True)
        args = parser.parse_args()
        
        subscription = Subscription.query.filter_by(
            user_id=user.id,
            chapter_id=args['chapter_id'],
            is_active=True
        ).first()
        
        if not subscription:
            return {'message': 'Not subscribed to this chapter'}, 404
        
        subscription.is_active = False
        db.session.commit()
        
        # Clear caches
        invalidate_user_cache(user.id)
        
        return {'message': 'Successfully unsubscribed from chapter'}


class UserExportResource(Resource):
    @jwt_required()
    @user_required
    def post(self):
        """Trigger user quiz export (async)"""
        user = get_current_user()
        
        # TODO: Implement with Celery
        return {
            'message': 'Export job started',
            'job_id': f'user_export_{user.id}_123',  # Would be actual Celery job ID
            'status': 'pending'
        }


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
        
        # Get chapter-wise performance
        subscriptions = Subscription.query.filter_by(user_id=user.id, is_active=True).all()
        chapter_performance = []
        
        for sub in subscriptions:
            chapter_quizzes = Quiz.query.filter_by(chapter_id=sub.chapter_id).all()
            chapter_quiz_ids = [q.id for q in chapter_quizzes]
            
            # Get submissions for this chapter
            chapter_submissions = Submission.query.filter(
                Submission.user_id == user.id,
                Submission.quiz_id.in_(chapter_quiz_ids)
            ).all()
            
            if chapter_submissions:
                total_questions = len(chapter_submissions)
                correct_answers = sum(1 for s in chapter_submissions if s.is_correct)
                accuracy = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
                
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


def register_user_api(api):
    api.add_resource(DashboardResource, '/user/dashboard')
    api.add_resource(QuizMetadataResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(QuizSubmissionResource, '/user/quiz/<int:quiz_id>')
    api.add_resource(SubscriptionsResource, '/user/subscriptions')
    api.add_resource(UserExportResource, '/user/export/csv')
    api.add_resource(UserStatsResource, '/user/stats')
