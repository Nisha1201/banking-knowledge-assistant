from app.database import Base, engine
import app.models

print("Creating database tables...")

Base.metadata.create_all(bind = engine) #here create_all()see the models and create corresponding tables in MYSQL.

print("Database tables created successfully")

# python -m app.create_tables