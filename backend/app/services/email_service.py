import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from app.models import User, Quiz, Subscription, Submission
from datetime import datetime, timedelta
from app.utils import get_user_quiz_stats
import tempfile
import os


EMAIL_TEMPLATES = {
    'certificate_completion': {
        'subject': '🎉 Congratulations! Your Quiz Certificate is Ready - {quiz_title}',
        'html_template': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f7fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; }}
                .header {{ background: linear-gradient(135deg, #4A90E2, #357ABD); padding: 30px; text-align: center; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 30px; }}
                .congratulations {{ background: linear-gradient(135deg, #f8f9ff, #e8f0ff); border-radius: 10px; padding: 20px; margin: 20px 0; text-align: center; }}
                .quiz-details {{ background: #f8f9fa; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .score-highlight {{ font-size: 24px; font-weight: bold; color: #4A90E2; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; }}
                .button {{ display: inline-block; background: #4A90E2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Certificate Ready!</h1>
                </div>
                
                <div class="content">
                    <div class="congratulations">
                        <h2>Congratulations, {user_name}!</h2>
                        <p>You have successfully completed the quiz and earned your certificate!</p>
                    </div>
                    
                    <div class="quiz-details">
                        <h3>Quiz Details:</h3>
                        <p><strong>Quiz:</strong> {quiz_title}</p>
                        <p><strong>Course:</strong> {course_name}</p>
                        <p><strong>Chapter:</strong> {chapter_name}</p>
                        <p><strong>Completion Date:</strong> {completion_date}</p>
                        
                        <div style="text-align: center; margin: 20px 0;">
                            <div class="score-highlight">{score_percentage}% Score</div>
                            <p>You answered {total_questions} questions and scored {obtained_marks}/{total_marks} marks</p>
                        </div>
                    </div>
                    
                    <p>Your certificate is attached to this email as a PDF file. You can also download it anytime from your dashboard.</p>
                    
                    <div style="text-align: center;">
                        <a href="{dashboard_url}" class="button">View Dashboard</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Thank you for using Quizzo Learning Platform!</p>
                    <p>Certificate ID: {certificate_id}</p>
                </div>
            </div>
        </body>
        </html>
        '''
    },
    'daily_reminder': {
        'subject': '📚 Quiz Reminders - Upcoming Quizzes Tomorrow!',
        'html_template': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f7fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4A90E2, #357ABD); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 30px; }}
                .quiz-item {{ background: #f8f9ff; border-radius: 8px; padding: 15px; margin: 10px 0; border-left: 4px solid #4A90E2; }}
                .button {{ display: inline-block; background: #4A90E2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📚 Quiz Reminders</h1>
                </div>
                
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <p>You have upcoming quizzes scheduled for tomorrow! Don't forget to take them:</p>
                    
                    {quiz_list}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">Go to Dashboard</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Good luck with your quizzes!<br>- Quizzo Team</p>
                </div>
            </div>
        </body>
        </html>
        '''
    },
    'monthly_report': {
        'subject': '📊 Your Monthly Quiz Report - {month_year}',
        'html_template': '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background-color: #f5f7fa; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #4A90E2, #357ABD); padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .header h1 {{ color: white; margin: 0; font-size: 28px; }}
                .content {{ padding: 30px; }}
                .stats-box {{ background: #f8f9ff; border-radius: 8px; padding: 20px; margin: 20px 0; }}
                .stats-title {{ color: #4A90E2; margin-top: 0; font-size: 18px; }}
                .stats-list {{ list-style: none; padding: 0; }}
                .stats-item {{ margin: 8px 0; padding: 8px 0; border-bottom: 1px solid #eee; }}
                .highlight {{ font-size: 24px; font-weight: bold; color: #4A90E2; text-align: center; margin: 15px 0; }}
                .button {{ display: inline-block; background: #4A90E2; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 14px; color: #666; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Monthly Report</h1>
                    <p style="color: #e8f0ff; margin: 10px 0 0 0; font-size: 18px;">{month_year}</p>
                </div>
                
                <div class="content">
                    <p>Hello {user_name},</p>
                    
                    <p>Here's your quiz performance summary for the past month:</p>
                    
                    <div class="stats-box">
                        <h3 class="stats-title">📈 Monthly Activity</h3>
                        <ul class="stats-list">
                            <li class="stats-item"><strong>Quizzes Taken:</strong> {monthly_quizzes}</li>
                            <li class="stats-item"><strong>Questions Answered:</strong> {monthly_questions}</li>
                            <li class="stats-item"><strong>Correct Answers:</strong> {monthly_correct}</li>
                        </ul>
                        <div class="highlight">{monthly_accuracy}% Monthly Accuracy</div>
                    </div>
                    
                    <div class="stats-box">
                        <h3 class="stats-title">🏆 Overall Performance</h3>
                        <ul class="stats-list">
                            <li class="stats-item"><strong>Total Quizzes:</strong> {total_quizzes}</li>
                            <li class="stats-item"><strong>Total Questions:</strong> {total_questions}</li>
                            <li class="stats-item"><strong>Overall Accuracy:</strong> {overall_accuracy}%</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{dashboard_url}" class="button">View Dashboard</a>
                    </div>
                </div>
                
                <div class="footer">
                    <p>Keep up the great work!<br>- Quizzo Team</p>
                </div>
            </div>
        </body>
        </html>
        '''
    }
}


class EmailService:
    """Email service for sending certificates and notifications"""

    def __init__(self):
        self._initialized = False
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_email = None
        self.smtp_password = None
        self.smtp_use_tls = None
        self.sender_name = None

    def _ensure_initialized(self):
        """Initialize configuration when first needed"""
        if not self._initialized:
            from flask import current_app
            self.smtp_server = current_app.config.get(
                'MAIL_SERVER', 'localhost')
            self.smtp_port = current_app.config.get('MAIL_PORT', 587)
            self.smtp_email = current_app.config.get('MAIL_EMAIL', '')
            self.smtp_password = current_app.config.get('MAIL_PASSWORD', '')
            self.smtp_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            self.sender_name = current_app.config.get(
                'MAIL_SENDER_NAME', 'Quizzo Team')
            self._initialized = True

    def send_email(self, recipient_email: str, subject: str, html_body: str, attachments: list = None):
        """Send an email with optional attachments"""
        self._ensure_initialized()

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.smtp_email}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject

            # Add HTML body
            html_part = MIMEText(html_body, 'html')
            msg.attach(html_part)

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if isinstance(attachment, dict):
                        filename = attachment.get('filename', 'attachment')
                        content = attachment.get('content', b'')
                        mimetype = attachment.get(
                            'mimetype', 'application/octet-stream')

                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(content)
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename= {filename}'
                        )
                        msg.attach(part)

            # Send email
            if self.smtp_email and self.smtp_password:
                # Use authenticated SMTP
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
                server.quit()
            else:
                # Use local SMTP without authentication
                server = smtplib.SMTP('localhost', 25)
                server.send_message(msg)
                server.quit()

            current_app.logger.info(
                f"Email sent successfully to {recipient_email}")
            return True

        except Exception as e:
            current_app.logger.error(
                f"Failed to send email to {recipient_email}: {str(e)}")
            return False

    def send_certificate_email(self, user_id: int, quiz_id: int):
        """Send certificate email to user after quiz completion"""
        self._ensure_initialized()

        try:
            # Import certificate generator
            from app.services.certificate_generator import get_certificate_generator
            cert_generator = get_certificate_generator()

            # Check if certificate can be generated
            can_generate, message = cert_generator.can_generate_certificate(
                user_id, quiz_id)
            if not can_generate:
                current_app.logger.warning(
                    f"Cannot generate certificate for user {user_id}, quiz {quiz_id}: {message}")
                return False

            # Get user and certificate data
            user = User.query.get(user_id)
            quiz = Quiz.query.get(quiz_id)

            if not user or not quiz:
                current_app.logger.error(
                    f"User {user_id} or Quiz {quiz_id} not found")
                return False

            certificate_data = cert_generator.get_certificate_data(
                user_id, quiz_id)

            # Generate certificate PDF
            pdf_bytes = cert_generator.generate_certificate_pdf(
                user_id, quiz_id)

            # Prepare email content
            template = EMAIL_TEMPLATES['certificate_completion']
            subject = template['subject'].format(quiz_title=quiz.title)

            # Dashboard URL (you can configure this in app config)
            dashboard_url = current_app.config.get(
                'FRONTEND_DASHBOARD_URL', 'http://localhost:3000/dashboard')

            html_body = template['html_template'].format(
                user_name=user.name,
                quiz_title=quiz.title,
                course_name=quiz.chapter.course.name,
                chapter_name=quiz.chapter.name,
                completion_date=certificate_data['completion_date'],
                score_percentage=certificate_data['score_percentage'],
                total_questions=certificate_data['total_questions'],
                obtained_marks=certificate_data['obtained_marks'],
                total_marks=certificate_data['total_marks'],
                certificate_id=certificate_data['certificate_id'],
                dashboard_url=dashboard_url
            )

            # Prepare attachment
            certificate_filename = f"certificate_{certificate_data['certificate_id']}.pdf"
            attachments = [{
                'filename': certificate_filename,
                'content': pdf_bytes,
                'mimetype': 'application/pdf'
            }]

            # Send email
            success = self.send_email(
                recipient_email=user.email,
                subject=subject,
                html_body=html_body,
                attachments=attachments
            )

            if success:
                current_app.logger.info(
                    f"Certificate email sent to {user.email} for quiz {quiz.title}")

            return success

        except ImportError:
            current_app.logger.error(
                "Certificate generator not available - cannot send certificate email")
            return False
        except Exception as e:
            current_app.logger.error(
                f"Failed to send certificate email: {str(e)}")
            return False

    def send_daily_reminder_email(self, user_id: int):
        """Send daily reminder email to user"""
        self._ensure_initialized()

        try:
            user = User.query.get(user_id)
            if not user:
                current_app.logger.error(f"User {user_id} not found")
                return False

            # Find upcoming quizzes for tomorrow
            tomorrow = datetime.now() + timedelta(days=1)

            # Get user's subscribed chapters
            subscriptions = Subscription.query.filter_by(
                user_id=user_id, is_active=True).all()
            chapter_ids = [sub.chapter_id for sub in subscriptions]

            if not chapter_ids:
                # No subscriptions, no reminders needed
                return False

            # Get upcoming scheduled quizzes for tomorrow
            upcoming_quizzes = Quiz.query.filter(
                Quiz.chapter_id.in_(chapter_ids),
                Quiz.is_scheduled == True,
                Quiz.date_of_quiz >= datetime.now(),
                Quiz.date_of_quiz <= tomorrow
            ).all()

            if not upcoming_quizzes:
                # No upcoming quizzes, no reminder needed
                return False

            # Prepare email content
            template = EMAIL_TEMPLATES['daily_reminder']
            subject = template['subject']

            # Dashboard URL
            dashboard_url = current_app.config.get(
                'FRONTEND_DASHBOARD_URL', 'http://localhost:3000/dashboard')

            # Generate quiz list HTML
            quiz_list_html = ""
            for quiz in upcoming_quizzes:
                quiz_time = quiz.date_of_quiz.strftime(
                    '%I:%M %p') if quiz.date_of_quiz else 'TBD'
                quiz_list_html += f'''
                <div class="quiz-item">
                    <h4 style="margin: 0 0 10px 0; color: #4A90E2;">{quiz.title}</h4>
                    <p style="margin: 5px 0;"><strong>Course:</strong> {quiz.chapter.course.name}</p>
                    <p style="margin: 5px 0;"><strong>Chapter:</strong> {quiz.chapter.name}</p>
                    <p style="margin: 5px 0;"><strong>Time:</strong> {quiz_time}</p>
                    <p style="margin: 5px 0;"><strong>Duration:</strong> {quiz.time_duration or 'No limit'}</p>
                </div>
                '''

            html_body = template['html_template'].format(
                user_name=user.name,
                quiz_list=quiz_list_html,
                dashboard_url=dashboard_url
            )

            # Send email
            success = self.send_email(
                recipient_email=user.email,
                subject=subject,
                html_body=html_body
            )

            if success:
                current_app.logger.info(
                    f"Daily reminder email sent to {user.email} for {len(upcoming_quizzes)} upcoming quizzes")

            return success

        except Exception as e:
            current_app.logger.error(
                f"Failed to send daily reminder email to user {user_id}: {str(e)}")
            return False

    def send_monthly_report_email(self, user_id: int):
        """Send monthly report email to user"""
        self._ensure_initialized()

        try:
            user = User.query.get(user_id)
            if not user:
                current_app.logger.error(f"User {user_id} not found")
                return False

            # Calculate monthly stats (last 30 days)
            last_month = datetime.now() - timedelta(days=30)

            recent_submissions = Submission.query.filter(
                Submission.user_id == user_id,
                Submission.timestamp >= last_month
            ).all()

            if not recent_submissions:
                # No activity in the last month, skip sending report
                current_app.logger.info(
                    f"No recent activity for user {user_id}, skipping monthly report")
                return False

            # Calculate monthly statistics
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

            # Get overall statistics
            overall_stats = get_user_quiz_stats(user_id)

            # Prepare email content
            template = EMAIL_TEMPLATES['monthly_report']
            month_year = datetime.now().strftime('%B %Y')
            subject = template['subject'].format(month_year=month_year)

            # Dashboard URL
            dashboard_url = current_app.config.get(
                'FRONTEND_DASHBOARD_URL', 'http://localhost:3000/dashboard')

            html_body = template['html_template'].format(
                user_name=user.name,
                month_year=month_year,
                monthly_quizzes=monthly_stats['quizzes_taken'],
                monthly_questions=monthly_stats['questions_answered'],
                monthly_correct=monthly_stats['correct_answers'],
                monthly_accuracy=round(monthly_stats['accuracy'], 1),
                total_quizzes=overall_stats['total_quizzes'],
                total_questions=overall_stats['total_questions'],
                overall_accuracy=round(overall_stats['overall_accuracy'], 1),
                dashboard_url=dashboard_url
            )

            # Send email
            success = self.send_email(
                recipient_email=user.email,
                subject=subject,
                html_body=html_body
            )

            if success:
                current_app.logger.info(
                    f"Monthly report email sent to {user.email} with {monthly_stats['quizzes_taken']} quizzes taken")

            return success

        except Exception as e:
            current_app.logger.error(
                f"Failed to send monthly report email to user {user_id}: {str(e)}")
            return False

    def send_bulk_daily_reminders(self):
        """Send daily reminder emails to all users with upcoming quizzes"""
        self._ensure_initialized()

        try:
            # Find users who have upcoming quizzes tomorrow
            tomorrow = datetime.now() + timedelta(days=1)

            upcoming_quizzes = Quiz.query.filter(
                Quiz.is_scheduled == True,
                Quiz.date_of_quiz >= datetime.now(),
                Quiz.date_of_quiz <= tomorrow
            ).all()

            if not upcoming_quizzes:
                current_app.logger.info(
                    "No upcoming quizzes for tomorrow, no reminders to send")
                return {'sent': 0, 'failed': 0}

            # Get all chapters with upcoming quizzes
            chapter_ids = [q.chapter_id for q in upcoming_quizzes]

            # Find users subscribed to these chapters
            subscribed_users = User.query.join(Subscription).filter(
                Subscription.chapter_id.in_(chapter_ids),
                Subscription.is_active == True,
                User.role == 'user'
            ).distinct().all()

            sent_count = 0
            failed_count = 0

            for user in subscribed_users:
                try:
                    success = self.send_daily_reminder_email(user.id)
                    if success:
                        sent_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    current_app.logger.error(
                        f"Failed to send reminder to user {user.id}: {e}")
                    failed_count += 1

            current_app.logger.info(
                f"Daily reminders completed: {sent_count} sent, {failed_count} failed")
            return {'sent': sent_count, 'failed': failed_count}

        except Exception as e:
            current_app.logger.error(
                f"Failed to send bulk daily reminders: {str(e)}")
            return {'sent': 0, 'failed': 1}

    def send_bulk_monthly_reports(self):
        """Send monthly report emails to all active users"""
        self._ensure_initialized()

        try:
            # Get all users with role 'user'
            users = User.query.filter_by(role='user').all()

            sent_count = 0
            failed_count = 0

            for user in users:
                try:
                    success = self.send_monthly_report_email(user.id)
                    if success:
                        sent_count += 1
                    else:
                        # User might not have activity, that's okay
                        pass
                except Exception as e:
                    current_app.logger.error(
                        f"Failed to send monthly report to user {user.id}: {e}")
                    failed_count += 1

            current_app.logger.info(
                f"Monthly reports completed: {sent_count} sent, {failed_count} failed")
            return {'sent': sent_count, 'failed': failed_count}

        except Exception as e:
            current_app.logger.error(
                f"Failed to send bulk monthly reports: {str(e)}")
            return {'sent': 0, 'failed': 1}


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get the global email service instance"""
    return email_service
