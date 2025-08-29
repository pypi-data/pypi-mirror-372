# flake8: noqa: D100
"""MySQL-specific SQL templates."""

from ..engine import template_engine


# {%- for relation in table.relations %}
#   {%- if relation.constraint_name %}
#   , CONSTRAINT {{ relation.constraint_name }}
#     FOREIGN KEY ({{ relation.bind_columns | map(attribute='source_column') | join_columns }})
#     REFERENCES {{ relation.target.table_name }} ({{ relation.bind_columns | map(attribute='target_column') | join_columns }})
#     {%- if relation.on_delete != 'RESTRICT' %} ON DELETE {{ relation.on_delete }}{% endif %}
#     {%- if relation.on_update != 'RESTRICT' %} ON UPDATE {{ relation.on_update }}{% endif %}
#   {%- endif %}
# {%- endfor %}


# CREATE TABLE template (without foreign key constraints)
CREATE_TABLE_TEMPLATE = """
CREATE TABLE {{ env }}.{{ table.table_name }} (
{%- for column in table.columns %}
  {{ column.column_name | escape_identifier }} {{ column.column_type.base_type }}
  {%- if column.column_type.length and column.column_type.length > 0 %}({{ column.column_type.length }}){% endif %}
  {%- if column.column_type.precision and column.column_type.scale %}({{ column.column_type.precision }}, {{ column.column_type.scale }}){% elif column.column_type.precision %}({{ column.column_type.precision }}){% endif %}
  {%- if not column.nullable %} NOT NULL{% endif %}
  {%- if column.auto_increment %} AUTO_INCREMENT{% endif %}
  {%- if column.expression %} GENERATED ALWAYS AS ({{ column.expression }}) {% if column.stored %}STORED{% else %}VIRTUAL{% endif %}{% elif column.default_value %} DEFAULT {{ column.default_value }}{% endif %}
  {%- if column.charset %} CHARACTER SET {{ column.charset }}{% endif %}
  {%- if column.collation %} COLLATE {{ column.collation }}{% endif %}
  {%- if not loop.last %},{% endif %}
{%- endfor %}
{%- set pk_columns = table.columns | selectattr('primary_key', 'ne', none) | sort(attribute='primary_key') | list %}
{%- if pk_columns %}
  , CONSTRAINT {{ table.table_name }}_PKC PRIMARY KEY ({{ pk_columns | map(attribute='column_name') | join_columns }})
{%- endif %}
)
{%- if table.mysql_options %}
{%- if table.mysql_options.engine %} ENGINE={{ table.mysql_options.engine }}{% endif %}
{%- if table.mysql_options.charset %} DEFAULT CHARSET={{ table.mysql_options.charset }}{% endif %}
{%- if table.mysql_options.collation %} COLLATE={{ table.mysql_options.collation }}{% endif %}
{%- if table.mysql_options.auto_increment %} AUTO_INCREMENT={{ table.mysql_options.auto_increment }}{% endif %}
{%- if table.mysql_options.row_format %} ROW_FORMAT={{ table.mysql_options.row_format }}{% endif %}
{%- endif %}
"""

# ALTER TABLE ADD FOREIGN KEY template
ALTER_TABLE_ADD_FOREIGN_KEY_TEMPLATE = """
ALTER TABLE {{ env }}.{{ table.table_name }}
ADD CONSTRAINT {{ relation.constraint_name }}
FOREIGN KEY ({{ relation.bind_columns | map(attribute='source_column') | join_columns }})
REFERENCES {{ relation.target.table_name }} ({{ relation.bind_columns | map(attribute='target_column') | join_columns }})
{%- if relation.on_delete != 'RESTRICT' %} ON DELETE {{ relation.on_delete }}{% endif %}
{%- if relation.on_update != 'RESTRICT' %} ON UPDATE {{ relation.on_update }}{% endif %}
"""

# DROP FOREIGN KEY template
DROP_FOREIGN_KEY_TEMPLATE = """
ALTER TABLE {{ env }}.{{ table_name }}
DROP FOREIGN KEY {{ constraint_name }}
"""

# CHECK FOREIGN KEY EXISTS template
CHECK_FOREIGN_KEY_EXISTS_TEMPLATE = """
SELECT CONSTRAINT_NAME FROM information_schema.table_constraints
WHERE table_schema = :env AND table_name = :table_name AND constraint_name = :constraint_name AND constraint_type = 'FOREIGN KEY'
"""

# CREATE INDEX template
CREATE_INDEX_TEMPLATE = """
CREATE {% if index.unique %}UNIQUE {% endif %}INDEX {{ index.index_name or (table.table_name + '_IX' + loop.index0|string) }}
{%- if index.index_type and index.index_type != 'BTREE' %} USING {{ index.index_type }}{% endif %}
 ON {{ env }}.{{ table.table_name }} ({{ index.columns | join_columns }})
{%- if index.partial_condition %} WHERE {{ index.partial_condition }}{% endif %}
"""

