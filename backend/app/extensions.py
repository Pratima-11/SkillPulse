"""
Shared extension instances.

Created here (not inside __init__.py) so that model files and route files
can import `db` without causing circular imports with the app factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
