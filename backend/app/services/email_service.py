import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import current_app
from app.models import User, Quiz
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
    }
}


class EmailService:
    """Email service for sending certificates and notifications"""

    def __init__(self):
        self._initialized = False
        self.smtp_server = None
        self.smtp_port = None
        self.smtp_username = None
        self.smtp_password = None
        self.smtp_use_tls = None
        self.sender_email = None
        self.sender_name = None

    def _ensure_initialized(self):
        """Initialize configuration when first needed"""
        if not self._initialized:
            from flask import current_app
            self.smtp_server = current_app.config.get(
                'MAIL_SERVER', 'localhost')
            self.smtp_port = current_app.config.get('MAIL_PORT', 587)
            self.smtp_username = current_app.config.get('MAIL_USERNAME', '')
            self.smtp_password = current_app.config.get('MAIL_PASSWORD', '')
            self.smtp_use_tls = current_app.config.get('MAIL_USE_TLS', True)
            self.sender_email = current_app.config.get(
                'MAIL_DEFAULT_SENDER', 'noreply@quizzo.com')
            self.sender_name = current_app.config.get(
                'MAIL_SENDER_NAME', 'Quizzo Team')
            self._initialized = True

    def send_email(self, recipient_email: str, subject: str, html_body: str, attachments: list = None):
        """Send an email with optional attachments"""
        self._ensure_initialized()

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.sender_name} <{self.sender_email}>"
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
            if self.smtp_username and self.smtp_password:
                # Use authenticated SMTP
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                if self.smtp_use_tls:
                    server.starttls()
                server.login(self.smtp_username, self.smtp_password)
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
        # TODO: Implement daily reminder functionality
        pass

    def send_monthly_report_email(self, user_id: int):
        """Send monthly report email to user"""
        self._ensure_initialized()
        # TODO: Implement monthly report functionality
        pass


# Global email service instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get the global email service instance"""
    return email_service
