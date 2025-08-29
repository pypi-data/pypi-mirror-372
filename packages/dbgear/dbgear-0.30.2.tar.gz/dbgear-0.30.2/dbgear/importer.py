"""
Generic schema importer with dynamic module loading.

This module provides a generic interface for importing schemas from various formats
by dynamically loading specific importer modules.
"""

import importlib
from pathlib import Path
from typing import Any, List, Optional


def import_schema(importer_type: str, *args, **kwargs) -> Any:
    """
    Import schema using the specified importer module.

    Dynamically loads the importer module and calls its retrieve function.

    Args:
        importer_type: Name of the importer module (e.g., 'a5sql_mk2')
        *args, **kwargs: Arguments to pass to the retrieve function

    Returns:
        SchemaManager: The imported schema manager object

    Raises:
        ImportError: If the importer module cannot be found
        AttributeError: If the importer module doesn't have a retrieve function
    """
    try:
        # Dynamically import the importer module
        module = importlib.import_module(f'dbgear_import.schema.{importer_type}')

        # Get and execute the retrieve function
        if hasattr(module, 'retrieve'):
            return module.retrieve(*args, **kwargs)
        else:
            raise AttributeError(f"Module '{importer_type}' does not have 'retrieve' function")

    except ImportError as e:
        raise ImportError(f"Importer '{importer_type}' not found: {e}")


def import_data(importer_type: str, source: str, schema, table_name: str,
                output_path: str, schema_name: str = 'main',
                json_fields: Optional[List[str]] = None, **kwargs) -> str:
    """
    Import data using the specified importer module.

    Dynamically loads the data importer module and calls its import_data function.

    Args:
        importer_type: Name of the importer module ('excel' or 'csv')
        source: Path to source file
        schema: Schema manager containing table definitions
        table_name: Name of the target table
        output_path: Directory path for output file
        schema_name: Name of the schema (default: 'main')
        json_fields: List of field names that should be treated as JSON paths
        **kwargs: Additional arguments to pass to the importer

    Returns:
        str: Path to the created .dat file

    Raises:
        ImportError: If the importer module cannot be found
        AttributeError: If the importer module doesn't have an import_data function
    """
    try:
        # Dynamically import the data importer module
        module = importlib.import_module(f'dbgear_import.data.{importer_type}')

        # Get and execute the import_data function
        if hasattr(module, 'import_data'):
            return module.import_data(source, schema, table_name, output_path,
                                    schema_name, json_fields, **kwargs)
        else:
            raise AttributeError(f"Module '{importer_type}' does not have 'import_data' function")

    except ImportError as e:
        raise ImportError(f"Data importer '{importer_type}' not found: {e}")


def list_importers() -> list[str]:
    """
    Get a list of available importer modules.

    Returns:
        List of available importer module names
    """
    importers_dir = Path(__file__).parent / 'schema'
    if not importers_dir.exists():
        return []

    return [f.stem for f in importers_dir.glob('*.py') if f.stem != '__init__']


def list_data_importers() -> list[str]:
    """
    Get a list of available data importer modules.

    Returns:
        List of available data importer module names
    """
    importers_dir = Path(__file__).parent / 'data'
    if not importers_dir.exists():
        return []

    return [f.stem for f in importers_dir.glob('*.py') if f.stem not in ('__init__', 'base', 'utils')]
