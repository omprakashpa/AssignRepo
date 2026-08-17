from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from config import DATABASE_URL

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def search_scans_by_query(db, query: str, owner_id: int) -> list:
    # Bind user input as a SQL parameter. Escape LIKE wildcards so the
    # caller controls the search term, not the SQL expression.
    escaped_query = (
        query.replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    pattern = f"%{escaped_query}%"

    sql = text(
        """
        SELECT id, title, description, severity, status, cve_id,
               affected_component, owner_id, created_at
        FROM scan_results
        WHERE owner_id = :owner_id
          AND (
              title LIKE :pattern ESCAPE '\\'
              OR description LIKE :pattern ESCAPE '\\'
              OR cve_id LIKE :pattern ESCAPE '\\'
          )
        """
    )
    result = db.execute(
        sql,
        {"owner_id": owner_id, "pattern": pattern},
    )
    return [dict(row._mapping) for row in result]
