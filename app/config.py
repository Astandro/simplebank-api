import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL')

# Redis configuration
REDIS_HOST = os.getenv('REDIS_HOST')
REDIS_PORT = os.getenv('REDIS_PORT')

# Build the connection string for pyodbc
DATABASE_URL = os.getenv('DATABASE_URL')

# Use the connection string where needed
print("Database connection string:", os.getenv('DATABASE_URL'))
