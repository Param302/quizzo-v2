import os
import csv
import tempfile
import threading
from flask import current_app
from datetime import datetime, timedelta
from app.utils import get_user_quiz_stats, calculate_quiz_score
from app.models import User, Quiz, Question, Submission, Course, Chapter, Subscription, db


class ReportGenerator:

    def __init__(self):
        self.output_dir = None

    def _get_output_dir(self):
        if self.output_dir is None:
            self.output_dir = current_app.config.get(
                'REPORTS_OUTPUT_DIR', '/tmp/quizzo_reports')
        os.makedirs(self.output_dir, exist_ok=True)
        return self.output_dir

    def _generate_job_id(self, report_type: str, user_id: int = None):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if user_id:
            return f"{report_type}_{user_id}_{timestamp}"
        return f"{report_type}_{timestamp}"

    def _update_job_status(self, job_id: str, status: str, progress: int = 0, message: str = "", download_url: str = ""):
        job_status = {
            'job_id': job_id,
            'status': status,  # pending, running, completed, failed
            'progress': progress,
            'message': message,
            'download_url': download_url,
            'created_at': datetime.now().isoformat() + 'Z',
            'updated_at': datetime.now().isoformat() + 'Z'
        }

        if status == 'completed':
            job_status['completed_at'] = datetime.now().isoformat() + 'Z'

        cache_key = f'job_status_{job_id}'
        current_app.cache.set(cache_key, job_status,
                              timeout=3600)  # Cache for 1 hour
        return job_status

    # USER EXPORT FUNCTIONALITY
    def export_user_data(self, user_id: int):
        return self.generate_user_export_async(user_id)

    def download_user_export(self, user_id: int, job_id: str):
        output_dir = self._get_output_dir()
        filename = f'user_export_{job_id}.csv'
        file_path = os.path.join(output_dir, filename)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            return content, filename
        return None, None

    def generate_user_export_async(self, user_id: int):
        job_id = self._generate_job_id('user_export', user_id)

        def background_task():
            try:
                self._update_job_status(
                    job_id, 'running', 10, 'Starting user export...')
                file_path = self._generate_user_export_csv(user_id, job_id)
                download_url = f'/downloads/user_export_{job_id}.csv'
                self._update_job_status(
                    job_id, 'completed', 100, 'User export completed successfully', download_url)
            except Exception as e:
                current_app.logger.error(
                    f"User export failed for job {job_id}: {e}")
                self._update_job_status(
                    job_id, 'failed', 0, f'Export failed: {str(e)}')

        # Start background thread
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

        # Initial job status
        self._update_job_status(job_id, 'pending', 0, 'User export job queued')
        return job_id

    def _generate_user_export_csv(self, user_id: int, job_id: str):
        user = User.query.get(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        self._update_job_status(job_id, 'running', 20,
                                'Collecting user data...')

        # Get user's quiz submissions
        submissions = db.session.query(Submission, Quiz, Question, Chapter, Course).join(
            Quiz, Submission.quiz_id == Quiz.id
        ).join(
            Question, Submission.question_id == Question.id
        ).join(
            Chapter, Quiz.chapter_id == Chapter.id
        ).join(
            Course, Chapter.course_id == Course.id
        ).filter(Submission.user_id == user_id).all()

        self._update_job_status(job_id, 'running', 40,
                                'Processing quiz data...')

        csv_data = []
        for submission, quiz, question, chapter, course in submissions:
            csv_data.append({
                'User ID': user.id,
                'User Name': user.name,
                'Username': user.username,
                'Email': user.email,
                'Course': course.name,
                'Chapter': chapter.name,
                'Quiz ID': quiz.id,
                'Quiz Title': quiz.title,
                'Quiz Date': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else 'Open Quiz',
                'Question ID': question.id,
                'Question Type': question.question_type,
                'Question Statement': question.question_statement[:100] + '...' if len(question.question_statement) > 100 else question.question_statement,
                'Question Marks': question.marks,
                'User Answer': str(submission.answer),
                'Correct Answer': str(question.correct_answer),
                'Is Correct': submission.is_correct,
                'Submission Time': submission.timestamp.isoformat(),
            })

        self._update_job_status(job_id, 'running', 60,
                                'Adding quiz summaries...')

        quiz_ids = db.session.query(Submission.quiz_id).filter_by(
            user_id=user_id).distinct().all()
        quiz_summaries = []

        for (quiz_id,) in quiz_ids:
            quiz = Quiz.query.get(quiz_id)
            score = calculate_quiz_score(quiz_id, user_id)

            quiz_summaries.append({
                'Quiz ID': quiz_id,
                'Quiz Title': quiz.title,
                'Course': quiz.chapter.course.name,
                'Chapter': quiz.chapter.name,
                'Total Questions': len(question for question in quiz.questions),
                'Total Marks': score['total_marks'],
                'Obtained Marks': score['obtained_marks'],
                'Percentage': round(score['percentage'], 2),
                'Completion Date': max([s.timestamp for s in Submission.query.filter_by(user_id=user_id, quiz_id=quiz_id).all()]).isoformat()
            })

        self._update_job_status(job_id, 'running', 80,
                                'Generating CSV file...')

        output_dir = self._get_output_dir()
        filename = f'user_export_{job_id}.csv'
        file_path = os.path.join(output_dir, filename)

        # Write detailed submissions to CSV
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
            else:
                # Empty file with headers only
                fieldnames = ['User ID', 'User Name',
                              'Username', 'Email', 'Message']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerow({
                    'User ID': user.id,
                    'User Name': user.name,
                    'Username': user.username,
                    'Email': user.email,
                    'Message': 'No quiz data available'
                })

        self._update_job_status(job_id, 'running', 90, 'Finalizing export...')

        return file_path

    def export_admin_data(self):
        return self.generate_admin_export_async()

    def download_admin_export(self, job_id: str):
        output_dir = self._get_output_dir()
        filename = f'admin_export_{job_id}.csv'
        file_path = os.path.join(output_dir, filename)

        if os.path.exists(file_path):
            with open(file_path, 'rb') as f:
                content = f.read()
            return content, filename
        return None, None

    def generate_admin_export_async(self):
        job_id = self._generate_job_id('admin_export')

        def background_task():
            try:
                self._update_job_status(
                    job_id, 'running', 10, 'Starting admin export...')
                file_path = self._generate_admin_export_csv(job_id)
                download_url = f'/downloads/admin_export_{job_id}.xlsx'
                self._update_job_status(
                    job_id, 'completed', 100, 'Admin export completed successfully', download_url)
            except Exception as e:
                current_app.logger.error(
                    f"Admin export failed for job {job_id}: {e}")
                self._update_job_status(
                    job_id, 'failed', 0, f'Export failed: {str(e)}')

        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

        self._update_job_status(job_id, 'pending', 0,
                                'Admin export job queued')
        return job_id

    def _generate_admin_export_csv(self, job_id: str):

        self._update_job_status(job_id, 'running', 15,
                                'Collecting platform data...')

        users = User.query.all()
        courses = Course.query.all()
        chapters = Chapter.query.all()
        quizzes = Quiz.query.all()
        questions = Question.query.all()
        submissions = Submission.query.all()
        subscriptions = Subscription.query.all()

        self._update_job_status(job_id, 'running', 30,
                                'Processing users data...')

        users_data = []
        for user in users:
            stats = get_user_quiz_stats(user.id)
            users_data.append({
                'User ID': user.id,
                'Name': user.name,
                'Username': user.username,
                'Email': user.email,
                'Role': user.role,
                'Total Quizzes': stats['total_quizzes'],
                'Total Questions': stats['total_questions'],
                'Correct Answers': stats['correct_answers'],
                'Accuracy (%)': round(stats['overall_accuracy'], 2) if stats['overall_accuracy'] else 0,
                'Active Subscriptions': len([s for s in subscriptions if s.user_id == user.id and s.is_active])
            })

        self._update_job_status(job_id, 'running', 45,
                                'Processing quizzes data...')

        quizzes_data = []
        for quiz in quizzes:
            participants = len(
                set([s.user_id for s in submissions if s.quiz_id == quiz.id]))
            total_submissions = len(
                [s for s in submissions if s.quiz_id == quiz.id])

            quizzes_data.append({
                'Quiz ID': quiz.id,
                'Title': quiz.title,
                'Course': quiz.chapter.course.name,
                'Chapter': quiz.chapter.name,
                'Is Scheduled': quiz.is_scheduled,
                'Date of Quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else 'Open',
                'Duration': quiz.time_duration or 'No limit',
                'Total Questions': len(quiz.questions),
                'Total Marks': sum(q.marks for q in quiz.questions),
                'Participants': participants,
                'Total Submissions': total_submissions,
                'Remarks': quiz.remarks or ''
            })

        self._update_job_status(job_id, 'running', 60,
                                'Processing submissions data...')

        recent_submissions = Submission.query.order_by(
            Submission.timestamp.desc()).limit(1000).all()
        submissions_data = []
        for submission in recent_submissions:
            submissions_data.append({
                'Submission ID': submission.id,
                'User ID': submission.user_id,
                'User Name': submission.user.name,
                'Quiz ID': submission.quiz_id,
                'Quiz Title': submission.quiz.title,
                'Question ID': submission.question_id,
                'Question Type': submission.question.question_type,
                'User Answer': str(submission.answer),
                'Is Correct': submission.is_correct,
                'Marks': submission.question.marks,
                'Timestamp': submission.timestamp.isoformat()
            })

        self._update_job_status(job_id, 'running', 75,
                                'Processing analytics...')

        total_users = len(users)
        total_quizzes = len(quizzes)
        total_submissions = len(submissions)
        active_users_last_week = len(set(
            [s.user_id for s in submissions if s.timestamp >= datetime.now() - timedelta(days=7)]))

        analytics_data = [{
            'Metric': 'Total Users',
            'Value': total_users
        }, {
            'Metric': 'Total Courses',
            'Value': len(courses)
        }, {
            'Metric': 'Total Chapters',
            'Value': len(chapters)
        }, {
            'Metric': 'Total Quizzes',
            'Value': total_quizzes
        }, {
            'Metric': 'Total Questions',
            'Value': len(questions)
        }, {
            'Metric': 'Total Submissions',
            'Value': total_submissions
        }, {
            'Metric': 'Active Users (Last 7 Days)',
            'Value': active_users_last_week
        }, {
            'Metric': 'Average Submissions per User',
            'Value': round(total_submissions / total_users, 2) if total_users > 0 else 0
        }, {
            'Metric': 'Report Generated On',
            'Value': datetime.now().isoformat()
        }]

        self._update_job_status(job_id, 'running', 90,
                                'Generating CSV file...')

        output_dir = self._get_output_dir()
        filename = f'admin_export_{job_id}.csv'
        file_path = os.path.join(output_dir, filename)

        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow(['=== PLATFORM ANALYTICS ==='])
            writer.writerow(['Metric', 'Value'])
            for item in analytics_data:
                writer.writerow([item['Metric'], item['Value']])
            writer.writerow([])

            writer.writerow(['=== USERS DATA ==='])
            if users_data:
                fieldnames = users_data[0].keys()
                dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(users_data)
            writer.writerow([])

            # Quizzes Section
            writer.writerow(['=== QUIZZES DATA ==='])
            if quizzes_data:
                fieldnames = quizzes_data[0].keys()
                dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(quizzes_data)
            writer.writerow([])

            writer.writerow(['=== RECENT SUBMISSIONS (Last 1000) ==='])
            if submissions_data:
                fieldnames = submissions_data[0].keys()
                dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(submissions_data)
            writer.writerow([])

            writer.writerow(['=== COURSES DATA ==='])
            courses_data = [{
                'Course ID': c.id,
                'Course Name': c.name,
                'Description': c.description or '',
                'Total Chapters': len(c.chapters),
                'Total Quizzes': sum(len(ch.quizzes) for ch in c.chapters)
            } for c in courses]
            if courses_data:
                fieldnames = courses_data[0].keys()
                dict_writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                dict_writer.writeheader()
                dict_writer.writerows(courses_data)

        return file_path

    def send_daily_reminders(self):
        return self.send_daily_reminders_async()

    def send_monthly_reports(self):
        return self.send_monthly_reports_async()

    def send_daily_reminders_async(self):
        job_id = self._generate_job_id('daily_reminder')

        def background_task():
            try:
                self._update_job_status(
                    job_id, 'running', 10, 'Starting daily reminders...')
                result = self._send_daily_reminders(job_id)
                self._update_job_status(
                    job_id, 'completed', 100, f'Daily reminders sent: {result["sent"]} emails, {result["failed"]} failed')
            except Exception as e:
                current_app.logger.error(
                    f"Daily reminders failed for job {job_id}: {e}")
                self._update_job_status(
                    job_id, 'failed', 0, f'Daily reminders failed: {str(e)}')

        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

        self._update_job_status(job_id, 'pending', 0,
                                'Daily reminder job queued')
        return job_id

    def _send_daily_reminders(self, job_id: str):
        from app.services.email_service import get_email_service

        try:
            email_service = get_email_service()
        except:
            raise Exception("Email service not available")

        self._update_job_status(job_id, 'running', 20,
                                'Finding users for reminders...')

        tomorrow = datetime.now() + timedelta(days=1)
        upcoming_quizzes = Quiz.query.filter(
            Quiz.is_scheduled == True,
            Quiz.date_of_quiz >= datetime.now(),
            Quiz.date_of_quiz <= tomorrow
        ).all()

        chapter_ids = [q.chapter_id for q in upcoming_quizzes]
        subscribed_users = db.session.query(Subscription.user_id).filter(
            Subscription.chapter_id.in_(chapter_ids),
            Subscription.is_active == True
        ).distinct().all()

        user_ids = [u[0] for u in subscribed_users]
        users = User.query.filter(User.id.in_(user_ids)).all()

        self._update_job_status(job_id, 'running', 40,
                                f'Sending reminders to {len(users)} users...')

        sent_count = 0
        failed_count = 0

        for i, user in enumerate(users):
            try:
                user_quizzes = []
                for quiz in upcoming_quizzes:
                    if any(s.chapter_id == quiz.chapter_id for s in user.subscriptions if s.is_active):
                        user_quizzes.append(quiz)

                if user_quizzes:
                    self._send_reminder_email(
                        email_service, user, user_quizzes)
                    sent_count += 1

                progress = 40 + int((i + 1) / len(users) * 50)
                self._update_job_status(
                    job_id, 'running', progress, f'Processed {i + 1}/{len(users)} users...')

            except Exception as e:
                current_app.logger.error(
                    f"Failed to send reminder to user {user.id}: {e}")
                failed_count += 1

        return {'sent': sent_count, 'failed': failed_count}

    def _send_reminder_email(self, email_service, user, quizzes):
        subject = "Quiz Reminders - Upcoming Quizzes Tomorrow!"

        quiz_list = ""
        for quiz in quizzes:
            quiz_list += f"""
            <li style="margin: 10px 0;">
                <strong>{quiz.title}</strong><br>
                Course: {quiz.chapter.course.name}<br>
                Chapter: {quiz.chapter.name}<br>
                Time: {quiz.date_of_quiz.strftime('%I:%M %p') if quiz.date_of_quiz else 'TBD'}<br>
                Duration: {quiz.time_duration or 'No limit'}
            </li>
            """

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f7fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #4A90E2; text-align: center;">Quiz Reminders</h2>
                
                <p>Hello {user.name},</p>
                
                <p>You have upcoming quizzes scheduled for tomorrow! Don't forget to take them:</p>
                
                <ul style="list-style-type: none; padding: 0;">
                    {quiz_list}
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_DASHBOARD_URL', '#')}" 
                       style="background: #4A90E2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Go to Dashboard
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Good luck with your quizzes!<br>
                    - Quizzo Team
                </p>
            </div>
        </body>
        </html>
        """

        return email_service.send_email(user.email, subject, html_body)

    def send_monthly_reports_async(self):
        job_id = self._generate_job_id('monthly_report')

        def background_task():
            try:
                self._update_job_status(
                    job_id, 'running', 10, 'Starting monthly reports...')
                result = self._send_monthly_reports(job_id)
                self._update_job_status(
                    job_id, 'completed', 100, f'Monthly reports sent: {result["sent"]} emails, {result["failed"]} failed')
            except Exception as e:
                current_app.logger.error(
                    f"Monthly reports failed for job {job_id}: {e}")
                self._update_job_status(
                    job_id, 'failed', 0, f'Monthly reports failed: {str(e)}')

        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()

        self._update_job_status(job_id, 'pending', 0,
                                'Monthly report job queued')
        return job_id

    def _send_monthly_reports(self, job_id: str):
        from app.services.email_service import get_email_service

        try:
            email_service = get_email_service()
        except:
            raise Exception("Email service not available")

        self._update_job_status(job_id, 'running', 20,
                                'Generating monthly reports...')

        users = User.query.filter_by(role='user').all()

        sent_count = 0
        failed_count = 0

        for i, user in enumerate(users):
            try:
                self._send_user_monthly_report(email_service, user)
                sent_count += 1

                progress = 20 + int((i + 1) / len(users) * 70)
                self._update_job_status(
                    job_id, 'running', progress, f'Processed {i + 1}/{len(users)} users...')

            except Exception as e:
                current_app.logger.error(
                    f"Failed to send monthly report to user {user.id}: {e}")
                failed_count += 1

        return {'sent': sent_count, 'failed': failed_count}

    def _send_user_monthly_report(self, email_service, user):
        last_month = datetime.now() - timedelta(days=30)

        recent_submissions = Submission.query.filter(
            Submission.user_id == user.id,
            Submission.timestamp >= last_month
        ).all()

        if not recent_submissions:
            return

        quiz_ids = list(set([s.quiz_id for s in recent_submissions]))
        monthly_stats = {
            'quizzes_taken': len(quiz_ids),
            'questions_answered': len(recent_submissions),
            'correct_answers': len([s for s in recent_submissions if s.is_correct]),
            'accuracy': 0
        }

        if monthly_stats['questions_answered'] > 0:
            monthly_stats['accuracy'] = (
                monthly_stats['correct_answers'] / monthly_stats['questions_answered']) * 100

        overall_stats = get_user_quiz_stats(user.id)

        subject = f"Your Monthly Quiz Report - {datetime.now().strftime('%B %Y')}"

        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f7fa;">
            <div style="max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2 style="color: #4A90E2; text-align: center;">Monthly Quiz Report</h2>
                <h3 style="text-align: center; color: #666;">{datetime.now().strftime('%B %Y')}</h3>
                
                <p>Hello {user.name},</p>
                
                <p>Here's your quiz performance summary for the past month:</p>
                
                <div style="background: #f8f9ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #4A90E2; margin-top: 0;">Monthly Activity</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 8px 0;"><strong>Quizzes Taken:</strong> {monthly_stats['quizzes_taken']}</li>
                        <li style="margin: 8px 0;"><strong>Questions Answered:</strong> {monthly_stats['questions_answered']}</li>
                        <li style="margin: 8px 0;"><strong>Correct Answers:</strong> {monthly_stats['correct_answers']}</li>
                        <li style="margin: 8px 0;"><strong>Monthly Accuracy:</strong> {round(monthly_stats['accuracy'], 1)}%</li>
                    </ul>
                </div>
                
                <div style="background: #e8f0ff; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #4A90E2; margin-top: 0;">Overall Performance</h3>
                    <ul style="list-style: none; padding: 0;">
                        <li style="margin: 8px 0;"><strong>Total Quizzes:</strong> {overall_stats['total_quizzes']}</li>
                        <li style="margin: 8px 0;"><strong>Total Questions:</strong> {overall_stats['total_questions']}</li>
                        <li style="margin: 8px 0;"><strong>Overall Accuracy:</strong> {round(overall_stats['overall_accuracy'], 1)}%</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{current_app.config.get('FRONTEND_DASHBOARD_URL', '#')}" 
                       style="background: #4A90E2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        View Dashboard
                    </a>
                </div>
                
                <p style="color: #666; font-size: 14px; text-align: center;">
                    Keep up the great work!<br>
                    - Quizzo Team
                </p>
            </div>
        </body>
        </html>
        """

        return email_service.send_email(user.email, subject, html_body)


def get_report_generator() -> ReportGenerator:
    report_generator = ReportGenerator()
    return report_generator
