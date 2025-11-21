#!/usr/bin/env python3
"""
Market Research Visualization - Main Application
Complete end-to-end solution for animated financial market visualizations
"""
import argparse
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_fetcher import DataFetcher
from src.data_processor import DataProcessor
from src.static_visualizer import StaticVisualizer
from src.animated_visualizer import AnimatedVisualizer
from src.utils import save_metadata, print_summary_stats, generate_report
import config


class MarketVisualizationApp:
    """Main application class for market visualization"""

    def __init__(self, start_date=None, end_date=None, max_stocks=None,
                 use_cache=True, animation_period='M'):
        """
        Initialize the application

        Args:
            start_date: Start date for data (YYYY-MM-DD)
            end_date: End date for data (YYYY-MM-DD)
            max_stocks: Maximum number of stocks to process (None for all)
            use_cache: Whether to use cached data
            animation_period: Period for animation ('D', 'W', 'M')
        """
        self.start_date = start_date or config.DEFAULT_START_DATE
        self.end_date = end_date or config.DEFAULT_END_DATE
        self.max_stocks = max_stocks
        self.use_cache = use_cache
        self.animation_period = animation_period

        self.fetcher = DataFetcher()
        self.processor = DataProcessor()
        self.static_viz = StaticVisualizer()
        self.animated_viz = AnimatedVisualizer()

        self.raw_data = None
        self.processed_data = None
        self.animation_data = None
        self.sector_summary = None

    def fetch_data(self):
        """Fetch raw data from sources"""
        print("\n" + "="*60)
        print("STEP 1: FETCHING DATA")
        print("="*60)

        self.raw_data = self.fetcher.fetch_complete_dataset(
            start_date=self.start_date,
            end_date=self.end_date,
            max_stocks=self.max_stocks,
            use_cache=self.use_cache
        )

        if self.raw_data.empty:
            print("ERROR: Failed to fetch data!")
            return False

        print_summary_stats(self.raw_data)
        return True

    def process_data(self):
        """Process and calculate metrics"""
        print("\n" + "="*60)
        print("STEP 2: PROCESSING DATA")
        print("="*60)

        if self.raw_data is None or self.raw_data.empty:
            print("ERROR: No raw data available!")
            return False

        results = self.processor.process_complete_pipeline(
            self.raw_data,
            animation_period=self.animation_period
        )

        if not results:
            print("ERROR: Failed to process data!")
            return False

        self.processed_data = results['processed']
        self.animation_data = results['animation']
        self.sector_summary = results['sector_summary']

        return True

    def create_static_visualizations(self):
        """Create all static visualizations"""
        print("\n" + "="*60)
        print("STEP 3: CREATING STATIC VISUALIZATIONS")
        print("="*60)

        output_dir = config.STATIC_OUTPUT_DIR

        try:
            # 1. Main bubble chart
            print("\n1. Creating bubble chart...")
            self.static_viz.create_bubble_chart(
                self.processed_data,
                save_path=os.path.join(output_dir, 'bubble_chart.html'),
                show=False
            )

            # 2. Sector performance
            print("\n2. Creating sector performance chart...")
            self.static_viz.create_sector_performance_chart(
                self.sector_summary,
                save_path=os.path.join(output_dir, 'sector_performance.html'),
                show=False
            )

            # 3. Market cap distribution
            print("\n3. Creating market cap distribution...")
            self.static_viz.create_market_cap_distribution(
                self.processed_data,
                save_path=os.path.join(output_dir, 'market_cap_distribution.html'),
                show=False
            )

            # 4. Top performers
            print("\n4. Creating top performers chart...")
            self.static_viz.create_top_performers_chart(
                self.processed_data,
                n=20,
                save_path=os.path.join(output_dir, 'top_performers.html'),
                show=False
            )

            # 5. Comprehensive dashboard
            print("\n5. Creating comprehensive dashboard...")
            self.static_viz.create_dashboard(
                self.processed_data,
                self.sector_summary,
                save_path=os.path.join(output_dir, 'dashboard.html'),
                show=False
            )

            print(f"\n✓ All static visualizations saved to: {output_dir}")
            return True

        except Exception as e:
            print(f"ERROR creating static visualizations: {e}")
            import traceback
            traceback.print_exc()
            return False

    def create_animated_visualizations(self):
        """Create all animated visualizations"""
        print("\n" + "="*60)
        print("STEP 4: CREATING ANIMATED VISUALIZATIONS")
        print("="*60)

        try:
            self.animated_viz.create_all_animations(
                self.animation_data,
                output_dir=config.ANIMATED_OUTPUT_DIR
            )

            print(f"\n✓ All animated visualizations saved to: {config.ANIMATED_OUTPUT_DIR}")
            return True

        except Exception as e:
            print(f"ERROR creating animated visualizations: {e}")
            import traceback
            traceback.print_exc()
            return False

    def generate_outputs(self):
        """Generate additional outputs (reports, metadata)"""
        print("\n" + "="*60)
        print("STEP 5: GENERATING OUTPUTS")
        print("="*60)

        try:
            # Generate text report
            report_path = os.path.join(config.OUTPUT_DIR, 'market_report.txt')
            generate_report(self.processed_data, self.sector_summary, report_path)

            # Save metadata
            metadata = {
                'run_date': datetime.now().isoformat(),
                'start_date': self.start_date,
                'end_date': self.end_date,
                'total_stocks': self.processed_data['Symbol'].nunique(),
                'total_data_points': len(self.processed_data),
                'animation_periods': self.animation_data['Year_Month'].nunique(),
                'sectors': sorted(self.processed_data['Sector'].unique().tolist())
            }
            save_metadata(metadata, os.path.join(config.OUTPUT_DIR, 'metadata.json'))

            # Save processed data
            self.processed_data.to_csv(
                os.path.join(config.DATA_DIR, 'processed_data.csv'),
                index=False
            )
            self.animation_data.to_csv(
                os.path.join(config.DATA_DIR, 'animation_data.csv'),
                index=False
            )
            self.sector_summary.to_csv(
                os.path.join(config.DATA_DIR, 'sector_summary.csv'),
                index=False
            )

            print("\n✓ All outputs generated successfully")
            return True

        except Exception as e:
            print(f"ERROR generating outputs: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, skip_static=False, skip_animated=False):
        """
        Run the complete pipeline

        Args:
            skip_static: Skip static visualizations
            skip_animated: Skip animated visualizations

        Returns:
            Boolean indicating success
        """
        print("\n" + "="*60)
        print("MARKET RESEARCH VISUALIZATION")
        print("Complete End-to-End Solution")
        print("="*60)
        print(f"Start Date: {self.start_date}")
        print(f"End Date: {self.end_date}")
        print(f"Max Stocks: {self.max_stocks or 'All'}")
        print(f"Animation Period: {self.animation_period}")
        print("="*60)

        # Step 1: Fetch data
        if not self.fetch_data():
            return False

        # Step 2: Process data
        if not self.process_data():
            return False

        # Step 3: Create static visualizations
        if not skip_static:
            if not self.create_static_visualizations():
                print("Warning: Some static visualizations failed")

        # Step 4: Create animated visualizations
        if not skip_animated:
            if not self.create_animated_visualizations():
                print("Warning: Some animated visualizations failed")

        # Step 5: Generate outputs
        self.generate_outputs()

        print("\n" + "="*60)
        print("PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nOutputs saved to:")
        print(f"  - Static visualizations: {config.STATIC_OUTPUT_DIR}")
        print(f"  - Animated visualizations: {config.ANIMATED_OUTPUT_DIR}")
        print(f"  - Data files: {config.DATA_DIR}")
        print(f"  - Reports: {config.OUTPUT_DIR}")
        print("\nOpen the HTML files in your browser to view the visualizations!")
        print("="*60 + "\n")

        return True


def main():
    """Main entry point with CLI"""
    parser = argparse.ArgumentParser(
        description='Market Research Visualization - Create animated financial market visualizations',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (last 1 year, all S&P 500 stocks)
  python app.py

  # Run with specific date range
  python app.py --start-date 2023-01-01 --end-date 2024-01-01

  # Run with limited stocks for testing
  python app.py --max-stocks 30

  # Skip animations (faster)
  python app.py --skip-animated

  # Use fresh data (no cache)
  python app.py --no-cache

  # Weekly animation periods
  python app.py --animation-period W
        """
    )

    parser.add_argument(
        '--start-date',
        type=str,
        help='Start date (YYYY-MM-DD). Default: 1 year ago'
    )

    parser.add_argument(
        '--end-date',
        type=str,
        help='End date (YYYY-MM-DD). Default: today'
    )

    parser.add_argument(
        '--max-stocks',
        type=int,
        help='Maximum number of stocks to process (for testing). Default: all'
    )

    parser.add_argument(
        '--no-cache',
        action='store_true',
        help='Fetch fresh data instead of using cache'
    )

    parser.add_argument(
        '--skip-static',
        action='store_true',
        help='Skip static visualizations'
    )

    parser.add_argument(
        '--skip-animated',
        action='store_true',
        help='Skip animated visualizations'
    )

    parser.add_argument(
        '--animation-period',
        type=str,
        choices=['D', 'W', 'M', 'Q'],
        default='M',
        help='Animation period: D=Daily, W=Weekly, M=Monthly, Q=Quarterly. Default: M'
    )

    args = parser.parse_args()

    # Create app instance
    app = MarketVisualizationApp(
        start_date=args.start_date,
        end_date=args.end_date,
        max_stocks=args.max_stocks,
        use_cache=not args.no_cache,
        animation_period=args.animation_period
    )

    # Run pipeline
    try:
        success = app.run(
            skip_static=args.skip_static,
            skip_animated=args.skip_animated
        )
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
