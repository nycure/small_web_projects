# PythonAnywhere Deployment Instructions

## Step-by-Step Deployment Guide

### 1. Upload Files to PythonAnywhere
- Upload all files to `/home/nity70/mysite/`
- Ensure all templates are in `/home/nity70/mysite/templates/`
- Create uploads directory: `/home/nity70/mysite/uploads/`

### 2. Install Dependencies
Open a PythonAnywhere Bash console and run:
```bash
cd ~/mysite
pip3.10 install --user -r requirements.txt
```

### 3. Configure Web App in PythonAnywhere Dashboard

#### In the Web tab:
- **Source code**: `/home/nity70/mysite`
- **Working directory**: `/home/nity70/mysite`
- **WSGI configuration file**: `/var/www/nity70_pythonanywhere_com_wsgi.py`

#### Edit the WSGI configuration file:
Replace the contents with:
```python
import sys
path = '/home/nity70/mysite'
if path not in sys.path:
    sys.path.append(path)

from wsgi import application
```

### 4. Set Environment Variables
In the Web tab, add these environment variables:
- `PYTHONANYWHERE_DOMAIN` = `True`
- `FLASK_ENV` = `production`
- `SECRET_KEY` = `your-secure-secret-key-here`

### 5. File Permissions
Ensure the uploads directory has proper permissions:
```bash
chmod 755 ~/mysite/uploads
```

### 6. Test the Application
- Click "Reload" in the Web tab
- Visit your domain: `https://nity70.pythonanywhere.com`

## Important Notes:

### File Size Limits:
- Maximum upload size: 50MB
- Consider PythonAnywhere disk space limits
- Files are automatically cleaned up after processing

### Security Features:
- File type validation (PDF, PNG, JPG, JPEG only)
- CSRF protection via Flask's SECRET_KEY
- Error handling for production environment

### Monitoring:
- Check error logs in PythonAnywhere dashboard
- Monitor disk usage for uploaded files
- Set up automatic cleanup if needed

## Troubleshooting:

### Common Issues:
1. **Import errors**: Check if all packages are installed
2. **Permission errors**: Verify file permissions in uploads directory
3. **Path issues**: Ensure all paths use absolute paths for production

### Log Files:
- Error logs: Available in PythonAnywhere Web tab
- Server logs: Check for any application errors

## Maintenance:

### Regular Tasks:
1. Monitor disk usage
2. Check for any failed file cleanups
3. Update dependencies as needed
4. Backup important configurations
