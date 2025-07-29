import os
import io
import base64
from jinja2 import Template
from flask import current_app
from datetime import datetime
from weasyprint import HTML, CSS
from app.utils import calculate_quiz_score
from app.models import User, Quiz, Submission, Question


CERTIFICATE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Certificate of Achievement</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Inter:wght@300;400;500;600&display=swap');
        
        body {
            margin: 0;
            padding: 0;
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        
        .certificate-container {
            width: 297mm;
            height: 210mm;
            margin: 0;
            padding: 0;
            position: relative;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            border: 8px solid #4A90E2;
            box-sizing: border-box;
        }
        
        .certificate-border {
            position: absolute;
            top: 15mm;
            left: 15mm;
            right: 15mm;
            bottom: 15mm;
            border: 3px solid #2C5AA0;
            border-radius: 10px;
            background: white;
            box-shadow: inset 0 0 30px rgba(0,0,0,0.1);
        }
        
        .certificate-content {
            padding: 30mm 25mm;
            text-align: center;
            position: relative;
            height: 100%;
            box-sizing: border-box;
        }
        
        .header {
            margin-bottom: 20mm;
        }
        
        .logo {
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #4A90E2, #357ABD);
            border-radius: 50%;
            margin: 0 auto 15mm;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        
        .title {
            font-family: 'Playfair Display', serif;
            font-size: 42px;
            font-weight: 700;
            color: #2C5AA0;
            margin: 0 0 8mm;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        
        .subtitle {
            font-size: 18px;
            color: #666;
            margin: 0 0 15mm;
            font-weight: 300;
        }
        
        .recipient-section {
            margin: 20mm 0;
        }
        
        .awarded-to {
            font-size: 16px;
            color: #888;
            margin-bottom: 8mm;
            font-weight: 400;
        }
        
        .recipient-name {
            font-family: 'Playfair Display', serif;
            font-size: 36px;
            font-weight: 700;
            color: #2C5AA0;
            margin: 0 0 15mm;
            padding-bottom: 5mm;
            border-bottom: 2px solid #4A90E2;
            display: inline-block;
            min-width: 200mm;
        }
        
        .achievement-text {
            font-size: 16px;
            line-height: 1.6;
            color: #555;
            margin: 15mm 0;
            max-width: 200mm;
            margin-left: auto;
            margin-right: auto;
        }
        
        .quiz-details {
            background: linear-gradient(135deg, #f8f9ff, #e8f0ff);
            border-radius: 10px;
            padding: 12mm;
            margin: 15mm 0;
            border: 1px solid #e0e8ff;
        }
        
        .quiz-title {
            font-size: 20px;
            font-weight: 600;
            color: #2C5AA0;
            margin-bottom: 8mm;
        }
        
        .quiz-info {
            display: flex;
            justify-content: space-between;
            font-size: 14px;
            color: #666;
            margin-bottom: 8mm;
        }
        
        .score-section {
            display: flex;
            justify-content: center;
            gap: 20mm;
            margin: 10mm 0;
        }
        
        .score-item {
            text-align: center;
        }
        
        .score-value {
            font-size: 24px;
            font-weight: 700;
            color: #4A90E2;
            display: block;
        }
        
        .score-label {
            font-size: 12px;
            color: #888;
            margin-top: 2mm;
        }
        
        .footer {
            position: absolute;
            bottom: 15mm;
            left: 25mm;
            right: 25mm;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid #ddd;
            padding-top: 8mm;
        }
        
        .certificate-id {
            font-size: 12px;
            color: #888;
        }
        
        .date-issued {
            font-size: 12px;
            color: #888;
        }
        
        .verification-note {
            font-size: 10px;
            color: #aaa;
            text-align: center;
            margin-top: 5mm;
        }
        
        .decorative-elements {
            position: absolute;
            top: 20mm;
            left: 20mm;
            right: 20mm;
            bottom: 20mm;
            pointer-events: none;
        }
        
        .corner-decoration {
            position: absolute;
            width: 30px;
            height: 30px;
            border: 3px solid #4A90E2;
            opacity: 0.3;
        }
        
        .corner-decoration.top-left {
            top: 0;
            left: 0;
            border-right: none;
            border-bottom: none;
        }
        
        .corner-decoration.top-right {
            top: 0;
            right: 0;
            border-left: none;
            border-bottom: none;
        }
        
        .corner-decoration.bottom-left {
            bottom: 0;
            left: 0;
            border-right: none;
            border-top: none;
        }
        
        .corner-decoration.bottom-right {
            bottom: 0;
            right: 0;
            border-left: none;
            border-top: none;
        }
        
        .achievement-badge {
            position: absolute;
            top: 15mm;
            right: 15mm;
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #FFD700, #FFA500);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 20px;
            font-weight: bold;
            box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        }
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="certificate-border">
            <div class="decorative-elements">
                <div class="corner-decoration top-left"></div>
                <div class="corner-decoration top-right"></div>
                <div class="corner-decoration bottom-left"></div>
                <div class="corner-decoration bottom-right"></div>
            </div>
            
            <div class="achievement-badge">★</div>
            
            <div class="certificate-content">
                <div class="header">
                    <div class="logo">Q</div>
                    <h1 class="title">Certificate of Achievement</h1>
                    <p class="subtitle">Quizzo Learning Platform</p>
                </div>
                
                <div class="recipient-section">
                    <p class="awarded-to">This certificate is proudly awarded to</p>
                    <h2 class="recipient-name">{{ user_name }}</h2>
                    
                    <p class="achievement-text">
                        For successfully completing the quiz and demonstrating excellent knowledge and understanding in the subject matter.
                    </p>
                </div>
                
                <div class="quiz-details">
                    <div class="quiz-title">{{ quiz_title }}</div>
                    <div class="quiz-info">
                        <span><strong>Course:</strong> {{ course_name }}</span>
                        <span><strong>Chapter:</strong> {{ chapter_name }}</span>
                    </div>
                    
                    <div class="score-section">
                        <div class="score-item">
                            <span class="score-value">{{ score_percentage }}%</span>
                            <div class="score-label">Overall Score</div>
                        </div>
                        <div class="score-item">
                            <span class="score-value">{{ obtained_marks }}/{{ total_marks }}</span>
                            <div class="score-label">Marks Obtained</div>
                        </div>
                        <div class="score-item">
                            <span class="score-value">{{ total_questions }}</span>
                            <div class="score-label">Questions Answered</div>
                        </div>
                    </div>
                </div>
                
                <div class="footer">
                    <div class="certificate-id">
                        Certificate ID: {{ certificate_id }}
                    </div>
                    <div class="date-issued">
                        Issued on: {{ completion_date }}
                    </div>
                </div>
                
                <div class="verification-note">
                    This certificate can be verified at quizzo.com/verify/{{ certificate_id }}
                </div>
            </div>
        </div>
    </div>
</body>
</html>
"""


class CertificateGenerator:

    def __init__(self):
        self.template = Template(CERTIFICATE_TEMPLATE)

    def generate_certificate_id(self, user_id: int, quiz_id: int) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"CERT-{user_id}-{quiz_id}-{timestamp}"

    def get_certificate_data(self, user_id: int, quiz_id: int) -> dict:
        user = User.query.get(user_id)
        quiz = Quiz.query.get(quiz_id)

        if not user or not quiz:
            raise ValueError("User or Quiz not found")

        submissions = Submission.query.filter_by(
            user_id=user_id,
            quiz_id=quiz_id
        ).all()

        if not submissions:
            raise ValueError("Quiz not completed by user")

        score = calculate_quiz_score(quiz_id, user_id)
        completion_date = max([s.timestamp for s in submissions])
        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        return {
            'user_name': user.name,
            'user_email': user.email,
            'quiz_title': quiz.title,
            'chapter_name': quiz.chapter.name,
            'course_name': quiz.chapter.course.name,
            'score_percentage': round(score['percentage'], 1),
            'obtained_marks': score['obtained_marks'],
            'total_marks': score['total_marks'],
            'total_questions': len(questions),
            'completion_date': completion_date.strftime("%B %d, %Y"),
            'certificate_id': self.generate_certificate_id(user_id, quiz_id),
            'quiz_id': quiz_id,
            'user_id': user_id
        }

    def generate_certificate_html(self, user_id: int, quiz_id: int) -> str:
        try:
            data = self.get_certificate_data(user_id, quiz_id)
            html_content = self.template.render(**data)
            return html_content
        except Exception as e:
            current_app.logger.error(
                f"Error generating certificate HTML: {str(e)}")
            raise

    def generate_certificate_pdf(self, user_id: int, quiz_id: int) -> bytes:
        try:
            html_content = self.generate_certificate_html(user_id, quiz_id)
            css = CSS(string="""
                @page {
                    size: A4 landscape;
                    margin: 0;
                }
                body {
                    margin: 0;
                    padding: 0;
                }
            """)

            # Generate PDF
            html_doc = HTML(string=html_content)
            pdf_bytes = html_doc.write_pdf(stylesheets=[css])

            return pdf_bytes

        except Exception as e:
            current_app.logger.error(
                f"Error generating certificate PDF: {str(e)}")
            raise

        except Exception as e:
            current_app.logger.error(
                f"Error saving certificate file: {str(e)}")
            raise

    def can_generate_certificate(self, user_id: int, quiz_id: int) -> tuple[bool, str]:
        try:
            user = User.query.get(user_id)
            if not user:
                return False, "User not found"

            quiz = Quiz.query.get(quiz_id)
            if not quiz:
                return False, "Quiz not found"

            submissions = Submission.query.filter_by(
                user_id=user_id,
                quiz_id=quiz_id
            ).all()

            if not submissions:
                return False, "Quiz not completed"

            return True, "Certificate can be generated"

        except Exception as e:
            current_app.logger.error(
                f"Error checking certificate eligibility: {str(e)}")
            return False, f"Error: {str(e)}"


def get_certificate_generator() -> CertificateGenerator:
    certificate_generator = CertificateGenerator()
    return certificate_generator
