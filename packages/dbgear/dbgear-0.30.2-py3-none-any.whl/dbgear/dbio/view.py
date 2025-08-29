from . import engine
from .templates.mysql import template_engine
from ..models.view import View


def is_exist(conn, env: str, view: View):
    """Check if view exists"""
    sql = template_engine.render('mysql_check_view_exists')
    result = engine.select_one(conn, sql, {'env': env, 'view_name': view.view_name})
    return result is not None


def drop(conn, env: str, view: View):
    """Drop view"""
    sql = template_engine.render('mysql_drop_view', env=env, view_name=view.view_name)
    engine.execute(conn, sql)


def create(conn, env: str, view: View):
    """Create view"""
    sql = template_engine.render('mysql_create_view', env=env, view=view)
    engine.execute(conn, sql)


def create_or_replace(conn, env: str, view: View):
    """Create or replace view"""
    sql = template_engine.render(
        'mysql_create_or_replace_view',
        env=env,
        view_name=view.view_name,
        view_select_statement=view.select_statement
    )
    engine.execute(conn, sql)


def get_view_definition(conn, env: str, view_name: str):
    """Get view definition from database"""
    sql = template_engine.render('mysql_get_view_definition')
    result = engine.select_one(conn, sql, {'env': env, 'view_name': view_name})
    return result['VIEW_DEFINITION'] if result else None


def validate_dependencies(conn, env: str, view: View):
    """Validate that all dependencies exist"""
    for dependency in view.get_dependencies():
        # Check if dependency is a table
        table_sql = template_engine.render('mysql_check_dependency_exists')
        table_exists = engine.select_one(conn, table_sql, {'env': env, 'dependency_name': dependency})

        # Check if dependency is a view
        view_sql = template_engine.render('mysql_check_view_dependency_exists')
        view_exists = engine.select_one(conn, view_sql, {'env': env, 'dependency_name': dependency})

        if not table_exists and not view_exists:
            raise ValueError(f"Dependency '{dependency}' not found for view '{view.view_name}'")
