#!/usr/bin/env python3
"""
Comprehensive Email Testing Script for Quizzo Application

This script:
1. Creates test users, courses, chapters, and quizzes
2. Simulates quiz attempts and submissions
3. Tests all email functionalities (certificates, reminders, monthly reports)
4. Cleans up test data after completion

Usage: python email_test_comprehensive.py
"""

from app.utils import hash_password, calculate_quiz_score
from app.services.email_service import get_email_service
from app.models import db, User, Course, Chapter, Quiz, Question, Submission, Subscription
from app import create_app
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the current directory to Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


class EmailTestSuite:
    """Comprehensive test suite for email functionality"""

    def __init__(self):
        # Ensure absolute path for database
        self.setup_database_path()
        self.app = create_app()
        self.email_service = get_email_service()
        self.test_users = []
        self.test_courses = []
        self.test_chapters = []
        self.test_quizzes = []
        self.test_questions = []
        self.test_submissions = []
        self.test_subscriptions = []

    def setup_database_path(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        instance_dir = os.path.join(current_dir, 'instance')

        # Create instance directory if it doesn't exist
        if not os.path.exists(instance_dir):
            os.makedirs(instance_dir)
            print(f"📁 Created instance directory: {instance_dir}")

        # Set absolute database path
        db_path = os.path.join(instance_dir, 'quiz.db')
        os.environ['DATABASE_URL'] = f'sqlite:///{db_path}'
        print(f"🗃️  Using database: {db_path}")

    def setup_test_data(self):
        """Create all test data needed for email testing"""
        print("🚀 Setting up test data...")

        with self.app.app_context():
            # Create test users
            print("👥 Creating test users...")
            user1 = User(
                name="Test User One",
                username="testuser1",
                email="mrintrovert.730@gmail.com",
                password=hash_password("password123"),
                role="user"
            )
            user2 = User(
                name="Test User Two",
                username="testuser2",
                email="connectwithparam.30@gmail.com",
                password=hash_password("password123"),
                role="user"
            )

            db.session.add(user1)
            db.session.add(user2)
            db.session.commit()

            self.test_users = [user1, user2]
            print(f"✅ Created users: {user1.email}, {user2.email}")

            # Create test course
            print("📚 Creating test course...")
            course = Course(
                name="Email Test Course",
                description="A course created for testing email functionality"
            )
            db.session.add(course)
            db.session.commit()

            self.test_courses = [course]
            print(f"✅ Created course: {course.name}")

            # Create test chapter
            print("📖 Creating test chapter...")
            chapter = Chapter(
                course_id=course.id,
                name="Email Test Chapter",
                description="A chapter for testing email features"
            )
            db.session.add(chapter)
            db.session.commit()

            self.test_chapters = [chapter]
            print(f"✅ Created chapter: {chapter.name}")

            # Create subscriptions for both users
            print("🔔 Creating subscriptions...")
            sub1 = Subscription(user_id=user1.id, chapter_id=chapter.id)
            sub2 = Subscription(user_id=user2.id, chapter_id=chapter.id)

            db.session.add(sub1)
            db.session.add(sub2)
            db.session.commit()

            self.test_subscriptions = [sub1, sub2]
            print("✅ Created subscriptions for both users")

            # Create test quizzes
            print("📝 Creating test quizzes...")

            # Quiz 1 - Available now
            quiz1 = Quiz(
                chapter_id=chapter.id,
                title="Python Basics Quiz",
                date_of_quiz=datetime.now() - timedelta(hours=1),
                time_duration="30:00",
                is_scheduled=False,
                remarks="Basic Python concepts"
            )

            # Quiz 2 - Scheduled for tomorrow (for reminder testing)
            quiz2 = Quiz(
                chapter_id=chapter.id,
                title="Advanced Python Quiz",
                date_of_quiz=datetime.now() + timedelta(days=1),
                time_duration="45:00",
                is_scheduled=True,
                remarks="Advanced Python concepts"
            )

            # Quiz 3 - Available now
            quiz3 = Quiz(
                chapter_id=chapter.id,
                title="Data Structures Quiz",
                date_of_quiz=datetime.now() - timedelta(minutes=30),
                time_duration="40:00",
                is_scheduled=False,
                remarks="Data structures and algorithms"
            )

            # Quiz 4 - Scheduled for tomorrow (another reminder test)
            quiz4 = Quiz(
                chapter_id=chapter.id,
                title="Web Development Quiz",
                date_of_quiz=datetime.now() + timedelta(days=1, hours=2),
                time_duration="60:00",
                is_scheduled=True,
                remarks="Web development fundamentals"
            )

            db.session.add_all([quiz1, quiz2, quiz3, quiz4])
            db.session.commit()

            self.test_quizzes = [quiz1, quiz2, quiz3, quiz4]
            print(f"✅ Created 4 quizzes")

            # Create questions for each quiz
            print("❓ Creating quiz questions...")
            self.create_quiz_questions()

            print("🎉 Test data setup completed!")

    def create_quiz_questions(self):
        """Create questions for all test quizzes"""
        questions_data = [
            # Quiz 1 questions
            {
                'quiz_id': self.test_quizzes[0].id,
                'questions': [
                    {
                        'statement': 'What is the output of print(2 + 2)?',
                        'type': 'MCQ',
                        'options': ['3', '4', '5', '6'],
                        'correct': [1],
                        'marks': 2.0
                    },
                    {
                        'statement': 'Which data type is mutable in Python?',
                        'type': 'MCQ',
                        'options': ['tuple', 'string', 'list', 'int'],
                        'correct': [2],
                        'marks': 2.0
                    },
                    {
                        'statement': 'What are valid Python variable naming conventions?',
                        'type': 'MSQ',
                        'options': ['snake_case', 'camelCase', 'PascalCase', '123start'],
                        'correct': [0, 1, 2],
                        'marks': 3.0
                    }
                ]
            },
            # Quiz 2 questions
            {
                'quiz_id': self.test_quizzes[1].id,
                'questions': [
                    {
                        'statement': 'What is a decorator in Python?',
                        'type': 'MCQ',
                        'options': ['A function that modifies another function', 'A class', 'A module', 'A variable'],
                        'correct': [0],
                        'marks': 3.0
                    },
                    {
                        'statement': 'Which are features of Python generators?',
                        'type': 'MSQ',
                        'options': ['Memory efficient', 'Lazy evaluation', 'Use yield keyword', 'Return multiple values at once'],
                        'correct': [0, 1, 2],
                        'marks': 4.0
                    }
                ]
            },
            # Quiz 3 questions
            {
                'quiz_id': self.test_quizzes[2].id,
                'questions': [
                    {
                        'statement': 'What is the time complexity of binary search?',
                        'type': 'MCQ',
                        'options': ['O(n)', 'O(log n)', 'O(n log n)', 'O(1)'],
                        'correct': [1],
                        'marks': 2.5
                    },
                    {
                        'statement': 'Which data structures use LIFO principle?',
                        'type': 'MSQ',
                        'options': ['Stack', 'Queue', 'Recursion call stack', 'Linked List'],
                        'correct': [0, 2],
                        'marks': 3.0
                    }
                ]
            }
        ]

        for quiz_data in questions_data:
            for q_data in quiz_data['questions']:
                question = Question(
                    quiz_id=quiz_data['quiz_id'],
                    question_statement=q_data['statement'],
                    question_type=q_data['type'],
                    options=q_data['options'],
                    correct_answer=q_data['correct'],
                    marks=q_data['marks']
                )
                db.session.add(question)
                self.test_questions.append(question)

        db.session.commit()
        print(f"✅ Created {len(self.test_questions)} questions")

    def simulate_quiz_attempts(self):
        print("🎮 Simulating quiz attempts...")

        with self.app.app_context():
            users = User.query.filter(User.email.in_([
                'mrintrovert.730@gmail.com',
                'connectwithparam.30@gmail.com'
            ])).all()
            user1, user2 = users[0], users[1]

            # Get quizzes by title to ensure fresh session binding
            quiz1 = Quiz.query.filter_by(title="Python Basics Quiz").first()
            quiz3 = Quiz.query.filter_by(title="Data Structures Quiz").first()

            # User 1 attempts Quiz 1 (Python Basics) - Perfect score
            print("📊 User 1 attempting Python Basics Quiz...")
            self.attempt_quiz(
                user_id=user1.id,
                quiz_id=quiz1.id,
                answers=[
                    [1],      # Correct: 4
                    [2],      # Correct: list
                    [0, 1, 2]  # Correct: all naming conventions
                ]
            )

            # User 1 attempts Quiz 3 (Data Structures) - Partial score
            print("📊 User 1 attempting Data Structures Quiz...")
            self.attempt_quiz(
                user_id=user1.id,
                quiz_id=quiz3.id,
                answers=[
                    [1],   # Correct: O(log n)
                    [0]    # Partial: Only stack (missing recursion call stack)
                ]
            )

            # User 2 attempts Quiz 1 (Python Basics) - Mixed score
            print("📊 User 2 attempting Python Basics Quiz...")
            self.attempt_quiz(
                user_id=user2.id,
                quiz_id=quiz1.id,
                answers=[
                    [1],   # Correct: 4
                    [0],   # Wrong: tuple (should be list)
                    [0, 1]  # Partial: missing PascalCase
                ]
            )

            print("✅ Quiz attempts simulation completed!")

    def attempt_quiz(self, user_id, quiz_id, answers):
        """Simulate a user attempting a quiz with given answers"""
        # Fresh query to ensure objects are bound to current session
        user = User.query.get(user_id)
        quiz = Quiz.query.get(quiz_id)
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        for i, question in enumerate(questions):
            if i < len(answers):
                user_answer = answers[i]
                is_correct = self.check_answer_correctness(
                    question, user_answer)

                submission = Submission(
                    user_id=user_id,
                    quiz_id=quiz_id,
                    question_id=question.id,
                    answer=user_answer,
                    is_correct=is_correct,
                    timestamp=datetime.now() - timedelta(minutes=30-i*5)  # Stagger timestamps
                )
                db.session.add(submission)
                self.test_submissions.append(submission)

        db.session.commit()
        print(f"  ✅ {user.name} completed {quiz.title}")

    def check_answer_correctness(self, question, user_answer):
        """Check if user's answer is correct"""
        correct_answer = question.correct_answer

        if question.question_type == 'MCQ':
            return user_answer == correct_answer
        elif question.question_type == 'MSQ':
            # For MSQ, check if user got all correct options
            return set(user_answer) == set(correct_answer)
        else:  # NAT
            return user_answer == correct_answer

    def test_certificate_emails(self):
        """Test certificate email sending"""
        print("📧 Testing certificate emails...")

        with self.app.app_context():
            # Get users and quizzes from database with fresh queries
            user1 = User.query.filter_by(
                email='mrintrovert.730@gmail.com').first()
            user2 = User.query.filter_by(
                email='connectwithparam.30@gmail.com').first()
            quiz1 = Quiz.query.filter_by(title="Python Basics Quiz").first()
            quiz3 = Quiz.query.filter_by(title="Data Structures Quiz").first()

            # Send certificate for User 1's completed quizzes
            print("📜 Sending certificate for User 1 - Python Basics Quiz...")
            success1 = self.email_service.send_certificate_email(
                user1.id,
                quiz1.id
            )
            print(
                f"  {'✅' if success1 else '❌'} Certificate email result: {success1}")

            print("📜 Sending certificate for User 1 - Data Structures Quiz...")
            success2 = self.email_service.send_certificate_email(
                user1.id,
                quiz3.id
            )
            print(
                f"  {'✅' if success2 else '❌'} Certificate email result: {success2}")

            print("📜 Sending certificate for User 2 - Python Basics Quiz...")
            success3 = self.email_service.send_certificate_email(
                user2.id,
                quiz1.id
            )
            print(
                f"  {'✅' if success3 else '❌'} Certificate email result: {success3}")

    def test_daily_reminder_emails(self):
        """Test daily reminder email sending"""
        print("📧 Testing daily reminder emails...")

        with self.app.app_context():
            # Get users with fresh queries
            user1 = User.query.filter_by(
                email='mrintrovert.730@gmail.com').first()
            user2 = User.query.filter_by(
                email='connectwithparam.30@gmail.com').first()

            print("⏰ Sending daily reminder to User 1...")
            success1 = self.email_service.send_daily_reminder_email(user1.id)
            print(f"  {'✅' if success1 else '❌'} Reminder email result: {success1}")

            print("⏰ Sending daily reminder to User 2...")
            success2 = self.email_service.send_daily_reminder_email(user2.id)
            print(f"  {'✅' if success2 else '❌'} Reminder email result: {success2}")

            print("⏰ Testing bulk daily reminders...")
            bulk_result = self.email_service.send_bulk_daily_reminders()
            print(
                f"  📊 Bulk reminders: {bulk_result['sent']} sent, {bulk_result['failed']} failed")

    def test_monthly_report_emails(self):
        """Test monthly report email sending"""
        print("📧 Testing monthly report emails...")

        with self.app.app_context():
            # Get users with fresh queries
            user1 = User.query.filter_by(
                email='mrintrovert.730@gmail.com').first()
            user2 = User.query.filter_by(
                email='connectwithparam.30@gmail.com').first()

            print("📊 Sending monthly report to User 1...")
            success1 = self.email_service.send_monthly_report_email(user1.id)
            print(f"  {'✅' if success1 else '❌'} Monthly report result: {success1}")

            print("📊 Sending monthly report to User 2...")
            success2 = self.email_service.send_monthly_report_email(user2.id)
            print(f"  {'✅' if success2 else '❌'} Monthly report result: {success2}")

            print("📊 Testing bulk monthly reports...")
            bulk_result = self.email_service.send_bulk_monthly_reports()
            print(
                f"  📊 Bulk reports: {bulk_result['sent']} sent, {bulk_result['failed']} failed")

    def cleanup_test_data(self):
        """Remove all test data from database"""
        print("🧹 Cleaning up test data...")

        with self.app.app_context():
            # Delete in reverse order of dependencies using fresh queries
            print("  🗑️  Removing submissions...")
            test_submissions = Submission.query.join(User).filter(
                User.email.in_(['mrintrovert.730@gmail.com',
                               'connectwithparam.30@gmail.com'])
            ).all()
            for submission in test_submissions:
                db.session.delete(submission)

            print("  🗑️  Removing subscriptions...")
            test_subscriptions = Subscription.query.join(User).filter(
                User.email.in_(['mrintrovert.730@gmail.com',
                               'connectwithparam.30@gmail.com'])
            ).all()
            for subscription in test_subscriptions:
                db.session.delete(subscription)

            print("  🗑️  Removing questions...")
            test_questions = Question.query.join(Quiz).join(Chapter).join(Course).filter(
                Course.name == 'Email Test Course'
            ).all()
            for question in test_questions:
                db.session.delete(question)

            print("  🗑️  Removing quizzes...")
            test_quizzes = Quiz.query.join(Chapter).join(Course).filter(
                Course.name == 'Email Test Course'
            ).all()
            for quiz in test_quizzes:
                db.session.delete(quiz)

            print("  🗑️  Removing chapters...")
            test_chapters = Chapter.query.join(Course).filter(
                Course.name == 'Email Test Course'
            ).all()
            for chapter in test_chapters:
                db.session.delete(chapter)

            print("  🗑️  Removing courses...")
            test_courses = Course.query.filter_by(
                name='Email Test Course').all()
            for course in test_courses:
                db.session.delete(course)

            print("  🗑️  Removing users...")
            test_users = User.query.filter(
                User.email.in_(['mrintrovert.730@gmail.com',
                               'connectwithparam.30@gmail.com'])
            ).all()
            for user in test_users:
                db.session.delete(user)

            db.session.commit()
            print("✅ All test data cleaned up!")

    def run_full_test_suite(self):
        """Run the complete email testing suite"""
        print("🎯 Starting Comprehensive Email Test Suite")
        print("=" * 50)

        with self.app.app_context():
            try:
                # Ensure database tables are created
                print("🗃️  Initializing database...")
                db.create_all()
                print("✅ Database initialized successfully")

                # Setup
                self.setup_test_data()
                print()

                # Simulate quiz activity
                self.simulate_quiz_attempts()
                print()

                # Test all email functionalities
                self.test_certificate_emails()
                print()

                self.test_daily_reminder_emails()
                print()

                self.test_monthly_report_emails()
                print()

                print("🎉 All email tests completed successfully!")

            except Exception as e:
                print(f"❌ Error during testing: {str(e)}")
                import traceback
                print(f"📋 Error details:\n{traceback.format_exc()}")
                raise
            finally:
                # Always cleanup, even if tests fail
                print()
                self.cleanup_test_data()
                print("🏁 Test suite completed!")

    def display_email_config(self):
        """Display current email configuration"""
        with self.app.app_context():
            print("📧 Email Configuration:")
            print(f"  SMTP Server: {self.app.config.get('MAIL_SERVER')}")
            print(f"  SMTP Port: {self.app.config.get('MAIL_PORT')}")
            print(f"  SMTP Email: {self.app.config.get('MAIL_EMAIL')}")
            print(f"  Use TLS: {self.app.config.get('MAIL_USE_TLS')}")
            print(f"  Sender Name: {self.app.config.get('MAIL_SENDER_NAME')}")
            print()


def main():
    """Main function to run the email test suite"""
    print("🚀 Quizzo Email Testing Suite")
    print("=" * 40)

    # Check for required environment variables
    required_env_vars = ['MAIL_SERVER', 'MAIL_EMAIL', 'MAIL_PASSWORD']
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these in your .env file or environment.")
        return

    try:
        # Create and run test suite
        print("🔧 Initializing test suite...")
        test_suite = EmailTestSuite()
        test_suite.display_email_config()
        test_suite.run_full_test_suite()
    except Exception as e:
        print(f"❌ Fatal error: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("  1. Check that the backend directory is accessible")
        print("  2. Verify database permissions")
        print("  3. Ensure all dependencies are installed")
        print("  4. Check your email configuration")
        import traceback
        print(f"\n📋 Full error details:\n{traceback.format_exc()}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code if exit_code else 0)
