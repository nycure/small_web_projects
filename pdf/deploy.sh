#!/bin/bash

# PythonAnywhere Deployment Script for nity70/mysite

echo "🚀 Starting PythonAnywhere deployment..."

# Set environment variables
export PYTHONANYWHERE_DOMAIN=True
export FLASK_ENV=production

# Create uploads directory if it doesn't exist
mkdir -p /home/nity70/mysite/uploads

# Set proper permissions
chmod 755 /home/nity70/mysite/uploads
chmod +x /home/nity70/mysite/wsgi.py

# Install requirements
echo "📦 Installing Python packages..."
pip3.10 install --user -r requirements.txt

echo "✅ Deployment preparation complete!"
echo ""
echo "Next steps:"
echo "1. Configure your web app in PythonAnywhere dashboard"
echo "2. Set WSGI configuration file to use wsgi.py"
echo "3. Add environment variables in Web tab"
echo "4. Reload your web app"
echo ""
echo "Your app will be available at: https://nity70.pythonanywhere.com"
