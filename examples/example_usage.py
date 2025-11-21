#!/usr/bin/env python3
"""
Example usage of the Market Research Visualization package
"""
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.static_visualizer import StaticVisualizer
from src.animated_visualizer import AnimatedVisualizer


def example_1_quick_start():
    """
    Example 1: Quick start - fetch and visualize data for a few stocks
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: QUICK START")
    print("="*60)

    # Fetch data for 10 stocks, last 6 months
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        end_date=datetime.now().strftime('%Y-%m-%d'),
        max_stocks=10,
        use_cache=True
    )

    # Process data
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_data, animation_period='M')

    # Create a simple bubble chart
    visualizer = StaticVisualizer()
    visualizer.create_bubble_chart(
        results['processed'],
        save_path='example_bubble_chart.html',
        show=True
    )

    print("\n✓ Example 1 complete! Open example_bubble_chart.html in your browser.")


def example_2_custom_visualization():
    """
    Example 2: Custom visualization with specific parameters
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: CUSTOM VISUALIZATION")
    print("="*60)

    # Fetch data
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_complete_dataset(
        start_date='2024-01-01',
        max_stocks=20,
        use_cache=True
    )

    # Process
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_data)

    # Create custom bubble chart with different axes
    visualizer = StaticVisualizer()

    # Volatility vs Return
    fig1 = visualizer.create_bubble_chart(
        results['processed'],
        x_col='Volatility_20',
        y_col='YTD_Return',
        size_col='Market_Cap',
        color_col='Sector',
        title='Risk vs Return Analysis',
        save_path='example_risk_return.html',
        show=False
    )

    # Price vs Market Cap
    fig2 = visualizer.create_bubble_chart(
        results['processed'],
        x_col='Close',
        y_col='Market_Cap_Billions',
        size_col='Volume',
        color_col='Sector',
        title='Price vs Market Cap Analysis',
        save_path='example_price_mcap.html',
        show=False
    )

    print("\n✓ Example 2 complete! Check example_risk_return.html and example_price_mcap.html")


def example_3_animated_visualization():
    """
    Example 3: Create animated visualization
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: ANIMATED VISUALIZATION")
    print("="*60)

    # Fetch data for animation (need time series)
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        max_stocks=15,
        use_cache=True
    )

    # Process with monthly aggregation
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_data, animation_period='M')

    # Create animated bubble chart
    animator = AnimatedVisualizer()
    animator.create_animated_bubble_chart(
        results['animation'],
        save_path='example_animated.html',
        show=False
    )

    # Create animated swarm plot
    animator.create_animated_swarm_plot(
        results['animation'],
        save_path='example_swarm.html',
        show=False
    )

    print("\n✓ Example 3 complete! Open example_animated.html and example_swarm.html")


def example_4_sector_analysis():
    """
    Example 4: Sector-focused analysis
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: SECTOR ANALYSIS")
    print("="*60)

    # Fetch data
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        max_stocks=50,
        use_cache=True
    )

    # Process
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_data)

    # Create sector visualizations
    visualizer = StaticVisualizer()

    # Sector performance
    visualizer.create_sector_performance_chart(
        results['sector_summary'],
        save_path='example_sector_performance.html',
        show=False
    )

    # Market cap distribution
    visualizer.create_market_cap_distribution(
        results['processed'],
        save_path='example_market_cap.html',
        show=False
    )

    # Print sector summary
    print("\nSector Summary:")
    print(results['sector_summary'].to_string())

    print("\n✓ Example 4 complete! Check example_sector_performance.html and example_market_cap.html")


def example_5_complete_dashboard():
    """
    Example 5: Create complete dashboard
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: COMPLETE DASHBOARD")
    print("="*60)

    # Fetch data
    fetcher = DataFetcher()
    raw_data = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d'),
        max_stocks=30,
        use_cache=True
    )

    # Process
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_data)

    # Create comprehensive dashboard
    visualizer = StaticVisualizer()
    visualizer.create_dashboard(
        results['processed'],
        results['sector_summary'],
        save_path='example_dashboard.html',
        show=True
    )

    print("\n✓ Example 5 complete! Open example_dashboard.html")


def example_6_specific_stocks():
    """
    Example 6: Analyze specific stocks
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: SPECIFIC STOCKS ANALYSIS")
    print("="*60)

    # Define specific stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'JPM', 'V', 'WMT']

    # Fetch S&P 500 list first
    fetcher = DataFetcher()
    constituents = fetcher.fetch_sp500_constituents()

    # Filter to our symbols
    constituents = constituents[constituents['Symbol'].isin(symbols)]

    # Fetch stock data
    stock_data = fetcher.fetch_stock_data(
        symbols,
        start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        use_cache=True
    )

    # Merge with constituent info
    merged = stock_data.merge(
        constituents[['Symbol', 'Security', 'Sector']],
        on='Symbol',
        how='left'
    )

    # Fetch market caps
    market_caps = fetcher.fetch_market_cap(symbols)
    merged = merged.merge(market_caps, on='Symbol', how='left')

    # Process
    processor = DataProcessor()
    results = processor.process_complete_pipeline(merged, animation_period='W')

    # Visualize
    visualizer = StaticVisualizer()
    visualizer.create_bubble_chart(
        results['processed'],
        save_path='example_specific_stocks.html',
        show=True
    )

    print("\n✓ Example 6 complete!")


def main():
    """Run examples"""
    print("Market Research Visualization - Examples")
    print("=" * 60)
    print("\nAvailable examples:")
    print("1. Quick start - simple visualization")
    print("2. Custom visualization with different parameters")
    print("3. Animated visualizations")
    print("4. Sector analysis")
    print("5. Complete dashboard")
    print("6. Specific stocks analysis")
    print("\n0. Run all examples")

    choice = input("\nSelect an example (0-6): ").strip()

    examples = {
        '1': example_1_quick_start,
        '2': example_2_custom_visualization,
        '3': example_3_animated_visualization,
        '4': example_4_sector_analysis,
        '5': example_5_complete_dashboard,
        '6': example_6_specific_stocks
    }

    if choice == '0':
        for func in examples.values():
            try:
                func()
            except Exception as e:
                print(f"\nError in example: {e}")
                import traceback
                traceback.print_exc()
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("Invalid choice!")


if __name__ == '__main__':
    main()
