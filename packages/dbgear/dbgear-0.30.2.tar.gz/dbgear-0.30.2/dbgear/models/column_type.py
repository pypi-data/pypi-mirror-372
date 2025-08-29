import pydantic
import re

from .base import BaseSchema


class ColumnTypeItem(BaseSchema):
    value: str
    caption_: str | None = pydantic.Field(default=None, alias='caption')
    description: str | None = None

    @classmethod
    def from_string(cls, value: str):
        return cls(value=value)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)

    @property
    def caption(self) -> str:
        return self.caption_ if self.caption_ is not None else self.value


class ColumnType(BaseSchema):
    column_type: str
    base_type: str  # Base type (e.g., INT, VARCHAR, etc.)
    length: int | None = None  # Length for VARCHAR, CHAR, etc.
    precision: int | None = None  # Precision for DECIMAL, NUMERIC, etc.
    scale: int | None = None  # Scale for DECIMAL, NUMERIC, etc.
    items: list[ColumnTypeItem] | None = None  # For ENUM or SET types
    json_schema: dict | None = None  # JSON Schema for JSON column types

    def get_item_values(self) -> list[str]:
        """Get list of item values for SQL generation."""
        if not self.items:
            return []
        return [item.value for item in self.items]

    def add_item(self, item: str | dict | ColumnTypeItem) -> None:
        """Add an item to the items list."""
        if self.items is None:
            self.items = []

        if isinstance(item, str):
            self.items.append(ColumnTypeItem.from_string(item))
        elif isinstance(item, dict):
            self.items.append(ColumnTypeItem.from_dict(item))
        elif isinstance(item, ColumnTypeItem):
            self.items.append(item)
        else:
            raise ValueError(f"Invalid item type: {type(item)}")

    def remove_item(self, value: str) -> bool:
        """Remove an item by its value. Returns True if found and removed."""
        if not self.items:
            return False

        for i, item in enumerate(self.items):
            if item.value == value:
                del self.items[i]
                return True
        return False


class ColumnTypeRegistry:

    def __init__(self, types: dict[str, ColumnType]):
        self.types = types

    def __getitem__(self, key: str) -> ColumnType:
        return self.types.get(key)

    def __iter__(self):
        yield from self.types.values()

    def __len__(self) -> int:
        return len(self.types)

    def __contains__(self, key: str) -> bool:
        return key in self.types

    def append(self, column_type: ColumnType) -> None:
        if column_type.column_type in self.types:
            raise ValueError(f"Column type '{column_type.column_type}' already exists")
        self.types[column_type.column_type] = column_type

    def remove(self, column_type: str) -> None:
        if column_type not in self.types:
            raise KeyError(f"Column type '{column_type}' not found")
        del self.types[column_type]


