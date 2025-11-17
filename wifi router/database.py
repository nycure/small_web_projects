import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.host = os.getenv('MYSQL_HOST', 'localhost')
        self.port = os.getenv('MYSQL_PORT', 3306)
        self.user = os.getenv('MYSQL_USER', 'root')
        self.password = os.getenv('MYSQL_PASSWORD', '')
        self.database = os.getenv('MYSQL_DATABASE', 'router_db')
        self.connection = None
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                print(f"Successfully connected to MySQL database: {self.database}")
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
    
    def create_database_and_table(self):
        """Create database and table if they don't exist"""
        try:
            # Connect without database first
            temp_connection = mysql.connector.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password
            )
            cursor = temp_connection.cursor()
            
            # Create database if it doesn't exist
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database}")
            print(f"Database '{self.database}' created or already exists")
            
            cursor.close()
            temp_connection.close()
            
            # Now connect to the specific database
            if self.connect():
                cursor = self.connection.cursor()
                
                # Create login_attempts table
                create_table_query = """
                CREATE TABLE IF NOT EXISTS login_attempts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255) NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    success BOOLEAN DEFAULT FALSE
                )
                """
                cursor.execute(create_table_query)
                print("Table 'login_attempts' created or already exists")
                
                cursor.close()
                return True
        except Error as e:
            print(f"Error creating database/table: {e}")
            return False
    
    def save_login_attempt(self, username, password, ip_address=None, user_agent=None, success=False):
        """Save login attempt to database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor()
            
            insert_query = """
            INSERT INTO login_attempts (username, password, ip_address, user_agent, success)
            VALUES (%s, %s, %s, %s, %s)
            """
            
            values = (username, password, ip_address, user_agent, success)
            cursor.execute(insert_query, values)
            self.connection.commit()
            
            print(f"Login attempt saved: {username} from {ip_address}")
            cursor.close()
            return True
            
        except Error as e:
            print(f"Error saving login attempt: {e}")
            return False
    
    def get_all_login_attempts(self):
        """Retrieve all login attempts from database"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM login_attempts ORDER BY timestamp DESC")
            results = cursor.fetchall()
            cursor.close()
            return results
            
        except Error as e:
            print(f"Error retrieving login attempts: {e}")
            return []
    
    def close_connection(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")

# Initialize database manager
db_manager = DatabaseManager()