# CREATE VIEW template
CREATE_VIEW_TEMPLATE = """
CREATE VIEW {{ env }}.{{ view.view_name }} AS
{{ view.select_statement }}
"""

# CREATE DATABASE template
CREATE_DATABASE_TEMPLATE = """
CREATE DATABASE {{ database_name }}
{%- if charset %} DEFAULT CHARACTER SET {{ charset }}{% endif %}
{%- if collation %} COLLATE {{ collation }}{% endif %}
"""

# DROP DATABASE template
DROP_DATABASE_TEMPLATE = """
DROP DATABASE {{ database_name }}
"""

# CHECK TABLE EXISTS template
CHECK_TABLE_EXISTS_TEMPLATE = """
SELECT TABLE_NAME FROM information_schema.tables
WHERE table_schema = :env AND table_name = :table_name
"""

# DROP TABLE template
DROP_TABLE_TEMPLATE = """
DROP TABLE {{ env }}.{{ table_name }}
"""

# INSERT INTO template
INSERT_INTO_TEMPLATE = """
INSERT INTO {{ env }}.{{ table_name }} ({{ column_names | join_columns }})
VALUES ({{ value_placeholders | join(', ') }})
"""

# BACKUP TABLE template (CREATE TABLE AS SELECT)
BACKUP_TABLE_TEMPLATE = """
CREATE TABLE {{ env }}.bak_{{ table_name }}_{{ ymd }} AS
SELECT * FROM {{ env }}.{{ table_name }}
"""

# RESTORE TABLE template (INSERT IGNORE SELECT)
RESTORE_TABLE_TEMPLATE = """
INSERT IGNORE INTO {{ env }}.{{ table_name }}
SELECT * FROM {{ env }}.bak_{{ table_name }}_{{ ymd }}
"""

# CHECK BACKUP EXISTS template
CHECK_BACKUP_EXISTS_TEMPLATE = """
SELECT TABLE_NAME FROM information_schema.tables
WHERE table_schema = :env AND table_name = :backup_table_name
"""

# CHECK DATABASE EXISTS template
CHECK_DATABASE_EXISTS_TEMPLATE = """
SHOW DATABASES LIKE :database_name
"""

# CHECK VIEW EXISTS template
CHECK_VIEW_EXISTS_TEMPLATE = """
SELECT TABLE_NAME FROM information_schema.views
WHERE table_schema = :env AND table_name = :view_name
"""

# DROP VIEW template
DROP_VIEW_TEMPLATE = """
DROP VIEW IF EXISTS {{ env }}.{{ view_name }}
"""

# CREATE OR REPLACE VIEW template
CREATE_OR_REPLACE_VIEW_TEMPLATE = """
CREATE OR REPLACE VIEW {{ env }}.{{ view_name }} AS
{{ view_select_statement }}
"""

# GET VIEW DEFINITION template
GET_VIEW_DEFINITION_TEMPLATE = """
SELECT VIEW_DEFINITION FROM information_schema.views
WHERE table_schema = :env AND table_name = :view_name
"""

# CHECK DEPENDENCY EXISTS template (for tables and views)
CHECK_DEPENDENCY_EXISTS_TEMPLATE = """
SELECT TABLE_NAME FROM information_schema.tables
WHERE table_schema = :env AND table_name = :dependency_name
"""

# CHECK VIEW DEPENDENCY EXISTS template
CHECK_VIEW_DEPENDENCY_EXISTS_TEMPLATE = """
SELECT TABLE_NAME FROM information_schema.views
WHERE table_schema = :env AND table_name = :dependency_name
"""

# CREATE TRIGGER template
CREATE_TRIGGER_TEMPLATE = """
CREATE TRIGGER {{ env }}.{{ trigger.trigger_name }}
{{ trigger.timing }} {{ trigger.event }} ON {{ env }}.{{ trigger.table_name }}
FOR EACH ROW
{% if trigger.condition %}
WHEN ({{ trigger.condition }})
{% endif -%}
{{ trigger.body }}
"""

# DROP TRIGGER template
DROP_TRIGGER_TEMPLATE = """
DROP TRIGGER IF EXISTS {{ env }}.{{ trigger_name }}
"""

# CHECK TRIGGER EXISTS template
CHECK_TRIGGER_EXISTS_TEMPLATE = """
SELECT TRIGGER_NAME FROM information_schema.triggers
WHERE trigger_schema = :env AND trigger_name = :trigger_name
"""

# CREATE PROCEDURE template
CREATE_PROCEDURE_TEMPLATE = """
CREATE PROCEDURE {{ env }}.{{ procedure.procedure_name }}(
{%- for param in procedure.parameters %}
{{ param.parameter_type }} {{ param.parameter_name }} {{ param.data_type }}
{%- if param.default_value %} DEFAULT {{ param.default_value }}{% endif %}
{%- if not loop.last %}, {% endif %}
{%- endfor %}
)
{% if procedure.deterministic %} DETERMINISTIC{% else %} NOT DETERMINISTIC{% endif %}
{% if procedure.reads_sql_data %} READS SQL DATA{% endif %}
{% if procedure.modifies_sql_data %} MODIFIES SQL DATA{% endif %}
 SQL SECURITY {{ procedure.security_type }}
BEGIN
{{ procedure.body }}
END
"""

