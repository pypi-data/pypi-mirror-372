"""
Table dependency analysis module.
Provides functionality to analyze table dependencies including relations,
views, triggers, indexes, and data sources.
"""

from typing import Dict, List, Any, Optional
import pathlib
import re
import yaml

from ..models.schema import SchemaManager


class DependencyItem:
    """Represents a single dependency item"""

    def __init__(
            self,
            dep_type: str,
            schema_name: str,
            table_name: Optional[str],
            object_name: str,
            details: Dict[str, Any],
            path: Optional[List[Dict[str, str]]] = None):
        self.type = dep_type
        self.schema_name = schema_name
        self.table_name = table_name
        self.object_name = object_name
        self.details = details
        self.path = path or []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format for JSON serialization"""
        result = {
            "type": self.type,
            "schema_name": self.schema_name,
            "table_name": self.table_name,
            "object_name": self.object_name,
            "details": self.details
        }
        if self.path:
            result["path"] = self.path
        return result


class TableDependencyAnalyzer:
    """Analyzes table dependencies and returns hierarchical relationship data"""

    def __init__(self, schema_manager: SchemaManager, project_folder: Optional[str] = None):
        self.schema_manager = schema_manager
        self.project_folder = project_folder

    def analyze(self, schema_name: str, table_name: str,
                left_level: int = 3, right_level: int = 3) -> Dict[str, Any]:
        """
        Analyze table dependencies up to specified levels.

        Args:
            schema_name: Target schema name
            table_name: Target table name
            left_level: Maximum level for left side (objects referencing target table)
            right_level: Maximum level for right side (objects referenced by target table)

        Returns:
            Dictionary containing hierarchical dependency information
        """
        if schema_name not in self.schema_manager:
            raise ValueError(f"Schema '{schema_name}' not found")

        schema = self.schema_manager[schema_name]
        if table_name not in schema.tables:
            raise ValueError(f"Table '{table_name}' not found in schema '{schema_name}'")

        # Validate levels
        if not (0 <= left_level <= 3):
            raise ValueError("left_level must be between 0 and 3")
        if not (0 <= right_level <= 3):
            raise ValueError("right_level must be between 0 and 3")

        result = {
            "target_table": {
                "schema_name": schema_name,
                "table_name": table_name
            },
            "left": {},
            "right": {}
        }

        # Build left side (objects referencing target table)
        if left_level > 0:
            result["left"] = self._build_left_dependencies(schema_name, table_name, left_level)

        # Build right side (objects referenced by target table)
        if right_level > 0:
            result["right"] = self._build_right_dependencies(schema_name, table_name, right_level)

        return result

    def _build_left_dependencies(self, schema_name: str, table_name: str, max_level: int) -> Dict[str, List[Dict[str, Any]]]:
        """Build left side dependencies (objects referencing target table)"""
        result = {}
        visited = set()

        for level in range(1, max_level + 1):
            level_key = f"level_{level}"
            result[level_key] = []

            if level == 1:
                # Direct references to target table
                items = self._get_direct_left_references(schema_name, table_name)
                result[level_key] = [item.to_dict() for item in items]
                visited.update(f"{item.schema_name}.{item.table_name or item.object_name}" for item in items)
            else:
                # Indirect references through previous level
                prev_level_key = f"level_{level - 1}"
                for prev_item_dict in result[prev_level_key]:
                    if prev_item_dict["table_name"]:  # Only follow table references
                        indirect_items = self._get_direct_left_references(
                            prev_item_dict["schema_name"],
                            prev_item_dict["table_name"]
                        )
                        for item in indirect_items:
                            item_key = f"{item.schema_name}.{item.table_name or item.object_name}"
                            if item_key not in visited:
                                # Add path information
                                item.path = [{
                                    "schema_name": prev_item_dict["schema_name"],
                                    "table_name": prev_item_dict["table_name"],
                                    "relation_type": prev_item_dict["type"]
                                }]
                                result[level_key].append(item.to_dict())
                                visited.add(item_key)

        return result

    def _build_right_dependencies(self, schema_name: str, table_name: str, max_level: int) -> Dict[str, List[Dict[str, Any]]]:
        """Build right side dependencies (objects referenced by target table)"""
        result = {}
        visited = set()

        for level in range(1, max_level + 1):
            level_key = f"level_{level}"
            result[level_key] = []

            if level == 1:
                # Direct references from target table
                items = self._get_direct_right_references(schema_name, table_name)
                result[level_key] = [item.to_dict() for item in items]
                visited.update(f"{item.schema_name}.{item.table_name or item.object_name}" for item in items)
            else:
                # Indirect references through previous level
                prev_level_key = f"level_{level - 1}"
                for prev_item_dict in result[prev_level_key]:
                    if prev_item_dict["table_name"] and prev_item_dict["type"] == "relation":
                        indirect_items = self._get_direct_right_references(
                            prev_item_dict["schema_name"],
                            prev_item_dict["table_name"]
                        )
                        for item in indirect_items:
                            item_key = f"{item.schema_name}.{item.table_name or item.object_name}"
                            if item_key not in visited:
                                # Add path information
                                item.path = [{
                                    "schema_name": prev_item_dict["schema_name"],
                                    "table_name": prev_item_dict["table_name"],
                                    "relation_type": prev_item_dict["type"]
                                }]
                                result[level_key].append(item.to_dict())
                                visited.add(item_key)

        return result

    def _get_direct_left_references(self, target_schema: str, target_table: str) -> List[DependencyItem]:
        """Get objects that directly reference the target table"""
        items = []

        # 1. Foreign key references from other tables
        for schema in self.schema_manager:
            for table in schema.tables:
                for relation in table.relations:
                    if (relation.target.schema_name == target_schema and relation.target.table_name == target_table):
                        items.append(DependencyItem(
                            dep_type="relation",
                            schema_name=schema.name,
                            table_name=table.table_name,
                            object_name=relation.constraint_name or f"fk_{table.table_name}_{target_table}",
                            details={
                                "constraint_name": relation.constraint_name,
                                "bind_columns": [
                                    {
                                        "source_column": bc.source_column,
                                        "target_column": bc.target_column
                                    } for bc in relation.bind_columns
                                ],
                                "on_delete": relation.on_delete,
                                "on_update": relation.on_update,
                                "cardinarity_source": relation.cardinarity_source,
                                "cardinarity_target": relation.cardinarity_target
                            }
                        ))

        # 2. Views that reference the target table
        for schema in self.schema_manager:
            for view in schema.views:
                if self._view_references_table(view.select_statement, target_schema, target_table):
                    items.append(DependencyItem(
                        dep_type="view",
                        schema_name=schema.name,
                        table_name=None,
                        object_name=view.view_name,
                        details={
                            "select_statement": view.select_statement,
                            "referenced_columns": self._extract_columns_from_view(view.select_statement, target_table),
                            "dependencies": view._dependencies
                        }
                    ))

        # 3. Triggers on the target table
        target_schema_obj = self.schema_manager[target_schema]
        if target_table in target_schema_obj.tables:
            # table_obj = target_schema_obj.tables[target_table]
            if hasattr(target_schema_obj, 'triggers'):
                for trigger in target_schema_obj.triggers:
                    if trigger.table_name == target_table:
                        items.append(DependencyItem(
                            dep_type="trigger",
                            schema_name=target_schema,
                            table_name=target_table,
                            object_name=trigger.trigger_name,
                            details={
                                "timing": trigger.timing,
                                "event": trigger.event,
                                "condition": trigger.condition,
                                "body": trigger.body
                            }
                        ))

        return items

    def _get_direct_right_references(self, source_schema: str, source_table: str) -> List[DependencyItem]:
        """Get objects that are directly referenced by the source table"""
        items = []

        source_schema_obj = self.schema_manager[source_schema]
        if source_table not in source_schema_obj.tables:
            return items

        table_obj = source_schema_obj.tables[source_table]

        # 1. Foreign key target tables
        for relation in table_obj.relations:
            items.append(DependencyItem(
                dep_type="relation",
                schema_name=relation.target.schema_name,
                table_name=relation.target.table_name,
                object_name=relation.constraint_name or f"fk_{source_table}_{relation.target.table_name}",
                details={
                    "constraint_name": relation.constraint_name,
                    "bind_columns": [
                        {
                            "source_column": bc.source_column,
                            "target_column": bc.target_column
                        } for bc in relation.bind_columns
                    ],
                    "on_delete": relation.on_delete,
                    "on_update": relation.on_update,
                    "cardinarity_source": relation.cardinarity_source,
                    "cardinarity_target": relation.cardinarity_target
                }
            ))

        # 2. Indexes on the source table
        for index in table_obj.indexes:
            items.append(DependencyItem(
                dep_type="index",
                schema_name=source_schema,
                table_name=source_table,
                object_name=index.index_name,
                details={
                    "columns": index.columns,
                    "index_type": index.index_type,
                    "unique": index.unique,
                    "partial_condition": index.partial_condition,
                    "include_columns": index.include_columns,
                    "storage_parameters": index.storage_parameters
                }
            ))


        return items


    def _view_references_table(self, select_statement: str, schema_name: str, table_name: str) -> bool:
        """Simple check if view references the specified table"""
        # This is a simple implementation - in practice, you might want proper SQL parsing
        statement_lower = select_statement.lower()

        # Check for table name references
        possible_refs = [
            f" {table_name} ",
            f" {table_name}.",
            f" {schema_name}.{table_name} ",
            f" {schema_name}.{table_name}.",
            f"\t{table_name}\t",
            f"\n{table_name}\n",
            f"from {table_name}",
            f"join {table_name}",
        ]

        return any(ref in statement_lower for ref in possible_refs)

    def _extract_columns_from_view(self, select_statement: str, table_name: str) -> List[str]:
        """Extract column names referenced from the specified table in the view"""
        # This is a simplified implementation
        # In practice, you would use proper SQL parsing
        columns = []

        statement_lower = select_statement.lower()
        if f"{table_name}." in statement_lower:
            # Very basic extraction - look for table_name.column_name patterns
            safe_table_name = re.escape(table_name)
            pattern = rf"{safe_table_name}\.(\w+)"
            matches = re.findall(pattern, statement_lower)
            columns.extend(matches)

        return list(set(columns))  # Remove duplicates
