#!/usr/bin/env python3
"""
Test script for the new email features (daily reminders and monthly reports)
Run this script to test the email functionality manually.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))


def test_email_service():
    """Test the email service functionality"""
    try:
        from app import create_app
        from app.services.email_service import get_email_service
        from app.models import db, User, Quiz, Subscription, Submission

        # Create Flask app
        app = create_app()

        with app.app_context():
            print("🧪 Testing Email Service Functionality")
            print("=" * 50)

            # Get email service
            email_service = get_email_service()

            # Test 1: Check if service initializes
            print("\n1. Testing email service initialization...")
            try:
                email_service._ensure_initialized()
                print("   ✅ Email service initialized successfully")
            except Exception as e:
                print(f"   ❌ Failed to initialize email service: {e}")
                return

            # Test 2: Test daily reminder for a specific user
            print("\n2. Testing daily reminder email...")
            users = User.query.filter_by(role='user').limit(1).all()
            if users:
                user = users[0]
                print(f"   Testing with user: {user.name} ({user.email})")
                try:
                    success = email_service.send_daily_reminder_email(user.id)
                    if success:
                        print("   ✅ Daily reminder email sent successfully")
                    else:
                        print("   ⚠️  No upcoming quizzes or email not sent")
                except Exception as e:
                    print(f"   ❌ Failed to send daily reminder: {e}")
            else:
                print("   ⚠️  No users found in database")

            # Test 3: Test monthly report for a specific user
            print("\n3. Testing monthly report email...")
            if users:
                user = users[0]
                print(f"   Testing with user: {user.name} ({user.email})")
                try:
                    success = email_service.send_monthly_report_email(user.id)
                    if success:
                        print("   ✅ Monthly report email sent successfully")
                    else:
                        print("   ⚠️  No recent activity or email not sent")
                except Exception as e:
                    print(f"   ❌ Failed to send monthly report: {e}")

            # Test 4: Test bulk daily reminders
            print("\n4. Testing bulk daily reminders...")
            try:
                result = email_service.send_bulk_daily_reminders()
                print(
                    f"   ✅ Bulk daily reminders completed: {result['sent']} sent, {result['failed']} failed")
            except Exception as e:
                print(f"   ❌ Failed to send bulk daily reminders: {e}")

            # Test 5: Test bulk monthly reports
            print("\n5. Testing bulk monthly reports...")
            try:
                result = email_service.send_bulk_monthly_reports()
                print(
                    f"   ✅ Bulk monthly reports completed: {result['sent']} sent, {result['failed']} failed")
            except Exception as e:
                print(f"   ❌ Failed to send bulk monthly reports: {e}")

            print("\n" + "=" * 50)
            print("🎉 Email service testing completed!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure Flask app and dependencies are properly installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def show_database_stats():
    """Show some database statistics"""
    try:
        from app import create_app
        from app.models import db, User, Quiz, Subscription, Submission

        app = create_app()

        with app.app_context():
            print("\n📊 Database Statistics")
            print("-" * 30)
            print(f"Total users: {User.query.count()}")
            print(f"Total quizzes: {Quiz.query.count()}")
            print(f"Total subscriptions: {Subscription.query.count()}")
            print(f"Total submissions: {Submission.query.count()}")

            # Show upcoming quizzes
            tomorrow = datetime.now() + timedelta(days=1)
            upcoming_quizzes = Quiz.query.filter(
                Quiz.is_scheduled == True,
                Quiz.date_of_quiz >= datetime.now(),
                Quiz.date_of_quiz <= tomorrow
            ).count()
            print(f"Upcoming quizzes tomorrow: {upcoming_quizzes}")

            # Show recent activity (last 30 days)
            last_month = datetime.now() - timedelta(days=30)
            recent_submissions = Submission.query.filter(
                Submission.timestamp >= last_month
            ).count()
            print(f"Recent submissions (last 30 days): {recent_submissions}")

    except Exception as e:
        print(f"❌ Failed to get database stats: {e}")


if __name__ == "__main__":
    print("🚀 Quizzo Email Features Test")
    print("Testing daily reminders and monthly reports functionality")

    # Show database stats first
    show_database_stats()

    # Test email service
    test_email_service()

    print("\n💡 Tips:")
    print("- Make sure your email configuration is set up in the Flask config")
    print("- Check the application logs for detailed error messages")
    print("- For production use, consider setting up email templates in a separate file")
    print("- You can schedule these functions using cron jobs or task queues")
