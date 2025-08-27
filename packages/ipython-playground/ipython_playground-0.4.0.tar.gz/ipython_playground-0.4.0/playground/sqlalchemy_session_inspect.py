def dump_session_sql(session):
    "this doesn't really work yet"
    operations = [f"INSERT: {obj.__class__.__name__} {getattr(obj, 'id', 'new')}" for obj in session.new] + \
                 [f"UPDATE: {obj.__class__.__name__} {getattr(obj, 'id', 'unknown')}" for obj in session.dirty if obj not in session.new] + \
                 [f"DELETE: {obj.__class__.__name__} {getattr(obj, 'id', 'unknown')}" for obj in session.deleted]
    sql_statements = []

    def capture_sql(conn, clauseelement, multiparams, params, execution_options):
        sql_statements.append(str(clauseelement))
        return clauseelement, multiparams, params

    # Use a savepoint to isolate flush effects
    event.listen(session.bind, "before_execute", capture_sql, once=True)
    session.begin_nested()  # Start a savepoint
    session.flush()         # Generate SQL within savepoint
    session.rollback()      # Roll back only to savepoint, preserving outer state

    return operations, sql_statements