def parse_column_type(type_string: str) -> ColumnType:
    """
    Parse a column type string and create a ColumnType object.

    Supports various MySQL type formats:
    - VARCHAR(255)
    - INT(11)
    - DECIMAL(10,2)
    - ENUM('a','b','c')
    - SET('x','y')
    - TEXT
    - DATETIME

    Args:
        type_string: The column type string to parse

    Returns:
        ColumnType object with parsed attributes

    Raises:
        ValueError: If the type string cannot be parsed
    """
    if not type_string or not isinstance(type_string, str):
        raise ValueError("type_string must be a non-empty string")

    original_type_string = type_string.strip()
    type_string_upper = original_type_string.upper()

    # Extract base type and parameters
    base_type_match = re.match(r'^([A-Z]+)', type_string_upper)
    if not base_type_match:
        raise ValueError(f"Cannot extract base type from: {type_string_upper}")

    base_type = base_type_match.group(1)

    # Initialize ColumnType with defaults
    column_type = ColumnType(
        column_type=original_type_string,
        base_type=base_type
    )

    # Parse length parameter for types like VARCHAR(255), CHAR(10)
    if base_type in ['VARCHAR', 'CHAR', 'VARBINARY', 'BINARY']:
        length_match = re.search(r'\((\d+)\)', type_string_upper)
        if length_match:
            column_type.length = int(length_match.group(1))

    # Parse length parameter for INT types
    elif base_type in ['TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER', 'BIGINT']:
        length_match = re.search(r'\((\d+)\)', type_string_upper)
        if length_match:
            column_type.length = int(length_match.group(1))

    # Parse precision and scale for DECIMAL/NUMERIC types
    elif base_type in ['DECIMAL', 'NUMERIC', 'DEC']:
        decimal_match = re.search(r'\((\d+)(?:,\s*(\d+))?\)', type_string_upper)
        if decimal_match:
            column_type.precision = int(decimal_match.group(1))
            if decimal_match.group(2):
                column_type.scale = int(decimal_match.group(2))

    # Parse ENUM and SET values
    elif base_type in ['ENUM', 'SET']:
        # codeql[python/polynomial-redos] - This regex is safe as it matches a specific pattern
        values_match = re.search(r'\((.*)\)', original_type_string)
        if values_match:
            values_str = values_match.group(1)
            # Parse comma-separated quoted values
            items = []
            for match in re.finditer(r"'([^']*)'", values_str):
                value_str = match.group(1)
                # Check if value contains colon for value:caption format
                if ':' in value_str:
                    value_parts = value_str.split(':', 1)  # Split only on first colon
                    value = value_parts[0]
                    caption = value_parts[1]
                    items.append(ColumnTypeItem(value=value, caption=caption))
                else:
                    # No colon, use same value for both value and caption
                    items.append(ColumnTypeItem.from_string(value_str))
            column_type.items = items

    # Parse FLOAT and DOUBLE precision
    elif base_type in ['FLOAT', 'DOUBLE', 'REAL']:
        precision_match = re.search(r'\((\d+)(?:,\s*(\d+))?\)', type_string_upper)
        if precision_match:
            column_type.precision = int(precision_match.group(1))
            if precision_match.group(2):
                column_type.scale = int(precision_match.group(2))

    return column_type


def create_simple_column_type(
        base_type: str,
        length: int | None = None,
        precision: int | None = None,
        scale: int | None = None,
        items: list[str | dict | ColumnTypeItem] | None = None,
        json_schema: dict | None = None) -> ColumnType:
    """
    Create a ColumnType object with specified parameters.

    Args:
        base_type: The base column type (e.g., 'VARCHAR', 'INT', 'DECIMAL')
        length: Length for string types or display width for integer types
        precision: Precision for decimal types
        scale: Scale for decimal types
        items: Items for ENUM or SET types (strings, dicts with value/caption/description, or ColumnTypeItem objects)
        json_schema: JSON Schema for JSON column types (optional)

    Returns:
        ColumnType object
    """
    base_type = base_type.upper()

    # Build the column_type string
    type_parts = [base_type]

    if base_type in ['ENUM', 'SET'] and items:
        # Convert items to ColumnTypeItem objects
        processed_items = []
        for item in items:
            if isinstance(item, str):
                processed_items.append(ColumnTypeItem.from_string(item))
            elif isinstance(item, dict):
                processed_items.append(ColumnTypeItem.from_dict(item))
            elif isinstance(item, ColumnTypeItem):
                processed_items.append(item)
            else:
                processed_items.append(ColumnTypeItem.from_string(str(item)))

        items_str = ', '.join(f"'{item.value}'" for item in processed_items)
        type_parts.append(f"({items_str})")
        column_type_str = ''.join(type_parts)

        # Store as ColumnTypeItem objects
        items = processed_items
    elif base_type in ['DECIMAL', 'NUMERIC', 'DEC'] and precision:
        if scale is not None:
            type_parts.append(f"({precision},{scale})")
        else:
            type_parts.append(f"({precision})")
        column_type_str = ''.join(type_parts)
    elif base_type in ['FLOAT', 'DOUBLE'] and precision:
        if scale is not None:
            type_parts.append(f"({precision},{scale})")
        else:
            type_parts.append(f"({precision})")
        column_type_str = ''.join(type_parts)
    elif length is not None:
        type_parts.append(f"({length})")
        column_type_str = ''.join(type_parts)
    else:
        column_type_str = base_type

    return ColumnType(
        column_type=column_type_str,
        base_type=base_type,
        length=length,
        precision=precision,
        scale=scale,
        items=items,
        json_schema=json_schema
    )


