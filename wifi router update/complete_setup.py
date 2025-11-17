#!/usr/bin/env python3
"""
Complete Database Setup Script for Router Firmware Upgrade Application
This script handles all database setup, schema updates, and testing in one place.
"""

import os
import sys
import mysql.connector
from mysql.connector import Error
import bcrypt
from dotenv import load_dotenv
from datetime import datetime

def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 60)
    print(title.center(60))
    print("=" * 60)

def print_step(step_num, description):
    """Print a formatted step"""
    print(f"\n{step_num}. {description}")

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

class CompleteDatabaseSetup:
    def __init__(self):
        load_dotenv()
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'router_management')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.connection = None

    def check_environment(self):
        """Check if all required environment variables are set"""
        print_step(1, "Checking environment configuration...")
        
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            print_error(f"Missing environment variables: {', '.join(missing_vars)}")
            print("\nPlease update your .env file with the following variables:")
            print("DB_HOST=localhost")
            print("DB_USER=root")
            print("DB_PASSWORD=your_mysql_password")
            print("DB_NAME=router_management")
            print("DB_PORT=3306")
            print("SECRET_KEY=your_secret_key_here")
            return False
        
        print_success("Environment configuration is complete!")
        
        print(f"\n📊 Database Configuration:")
        print(f"   Host: {self.host}")
        print(f"   User: {self.user}")
        print(f"   Database: {self.database}")
        print(f"   Port: {self.port}")
        
        return True

    def test_mysql_connection(self):
        """Test basic MySQL server connection"""
        print_step(2, "Testing MySQL server connection...")
        
        try:
            # Test connection without database
            test_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            
            if test_connection.is_connected():
                cursor = test_connection.cursor()
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print_success(f"MySQL server connection successful!")
                print_info(f"MySQL Version: {version[0]}")
                
                cursor.close()
                test_connection.close()
                return True
            else:
                print_error("Failed to connect to MySQL server")
                return False
                
        except Error as e:
            print_error(f"MySQL connection failed: {e}")
            print("\n🔧 Troubleshooting tips:")
            print("1. Make sure MySQL server is running")
            print("2. Check if credentials in .env file are correct")
            print("3. Verify user has necessary permissions")
            print("4. Try: net start mysql (Windows)")
            return False

    def create_database_and_tables(self):
        """Create database and all required tables"""
        print_step(3, "Creating database and tables...")
        
        try:
            # Connect without specifying database
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = connection.cursor()
            
            # Create database if it doesn't exist
            print_info(f"Creating database '{self.database}' if it doesn't exist...")
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            print_success(f"Database '{self.database}' is ready!")
            
            # Create admin_passwords table with both plain and hashed passwords
            print_info("Creating 'admin_passwords' table...")
            create_passwords_table = """
            CREATE TABLE IF NOT EXISTS admin_passwords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                password_plain VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                session_info TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT,
                INDEX idx_created_at (created_at),
                INDEX idx_ip_address (ip_address)
            )
            """
            cursor.execute(create_passwords_table)
            print_success("admin_passwords table created!")
            
            # Create upgrade_logs table
            print_info("Creating 'upgrade_logs' table...")
            create_logs_table = """
            CREATE TABLE IF NOT EXISTS upgrade_logs (
                id INT AUTO_INCREMENT PRIMARY KEY,
                upgrade_started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                upgrade_completed_at TIMESTAMP NULL,
                status ENUM('started', 'in_progress', 'completed', 'failed') DEFAULT 'started',
                progress INT DEFAULT 0,
                current_step VARCHAR(255),
                ip_address VARCHAR(45),
                user_agent TEXT,
                firmware_version_from VARCHAR(50),
                firmware_version_to VARCHAR(50),
                error_message TEXT,
                INDEX idx_status (status),
                INDEX idx_started_at (upgrade_started_at)
            )
            """
            cursor.execute(create_logs_table)
            print_success("upgrade_logs table created!")
            
            connection.commit()
            cursor.close()
            connection.close()
            
            print_success("All database tables created successfully!")
            return True
            
        except Error as e:
            print_error(f"Error creating database/tables: {e}")
            return False

    def update_schema_if_needed(self):
        """Update existing schema to add new columns if needed"""
        print_step(4, "Checking and updating database schema...")
        
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port
            )
            cursor = connection.cursor()
            
            # Check if password_plain column exists
            cursor.execute("SHOW COLUMNS FROM admin_passwords LIKE 'password_plain'")
            result = cursor.fetchone()
            
            if not result:
                print_info("Adding 'password_plain' column to existing table...")
                cursor.execute("ALTER TABLE admin_passwords ADD COLUMN password_plain VARCHAR(255) AFTER id")
                connection.commit()
                print_success("password_plain column added successfully!")
            else:
                print_success("Schema is already up to date!")
            
            # Show final table structure
            cursor.execute("DESCRIBE admin_passwords")
            columns = cursor.fetchall()
            print_info("Final admin_passwords table structure:")
            for col in columns:
                print(f"  - {col[0]} ({col[1]})")
            
            cursor.close()
            connection.close()
            return True
            
        except Error as e:
            print_error(f"Error updating schema: {e}")
            return False

    def test_database_operations(self):
        """Test all database operations"""
        print_step(5, "Testing database operations...")
        
        try:
            from database import DatabaseManager
            
            dm = DatabaseManager()
            if not dm.connect():
                print_error("Failed to connect using DatabaseManager")
                return False
            
            print_success("DatabaseManager connection successful!")
            
            # Test password saving with plain text
            print_info("Testing password saving functionality...")
            test_password = f"TestSetup{datetime.now().strftime('%H%M%S')}"
            password_id = dm.save_password(
                test_password,
                "127.0.0.1",
                "Complete Setup Script Test",
                f"Database setup test - {datetime.now()}"
            )
            
            if password_id:
                print_success(f"Test password saved successfully! ID: {password_id}")
            else:
                print_error("Failed to save test password")
                return False
            
            # Test upgrade logging
            print_info("Testing upgrade logging functionality...")
            log_id = dm.log_upgrade_start(
                "127.0.0.1",
                "Complete Setup Script Test",
                "v2.4.1",
                "v2.5.0"
            )
            
            if log_id:
                print_success(f"Test upgrade log created! ID: {log_id}")
                
                # Test progress updates
                dm.update_upgrade_progress(log_id, 25, "Testing progress update", "in_progress")
                dm.update_upgrade_progress(log_id, 75, "Testing advanced progress", "in_progress")
                dm.complete_upgrade_log(log_id, success=True)
                print_success("Progress update and completion tests successful!")
            else:
                print_error("Failed to create test upgrade log")
                return False
            
            # Display recent data
            print_info("Retrieving recent data...")
            passwords = dm.get_recent_passwords(3)
            upgrades = dm.get_upgrade_history(3)
            
            print(f"\n📊 Recent Passwords ({len(passwords)} found):")
            for pwd in passwords:
                print(f"  ID: {pwd['id']} | Plain: {pwd.get('password_plain', 'N/A')} | IP: {pwd.get('ip_address', 'N/A')}")
            
            print(f"\n📈 Recent Upgrades ({len(upgrades)} found):")
            for upg in upgrades:
                print(f"  ID: {upg['id']} | Status: {upg.get('status', 'N/A')} | Progress: {upg.get('progress', 0)}%")
            
            dm.close_connection()
            print_success("All database operations tested successfully!")
            return True
            
        except Exception as e:
            print_error(f"Database operations test failed: {e}")
            return False

    def create_quick_reference(self):
        """Create a quick reference guide"""
        print_step(6, "Creating quick reference guide...")
        
        reference_content = f"""
# 🚀 Router Firmware Upgrade - Quick Reference

## 📋 Database Information
- **Host**: {self.host}
- **Database**: {self.database}
- **Port**: {self.port}
- **User**: {self.user}

## 🔗 Application URLs
- **Main App**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin/logs
- **Upgrade Progress**: http://localhost:5000/upgrading
- **Success Page**: http://localhost:5000/success

## 🗂️ Database Tables
1. **admin_passwords**: Stores user passwords (plain + hashed)
2. **upgrade_logs**: Tracks all firmware upgrade attempts

## 🎯 Next Steps
1. Start the application: `python app.py`
2. Open browser: `http://localhost:5000`
3. Test firmware upgrade process
4. Check admin panel for saved passwords
5. Monitor upgrade history

## 🛠️ Maintenance Commands
- **Restart Flask**: `python app.py`
- **Check database**: `python -c "from database import DatabaseManager; dm = DatabaseManager(); dm.connect()"`
- **View logs**: Visit admin panel or check MySQL directly

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        try:
            with open('QUICK_REFERENCE.md', 'w', encoding='utf-8') as f:
                f.write(reference_content)
            print_success("Quick reference guide created: QUICK_REFERENCE.md")
        except Exception as e:
            print_info(f"Could not create reference file: {e}")

def print_help():
    """Print help information"""
    print_header("MySQL Setup Help")
    print("\n1. Install MySQL Server:")
    print("   - Download: https://dev.mysql.com/downloads/mysql/")
    print("   - Windows: choco install mysql")
    print("   - Or use MySQL Installer")
    
    print("\n2. Start MySQL Service:")
    print("   - Windows: net start mysql")
    print("   - Or use MySQL Workbench")
    
    print("\n3. Create Database User (Optional):")
    print("   CREATE USER 'router_admin'@'localhost' IDENTIFIED BY 'secure_password';")
    print("   GRANT ALL PRIVILEGES ON router_management.* TO 'router_admin'@'localhost';")
    print("   FLUSH PRIVILEGES;")
    
    print("\n4. Update .env file with your credentials")
    print("\n5. Run this script: python complete_setup.py")

def main():
    """Main setup function"""
    print_header("Router Firmware Upgrade - Complete Database Setup")
    
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        print_help()
        return
    
    setup = CompleteDatabaseSetup()
    
    try:
        # Run all setup steps
        if not setup.check_environment():
            return False
        
        if not setup.test_mysql_connection():
            return False
        
        if not setup.create_database_and_tables():
            return False
        
        if not setup.update_schema_if_needed():
            return False
        
        if not setup.test_database_operations():
            return False
        
        setup.create_quick_reference()
        
        # Final success message
        print_header("🎉 COMPLETE SETUP SUCCESSFUL! 🎉")
        print("\n🚀 Your Router Firmware Upgrade Application is ready!")
        print("\n📋 What was completed:")
        print("   ✅ Environment configuration verified")
        print("   ✅ MySQL server connection tested")
        print("   ✅ Database and tables created")
        print("   ✅ Schema updated for password display")
        print("   ✅ All database operations tested")
        print("   ✅ Quick reference guide created")
        
        print("\n🎯 Next Steps:")
        print("   1. Run: python app.py")
        print("   2. Open: http://localhost:5000")
        print("   3. Test firmware upgrade process")
        print("   4. Check admin panel: http://localhost:5000/admin/logs")
        print("   5. See passwords and upgrade history!")
        
        print("\n📖 Documentation:")
        print("   - README.md: Complete documentation")
        print("   - QUICK_REFERENCE.md: Quick reference guide")
        
        return True
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
        return False
    except Exception as e:
        print_error(f"Setup failed with unexpected error: {e}")
        print("\n🆘 For help, run: python complete_setup.py --help")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Setup failed! Check the error messages above.")
        sys.exit(1)
    else:
        print(f"\n✨ Setup completed successfully at {datetime.now().strftime('%H:%M:%S')}")
        sys.exit(0)
