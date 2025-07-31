from datetime import datetime
from flask import current_app, request
from flask_jwt_extended import jwt_required
from app.cache import invalidate_quiz_cache
from app.services.report_generator import ReportGenerator
from flask_restful import Resource, reqparse
from app.utils import admin_required, cache_key, categorize_quizzes, get_quiz_status
from app.models import Course, Chapter, Quiz, Question, User, Subscription, Submission, db
from sqlalchemy import func, extract


def revaluate_quiz_submissions(quiz_id):
    """Revaluate all submissions for a quiz after questions have been updated"""

    # Get all questions for the quiz
    questions = Question.query.filter_by(quiz_id=quiz_id).all()

    # Get all unique users who submitted this quiz
    user_submissions = db.session.query(Submission.user_id).filter_by(
        quiz_id=quiz_id).distinct().all()

    for (user_id,) in user_submissions:
        # Get all submissions for this user and quiz
        user_quiz_submissions = Submission.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).all()

        # Create a mapping of question_id to submission
        submission_map = {
            sub.question_id: sub for sub in user_quiz_submissions}

        # Revaluate each question
        for question in questions:
            if question.id in submission_map:
                submission = submission_map[question.id]

                # Revaluate the answer
                is_correct = False
                user_answer = submission.answer
                correct_answer = question.correct_answer

                if question.question_type == 'MCQ':
                    # For MCQ, check if selected option matches correct option
                    if isinstance(user_answer, list) and len(user_answer) > 0:
                        is_correct = user_answer[0] == correct_answer[0]

                elif question.question_type == 'MSQ':
                    # For MSQ, check if all selected options match correct options
                    if isinstance(user_answer, list) and isinstance(correct_answer, list):
                        user_set = set(user_answer)
                        correct_set = set(correct_answer)
                        is_correct = user_set == correct_set

                elif question.question_type == 'NAT':
                    # For NAT, check if numeric answer matches
                    if isinstance(user_answer, list) and len(user_answer) > 0 and len(correct_answer) > 0:
                        try:
                            user_num = float(user_answer[0])
                            correct_num = float(correct_answer[0])
                            # Allow small floating point differences
                            is_correct = abs(user_num - correct_num) < 0.01
                        except (ValueError, TypeError):
                            is_correct = False

                # Update the submission
                submission.is_correct = is_correct

        db.session.commit()

    # Clear relevant caches
    current_app.cache.delete(f'quiz_{quiz_id}_results')
    current_app.cache.delete(f'quiz_{quiz_id}_stats')

    # Clear user-specific caches for all affected users
    for (user_id,) in user_submissions:
        current_app.cache.delete(f'user_{user_id}_quiz_stats')
        current_app.cache.delete(f'user_{user_id}_submissions')


class CourseResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create new course"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='Course name is required')
        parser.add_argument('description', type=str, default='')
        args = parser.parse_args()

        course = Course(
            name=args['name'],
            description=args['description']
        )

        db.session.add(course)
        db.session.commit()

        # Clear courses cache
        current_app.cache.delete('admin_courses_list')

        return {
            'message': 'Course created successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'description': course.description
            }
        }, 201

    @jwt_required()
    @admin_required
    def get(self):
        """List all courses with detailed info"""
        from flask import request

        # Check if detailed view is requested
        detailed = request.args.get('detailed', 'false').lower() == 'true'
        search_query = request.args.get('search', '').lower()

        # Try to get from cache first
        cache_key_name = f'admin_courses_list_{"detailed" if detailed else "simple"}_{search_query}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        courses_query = Course.query
        if search_query:
            courses_query = courses_query.filter(
                Course.name.ilike(f'%{search_query}%'))

        courses = courses_query.all()

        if detailed:
            # Return detailed course info for management interface
            result_courses = []
            for course in courses:
                # Get quiz counts by type for each chapter
                chapters_data = []
                total_quizzes = 0
                live_quizzes = 0
                upcoming_quizzes = 0
                general_quizzes = 0

                for chapter in course.chapters:
                    # Use new categorization function
                    categorized = categorize_quizzes(
                        chapter.quizzes, datetime.now())

                    chapter_quiz_counts = {
                        'total': len(chapter.quizzes),
                        'live': len(categorized['live']),
                        'upcoming': len(categorized['upcoming']),
                        'general': len(categorized['general']),
                        'ended': len(categorized['ended'])
                    }

                    # Update totals
                    live_quizzes += chapter_quiz_counts['live']
                    upcoming_quizzes += chapter_quiz_counts['upcoming']
                    general_quizzes += chapter_quiz_counts['general']

                    total_quizzes += chapter_quiz_counts['total']

                    chapters_data.append({
                        'id': chapter.id,
                        'name': chapter.name,
                        'description': chapter.description,
                        'quiz_counts': chapter_quiz_counts
                    })

                course_data = {
                    'id': course.id,
                    'name': course.name,
                    'description': course.description,
                    'chapters_count': len(course.chapters),
                    'total_quizzes': total_quizzes,
                    'live_quizzes': live_quizzes,
                    'upcoming_quizzes': upcoming_quizzes,
                    'general_quizzes': general_quizzes,
                    'chapters': chapters_data
                }
                result_courses.append(course_data)

            result = {'courses': result_courses}
        else:
            # Return simple course info
            result = {
                'courses': [
                    {
                        'id': course.id,
                        'name': course.name,
                        'description': course.description,
                        'chapters_count': len(course.chapters)
                    }
                    for course in courses
                ]
            }

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result


