from psycopg_pool import ConnectionPool
import psycopg
from psycopg.abc import Query
from contextlib import contextmanager
from typing import Optional


def create_db_pool(app):
    """
    Create Database connection pool

    Note: all returned connections are autocommit connection. If it's not the wanted behavior, wrap the query in an explicit transaction, or acquire a connection outside of the pool.
    """
    if hasattr(app, "pool"):
        return
    min_size = int(app.config["DB_MIN_CNX"])
    max_size = int(app.config["DB_MAX_CNX"])
    statement_timeout = app.config["DB_STATEMENT_TIMEOUT"]
    args = {"autocommit": True}
    if statement_timeout > 0:
        args["options"] = f"-c statement_timeout={statement_timeout}"
    app.pool = ConnectionPool(conninfo=app.config["DB_URL"], min_size=min_size, max_size=max_size, open=True, kwargs=args)
    # add also a connection pool without timeout for queries that are known to be long
    # This is useful for example for refreshing the pictures_grid materialized view
    app.long_queries_pool = ConnectionPool(
        conninfo=app.config["DB_URL"], min_size=0, max_size=max_size, open=True, kwargs={"autocommit": True}
    )


@contextmanager
def conn(app, timeout: Optional[float] = None):
    """Get a psycopg connection from the connection pool"""
    with app.pool.connection(timeout=timeout) as conn:
        yield conn


@contextmanager
def cursor(app, timeout: Optional[float] = None, **kwargs):
    """Get a psycopg cursor from the connection pool"""
    with app.pool.connection(timeout=timeout) as conn:
        yield conn.cursor(**kwargs)


@contextmanager
def execute(app, sql, params=None, timeout: Optional[float] = None, **kwargs):
    """Simple helpers to simplify simple calls to get a cursor and execute a query on it"""
    with cursor(app, timeout=timeout, **kwargs) as c:
        yield c.execute(sql, params=params)


def fetchone(app, sql, params=None, timeout: Optional[float] = None, **kwargs):
    """Simple helpers to simplify simple calls to fetchone"""
    with execute(app, sql, params, timeout=timeout, **kwargs) as q:
        return q.fetchone()


def fetchall(app, sql, params=None, timeout: Optional[float] = None, **kwargs):
    """Simple helpers to simplify simple calls to fetchall"""
    with execute(app, sql, params, timeout=timeout, **kwargs) as q:
        return q.fetchall()


@contextmanager
def long_queries_conn(app, connection_timeout: Optional[float] = None):
    """Get a psycopg connection for queries that are known to be long from the connection pool"""
    with app.long_queries_pool.connection(timeout=connection_timeout) as conn:
        yield conn


def query_as_string(conn: psycopg.Connection, query: Query, params: dict):
    """Get query as string for debug purpose"""
    return psycopg.ClientCursor(conn).mogrify(query, params)
