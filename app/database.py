from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker

from .config import get_settings


settings = get_settings()


# ---------------------------------------------------------
# SQLite database setup
# ---------------------------------------------------------

if settings.database_url.startswith("sqlite:///"):

    # Get database path from DATABASE_URL
    database_path = settings.database_url.replace(
        "sqlite:///",
        "",
        1
    )

    database_path = Path(database_path)

    # Convert relative path to absolute path
    if not database_path.is_absolute():

        database_path = (
            Path.cwd() / database_path
        )

    # Create parent directory automatically
    database_path.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Use absolute SQLite path
    database_url = (
        "sqlite:///"
        + database_path.as_posix()
    )

    connect_args = {
        "check_same_thread": False
    }

else:

    database_url = settings.database_url

    connect_args = {}


# ---------------------------------------------------------
# SQLAlchemy engine
# ---------------------------------------------------------

engine = create_engine(

    database_url,

    connect_args=connect_args,

    future=True
)


# ---------------------------------------------------------
# Database session
# ---------------------------------------------------------

SessionLocal = sessionmaker(

    bind=engine,

    autoflush=False,

    autocommit=False,

    expire_on_commit=False
)


# ---------------------------------------------------------
# Base model
# ---------------------------------------------------------

class Base(DeclarativeBase):

    pass


# ---------------------------------------------------------
# Dependency
# ---------------------------------------------------------

def get_db():

    db = SessionLocal()

    try:

        yield db

    finally:

        db.close()


# ---------------------------------------------------------
# Initialize database
# ---------------------------------------------------------

def init_db():

    from . import models

    Base.metadata.create_all(

        bind=engine
    )