#!/usr/bin/env python3
"""
Migrate data from CSV files to SQLite database
Reads existing CSV cache and moves it to database
"""
import os
import sys
import pandas as pd
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.storage import CSVStore, SQLiteStore
from src.logging_config import setup_logging, get_logger
import config

# Setup logging
setup_logging(log_level='INFO')
logger = get_logger(__name__)


def migrate_csv_to_sqlite(
    csv_cache_dir: str = None,
    database_url: str = None,
    verbose: bool = True
):
    """
    Migrate data from CSV files to SQLite database
    
    Args:
        csv_cache_dir: Path to CSV cache directory
        database_url: SQLAlchemy database URL
        verbose: Print progress information
    
    Returns:
        Dictionary with migration statistics
    """
    # Initialize stores
    if csv_cache_dir is None:
        csv_cache_dir = config.CACHE_DIR
    
    if database_url is None:
        database_url = 'sqlite:///./data/market_viz.db'
    
    csv_store = CSVStore(cache_dir=csv_cache_dir)
    sqlite_store = SQLiteStore(database_url=database_url)
    
    logger.info("migration_started", 
                csv_cache_dir=csv_cache_dir,
                database_url=database_url)
    
    stats = {
        'constituents': 0,
        'stock_prices': 0,
        'symbols_migrated': 0,
        'errors': 0,
        'skipped': 0
    }
    
    # Migrate S&P 500 constituents
    if verbose:
        print("\n=== Migrating S&P 500 Constituents ===")
    
    constituents = csv_store.load_constituents()
    if constituents is not None:
        success = sqlite_store.save_constituents(constituents)
        if success:
            stats['constituents'] = len(constituents)
            if verbose:
                print(f"✓ Migrated {len(constituents)} constituents")
                logger.info("migrated_constituents", count=len(constituents))
        else:
            stats['errors'] += 1
            if verbose:
                print("✗ Failed to migrate constituents")
                logger.error("failed_to_migrate_constituents")
    else:
        if verbose:
            print("⊘ No constituents found in CSV")
    
    # Migrate stock prices for each symbol
    if verbose:
        print("\n=== Migrating Stock Prices ===")
    
    available_symbols = csv_store.get_available_symbols()
    
    if verbose:
        print(f"Found {len(available_symbols)} symbols with cached data")
    
    for i, symbol in enumerate(available_symbols, 1):
        try:
            if verbose:
                print(f"\r[{i}/{len(available_symbols)}] Migrating {symbol}...", end='', flush=True)
            
            # Get date range from CSV filename
            date_range = csv_store.get_date_range(symbol)
            if not date_range:
                stats['skipped'] += 1
                logger.warning("no_date_range_found", symbol=symbol)
                continue
            
            start_date, end_date = date_range
            
            # Load price data from CSV
            price_data = csv_store.load_stock_prices(symbol, start_date, end_date)
            if price_data is None or price_data.empty:
                stats['skipped'] += 1
                logger.warning("no_price_data_found", symbol=symbol)
                continue
            
            # Save to SQLite
            success = sqlite_store.save_stock_prices(symbol, price_data, start_date, end_date)
            if success:
                stats['stock_prices'] += len(price_data)
                stats['symbols_migrated'] += 1
            else:
                stats['errors'] += 1
                logger.error("failed_to_migrate_symbol", symbol=symbol)
        
        except Exception as e:
            stats['errors'] += 1
            logger.error("error_migrating_symbol", symbol=symbol, error=str(e))
            if verbose:
                print(f"\n✗ Error migrating {symbol}: {e}")
    
    if verbose:
        print()  # New line after progress
    
    # Print summary
    if verbose:
        print("\n=== Migration Summary ===")
        print(f"Constituents migrated: {stats['constituents']}")
        print(f"Symbols migrated: {stats['symbols_migrated']}")
        print(f"Price records migrated: {stats['stock_prices']}")
        print(f"Symbols skipped: {stats['skipped']}")
        print(f"Errors: {stats['errors']}")
        print("\n✓ Migration complete!")
    
    logger.info("migration_completed", stats=stats)
    
    return stats


def validate_migration(csv_cache_dir: str = None, database_url: str = None):
    """
    Validate that migration was successful by comparing record counts
    
    Args:
        csv_cache_dir: Path to CSV cache directory
        database_url: SQLAlchemy database URL
    
    Returns:
        Boolean indicating if validation passed
    """
    if csv_cache_dir is None:
        csv_cache_dir = config.CACHE_DIR
    
    if database_url is None:
        database_url = 'sqlite:///./data/market_viz.db'
    
    csv_store = CSVStore(cache_dir=csv_cache_dir)
    sqlite_store = SQLiteStore(database_url=database_url)
    
    print("\n=== Validating Migration ===")
    
    # Check constituents
    csv_constituents = csv_store.load_constituents()
    db_constituents = sqlite_store.load_constituents()
    
    csv_count = len(csv_constituents) if csv_constituents is not None else 0
    db_count = len(db_constituents) if db_constituents is not None else 0
    
    print(f"Constituents: CSV={csv_count}, DB={db_count}")
    
    if csv_count != db_count:
        print("✗ Constituent count mismatch!")
        return False
    
    # Check available symbols
    csv_symbols = set(csv_store.get_available_symbols())
    db_symbols = set(sqlite_store.get_available_symbols())
    
    print(f"Available symbols: CSV={len(csv_symbols)}, DB={len(db_symbols)}")
    
    missing_in_db = csv_symbols - db_symbols
    if missing_in_db:
        print(f"✗ Symbols missing in DB: {missing_in_db}")
        return False
    
    print("✓ Validation passed!")
    return True


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate market data from CSV to SQLite'
    )
    parser.add_argument(
        '--csv-dir',
        type=str,
        help='CSV cache directory (default: from config)'
    )
    parser.add_argument(
        '--database-url',
        type=str,
        help='SQLAlchemy database URL (default: sqlite:///./data/market_viz.db)'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate migration after completion'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress output'
    )
    
    args = parser.parse_args()
    
    try:
        # Run migration
        stats = migrate_csv_to_sqlite(
            csv_cache_dir=args.csv_dir,
            database_url=args.database_url,
            verbose=not args.quiet
        )
        
        # Validate if requested
        if args.validate:
            validate_migration(
                csv_cache_dir=args.csv_dir,
                database_url=args.database_url
            )
        
        sys.exit(0)
    
    except Exception as e:
        logger.error("migration_failed", error=str(e), exc_info=True)
        print(f"\n✗ Migration failed: {e}")
        sys.exit(1)

