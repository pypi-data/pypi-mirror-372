"""Database trigger operations."""

from . import engine
from .templates.mysql import template_engine
from ..models.trigger import Trigger


def is_exist(conn, env: str, trigger: Trigger):
    """Check if trigger exists"""
    sql = template_engine.render('mysql_check_trigger_exists')
    result = engine.select_one(conn, sql, {'env': env, 'trigger_name': trigger.trigger_name})
    return result is not None


def drop(conn, env: str, trigger: Trigger):
    """Drop trigger"""
    sql = template_engine.render('mysql_drop_trigger', env=env, trigger_name=trigger.trigger_name)
    engine.execute(conn, sql)


def create(conn, env: str, trigger: Trigger):
    """Create trigger"""
    sql = template_engine.render('mysql_create_trigger', env=env, trigger=trigger)
    engine.execute(conn, sql)
