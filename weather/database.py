import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.ext.declarative import declarative_base


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:password@database/home"
engine = sa.create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = so.sessionmaker(autocommit=False, autoflush=False, bind=engine)
BaseModel = declarative_base()


def get():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
