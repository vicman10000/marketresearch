"""
Storage abstraction layer

Provides unified interface for data storage (CSV, SQLite, PostgreSQL).
"""
from .base import DataStore
from .csv_store import CSVDataStore
from .sqlite_store import SQLiteDataStore

__all__ = ['DataStore', 'CSVDataStore', 'SQLiteDataStore', 'get_datastore']


def get_datastore(storage_type: str = 'csv', **kwargs) -> DataStore:
    """
    Factory function to get appropriate datastore
    
    Args:
        storage_type: Type of storage ('csv', 'sqlite', 'postgres')
        **kwargs: Additional arguments passed to datastore constructor
        
    Returns:
        DataStore instance
        
    Raises:
        ValueError: If storage_type is not supported
    """
    storage_type = storage_type.lower()
    
    if storage_type == 'csv':
        return CSVDataStore(**kwargs)
    elif storage_type == 'sqlite':
        return SQLiteDataStore(**kwargs)
    elif storage_type == 'postgres' or storage_type == 'postgresql':
        # PostgreSQL uses same implementation as SQLite (SQLAlchemy)
        return SQLiteDataStore(**kwargs)
    else:
        raise ValueError(f"Unsupported storage type: {storage_type}")
