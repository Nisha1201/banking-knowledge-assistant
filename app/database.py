import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()  #it load variables from .env in python

DB_HOST=os.getenv("DB_HOST")  #os.getenv()->it gets the value from .env
DB_PORT=os.getenv("DB_PORT")
DB_NAME=os.getenv("DB_NAME")
DB_USER=os.getenv("DB_USER")
DB_PASSWORD=os.getenv("DB_PASSWORD")

DATABASE_URL=(
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}" # Mysql DB se connect karne ke liye PyMYSQL use karo.
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
)


# Ye SQLAlchemy ka main DB connection interface hai
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal=sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()  #this classes represent database tables.

if __name__ =="__main__":
    try:
        with engine.connect():
            print("MYSQL connection successful")

    except Exception as error:
        print("MYSQL connection failed")
        print(error)


# Create Database->.env ->database.py ->test connection-> create documents and question_history tables.
# python -m app.database