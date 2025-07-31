import secrets
import hashlib
from functools import wraps
from app.models import User, db
from flask import jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, get_jwt


def hash_password(password):
    """Hash password using werkzeug security"""
    return generate_password_hash(password)


def verify_password(password, password_hash):
    """Verify password against hash"""
    return check_password_hash(password_hash, password)


def admin_required(f):
    """Decorator to ensure user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        try:
            user_id = int(get_jwt_identity())  # Convert string back to int
        except (ValueError, TypeError):
            return {'message': 'Invalid token format'}, 401

        user = User.query.get(user_id)

        if not user or user.role != 'admin':
            return {'message': 'Admin access required'}, 403

        return f(*args, **kwargs)
    return decorated_function


def user_required(f):
    """Decorator to ensure user is authenticated"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        verify_jwt_in_request()
        try:
            user_id = int(get_jwt_identity())  # Convert string back to int
        except (ValueError, TypeError):
            return {'message': 'Invalid token format'}, 401

        user = User.query.get(user_id)

        if not user:
            return {'message': 'Authentication required'}, 401

        return f(*args, **kwargs)
    return decorated_function


def get_current_user():
    """Get current authenticated user"""
    try:
        user_id = int(get_jwt_identity())  # Convert string back to int
        return User.query.get(user_id)
    except (ValueError, TypeError):
        return None


def cache_key(*args, **kwargs):
    """Generate cache key from arguments"""
    key_parts = [str(arg) for arg in args]
    key_parts.extend([f"{k}:{v}" for k, v in sorted(kwargs.items())])
    key_string = "_".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def calculate_quiz_score(quiz_id, user_id):
    """Calculate quiz score for a user"""
    from app.models import Submission, Question

    submissions = Submission.query.filter_by(
        quiz_id=quiz_id,
        user_id=user_id
    ).all()

    total_marks = 0
    obtained_marks = 0

    for submission in submissions:
        question = Question.query.get(submission.question_id)
        total_marks += question.marks
        if submission.is_correct:
            obtained_marks += question.marks

    return {
        'total_marks': total_marks,
        'obtained_marks': obtained_marks,
        'percentage': (obtained_marks / total_marks * 100) if total_marks > 0 else 0
    }


def get_user_quiz_stats(user_id):
    """Get comprehensive quiz statistics for a user"""
    from app.models import Submission, Quiz

    # Get all quizzes user has participated in
    quiz_ids = db.session.query(Submission.quiz_id).filter_by(
        user_id=user_id).distinct().all()
    quiz_ids = [q[0] for q in quiz_ids]

    stats = {
        'total_quizzes': len(quiz_ids),
        'total_questions': 0,
        'correct_answers': 0,
        'quiz_scores': []
    }

    for quiz_id in quiz_ids:
        score_data = calculate_quiz_score(quiz_id, user_id)
        quiz = Quiz.query.get(quiz_id)

        stats['quiz_scores'].append({
            'quiz_id': quiz_id,
            'quiz_title': quiz.title,
            'score': score_data['percentage']  # Extract the percentage value
        })

        submissions = Submission.query.filter_by(
            quiz_id=quiz_id,
            user_id=user_id
        ).all()

        stats['total_questions'] += len(submissions)
        stats['correct_answers'] += sum(1 for s in submissions if s.is_correct)

    if stats['total_questions'] > 0:
        stats['overall_accuracy'] = (
            stats['correct_answers'] / stats['total_questions']) * 100
    else:
        stats['overall_accuracy'] = 0

    return stats


def validate_quiz_access(quiz_id, user_id):
    """Validate if user can access a quiz"""
    from app.models import Quiz, Subscription
    from datetime import datetime

    quiz = Quiz.query.get(quiz_id)
    if not quiz:
        return False, "Quiz not found"

    # Check if user is subscribed to the chapter
    subscription = Subscription.query.filter_by(
        user_id=user_id,
        chapter_id=quiz.chapter_id,
        is_active=True
    ).first()

    if not subscription:
        return False, "Not subscribed to this chapter"

    # Check if quiz is scheduled and time is valid
    if quiz.is_scheduled and quiz.date_of_quiz:
        if datetime.now() < quiz.date_of_quiz:
            return False, "Quiz not yet started"

    return True, "Access granted"


def format_quiz_result(quiz_id, user_id):
    """Format quiz result with analytics"""
    from app.models import Quiz, Question, Submission

    quiz = Quiz.query.get(quiz_id)
    score = calculate_quiz_score(quiz_id, user_id)

    # Get question-wise performance
    questions = Question.query.filter_by(quiz_id=quiz_id).all()
    question_performance = []

    for question in questions:
        submission = Submission.query.filter_by(
            quiz_id=quiz_id,
            user_id=user_id,
            question_id=question.id
        ).first()

        question_performance.append({
            'question_id': question.id,
            'question_statement': question.question_statement,
            'correct_answer': question.correct_answer,
            'user_answer': submission.answer if submission else None,
            'is_correct': submission.is_correct if submission else False,
            'marks': question.marks
        })

    return {
        'quiz': {
            'id': quiz.id,
            'title': quiz.title,
            'chapter': quiz.chapter.name,
            'course': quiz.chapter.course.name
        },
        'score': score,
        'question_performance': question_performance,
        'completed_at': max([s.timestamp for s in Submission.query.filter_by(
            quiz_id=quiz_id, user_id=user_id
        ).all()]) if Submission.query.filter_by(quiz_id=quiz_id, user_id=user_id).first() else None
    }


def get_quiz_status(quiz, current_time=None):
    """
    Categorize quiz based on current time and quiz schedule.

    Args:
        quiz: Quiz object
        current_time: datetime object (defaults to now)

    Returns:
        str: 'live', 'upcoming', 'ended', or 'general'
    """
    from datetime import datetime, timedelta

    if current_time is None:
        current_time = datetime.now()

    # If quiz is not scheduled, it's always general
    if not quiz.is_scheduled or not quiz.date_of_quiz:
        return 'general'

    quiz_start_time = quiz.date_of_quiz

    # Calculate quiz end time if duration is provided
    quiz_end_time = None
    if quiz.time_duration:
        try:
            # Parse duration in HH:MM format
            hours, minutes = map(int, quiz.time_duration.split(':'))
            duration = timedelta(hours=hours, minutes=minutes)
            quiz_end_time = quiz_start_time + duration
        except (ValueError, AttributeError):
            # If duration parsing fails, assume 2 hours default
            quiz_end_time = quiz_start_time + timedelta(hours=2)
    else:
        # Default duration if not specified
        quiz_end_time = quiz_start_time + timedelta(hours=2)

    if current_time < quiz_start_time:
        return 'upcoming'
    elif current_time >= quiz_start_time and current_time < quiz_end_time:
        return 'live'
    else:  # current_time >= quiz_end_time
        return 'ended'


def categorize_quizzes(quizzes, current_time=None):
    """
    Categorize a list of quizzes into live, upcoming, general, and ended.

    Args:
        quizzes: List of Quiz objects
        current_time: datetime object (defaults to now)

    Returns:
        dict: Dictionary with categorized quizzes
    """
    categorized = {
        'live': [],
        'upcoming': [],
        'general': [],
        'ended': []
    }

    for quiz in quizzes:
        status = get_quiz_status(quiz, current_time)
        categorized[status].append(quiz)

    return categorized
