from datetime import datetime
from flask import current_app, request
from flask_jwt_extended import jwt_required
from app.cache import invalidate_quiz_cache
from app.services.report_generator import ReportGenerator
from flask_restful import Resource, reqparse
from app.utils import admin_required, cache_key
from app.models import Course, Chapter, Quiz, Question, User, Subscription, Submission, db
from sqlalchemy import func, extract


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
                    chapter_quiz_counts = {
                        'total': len(chapter.quizzes),
                        'live': 0,
                        'upcoming': 0,
                        'general': 0
                    }

                    # Count quizzes by type
                    for quiz in chapter.quizzes:
                        if quiz.is_scheduled and quiz.date_of_quiz:
                            if quiz.date_of_quiz <= datetime.now():
                                chapter_quiz_counts['live'] += 1
                                live_quizzes += 1
                            else:
                                chapter_quiz_counts['upcoming'] += 1
                                upcoming_quizzes += 1
                        else:
                            chapter_quiz_counts['general'] += 1
                            general_quizzes += 1

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
            chapter_quiz_counts = {
                'total': len(chapter.quizzes),
                'live': 0,
                'upcoming': 0,
                'general': 0
            }

            # Count quizzes by type
            for quiz in chapter.quizzes:
                if quiz.is_scheduled and quiz.date_of_quiz:
                    if quiz.date_of_quiz <= datetime.now():
                        chapter_quiz_counts['live'] += 1
                    else:
                        chapter_quiz_counts['upcoming'] += 1
                else:
                    chapter_quiz_counts['general'] += 1

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
        """Create quiz"""
        parser = reqparse.RequestParser()
        parser.add_argument('chapter_id', type=int, required=True)
        parser.add_argument('title', type=str, required=True)
        parser.add_argument('date_of_quiz', type=str,
                            help='Format: YYYY-MM-DD HH:MM:SS')
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
                date_of_quiz = datetime.strptime(
                    args['date_of_quiz'], '%Y-%m-%d %H:%M:%S')
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
                quiz.date_of_quiz = datetime.strptime(
                    args['date_of_quiz'], '%Y-%m-%d %H:%M:%S')
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
        total_submissions = Submission.query.count()

        # Recent activity (last 7 days)
        from datetime import datetime, timedelta
        week_ago = datetime.now() - timedelta(days=7)
        recent_submissions = Submission.query.filter(
            Submission.timestamp >= week_ago).count()

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
                    'total_submissions': total_submissions,
                    'recent_submissions': recent_submissions
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
            # Get user's submission count and average score
            submissions = Submission.query.filter_by(user_id=user.id).all()
            submission_count = len(submissions)

            if submissions:
                total_marks = sum(s.obtained_marks for s in submissions)
                total_possible = sum(s.total_marks for s in submissions)
                avg_score = round(
                    (total_marks / total_possible * 100), 2) if total_possible > 0 else 0
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
                    'quiz_attempts': submission_count,
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
