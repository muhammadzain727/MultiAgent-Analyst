
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

# Get database credentials
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Create database URL
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Connect to PostgreSQL
engine = create_engine(DATABASE_URL)

# Test connection
with engine.connect() as connection:
    print("Database connected successfully!")
