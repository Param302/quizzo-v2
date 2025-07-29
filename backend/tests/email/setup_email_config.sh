#!/bin/bash

# Email Configuration Setup Script for Quizzo
# This script helps you set up email configuration for testing

echo "🚀 Quizzo Email Configuration Setup"
echo "======================================"

# Check if .env file exists
if [ -f ".env" ]; then
    echo "⚠️  .env file already exists!"
    read -p "Do you want to overwrite it? (y/N): " confirm
    if [[ $confirm != [yY] && $confirm != [yY][eE][sS] ]]; then
        echo "❌ Setup cancelled."
        exit 1
    fi
fi

echo "📧 Setting up email configuration..."
echo

# Copy example file
cp .env.example .env

# Collect email configuration
echo "Please provide your email settings:"
echo

read -p "📧 SMTP Server (e.g., smtp.gmail.com): " smtp_server
read -p "🔢 SMTP Port (usually 587 for TLS): " smtp_port
read -p "📧 Your email address: " email_address
read -s -p "🔐 Your email password/app password: " email_password
echo
read -p "👤 Sender name (e.g., Quizzo Team): " sender_name

# Update .env file
sed -i "s/MAIL_SERVER=.*/MAIL_SERVER=$smtp_server/" .env
sed -i "s/MAIL_PORT=.*/MAIL_PORT=$smtp_port/" .env
sed -i "s/MAIL_EMAIL=.*/MAIL_EMAIL=$email_address/" .env
sed -i "s/MAIL_PASSWORD=.*/MAIL_PASSWORD=$email_password/" .env
sed -i "s/MAIL_SENDER_NAME=.*/MAIL_SENDER_NAME=$sender_name/" .env

# Generate random secrets
secret_key=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
jwt_secret=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

sed -i "s/SECRET_KEY=.*/SECRET_KEY=$secret_key/" .env
sed -i "s/JWT_SECRET_KEY=.*/JWT_SECRET_KEY=$jwt_secret/" .env

echo
echo "✅ Email configuration saved to .env file!"
echo
echo "📝 Important Notes:"
echo "  - For Gmail, you need to enable 2-factor authentication"
echo "  - Use an 'App Password' instead of your regular password"
echo "  - Generate app password at: https://myaccount.google.com/apppasswords"
echo
echo "🧪 You can now run the email test script:"
echo "  python email_test_comprehensive.py"
echo

# Install required dependencies if needed
echo "📦 Checking Python dependencies..."
if ! python3 -c "import dotenv" 2>/dev/null; then
    echo "Installing python-dotenv..."
    pip install python-dotenv
fi

echo "🎉 Setup complete!"
