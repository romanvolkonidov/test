import sys
import os

# Add your project directory to the sys.path
project_home = u'/home/yourusername/yourproject'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set the environment variable for the Flask app
os.environ['FLASK_APP'] = 'main'

# Import the Flask app
from main import app as application