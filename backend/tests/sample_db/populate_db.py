#!/usr/bin/env python3
"""
Script to populate quiz.db from JSON course files.
This script reads JSON files containing course data and stores them in the SQLite database.

Usage:
    python populate_db.py

This script will:
1. Read all JSON files from tests/sample_db/data/
2. Parse course, chapter, quiz, and question data
3. Store everything in the quiz.db SQLite database
4. Skip existing courses to avoid duplicates
"""

from app.models import db, Course, Chapter, Quiz, Question
from app import create_app
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the backend directory to Python path to import app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


def load_json_file(file_path):
    """Load and parse a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def parse_datetime(date_string):
    """Parse datetime string from JSON."""
    if not date_string:
        return None
    try:
        # Handle ISO format datetime strings
        return datetime.fromisoformat(date_string.replace('Z', '+00:00'))
    except Exception as e:
        print(f"Error parsing datetime {date_string}: {e}")
        return None


def create_course_from_json(course_data, file_name):
    """Create a course and all its related data from JSON."""

    # Handle different JSON structures
    if 'courses' in course_data:
        # Structure like generative_ai_course.json
        course_info = course_data['courses'][0]
        course_name = course_info.get('name', file_name.replace(
            '_', ' ').replace('.json', '').title())
        course_description = course_info.get(
            'description', f"Course content for {course_name}")
        chapters_data = course_info.get('chapters', [])
    else:
        # Structure like intro_to_python_programming.json
        course_name = course_data.get('name', file_name.replace(
            '_', ' ').replace('.json', '').title())
        course_description = course_data.get(
            'description', f"Course content for {course_name}")
        chapters_data = course_data.get('chapters', [])

    # Check if course already exists
    existing_course = Course.query.filter_by(name=course_name).first()
    if existing_course:
        print(f"Course '{course_name}' already exists. Skipping...")
        return existing_course

    # Create course
    course = Course(
        name=course_name,
        description=course_description
    )
    db.session.add(course)
    db.session.flush()  # Get the course ID

    print(f"Created course: {course_name}")

    # Process chapters
    for chapter_data in chapters_data:
        chapter = Chapter(
            course_id=course.id,
            name=chapter_data.get('name', 'Untitled Chapter'),
            description=chapter_data.get('description', '')
        )
        db.session.add(chapter)
        db.session.flush()  # Get the chapter ID

        print(f"  Created chapter: {chapter.name}")

        # Process quizzes
        for quiz_data in chapter_data.get('quizzes', []):
            quiz = Quiz(
                chapter_id=chapter.id,
                title=quiz_data.get('title', 'Untitled Quiz'),
                date_of_quiz=parse_datetime(quiz_data.get('date_of_quiz')),
                time_duration=quiz_data.get('time_duration'),
                is_scheduled=quiz_data.get('is_scheduled', False),
                remarks=quiz_data.get('remarks', '')
            )
            db.session.add(quiz)
            db.session.flush()  # Get the quiz ID

            print(f"    Created quiz: {quiz.title}")

            # Process questions
            question_count = 0
            for question_data in quiz_data.get('questions', []):
                # Skip incomplete questions
                if not question_data.get('question_statement'):
                    continue

                # Ensure correct_answer is properly formatted
                correct_answer = question_data.get('correct_answer', [])
                if not isinstance(correct_answer, list):
                    correct_answer = [correct_answer]

                question = Question(
                    quiz_id=quiz.id,
                    question_statement=question_data.get(
                        'question_statement', ''),
                    question_type=question_data.get('question_type', 'MCQ'),
                    options=question_data.get('options'),
                    correct_answer=correct_answer,
                    marks=float(question_data.get('marks', 1.0))
                )
                db.session.add(question)
                question_count += 1

            print(f"      Created {question_count} questions")

    return course


def main():
    """Main function to populate the database."""

    # Initialize Flask app
    app = create_app()

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

        # Path to JSON files
        data_dir = Path(__file__).parent / 'tests' / 'sample_db' / 'data'

        if not data_dir.exists():
            print(f"Data directory not found: {data_dir}")
            return

        # List of JSON files to process
        json_files = [
            'artificial_intelligence_ml.json',
            'deep_learning_course_actual_questions.json',
            'generative_ai_course.json',
            'intro_to_python_programming.json',
            'intro_to_web_dev.json',
            'mathematics_I_course.json',
            'statistics_course.json'
        ]

        print("Starting database population...")
        print("=" * 50)

        courses_created = 0

        for json_file in json_files:
            file_path = data_dir / json_file

            if not file_path.exists():
                print(f"File not found: {file_path}")
                continue

            print(f"\nProcessing: {json_file}")
            print("-" * 30)

            # Load JSON data
            course_data = load_json_file(file_path)
            if not course_data:
                continue

            # Create course and related data
            try:
                course = create_course_from_json(course_data, json_file)
                if course:
                    courses_created += 1

                # Commit after each file
                db.session.commit()
                print(f"Successfully processed: {json_file}")

            except Exception as e:
                print(f"Error processing {json_file}: {e}")
                db.session.rollback()
                continue

        print("\n" + "=" * 50)
        print(f"Database population completed!")
        print(f"Courses created: {courses_created}")

        # Print summary
        total_courses = Course.query.count()
        total_chapters = Chapter.query.count()
        total_quizzes = Quiz.query.count()
        total_questions = Question.query.count()

        print(f"\nDatabase Summary:")
        print(f"  Total Courses: {total_courses}")
        print(f"  Total Chapters: {total_chapters}")
        print(f"  Total Quizzes: {total_quizzes}")
        print(f"  Total Questions: {total_questions}")


if __name__ == '__main__':
    main()
