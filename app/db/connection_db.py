from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from dotenv import load_dotenv
import os


load_dotenv()

database_uri=os.getenv("db_uri")
engine=create_engine(database_uri)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base=declarative_base()

def db_connection():
    db=SessionLocal()
    try:
        yield db
        print("Connection is comming back in Action")
    except Exception as e:
        print("Error ")
        raise
    finally:
        db.close()
        print("Connection is closed")
