#!/usr/bin/env python3
"""
Setup script for Router Login Database
This script will help you set up the MySQL database and test the connection.
"""

import sys
import os
from database import db_manager

def main():
    print("=== Router Login Database Setup ===\n")
    
    print("1. Testing database connection...")
    if db_manager.create_database_and_table():
        print("✅ Database setup completed successfully!\n")
        
        print("2. Testing database operations...")
        # Test saving a sample login attempt
        test_success = db_manager.save_login_attempt(
            username="test_user",
            password="test_password",
            ip_address="127.0.0.1",
            user_agent="Setup Script",
            success=False
        )
        
        if test_success:
            print("✅ Database operations working correctly!\n")
            
            # Show recent attempts
            attempts = db_manager.get_all_login_attempts()
            print(f"📊 Current database has {len(attempts)} login attempts")
            
            if attempts:
                print("\nMost recent attempt:")
                latest = attempts[0]
                print(f"  - Username: {latest['username']}")
                print(f"  - Timestamp: {latest['timestamp']}")
                print(f"  - IP: {latest['ip_address']}")
                print(f"  - Success: {latest['success']}")
        else:
            print("❌ Database operations test failed")
            return False
    else:
        print("❌ Database setup failed")
        print("\nPlease check your .env file and MySQL configuration:")
        print("- Ensure MySQL server is running")
        print("- Verify credentials in .env file")
        print("- Check if user has necessary permissions")
        return False
    
    print("\n=== Setup Complete ===")
    print("You can now run the Flask application with: python app.py")
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        sys.exit(1)
