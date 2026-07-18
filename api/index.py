import sys
import os

# Add the backend directory to the Python path so Vercel can resolve local imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.main import app
