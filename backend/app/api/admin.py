from datetime import datetime
from flask import current_app, request
from flask_jwt_extended import jwt_required
from app.cache import invalidate_quiz_cache
from flask_restful import Resource, reqparse
from app.utils import admin_required, cache_key
from app.models import Course, Chapter, Quiz, Question, User, Submission, db


class CourseResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Create new course"""
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True, help='Course name is required')
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
        """List all courses"""
        # Try to get from cache first
        cache_key_name = 'admin_courses_list'
        cached_result = current_app.cache.get(cache_key_name)
        
        if cached_result:
            return cached_result
        
        courses = Course.query.all()
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
    def put(self, course_id):
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
        """Create quiz"""
        parser = reqparse.RequestParser()
        parser.add_argument('chapter_id', type=int, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('date_of_quiz', type=str, help='Format: YYYY-MM-DD HH:MM:SS')
        parser.add_argument('time_duration', type=str, help='Format: HH:MM')
        parser.add_argument('is_scheduled', type=bool, default=False)
        parser.add_argument('remarks', type=str, default='')
        args = parser.parse_args()
        
        chapter = Chapter.query.get(args['chapter_id'])
        if not chapter:
            return {'message': 'Chapter not found'}, 404
        
        # Parse date if provided
        date_of_quiz = None
        if args['date_of_quiz']:
            try:
                date_of_quiz = datetime.strptime(args['date_of_quiz'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}, 400
        
        quiz = Quiz(
            chapter_id=args['chapter_id'],
            title=args['title'],
            date_of_quiz=date_of_quiz,
            time_duration=args['time_duration'],
            is_scheduled=args['is_scheduled'],
            remarks=args['remarks']
        )
        
        db.session.add(quiz)
        db.session.commit()
        
        # Clear caches
        current_app.cache.delete(f'chapter_{args["chapter_id"]}_quizzes')
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
                'remarks': quiz.remarks
            }
        }, 201


class QuizDetailResource(Resource):
    @jwt_required()
    @admin_required
    def put(self, quiz_id):
        """Update quiz"""
        parser = reqparse.RequestParser()
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('date_of_quiz', type=str)
        parser.add_argument('time_duration', type=str)
        parser.add_argument('is_scheduled', type=bool, default=False)
        parser.add_argument('remarks', type=str, default='')
        args = parser.parse_args()
        
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return {'message': 'Quiz not found'}, 404
        
        # Parse date if provided
        if args['date_of_quiz']:
            try:
                quiz.date_of_quiz = datetime.strptime(args['date_of_quiz'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                return {'message': 'Invalid date format. Use YYYY-MM-DD HH:MM:SS'}, 400
        
        quiz.title = args['title']
        quiz.time_duration = args['time_duration']
        quiz.is_scheduled = args['is_scheduled']
        quiz.remarks = args['remarks']
        
        db.session.commit()
        
        # Clear caches
        current_app.cache.delete(f'chapter_{quiz.chapter_id}_quizzes')
        current_app.cache.delete('upcoming_quizzes')
        current_app.cache.delete('open_quizzes')
        current_app.cache.delete(f'quiz_{quiz_id}_details')
        
        return {
            'message': 'Quiz updated successfully',
            'quiz': {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'title': quiz.title,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'is_scheduled': quiz.is_scheduled,
                'remarks': quiz.remarks
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
        parser.add_argument('question_type', type=str, required=True, choices=['MCQ', 'MSQ', 'NAT'])
        parser.add_argument('options', type=list, location='json')
        parser.add_argument('correct_answer', type=list, location='json', required=True)
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
        parser.add_argument('question_type', type=str, required=True, choices=['MCQ', 'MSQ', 'NAT'])
        parser.add_argument('options', type=list, location='json')
        parser.add_argument('correct_answer', type=list, location='json', required=True)
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
        total_submissions = Submission.query.count()
        
        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_submissions = Submission.query.filter(Submission.timestamp >= week_ago).count()
        
        result = {
            'stats': {
                'users': {
                    'total': total_users,
                    'admins': total_admins
                },
                'content': {
                    'courses': total_courses,
                    'chapters': total_chapters,
                    'quizzes': total_quizzes,
                    'questions': total_questions
                },
                'activity': {
                    'total_submissions': total_submissions,
                    'recent_submissions': recent_submissions
                }
            }
        }
        
        # Cache for 10 minutes
        current_app.cache.set(cache_key_name, result, timeout=600)
        return result


class AdminExportResource(Resource):
    @jwt_required()
    @admin_required
    def post(self):
        """Trigger admin export (async)"""
        # TODO: Implement with Celery
        return {
            'message': 'Export job started',
            'job_id': 'admin_export_123',  # Would be actual Celery job ID
            'status': 'pending'
        }


def register_admin_routes(api):
    """Register admin routes"""
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
    api.add_resource(QuestionDetailResource, '/admin/questions/<int:question_id>')
    
    # Search and dashboard
    api.add_resource(SearchUsersResource, '/admin/search/users')
    api.add_resource(SearchQuizzesResource, '/admin/search/quizzes')
    api.add_resource(DashboardStatsResource, '/admin/dashboard/stats')
    api.add_resource(AdminExportResource, '/admin/export/csv')