# CREATE FUNCTION template
CREATE_FUNCTION_TEMPLATE = """
CREATE FUNCTION {{ env }}.{{ procedure.procedure_name }}(
{%- for param in procedure.parameters %}
{{ param.parameter_name }} {{ param.data_type }}
{%- if not loop.last %}, {% endif %}
{%- endfor %}
)
RETURNS {{ procedure.return_type }}
{%- if procedure.deterministic %} DETERMINISTIC{% else %} NOT DETERMINISTIC{% endif %}
{% if procedure.reads_sql_data %} READS SQL DATA{% endif %}
{% if procedure.modifies_sql_data %} MODIFIES SQL DATA{% endif %}
 SQL SECURITY {{ procedure.security_type }}
BEGIN
{{ procedure.body }}
END
"""

# DROP PROCEDURE template
DROP_PROCEDURE_TEMPLATE = """
DROP PROCEDURE IF EXISTS {{ env }}.{{ procedure_name }}
"""

# DROP FUNCTION template
DROP_FUNCTION_TEMPLATE = """
DROP FUNCTION IF EXISTS {{ env }}.{{ procedure_name }}
"""

# CHECK PROCEDURE EXISTS template
CHECK_PROCEDURE_EXISTS_TEMPLATE = """
SELECT ROUTINE_NAME FROM information_schema.routines
WHERE routine_schema = :env AND routine_name = :procedure_name AND routine_type = :routine_type
"""

# Register templates
template_engine.add_template('mysql_create_table', CREATE_TABLE_TEMPLATE)
template_engine.add_template('mysql_create_index', CREATE_INDEX_TEMPLATE)
template_engine.add_template('mysql_create_view', CREATE_VIEW_TEMPLATE)
template_engine.add_template('mysql_create_database', CREATE_DATABASE_TEMPLATE)
template_engine.add_template('mysql_drop_database', DROP_DATABASE_TEMPLATE)
template_engine.add_template('mysql_check_table_exists', CHECK_TABLE_EXISTS_TEMPLATE)
template_engine.add_template('mysql_drop_table', DROP_TABLE_TEMPLATE)
template_engine.add_template('mysql_insert_into', INSERT_INTO_TEMPLATE)
template_engine.add_template('mysql_backup_table', BACKUP_TABLE_TEMPLATE)
template_engine.add_template('mysql_restore_table', RESTORE_TABLE_TEMPLATE)
template_engine.add_template('mysql_check_backup_exists', CHECK_BACKUP_EXISTS_TEMPLATE)
template_engine.add_template('mysql_check_database_exists', CHECK_DATABASE_EXISTS_TEMPLATE)
template_engine.add_template('mysql_check_view_exists', CHECK_VIEW_EXISTS_TEMPLATE)
template_engine.add_template('mysql_drop_view', DROP_VIEW_TEMPLATE)
template_engine.add_template('mysql_create_or_replace_view', CREATE_OR_REPLACE_VIEW_TEMPLATE)
template_engine.add_template('mysql_get_view_definition', GET_VIEW_DEFINITION_TEMPLATE)
template_engine.add_template('mysql_check_dependency_exists', CHECK_DEPENDENCY_EXISTS_TEMPLATE)
template_engine.add_template('mysql_check_view_dependency_exists', CHECK_VIEW_DEPENDENCY_EXISTS_TEMPLATE)
template_engine.add_template('mysql_create_trigger', CREATE_TRIGGER_TEMPLATE)
template_engine.add_template('mysql_drop_trigger', DROP_TRIGGER_TEMPLATE)
template_engine.add_template('mysql_check_trigger_exists', CHECK_TRIGGER_EXISTS_TEMPLATE)
template_engine.add_template('mysql_create_procedure', CREATE_PROCEDURE_TEMPLATE)
template_engine.add_template('mysql_create_function', CREATE_FUNCTION_TEMPLATE)
template_engine.add_template('mysql_drop_procedure', DROP_PROCEDURE_TEMPLATE)
template_engine.add_template('mysql_drop_function', DROP_FUNCTION_TEMPLATE)
template_engine.add_template('mysql_check_procedure_exists', CHECK_PROCEDURE_EXISTS_TEMPLATE)
# Foreign key constraint templates
template_engine.add_template('mysql_add_foreign_key', ALTER_TABLE_ADD_FOREIGN_KEY_TEMPLATE)
template_engine.add_template('mysql_drop_foreign_key', DROP_FOREIGN_KEY_TEMPLATE)
template_engine.add_template('mysql_check_foreign_key_exists', CHECK_FOREIGN_KEY_EXISTS_TEMPLATE)
