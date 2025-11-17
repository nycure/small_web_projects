import sys
import os

# Add your project directory to the Python path
project_home = '/home/nity70/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

from app import app as application

if __name__ == "__main__":
    application.run()
