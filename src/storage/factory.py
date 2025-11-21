"""
Factory for creating storage instances
Provides simple interface to switch between storage backends
"""
from typing import Optional
from .base import DataStore
from .csv_store import CSVStore
from .sqlite_store import SQLiteStore
from src.logging_config import get_logger

logger = get_logger(__name__)

# Global storage instance
_storage_instance: Optional[DataStore] = None


def create_data_store(
    storage_type: str = 'csv',
    **kwargs
) -> DataStore:
    """
    Create a data store instance
    
    Args:
        storage_type: Type of storage ('csv', 'sqlite', 'postgresql')
        **kwargs: Additional arguments for the storage backend
            - cache_dir: For CSV storage
            - database_url: For database storage
    
    Returns:
        DataStore instance
    
    Example:
        # Create CSV store
        store = create_data_store('csv', cache_dir='./data/cache')
        
        # Create SQLite store
        store = create_data_store('sqlite', database_url='sqlite:///./data/market.db')
    """
    storage_type = storage_type.lower()
    
    if storage_type == 'csv':
        cache_dir = kwargs.get('cache_dir', './data/cache')
        logger.info("creating_csv_store", cache_dir=cache_dir)
        return CSVStore(cache_dir=cache_dir)
    
    elif storage_type in ['sqlite', 'sql']:
        database_url = kwargs.get('database_url', 'sqlite:///./data/market_viz.db')
        logger.info("creating_sqlite_store", database_url=database_url)
        return SQLiteStore(database_url=database_url)
    
    elif storage_type in ['postgresql', 'postgres']:
        # Future implementation
        database_url = kwargs.get('database_url')
        if not database_url:
            raise ValueError("PostgreSQL requires database_url parameter")
        logger.info("creating_postgresql_store", database_url=database_url)
        # For now, use SQLite store as it works with PostgreSQL too
        return SQLiteStore(database_url=database_url)
    
    else:
        raise ValueError(
            f"Unknown storage type: {storage_type}. "
            f"Valid options: 'csv', 'sqlite', 'postgresql'"
        )


def get_data_store(
    storage_type: str = None,
    use_database: bool = False,
    **kwargs
) -> DataStore:
    """
    Get the global data store instance (singleton pattern)
    
    Args:
        storage_type: Type of storage backend
        use_database: If True, use database; if False, use CSV
        **kwargs: Additional arguments
    
    Returns:
        DataStore instance
    """
    global _storage_instance
    
    if _storage_instance is None:
        # Determine storage type
        if storage_type is None:
            storage_type = 'sqlite' if use_database else 'csv'
        
        _storage_instance = create_data_store(storage_type, **kwargs)
        logger.info("initialized_global_data_store", storage_type=storage_type)
    
    return _storage_instance


def reset_data_store():
    """Reset the global data store instance (mainly for testing)"""
    global _storage_instance
    _storage_instance = None
    logger.debug("reset_global_data_store")