def get_mysql_type_defaults() -> dict[str, ColumnType]:
    """
    Get a dictionary of common MySQL column types with their default configurations.

    Returns:
        Dictionary mapping type names to ColumnType objects
    """
    return {
        # String types
        'VARCHAR': create_simple_column_type('VARCHAR', length=255),
        'CHAR': create_simple_column_type('CHAR', length=1),
        'TEXT': create_simple_column_type('TEXT'),
        'LONGTEXT': create_simple_column_type('LONGTEXT'),
        'MEDIUMTEXT': create_simple_column_type('MEDIUMTEXT'),
        'TINYTEXT': create_simple_column_type('TINYTEXT'),

        # Integer types
        'INT': create_simple_column_type('INT', length=11),
        'BIGINT': create_simple_column_type('BIGINT', length=20),
        'SMALLINT': create_simple_column_type('SMALLINT', length=6),
        'TINYINT': create_simple_column_type('TINYINT', length=4),
        'MEDIUMINT': create_simple_column_type('MEDIUMINT', length=9),

        # Decimal types
        'DECIMAL': create_simple_column_type('DECIMAL', precision=10, scale=2),
        'FLOAT': create_simple_column_type('FLOAT'),
        'DOUBLE': create_simple_column_type('DOUBLE'),

        # Date/time types
        'DATETIME': create_simple_column_type('DATETIME'),
        'DATE': create_simple_column_type('DATE'),
        'TIME': create_simple_column_type('TIME'),
        'TIMESTAMP': create_simple_column_type('TIMESTAMP'),
        'YEAR': create_simple_column_type('YEAR'),

        # Binary types
        'BLOB': create_simple_column_type('BLOB'),
        'LONGBLOB': create_simple_column_type('LONGBLOB'),
        'MEDIUMBLOB': create_simple_column_type('MEDIUMBLOB'),
        'TINYBLOB': create_simple_column_type('TINYBLOB'),
        'VARBINARY': create_simple_column_type('VARBINARY', length=255),
        'BINARY': create_simple_column_type('BINARY', length=1),

        # JSON type (MySQL 5.7+)
        'JSON': create_simple_column_type('JSON'),

        # Boolean type (alias for TINYINT(1))
        'BOOLEAN': create_simple_column_type('TINYINT', length=1),
        'BOOL': create_simple_column_type('TINYINT', length=1),
    }


def is_numeric_type(column_type: ColumnType) -> bool:
    """
    Check if a column type is numeric.

    Args:
        column_type: The ColumnType to check

    Returns:
        True if the type is numeric, False otherwise
    """
    numeric_types = {
        'TINYINT', 'SMALLINT', 'MEDIUMINT', 'INT', 'INTEGER', 'BIGINT',
        'DECIMAL', 'NUMERIC', 'DEC', 'FLOAT', 'DOUBLE', 'REAL', 'BIT'
    }
    return column_type.base_type in numeric_types


def is_string_type(column_type: ColumnType) -> bool:
    """
    Check if a column type is a string type.

    Args:
        column_type: The ColumnType to check

    Returns:
        True if the type is a string type, False otherwise
    """
    string_types = {
        'CHAR', 'VARCHAR', 'TEXT', 'TINYTEXT', 'MEDIUMTEXT', 'LONGTEXT',
        'ENUM', 'SET'
    }
    return column_type.base_type in string_types


def is_date_time_type(column_type: ColumnType) -> bool:
    """
    Check if a column type is a date/time type.

    Args:
        column_type: The ColumnType to check

    Returns:
        True if the type is a date/time type, False otherwise
    """
    datetime_types = {
        'DATE', 'TIME', 'DATETIME', 'TIMESTAMP', 'YEAR'
    }
    return column_type.base_type in datetime_types
