from sqlalchemy import create_engine

DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/myfashionhub"

engine = create_engine(DATABASE_URL)

# Your task:
# 1. Create a database connection.
# 2. Test the connection.
# 3. Handle connection errors.