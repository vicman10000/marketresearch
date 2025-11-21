"""
Utility functions for the market visualization package
"""
import os
import json
from datetime import datetime
import pandas as pd
from src.logging_config import get_logger

logger = get_logger(__name__)


def save_metadata(data_dict, output_path):
    """
    Save metadata about the visualization run

    Args:
        data_dict: Dictionary containing metadata
        output_path: Path to save JSON file
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data_dict, f, indent=2, default=str)

    logger.info("metadata_saved", output_path=output_path)


def load_cached_data(cache_path):
    """
    Load cached data if available and not expired

    Args:
        cache_path: Path to cached CSV file

    Returns:
        DataFrame or None
    """
    if not os.path.exists(cache_path):
        return None

    try:
        df = pd.read_csv(cache_path, parse_dates=['Date'])
        logger.info("loaded_cached_data", cache_path=cache_path)
        return df
    except Exception as e:
        logger.error("error_loading_cached_data", cache_path=cache_path, error=str(e))
        return None


def format_currency(value):
    """Format value as currency"""
    if value >= 1e9:
        return f"${value/1e9:.2f}B"
    elif value >= 1e6:
        return f"${value/1e6:.2f}M"
    elif value >= 1e3:
        return f"${value/1e3:.2f}K"
    else:
        return f"${value:.2f}"


def format_percentage(value):
    """Format value as percentage"""
    return f"{value:.2f}%"


def print_summary_stats(df):
    """
    Print summary statistics for a dataset

    Args:
        df: DataFrame to summarize
    """
    sector_breakdown = df['Sector'].value_counts().to_dict()
    
    logger.info("dataset_summary",
                total_rows=len(df),
                unique_stocks=df['Symbol'].nunique(),
                date_range_start=str(df['Date'].min()),
                date_range_end=str(df['Date'].max()),
                total_sectors=df['Sector'].nunique(),
                sector_breakdown=sector_breakdown)
    
    # Also print for user visibility (legacy compatibility)
    print("\n" + "="*50)
    print("DATASET SUMMARY")
    print("="*50)
    print(f"Total rows: {len(df):,}")
    print(f"Unique stocks: {df['Symbol'].nunique()}")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Sectors: {df['Sector'].nunique()}")
    print(f"\nSector breakdown:")
    print(df['Sector'].value_counts())
    print("="*50 + "\n")


def generate_report(processed_data, sector_summary, output_path):
    """
    Generate a text report summarizing the data

    Args:
        processed_data: Processed DataFrame
        sector_summary: Sector summary DataFrame
        output_path: Path to save report
    """
    latest_date = processed_data['Date'].max()
    latest_data = processed_data[processed_data['Date'] == latest_date]

    report_lines = []
    report_lines.append("="*60)
    report_lines.append("MARKET RESEARCH VISUALIZATION REPORT")
    report_lines.append("="*60)
    report_lines.append(f"\nReport Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Data Date: {latest_date.strftime('%Y-%m-%d')}")
    report_lines.append(f"\n{'='*60}")
    report_lines.append("OVERVIEW")
    report_lines.append("="*60)
    report_lines.append(f"Total Stocks Analyzed: {latest_data['Symbol'].nunique()}")
    report_lines.append(f"Total Market Cap: {format_currency(latest_data['Market_Cap'].sum())}")
    report_lines.append(f"Average YTD Return: {format_percentage(latest_data['YTD_Return'].mean())}")
    report_lines.append(f"Average Volatility: {latest_data['Volatility_20'].mean():.2f}%")

    report_lines.append(f"\n{'='*60}")
    report_lines.append("SECTOR PERFORMANCE")
    report_lines.append("="*60)
    for _, row in sector_summary.iterrows():
        report_lines.append(f"\n{row['Sector']}:")
        report_lines.append(f"  Stocks: {row['Stock_Count']}")
        report_lines.append(f"  Market Cap: {format_currency(row['Total_Market_Cap'])}")
        report_lines.append(f"  Avg Return: {format_percentage(row['Avg_YTD_Return'])}")
        report_lines.append(f"  Avg Volatility: {row['Avg_Volatility']:.2f}%")

    report_lines.append(f"\n{'='*60}")
    report_lines.append("TOP 10 PERFORMERS")
    report_lines.append("="*60)
    top_10 = latest_data.nlargest(10, 'YTD_Return')[['Symbol', 'Security', 'Sector', 'YTD_Return']]
    for i, row in top_10.iterrows():
        report_lines.append(f"{row['Symbol']:6} {row['Security'][:30]:30} {row['Sector'][:20]:20} {format_percentage(row['YTD_Return']):>10}")

    report_lines.append(f"\n{'='*60}")
    report_lines.append("BOTTOM 10 PERFORMERS")
    report_lines.append("="*60)
    bottom_10 = latest_data.nsmallest(10, 'YTD_Return')[['Symbol', 'Security', 'Sector', 'YTD_Return']]
    for i, row in bottom_10.iterrows():
        report_lines.append(f"{row['Symbol']:6} {row['Security'][:30]:30} {row['Sector'][:20]:20} {format_percentage(row['YTD_Return']):>10}")

    report_lines.append(f"\n{'='*60}")
    report_lines.append("END OF REPORT")
    report_lines.append("="*60)

    report_text = "\n".join(report_lines)

    # Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(report_text)

    print(report_text)
    logger.info("report_generated", output_path=output_path)


def validate_dataframe(df, required_columns):
    """
    Validate that DataFrame has required columns

    Args:
        df: DataFrame to validate
        required_columns: List of required column names

    Returns:
        Boolean indicating if valid
    """
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        logger.error("missing_required_columns", missing_columns=missing)
        return False

    return True
