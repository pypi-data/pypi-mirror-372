from sqlalchemy import create_engine
from sqlalchemy import text


def _get_engine(conn):
    return create_engine(conn, echo=False)


def get_connection(conn):
    engine = _get_engine(conn)
    return engine.connect()


def execute(conn, sql, params=None):
    return conn.execute(text(sql), params)


def select_all(conn, sql, params=None):
    return execute(conn, sql, params).mappings().fetchall()


def select_one(conn, sql, params=None):
    return execute(conn, sql, params).mappings().fetchone()


def commit(conn):
    conn.commit()
