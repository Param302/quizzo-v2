#!/usr/bin/env python3
"""
Simple Demo of Email Testing Script Usage

This is a minimal example showing how to use the email testing functionality.
Run this after setting up your email configuration.
"""

import os
from datetime import datetime

# Colors for output


class Colors:
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text, color):
    print(f"{color}{text}{Colors.END}")


def main():
    print_colored("🚀 Quizzo Email Testing Demo", Colors.BOLD)
    print("=" * 40)

    # Check if .env exists
    if not os.path.exists('.env'):
        print_colored("❌ No .env file found!", Colors.RED)
        print("\n📝 To set up email configuration:")
        print("   1. Run: ./setup_email_config.sh")
        print("   2. Or copy .env.example to .env and edit it")
        print("\n📖 See README.md for detailed instructions")
        return

    # Check for required environment variables
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['MAIL_SERVER', 'MAIL_EMAIL', 'MAIL_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]

    if missing:
        print_colored(
            f"❌ Missing environment variables: {', '.join(missing)}", Colors.RED)
        print("\n📝 Please update your .env file with these values")
        return

    print_colored("✅ Email configuration found!", Colors.GREEN)
    print(f"📧 SMTP Server: {os.getenv('MAIL_SERVER')}")
    print(f"📧 Email: {os.getenv('MAIL_EMAIL')}")
    print()

    # Show what the test will do
    print_colored("🎯 The email test will:", Colors.BLUE)
    print("  1. Create 2 test users:")
    print("     - mrintrovert.730@gmail.com")
    print("     - connectwithparam.30@gmail.com")
    print("  2. Create 1 course with 4 quizzes")
    print("  3. Simulate quiz attempts")
    print("  4. Send test emails:")
    print("     - Certificate emails (with PDF attachments)")
    print("     - Daily reminder emails")
    print("     - Monthly report emails")
    print("  5. Clean up all test data")
    print()

    # Confirm before running
    response = input("🚀 Ready to run the comprehensive email test? (y/N): ")
    if response.lower() not in ['y', 'yes']:
        print_colored("❌ Test cancelled.", Colors.YELLOW)
        return

    print()
    print_colored("🎬 Starting email test suite...", Colors.BLUE)
    print("=" * 50)

    # Import and run the test suite
    try:
        from email_test_comprehensive import EmailTestSuite

        test_suite = EmailTestSuite()
        test_suite.run_full_test_suite()

        print()
        print_colored("🎉 Email testing completed successfully!", Colors.GREEN)
        print_colored(
            "📧 Check the recipient email inboxes for test emails", Colors.BLUE)

    except ImportError as e:
        print_colored(f"❌ Import error: {e}", Colors.RED)
        print("Make sure you're running this from the backend directory")
    except Exception as e:
        print_colored(f"❌ Test failed: {e}", Colors.RED)
        print("Check the error details above and your email configuration")


if __name__ == "__main__":
    main()
