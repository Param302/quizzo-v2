from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.sqlite import JSON

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)  # hashed
    role = db.Column(db.String(10), nullable=False)  # 'admin' or 'user'
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    submissions = db.relationship(
        "Submission", backref="user", lazy=True, cascade="all,delete")
    subscriptions = db.relationship(
        "Subscription", backref="user", lazy=True, cascade="all,delete")


class Course(db.Model):
    __tablename__ = "course"
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    chapters = db.relationship(
        "Chapter", backref="course", lazy=True, cascade="all,delete")


class Chapter(db.Model):
    __tablename__ = "chapter"
    id = db.Column(db.Integer, primary_key=True)

    course_id = db.Column(db.Integer, db.ForeignKey(
        "course.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    quizzes = db.relationship(
        "Quiz", backref="chapter", lazy=True, cascade="all,delete")
    subscriptions = db.relationship(
        "Subscription", backref="chapter", lazy=True, cascade="all,delete")


class Quiz(db.Model):
    __tablename__ = "quiz"
    id = db.Column(db.Integer, primary_key=True)

    chapter_id = db.Column(db.Integer, db.ForeignKey(
        "chapter.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    # Nullable if open quiz
    date_of_quiz = db.Column(db.DateTime, nullable=True)
    time_duration = db.Column(db.String(10), nullable=True)  # Format: HH:MM
    is_scheduled = db.Column(db.Boolean, default=False)
    remarks = db.Column(db.Text)

    questions = db.relationship(
        "Question", backref="quiz", lazy=True, cascade="all,delete")
    submissions = db.relationship(
        "Submission", backref="quiz", lazy=True, cascade="all,delete")


class Question(db.Model):
    __tablename__ = "question"
    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_statement = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(10), nullable=False)  # MCQ, MSQ, NAT
    # List of options for MCQ/MSQ, null for NAT
    options = db.Column(JSON, nullable=True)
    # For MCQ: [index], MSQ: [indices], NAT: [value or range]
    correct_answer = db.Column(JSON, nullable=False)
    marks = db.Column(db.Float, nullable=False, default=1.0)


class Submission(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    quiz_id = db.Column(db.Integer, db.ForeignKey("quiz.id"), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey(
        "question.id"), nullable=False)
    # Matches format of correct_answer
    answer = db.Column(JSON, nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    question = db.relationship("Question", backref="submissions")


class Subscription(db.Model):
    __tablename__ = "subscription"
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    chapter_id = db.Column(db.Integer, db.ForeignKey(
        "chapter.id"), nullable=False)
    subscribed_on = db.Column(db.DateTime, default=datetime.now)
    # Active or inactive subscription
    is_active = db.Column(db.Boolean, default=True)
