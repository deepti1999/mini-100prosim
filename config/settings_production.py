import os
from .settings import *

# Production settings
DEBUG = False
ALLOWED_HOSTS = ['mini100prosim-energy.herokuapp.com', 'localhost', '127.0.0.1']

# Static files configuration for production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database configuration (if needed)
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3'
    )
}
