"""Database stored procedure operations."""

from . import engine
from .templates.mysql import template_engine
from ..models.procedure import Procedure


def is_exist(conn, env: str, procedure: Procedure):
    """Check if stored procedure exists"""
    sql = template_engine.render('mysql_check_procedure_exists')
    result = engine.select_one(conn, sql, {
        'env': env,
        'procedure_name': procedure.procedure_name,
        'routine_type': 'FUNCTION' if procedure.is_function else 'PROCEDURE'
    })
    return result is not None


def drop(conn, env: str, procedure: Procedure):
    """Drop stored procedure or function"""
    if procedure.is_function:
        sql = template_engine.render('mysql_drop_function', env=env, procedure_name=procedure.procedure_name)
    else:
        sql = template_engine.render('mysql_drop_procedure', env=env, procedure_name=procedure.procedure_name)
    engine.execute(conn, sql)


def create(conn, env: str, procedure: Procedure):
    """Create stored procedure or function"""
    if procedure.is_function:
        sql = template_engine.render('mysql_create_function', env=env, procedure=procedure)
    else:
        sql = template_engine.render('mysql_create_procedure', env=env, procedure=procedure)
    engine.execute(conn, sql)