class CourseDetailResource(Resource):
    @jwt_required()
    @admin_required
    def get(self, course_id):
        """Get detailed course info with chapters"""
        course = Course.query.get(course_id)
        if not course:
            return {'message': 'Course not found'}, 404

        # Get chapters with detailed quiz info
        chapters_data = []
        for chapter in course.chapters:
            # Use new categorization function
            categorized = categorize_quizzes(chapter.quizzes, datetime.now())

            chapter_quiz_counts = {
                'total': len(chapter.quizzes),
                'live': len(categorized['live']),
                'upcoming': len(categorized['upcoming']),
                'general': len(categorized['general']),
                'ended': len(categorized['ended'])
            }

            chapters_data.append({
                'id': chapter.id,
                'name': chapter.name,
                'description': chapter.description,
                'quiz_counts': chapter_quiz_counts
            })

        return {
            'course': {
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'chapters_count': len(course.chapters),
                'chapters': chapters_data
            }
        }

    @jwt_required()
    @admin_required
    def put(self, course_id):
        """Update course and chapters"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, default='')
        parser.add_argument('chapters', type=list, location='json', default=[])
        args = parser.parse_args()

        course = Course.query.get(course_id)
        if not course:
            return {'message': 'Course not found'}, 404

        # Update course details
        course.name = args['name']
        course.description = args['description']

        # Process chapters
        existing_chapter_ids = {ch.id for ch in course.chapters}
        new_chapter_ids = set()

        for chapter_data in args['chapters']:
            chapter_id = chapter_data.get('id')
            if chapter_id and chapter_id in existing_chapter_ids:
                # Update existing chapter
                chapter = Chapter.query.get(chapter_id)
                if chapter:
                    chapter.name = chapter_data.get('name', chapter.name)
                    chapter.description = chapter_data.get(
                        'description', chapter.description)
                    new_chapter_ids.add(chapter_id)
            elif not chapter_id:
                # Create new chapter
                new_chapter = Chapter(
                    course_id=course_id,
                    name=chapter_data.get('name', ''),
                    description=chapter_data.get('description', '')
                )
                db.session.add(new_chapter)
                db.session.flush()  # Get the ID
                new_chapter_ids.add(new_chapter.id)

        # Delete chapters that were removed
        chapters_to_delete = existing_chapter_ids - new_chapter_ids
        for chapter_id in chapters_to_delete:
            chapter = Chapter.query.get(chapter_id)
            if chapter:
                db.session.delete(chapter)

        db.session.commit()

        # Clear caches
        current_app.cache.delete('admin_courses_list_detailed_')
        current_app.cache.delete('admin_courses_list_simple_')
        current_app.cache.delete(f'course_{course_id}_chapters')

        return {
            'message': 'Course updated successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'description': course.description
            }
        }

    @jwt_required()
    @admin_required
    def put_old(self, course_id):
        """Update course"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, default='')
        args = parser.parse_args()

        course = Course.query.get(course_id)
        if not course:
            return {'message': 'Course not found'}, 404

        course.name = args['name']
        course.description = args['description']

        db.session.commit()

        # Clear cache
        current_app.cache.delete('admin_courses_list')

        return {
            'message': 'Course updated successfully',
            'course': {
                'id': course.id,
                'name': course.name,
                'description': course.description
            }
        }

    @jwt_required()
    @admin_required
    def delete(self, course_id):
        """Delete course"""
        course = Course.query.get(course_id)
        if not course:
            return {'message': 'Course not found'}, 404

        db.session.delete(course)
        db.session.commit()

        # Clear cache
        current_app.cache.delete('admin_courses_list')

        return {'message': 'Course deleted successfully'}


class ChapterResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create new chapter"""
        parser = reqparse.RequestParser()
        parser.add_argument('course_id', type=int, required=True)
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, default='')
        args = parser.parse_args()

        course = Course.query.get(args['course_id'])
        if not course:
            return {'message': 'Course not found'}, 404

        chapter = Chapter(
            course_id=args['course_id'],
            name=args['name'],
            description=args['description']
        )

        db.session.add(chapter)
        db.session.commit()

        # Clear related caches
        current_app.cache.delete('admin_courses_list')
        current_app.cache.delete(f'course_{args["course_id"]}_chapters')

        return {
            'message': 'Chapter created successfully',
            'chapter': {
                'id': chapter.id,
                'course_id': chapter.course_id,
                'name': chapter.name,
                'description': chapter.description
            }
        }, 201


class ChapterDetailResource(Resource):
    @jwt_required()
    @admin_required
    def put(self, chapter_id):
        """Update chapter"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True)
        parser.add_argument('description', type=str, default='')
        args = parser.parse_args()

        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        chapter.name = args['name']
        chapter.description = args['description']

        db.session.commit()

        # Clear caches
        current_app.cache.delete('admin_courses_list')
        current_app.cache.delete(f'course_{chapter.course_id}_chapters')

        return {
            'message': 'Chapter updated successfully',
            'chapter': {
                'id': chapter.id,
                'course_id': chapter.course_id,
                'name': chapter.name,
                'description': chapter.description
            }
        }

    @jwt_required()
    @admin_required
    def delete(self, chapter_id):
        """Delete chapter"""
        chapter = Chapter.query.get(chapter_id)
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        course_id = chapter.course_id
        db.session.delete(chapter)
        db.session.commit()

        # Clear caches
        current_app.cache.delete('admin_courses_list')
        current_app.cache.delete(f'course_{course_id}_chapters')

        return {'message': 'Chapter deleted successfully'}


class QuizResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create quiz with questions"""
        data = request.get_json()

        if not data:
            return {'message': 'No data provided'}, 400

        # Validate required fields
        required_fields = ['chapter_id', 'title']
        for field in required_fields:
            if field not in data:
                return {'message': f'{field} is required'}, 400

        chapter = Chapter.query.get(data['chapter_id'])
        if not chapter:
            return {'message': 'Chapter not found'}, 404

        # Parse date if provided
        date_of_quiz = None
        if data.get('date_of_quiz') and data.get('is_scheduled'):
            try:
                # Handle ISO format from frontend
                date_str = data['date_of_quiz']
                if 'T' in date_str:
                    date_of_quiz = datetime.fromisoformat(
                        date_str.replace('Z', '+00:00'))
                else:
                    date_of_quiz = datetime.strptime(
                        date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid date format'}, 400

        # Create quiz
        quiz = Quiz(
            chapter_id=data['chapter_id'],
            title=data['title'],
            date_of_quiz=date_of_quiz,
            time_duration=data.get('time_duration'),
            is_scheduled=data.get('is_scheduled', False),
            remarks=data.get('remarks', '')
        )

        db.session.add(quiz)
        db.session.flush()  # Get quiz ID

        # Create questions if provided
        questions_data = data.get('questions', [])
        created_questions = []

        for question_data in questions_data:
            if not question_data.get('question_statement') or not question_data.get('question_type'):
                continue

            question = Question(
                quiz_id=quiz.id,
                question_statement=question_data['question_statement'],
                question_type=question_data['question_type'],
                options=question_data.get('options'),
                correct_answer=question_data.get('correct_answer', []),
                marks=question_data.get('marks', 1.0)
            )

            db.session.add(question)
            created_questions.append(question)

        db.session.commit()

        # Clear caches
        current_app.cache.delete(f'chapter_{data["chapter_id"]}_quizzes')
        current_app.cache.delete(
            f'public_chapter_{data["chapter_id"]}_quizzes')
        current_app.cache.delete('upcoming_quizzes')
        current_app.cache.delete('open_quizzes')

        return {
            'message': 'Quiz created successfully',
            'quiz': {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'title': quiz.title,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'question_count': len(created_questions)
            }
        }, 201


class QuizDetailResource(Resource):
    @jwt_required()
    @admin_required
    def get(self, quiz_id):
        """Get quiz details with questions for editing"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        # Get questions for this quiz
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        return {
            'quiz': {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'title': quiz.title,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'questions': [
                    {
                        'id': q.id,
                        'question_statement': q.question_statement,
                        'question_type': q.question_type,
                        'options': q.options,
                        'correct_answer': q.correct_answer,
                        'marks': q.marks
                    }
                    for q in questions
                ]
            }
        }

    @jwt_required()
    @admin_required
    def put(self, quiz_id):
        """Update quiz with questions"""
        data = request.get_json()

        if not data:
            return {'message': 'No data provided'}, 400

        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        # Parse date if provided
        date_of_quiz = None
        if data.get('date_of_quiz') and data.get('is_scheduled'):
            try:
                # Handle ISO format from frontend
                date_str = data['date_of_quiz']
                if 'T' in date_str:
                    date_of_quiz = datetime.fromisoformat(
                        date_str.replace('Z', '+00:00'))
                else:
                    date_of_quiz = datetime.strptime(
                        date_str, '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid date format'}, 400

        # Update quiz basic info
        quiz.title = data.get('title', quiz.title)
        quiz.date_of_quiz = date_of_quiz
        quiz.time_duration = data.get('time_duration')
        quiz.is_scheduled = data.get('is_scheduled', False)
        quiz.remarks = data.get('remarks', '')

        # Handle questions update
        questions_data = data.get('questions', [])

        # Check if this is a general quiz (not scheduled) and has existing submissions
        needs_revaluation = False
        if not quiz.is_scheduled:
            existing_submissions = Submission.query.filter_by(
                quiz_id=quiz_id).first()
            if existing_submissions:
                needs_revaluation = True

        # Delete existing questions (simple approach - could be optimized)
        Question.query.filter_by(quiz_id=quiz_id).delete()

        # Create new questions
        created_questions = []
        for question_data in questions_data:
            if not question_data.get('question_statement') or not question_data.get('question_type'):
                continue

            question = Question(
                quiz_id=quiz.id,
                question_statement=question_data['question_statement'],
                question_type=question_data['question_type'],
                options=question_data.get('options'),
                correct_answer=question_data.get('correct_answer', []),
                marks=question_data.get('marks', 1.0)
            )

            db.session.add(question)
            created_questions.append(question)

        db.session.commit()

        # Perform revaluation if needed
        if needs_revaluation:
            try:
                revaluate_quiz_submissions(quiz_id)
                message = 'Quiz updated successfully and submissions revaluated'
            except Exception as e:
                current_app.logger.error(
                    f"Revaluation failed for quiz {quiz_id}: {str(e)}")
                message = 'Quiz updated successfully but revaluation failed'
        else:
            message = 'Quiz updated successfully'

        # Clear caches
        current_app.cache.delete(f'chapter_{quiz.chapter_id}_quizzes')
        current_app.cache.delete(f'public_chapter_{quiz.chapter_id}_quizzes')
        current_app.cache.delete('upcoming_quizzes')
        current_app.cache.delete('open_quizzes')
        current_app.cache.delete(f'quiz_{quiz_id}_details')
        current_app.cache.delete(f'quiz_{quiz_id}_questions_user')

        return {
            'message': message,
            'quiz': {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'title': quiz.title,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks,
                'question_count': len(created_questions)
            }
        }

    @jwt_required()
    @admin_required
    def delete(self, quiz_id):
        """Delete quiz"""
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        chapter_id = quiz.chapter_id
        db.session.delete(quiz)
        db.session.commit()

        # Clear caches
        current_app.cache.delete(f'chapter_{chapter_id}_quizzes')
        current_app.cache.delete('upcoming_quizzes')
        current_app.cache.delete('open_quizzes')
        current_app.cache.delete(f'quiz_{quiz_id}_details')

        return {'message': 'Quiz deleted successfully'}


class QuestionResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create question"""
        parser = reqparse.RequestParser()
        parser.add_argument('quiz_id', type=int, required=True)
        parser.add_argument('question_statement', type=str, required=True)
        parser.add_argument('question_type', type=str,
                            required=True, choices=['MCQ', 'MSQ', 'NAT'])
        parser.add_argument('options', type=list, location='json')
        parser.add_argument('correct_answer', type=list,
                            location='json', required=True)
        parser.add_argument('marks', type=float, default=1.0)
        args = parser.parse_args()

        quiz = Quiz.query.get(args['quiz_id'])
        if not quiz:
            return {'message': 'Quiz not found'}, 404

        question = Question(
            quiz_id=args['quiz_id'],
            question_statement=args['question_statement'],
            question_type=args['question_type'],
            options=args['options'],
            correct_answer=args['correct_answer'],
            marks=args['marks']
        )

        db.session.add(question)
        db.session.commit()

        # Clear quiz cache
        current_app.cache.delete(f'quiz_{args["quiz_id"]}_questions')
        current_app.cache.delete(f'quiz_{args["quiz_id"]}_details')

        return {
            'message': 'Question created successfully',
            'question': {
                'id': question.id,
                'quiz_id': question.quiz_id,
                'question_statement': question.question_statement,
                'question_type': question.question_type,
                'options': question.options,
                'marks': question.marks
            }
        }, 201


class QuestionDetailResource(Resource):
    @jwt_required()
    @admin_required
    def put(self, question_id):
        """Edit question"""
        parser = reqparse.RequestParser()
        parser.add_argument('question_statement', type=str, required=True)
        parser.add_argument('question_type', type=str,
                            required=True, choices=['MCQ', 'MSQ', 'NAT'])
        parser.add_argument('options', type=list, location='json')
        parser.add_argument('correct_answer', type=list,
                            location='json', required=True)
        parser.add_argument('marks', type=float, default=1.0)
        args = parser.parse_args()

        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found'}, 404

        question.question_statement = args['question_statement']
        question.question_type = args['question_type']
        question.options = args['options']
        question.correct_answer = args['correct_answer']
        question.marks = args['marks']

        db.session.commit()

        # Clear caches
        current_app.cache.delete(f'quiz_{question.quiz_id}_questions')
        current_app.cache.delete(f'quiz_{question.quiz_id}_details')

        return {
            'message': 'Question updated successfully',
            'question': {
                'id': question.id,
                'quiz_id': question.quiz_id,
                'question_statement': question.question_statement,
                'question_type': question.question_type,
                'options': question.options,
                'marks': question.marks
            }
        }

    @jwt_required()
    @admin_required
    def delete(self, question_id):
        """Delete question"""
        question = Question.query.get(question_id)
        if not question:
            return {'message': 'Question not found'}, 404

        quiz_id = question.quiz_id
        db.session.delete(question)
        db.session.commit()

        # Clear caches
        current_app.cache.delete(f'quiz_{quiz_id}_questions')
        current_app.cache.delete(f'quiz_{quiz_id}_details')

        return {'message': 'Question deleted successfully'}


class SearchUsersResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Search users"""
        query_text = request.args.get('query', '')
        role = request.args.get('role')
        limit = int(request.args.get('limit', 50))

        query = User.query

        if query_text:
            search = f"%{query_text}%"
            query = query.filter(
                (User.name.like(search)) |
                (User.username.like(search)) |
                (User.email.like(search))
            )

        if role and role in ['user', 'admin']:
            query = query.filter(User.role == role)

        users = query.limit(limit).all()

        return {
            'users': [
                {
                    'id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
                for user in users
            ]
        }


class SearchQuizzesResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Search quizzes"""
        from flask import request

        query_text = request.args.get('query', '')
        chapter_id = request.args.get('chapter_id', type=int)
        is_scheduled = request.args.get('is_scheduled', type=bool)
        limit = int(request.args.get('limit', 50))

        query = Quiz.query.join(Chapter)

        if query_text:
            search = f"%{query_text}%"
            query = query.filter(Quiz.title.like(search))

        if chapter_id:
            query = query.filter(Quiz.chapter_id == chapter_id)

        if is_scheduled is not None:
            query = query.filter(Quiz.is_scheduled == is_scheduled)

        quizzes = query.limit(limit).all()

        return {
            'quizzes': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'course': quiz.chapter.course.name,
                    'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                    'is_scheduled': quiz.is_scheduled
                }
                for quiz in quizzes
            ]
        }


class DashboardStatsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Admin dashboard statistics"""
        cache_key_name = 'admin_dashboard_stats'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Get basic counts
        total_users = User.query.filter_by(role='user').count()
        total_admins = User.query.filter_by(role='admin').count()
        total_courses = Course.query.count()
        total_chapters = Chapter.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()

        # Count unique quiz attempts (unique user-quiz combinations)
        total_quiz_attempts = db.session.query(
            Submission.user_id,
            Submission.quiz_id
        ).distinct().count()

        # Recent activity (last 7 days) - also count unique attempts
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_quiz_attempts = db.session.query(
            Submission.user_id,
            Submission.quiz_id
        ).filter(
            Submission.timestamp >= week_ago
        ).distinct().count()

        # User engagement stats
        subscribed_users = db.session.query(
            User.id).join(Subscription).distinct().count()
        subscription_rate = (subscribed_users /
                             total_users * 100) if total_users > 0 else 0

        result = {
            'stats': {
                'users': {
                    'total': total_users,
                    'admins': total_admins,
                    'subscribed': subscribed_users,
                    'subscription_rate': round(subscription_rate, 2)
                },
                'content': {
                    'courses': total_courses,
                    'chapters': total_chapters,
                    'quizzes': total_quizzes,
                    'questions': total_questions
                },
                'activity': {
                    'total_submissions': total_quiz_attempts,
                    'recent_submissions': recent_quiz_attempts
                }
            }
        }

        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result


class DashboardChartsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Dashboard charts data"""
        cache_key_name = 'admin_dashboard_charts'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        from datetime import datetime, timedelta

        # User signups over time (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        user_signups = db.session.query(
            func.date(User.created_at).label('date'),
            func.count(User.id).label('count')
        ).filter(
            User.created_at >= thirty_days_ago,
            User.role == 'user'
        ).group_by(func.date(User.created_at)).all()

        # Quiz submission volume by day (last 30 days)
        submission_volume = db.session.query(
            func.date(Submission.timestamp).label('date'),
            func.count(Submission.id).label('count')
        ).filter(
            Submission.timestamp >= thirty_days_ago
        ).group_by(func.date(Submission.timestamp)).all()

        # Course popularity (submission counts)
        course_popularity = db.session.query(
            Course.name,
            func.count(Submission.id).label('submissions')
        ).select_from(Course).join(Chapter).join(Quiz).join(Submission).group_by(Course.id, Course.name).all()

        # User engagement data
        total_users = User.query.filter_by(role='user').count()
        subscribed_users = db.session.query(
            User.id).join(Subscription).distinct().count()
        unsubscribed_users = total_users - subscribed_users

        result = {
            'user_signups': [
                {'date': str(item.date), 'count': item.count}
                for item in user_signups
            ],
            'submission_volume': [
                {'date': str(item.date), 'count': item.count}
                for item in submission_volume
            ],
            'course_popularity': [
                {'course': item.name, 'submissions': item.submissions}
                for item in course_popularity
            ],
            'user_engagement': {
                'subscribed': subscribed_users,
                'unsubscribed': unsubscribed_users
            }
        }

        # Cache for 15 minutes
        current_app.cache.set(cache_key_name, result, timeout=900)
        return result


class CourseAnalyticsResource(Resource):
    @jwt_required()
    @admin_required
    def get(self, course_id):
        """Course-specific analytics"""
        cache_key_name = f'admin_course_analytics_{course_id}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        course = Course.query.get_or_404(course_id)

        # Chapter quiz attempt rates
        chapter_analytics = db.session.query(
            Chapter.name,
            func.count(Submission.id).label('attempts')
        ).select_from(Chapter).outerjoin(Quiz).outerjoin(Submission).filter(
            Chapter.course_id == course_id
        ).group_by(Chapter.id, Chapter.name).all()

        # Today's live quizzes for this course - SIMPLIFIED
        from datetime import date

        today = date.today()
        print(f"Looking for quizzes on {today} for course {course_id}")

        # Simple query: quizzes with date_of_quiz = today's date
        live_quizzes = Quiz.query.join(Chapter).filter(
            Chapter.course_id == course_id,
            func.date(Quiz.date_of_quiz) == today,
            Quiz.date_of_quiz.isnot(None)  # Must have a time set
        ).all()

        print(f"Found {len(live_quizzes)} live quizzes for course {course_id}")

        # Debug: Show what we found
        for quiz in live_quizzes:
            print(f"Quiz: {quiz.title}, Date: {quiz.date_of_quiz}")

        result = {
            'course_name': course.name,
            'chapter_analytics': [
                {'chapter': item.name, 'attempts': item.attempts}
                for item in chapter_analytics
            ],
            'live_quizzes_today': [
                {
                    'id': quiz.id,
                    'title': quiz.title,
                    'chapter': quiz.chapter.name,
                    'time': quiz.date_of_quiz.strftime('%H:%M') if quiz.date_of_quiz else None
                }
                for quiz in live_quizzes
            ]
        }

        # Cache for 30 minutes
        current_app.cache.set(cache_key_name, result, timeout=1800)
        return result


class UsersManagementResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get all users with their stats and search functionality"""
        search_query = request.args.get('search', '').strip()
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)

        # Build cache key based on search parameters
        cache_key_name = f'admin_users_management_{search_query}_{page}_{per_page}'
        cached_result = current_app.cache.get(cache_key_name)

        if cached_result:
            return cached_result

        # Start with base query (exclude admin users)
        query = User.query.filter_by(role='user')

        # Apply search filter
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (User.name.like(search)) |
                (User.username.like(search)) |
                (User.email.like(search))
            )

        # Get total count
        total_users = query.count()

        # Apply pagination
        users = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        ).items

        # Get user stats
        users_data = []
        for user in users:
            # Get user's submission count (unique quizzes taken)
            quiz_submissions = db.session.query(Submission.quiz_id).filter_by(
                user_id=user.id).distinct().count()

            if quiz_submissions > 0:
                # Get all submissions for the user
                submissions = Submission.query.filter_by(user_id=user.id).all()

                # Group submissions by quiz and calculate scores
                quiz_scores = {}
                for submission in submissions:
                    quiz_id = submission.quiz_id
                    if quiz_id not in quiz_scores:
                        quiz_scores[quiz_id] = {
                            'correct': 0,
                            'total': 0
                        }

                    quiz_scores[quiz_id]['total'] += 1
                    if submission.is_correct:
                        quiz_scores[quiz_id]['correct'] += 1

                # Calculate average score across all quizzes
                if quiz_scores:
                    total_score = sum(
                        scores['correct'] / scores['total'] * 100 for scores in quiz_scores.values())
                    avg_score = round(total_score / len(quiz_scores), 2)
                else:
                    avg_score = 0
            else:
                avg_score = 0

            # Get user's subscription count
            subscription_count = Subscription.query.filter_by(
                user_id=user.id).count()

            users_data.append({
                'id': user.id,
                'name': user.name or 'N/A',
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'stats': {
                    'quiz_attempts': quiz_submissions,
                    'subscriptions': subscription_count,
                    'average_score': avg_score
                }
            })

        result = {
            'users': users_data,
            'total_users': total_users,
            'page': page,
            'per_page': per_page,
            'has_next': len(users) == per_page and (page * per_page) < total_users,
            'has_prev': page > 1
        }

        # Cache for 5 minutes
        current_app.cache.set(cache_key_name, result, timeout=300)
        return result

    @jwt_required()
    @admin_required
    def delete(self):
        """Delete a user and all associated data"""
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int,
                            required=True, help='User ID is required')
        args = parser.parse_args()

        user = User.query.get_or_404(args['user_id'])

        if user.role == 'admin':
            return {'message': 'Cannot delete admin users'}, 400

        try:
            # Delete all user's data in correct order to avoid foreign key constraints

            # 1. Delete user's submissions first
            submissions_deleted = Submission.query.filter_by(
                user_id=user.id).delete()

            # 2. Delete user's subscriptions
            subscriptions_deleted = Subscription.query.filter_by(
                user_id=user.id).delete()

            # 3. Finally delete the user
            db.session.delete(user)
            db.session.commit()

            # Clear all related caches
            current_app.cache.delete_pattern('admin_users_management*')
            current_app.cache.delete('admin_dashboard_stats')
            current_app.cache.delete('admin_charts_data')

            current_app.logger.info(
                f"Admin deleted user {user.username} (ID: {user.id}). "
                f"Removed {submissions_deleted} submissions, {subscriptions_deleted} subscriptions."
            )

            return {
                'message': 'User and all associated data deleted successfully',
                'deleted_items': {
                    'submissions': submissions_deleted,
                    'subscriptions': subscriptions_deleted
                }
            }, 200

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(
                f"Error deleting user {user.id}: {str(e)}")
            return {'message': 'Failed to delete user'}, 500


class AdminExportResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Trigger admin export (async)"""
        try:
            report_gen = ReportGenerator()
            job_id = report_gen.export_admin_data()

            return {
                'message': 'Export job started',
                'job_id': job_id,
                'status': 'running',
                'download_url': f'/api/export/download/admin/{job_id}'
            }
        except Exception as e:
            current_app.logger.error(f"Admin export failed: {str(e)}")
            return {'message': 'Failed to start export'}, 500


class AdminDataExportResource(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Export all admin data as CSV"""
        from flask import make_response
        import csv
        import io

        try:
            # Prepare CSV data
            output = io.StringIO()
            writer = csv.writer(output)

            # Write header
            writer.writerow(['Quizzo Admin Data Export'])
            writer.writerow(
                ['Generated on:', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
            writer.writerow([])  # Empty row

            # Users data
            writer.writerow(['USERS'])
            writer.writerow(['ID', 'Name', 'Username',
                            'Email', 'Role', 'Created At'])

            users = User.query.order_by(User.created_at.desc()).all()
            for user in users:
                writer.writerow([
                    user.id,
                    user.name or '',
                    user.username,
                    user.email,
                    user.role,
                    user.created_at.strftime(
                        '%Y-%m-%d %H:%M:%S') if user.created_at else ''
                ])

            writer.writerow([])  # Empty row

            # Courses data
            writer.writerow(['COURSES'])
            writer.writerow(['ID', 'Name', 'Description', 'Chapters Count'])

            courses = Course.query.all()
            for course in courses:
                chapters_count = Chapter.query.filter_by(
                    course_id=course.id).count()
                writer.writerow([
                    course.id,
                    course.name,
                    course.description or '',
                    chapters_count
                ])

            writer.writerow([])  # Empty row

            # Chapters data
            writer.writerow(['CHAPTERS'])
            writer.writerow(['ID', 'Name', 'Course', 'Description',
                            'Quizzes Count', 'Subscriptions Count'])

            chapters = db.session.query(Chapter, Course).join(Course).all()
            for chapter, course in chapters:
                quizzes_count = Quiz.query.filter_by(
                    chapter_id=chapter.id).count()
                subscriptions_count = Subscription.query.filter_by(
                    chapter_id=chapter.id).count()
                writer.writerow([
                    chapter.id,
                    chapter.name,
                    course.name,
                    chapter.description or '',
                    quizzes_count,
                    subscriptions_count
                ])

            writer.writerow([])  # Empty row

            # Quizzes data
            writer.writerow(['QUIZZES'])
            writer.writerow(['ID', 'Title', 'Chapter', 'Course', 'Date',
                            'Time Duration', 'Questions Count', 'Submissions Count'])

            quizzes = db.session.query(Quiz, Chapter, Course).join(
                Chapter, Quiz.chapter_id == Chapter.id
            ).join(
                Course, Chapter.course_id == Course.id
            ).all()

            for quiz, chapter, course in quizzes:
                questions_count = Question.query.filter_by(
                    quiz_id=quiz.id).count()
                submissions_count = db.session.query(Submission.user_id).filter_by(
                    quiz_id=quiz.id).distinct().count()
                writer.writerow([
                    quiz.id,
                    quiz.title,
                    chapter.name,
                    course.name,
                    quiz.date_of_quiz.strftime(
                        '%Y-%m-%d') if quiz.date_of_quiz else '',
                    quiz.time_duration or '',
                    questions_count,
                    submissions_count
                ])

            writer.writerow([])  # Empty row

            # Questions data
            writer.writerow(['QUESTIONS'])
            writer.writerow(
                ['ID', 'Quiz', 'Chapter', 'Course', 'Type', 'Marks'])

            questions = db.session.query(Question, Quiz, Chapter, Course).join(
                Quiz, Question.quiz_id == Quiz.id
            ).join(
                Chapter, Quiz.chapter_id == Chapter.id
            ).join(
                Course, Chapter.course_id == Course.id
            ).all()

            for question, quiz, chapter, course in questions:
                writer.writerow([
                    question.id,
                    quiz.title,
                    chapter.name,
                    course.name,
                    question.question_type or '',
                    question.marks or 0
                ])

            writer.writerow([])  # Empty row

            # Subscriptions data
            writer.writerow(['SUBSCRIPTIONS'])
            writer.writerow(
                ['ID', 'User', 'Chapter', 'Course', 'Subscribed On'])

            subscriptions = db.session.query(Subscription, User, Chapter, Course).join(
                User, Subscription.user_id == User.id
            ).join(
                Chapter, Subscription.chapter_id == Chapter.id
            ).join(
                Course, Chapter.course_id == Course.id
            ).order_by(Subscription.subscribed_on.desc()).all()

            for subscription, user, chapter, course in subscriptions:
                writer.writerow([
                    subscription.id,
                    user.username,
                    chapter.name,
                    course.name,
                    subscription.subscribed_on.strftime(
                        '%Y-%m-%d %H:%M:%S') if subscription.subscribed_on else ''
                ])

            writer.writerow([])  # Empty row

            # Submissions summary
            writer.writerow(['SUBMISSIONS SUMMARY'])
            writer.writerow(['User', 'Quiz', 'Chapter', 'Course', 'Score', 'Correct Answers',
                            'Total Questions', 'Percentage', 'Time Taken', 'Attempted On'])

            # Get quiz submissions grouped by user and quiz
            submission_groups = db.session.query(
                Submission.user_id,
                Submission.quiz_id,
                func.count(Submission.id).label('total_questions'),
                func.sum(func.cast(Submission.is_correct, db.Integer)
                         ).label('correct_answers'),
                func.min(Submission.timestamp).label('first_submission'),
                func.max(Submission.timestamp).label('last_submission')
            ).group_by(
                Submission.user_id,
                Submission.quiz_id
            ).order_by(func.max(Submission.timestamp).desc()).all()

            for group in submission_groups:
                # Get user, quiz, chapter, course info
                user = User.query.get(group.user_id)
                quiz = Quiz.query.get(group.quiz_id)
                if not user or not quiz:
                    continue

                chapter = Chapter.query.get(quiz.chapter_id)
                course = Course.query.get(
                    chapter.course_id) if chapter else None

                # Calculate time taken
                time_taken = ''
                if group.first_submission and group.last_submission:
                    time_diff = group.last_submission - group.first_submission
                    minutes = int(time_diff.total_seconds() // 60)
                    seconds = int(time_diff.total_seconds() % 60)
                    time_taken = f"{minutes}min {seconds}sec"

                # Calculate percentage
                percentage = 0
                if group.total_questions > 0:
                    percentage = round(
                        (group.correct_answers / group.total_questions) * 100, 2)

                writer.writerow([
                    user.username if user else '',
                    quiz.title if quiz else '',
                    chapter.name if chapter else '',
                    course.name if course else '',
                    f"{group.correct_answers}/{group.total_questions}",
                    group.correct_answers,
                    group.total_questions,
                    f"{percentage}%",
                    time_taken,
                    group.last_submission.strftime(
                        '%Y-%m-%d %H:%M:%S') if group.last_submission else ''
                ])

            # Create the response
            csv_data = output.getvalue()
            output.close()

            response = make_response(csv_data)
            response.headers['Content-Type'] = 'text/csv'
            response.headers[
                'Content-Disposition'] = f'attachment; filename=admin_data_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'

            return response

        except Exception as e:
            current_app.logger.error(f"Admin data export failed: {str(e)}")
            return {'message': 'Failed to export admin data'}, 500


def register_admin_api(api):
    # Course management
    api.add_resource(CourseResource, '/admin/courses')
    api.add_resource(CourseDetailResource, '/admin/courses/<int:course_id>')

    # Chapter management
    api.add_resource(ChapterResource, '/admin/chapters')
    api.add_resource(ChapterDetailResource, '/admin/chapters/<int:chapter_id>')

    # Quiz management
    api.add_resource(QuizResource, '/admin/quizzes')
    api.add_resource(QuizDetailResource, '/admin/quizzes/<int:quiz_id>')

    # Question management
    api.add_resource(QuestionResource, '/admin/questions')
    api.add_resource(QuestionDetailResource,
                     '/admin/questions/<int:question_id>')

    # Search and dashboard
    api.add_resource(SearchUsersResource, '/admin/search/users')
    api.add_resource(SearchQuizzesResource, '/admin/search/quizzes')
    api.add_resource(DashboardStatsResource, '/admin/dashboard/stats')
    api.add_resource(DashboardChartsResource, '/admin/dashboard/charts')
    api.add_resource(CourseAnalyticsResource,
                     '/admin/courses/<int:course_id>/analytics')
    api.add_resource(UsersManagementResource, '/admin/users')
    api.add_resource(AdminExportResource, '/admin/export/csv')
    api.add_resource(AdminDataExportResource, '/admin/export-data')
