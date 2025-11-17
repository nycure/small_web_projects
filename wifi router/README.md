# Syrotech Router Login with MySQL Integration

A beautiful, modern router login page that captures and stores login attempts in a MySQL database.

## Features

- 🎨 Modern, responsive UI design
- 🔒 Password toggle functionality
- 🗄️ MySQL database integration
- 📊 Login attempt tracking
- 🌐 IP address and user agent logging
- 📈 Dashboard with attempt statistics

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install and Configure MySQL

Make sure you have MySQL server installed and running:

**Windows:**
- Download MySQL from [mysql.com](https://dev.mysql.com/downloads/mysql/)
- Or use XAMPP/WAMP for easy setup

**Linux:**
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### 3. Configure Database Settings

Edit the `.env` file with your MySQL credentials:

```env
# Database Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=router_db

# Flask Configuration
SECRET_KEY=your-secret-key-change-this-in-production
DEBUG=True
```

### 4. Setup Database

Run the setup script to create the database and tables:

```bash
python setup_database.py
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Database Schema

The application creates a `login_attempts` table with the following structure:

```sql
CREATE TABLE login_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT FALSE
);
```

## Usage

1. **Login Page**: Visit `http://localhost:5000`
   - Only password field is visible
   - Username is automatically set to "user"
   - All login attempts are logged to database

2. **Dashboard**: After successful login
   - View router status
   - See recent login attempts
   - Monitor system statistics

3. **View All Attempts**: Visit `http://localhost:5000/view-attempts`
   - JSON format of all login attempts
   - Useful for analysis or integration

## Security Features

- All login attempts are logged (successful and failed)
- IP address tracking
- User agent logging
- Timestamp recording
- Password masking in dashboard display

## Default Credentials

For testing purposes:
- **Username**: admin
- **Password**: admin123

**Note**: Change these in production!

## API Endpoints

- `GET /` - Login page
- `POST /login` - Process login attempt
- `GET /dashboard` - Admin dashboard
- `GET /view-attempts` - JSON of all attempts

## Troubleshooting

### Database Connection Issues

1. **Check MySQL Service**:
   ```bash
   # Windows
   net start mysql
   
   # Linux
   sudo systemctl start mysql
   ```

2. **Verify Credentials**:
   - Test connection with MySQL client
   - Check username/password in `.env`

3. **Permission Issues**:
   ```sql
   GRANT ALL PRIVILEGES ON router_db.* TO 'your_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

### Import Errors

If you get import errors for `mysql.connector`:
```bash
pip install mysql-connector-python
```

## File Structure

```
wifi router/
├── app.py                 # Main Flask application
├── database.py           # Database management
├── setup_database.py     # Database setup script
├── requirements.txt      # Python dependencies
├── .env                  # Environment configuration
├── templates/
│   └── index.html        # Login page template
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # JavaScript functionality
└── README.md             # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Use responsibly and ensure compliance with local laws.
