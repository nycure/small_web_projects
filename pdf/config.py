import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    
class DevelopmentConfig(Config):
    DEBUG = True
    UPLOAD_FOLDER = 'uploads'

class ProductionConfig(Config):
    DEBUG = False
    UPLOAD_FOLDER = '/home/nity70/mysite/uploads'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
