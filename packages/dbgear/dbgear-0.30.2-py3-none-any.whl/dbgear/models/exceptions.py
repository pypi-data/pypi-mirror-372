"""
DBGear unified exception classes
"""


class DBGearError(Exception):
    """Base exception class for all DBGear model errors"""
    pass


class DBGearEntityExistsError(DBGearError):
    """Raised when attempting to create an entity that already exists"""
    pass


class DBGearEntityNotFoundError(DBGearError):
    """Raised when attempting to access an entity that does not exist"""
    pass


class DBGearEntityRemovalError(DBGearError):
    """Raised when an entity cannot be removed due to constraints"""
    pass
