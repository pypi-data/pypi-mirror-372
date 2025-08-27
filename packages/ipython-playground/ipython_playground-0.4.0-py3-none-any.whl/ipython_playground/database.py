from typing import Optional

from .utils import log


def setup_database_session(database_url):
    """Set up the SQLAlchemy engine and session, return helpful globals"""
    from activemodel import SessionManager
    from activemodel.session_manager import _session_context
    from activemodel.utils import compile_sql
    from sqlalchemy import create_engine

    def sa_run(stmt):
        result = session.execute(stmt).all()
        return result

    def sa_sql(stmt):
        return compile_sql(stmt)

    engine = create_engine(database_url, echo=True)
    session = SessionManager.get_instance().get_session().__enter__()
    _session_context.set(session)

    return {"engine": engine, "session": session, "sa_sql": sa_sql, "sa_run": sa_run}


def reset_database_session(database_url: str):
    """Reset the database session with a new database URL"""
    from activemodel.session_manager import _session_context

    log.info(f"Resetting database session with URL: {database_url}")

    # Close existing session if any
    try:
        current_session = _session_context.get()
        if current_session:
            current_session.close()
    except Exception as e:
        log.debug(f"No existing session to close: {e}")

    # Set up new session
    return setup_database_session(database_url)


def get_database_url() -> Optional[str]:
    """Attempt to get database URL from app configuration"""
    try:
        from app.configuration.database import (
            database_url as database_url_generator,
        )

        return database_url_generator()
    except ImportError:
        log.debug("Could not import database URL from app configuration")
        return None
