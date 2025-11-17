# Router Firmware Upgrade Interface

A professional web interface for router firmware upgrades built with Flask and modern UI standards, with MySQL database integration for secure password storage and upgrade logging.

## Features

- **🔐 Secure Password Storage**: Passwords hashed with bcrypt and stored in MySQL
- **📊 Upgrade Logging**: Complete audit trail of firmware upgrades
- **📈 Admin Dashboard**: View password entries and upgrade history
- **🔒 Database Security**: Secure MySQL integration with environment variables
- **📊 Real-time Progress**: Live progress tracking with database logging
- **🎨 Modern UI**: Industry-standard design with responsive layout
- **⚡ Interactive Features**: Form validation, animations, and error handling

## Database Features

- **Password Management**: Secure bcrypt hashing and storage
- **Upgrade Tracking**: Complete upgrade history with timestamps
- **Session Logging**: IP addresses and user agent tracking
- **Progress Monitoring**: Real-time upgrade progress logging
- **Admin Analytics**: View usage patterns and upgrade statistics

## Installation

### 1. Prerequisites

- Python 3.7+
- MySQL Server 5.7+ or 8.0+
- pip package manager

### 2. MySQL Setup

Install and start MySQL server:

**Windows:**
```powershell
# Using Chocolatey
choco install mysql

# Or download from: https://dev.mysql.com/downloads/mysql/
# Start MySQL service
net start mysql
```

**Connect to MySQL and create a user (optional):**
```sql
CREATE USER 'router_admin'@'localhost' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON *.* TO 'router_admin'@'localhost' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

### 3. Project Setup

1. Navigate to the project directory:
   ```powershell
   cd "d:\website\wifi router update"
   ```

2. Install Python dependencies:
   ```powershell
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   
   Edit the `.env` file with your MySQL credentials:
   ```env
   DB_HOST=localhost
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_NAME=router_management
   DB_PORT=3306
   SECRET_KEY=your_secret_key_here
   ```

4. **Complete Database Setup (One Command!):**
   ```powershell
   python complete_setup.py
   ```
   
   This single script will:
   - ✅ Verify environment configuration
   - ✅ Test MySQL server connection
   - ✅ Create database and tables
   - ✅ Update schema for password display
   - ✅ Test all database operations
   - ✅ Create quick reference guide

5. Run the Flask application:
   ```powershell
   python app.py
   ```

6. Open your browser and visit: `http://localhost:5000`

## Usage

1. **Main Page**: Enter admin password (minimum 8 characters) and confirm
2. **Acknowledge Risks**: Check the confirmation box to proceed
3. **Start Upgrade**: Click the upgrade button to begin the process
4. **Monitor Progress**: Watch the real-time progress with visual indicators
5. **Completion**: View the success page with upgrade details
6. **Admin Dashboard**: Visit `/admin/logs` to view password and upgrade history

## Database Schema

### admin_passwords Table
- `id`: Primary key (auto-increment)
- `password_hash`: Bcrypt hashed password
- `created_at`: Timestamp of password creation
- `updated_at`: Last update timestamp
- `is_active`: Boolean status flag
- `session_info`: JSON session information
- `ip_address`: Client IP address
- `user_agent`: Browser/client information

### upgrade_logs Table
- `id`: Primary key (auto-increment)
- `upgrade_started_at`: Upgrade start timestamp
- `upgrade_completed_at`: Upgrade completion timestamp
- `status`: Enum (started, in_progress, completed, failed)
- `progress`: Integer percentage (0-100)
- `current_step`: Current upgrade step description
- `ip_address`: Client IP address
- `user_agent`: Browser/client information
- `firmware_version_from`: Source firmware version
- `firmware_version_to`: Target firmware version
- `error_message`: Error details (if failed)

## API Endpoints

- `GET /` - Main firmware upgrade page
- `POST /upgrade` - Start firmware upgrade process (saves password to MySQL)
- `GET /progress` - Get current upgrade progress (JSON)
- `GET /upgrading` - Upgrade progress monitoring page
- `GET /success` - Upgrade completion page
- `GET /admin/logs` - Admin dashboard with password and upgrade logs

## Security Features

- **Password Hashing**: All passwords encrypted with bcrypt
- **Environment Variables**: Database credentials stored securely
- **Session Tracking**: IP addresses and user agents logged
- **Input Validation**: Server-side and client-side validation
- **SQL Injection Protection**: Parameterized queries
- **XSS Prevention**: Template escaping enabled

## Project Structure

```
wifi router update/
├── app.py                 # Main Flask application with MySQL integration
├── database.py            # Database manager and operations
├── complete_setup.py      # Complete database setup (replaces old setup files)
├── requirements.txt       # Python dependencies (includes MySQL connector)
├── .env                   # Environment variables (MySQL credentials)
├── QUICK_REFERENCE.md     # Auto-generated quick reference guide
├── static/
│   ├── css/
│   │   └── style.css     # Modern styling with gradients and animations
│   └── js/
│       └── script.js     # Interactive functionality and form validation
└── templates/
    ├── index.html        # Main upgrade form page
    ├── upgrading.html    # Progress monitoring page
    ├── success.html      # Completion confirmation page
    └── admin_logs.html   # Admin dashboard for viewing logs
```

## Customization

The interface is designed to be easily customizable:

- **Branding**: Update the router name in templates
- **Styling**: Modify CSS variables for colors and themes
- **Upgrade Process**: Adjust timing and steps in `app.py`
- **Validation**: Customize password requirements in JavaScript

## Browser Compatibility

- Chrome 60+
- Firefox 55+
- Safari 12+
- Edge 79+

## License

This project is created for educational and demonstration purposes.
