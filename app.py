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
from src.logging_config import setup_logging, get_logger
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
        self.logger = get_logger(__name__)
        self.start_date = start_date or config.DEFAULT_START_DATE
        self.end_date = end_date or config.DEFAULT_END_DATE
        self.max_stocks = max_stocks
        self.use_cache = use_cache
        self.animation_period = animation_period

        self.logger.info("app_initialized",
                        start_date=self.start_date,
                        end_date=self.end_date,
                        max_stocks=self.max_stocks,
                        animation_period=self.animation_period)

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
        self.logger.info("step_starting", step=1, description="Fetching data")

        self.raw_data = self.fetcher.fetch_complete_dataset(
            start_date=self.start_date,
            end_date=self.end_date,
            max_stocks=self.max_stocks,
            use_cache=self.use_cache
        )

        if self.raw_data.empty:
            self.logger.error("failed_to_fetch_data")
            return False

        self.logger.info("data_fetched_successfully",
                        rows=len(self.raw_data),
                        unique_symbols=self.raw_data['Symbol'].nunique())
        print_summary_stats(self.raw_data)
        return True

    def process_data(self):
        """Process and calculate metrics"""
        self.logger.info("step_starting", step=2, description="Processing data")

        if self.raw_data is None or self.raw_data.empty:
            self.logger.error("no_raw_data_available")
            return False

        results = self.processor.process_complete_pipeline(
            self.raw_data,
            animation_period=self.animation_period
        )

        if not results:
            self.logger.error("failed_to_process_data")
            return False

        self.processed_data = results['processed']
        self.animation_data = results['animation']
        self.sector_summary = results['sector_summary']

        self.logger.info("data_processed_successfully",
                        processed_rows=len(self.processed_data),
                        animation_rows=len(self.animation_data),
                        sectors=len(self.sector_summary))
        return True

    def create_static_visualizations(self):
        """Create all static visualizations"""
        self.logger.info("step_starting", step=3, description="Creating static visualizations")

        output_dir = config.STATIC_OUTPUT_DIR

        try:
            # 1. Main bubble chart
            self.logger.info("creating_visualization", type="bubble_chart")
            self.static_viz.create_bubble_chart(
                self.processed_data,
                save_path=os.path.join(output_dir, 'bubble_chart.html'),
                show=False
            )

            # 2. Sector performance
            self.logger.info("creating_visualization", type="sector_performance")
            self.static_viz.create_sector_performance_chart(
                self.sector_summary,
                save_path=os.path.join(output_dir, 'sector_performance.html'),
                show=False
            )

            # 3. Market cap distribution
            self.logger.info("creating_visualization", type="market_cap_distribution")
            self.static_viz.create_market_cap_distribution(
                self.processed_data,
                save_path=os.path.join(output_dir, 'market_cap_distribution.html'),
                show=False
            )

            # 4. Top performers
            self.logger.info("creating_visualization", type="top_performers")
            self.static_viz.create_top_performers_chart(
                self.processed_data,
                n=20,
                save_path=os.path.join(output_dir, 'top_performers.html'),
                show=False
            )

            # 5. Comprehensive dashboard
            self.logger.info("creating_visualization", type="dashboard")
            self.static_viz.create_dashboard(
                self.processed_data,
                self.sector_summary,
                save_path=os.path.join(output_dir, 'dashboard.html'),
                show=False
            )

            self.logger.info("static_visualizations_complete", output_dir=output_dir)
            return True

        except Exception as e:
            self.logger.error("error_creating_static_visualizations", 
                            error=str(e),
                            exc_info=True)
            return False

    def create_animated_visualizations(self):
        """Create all animated visualizations"""
        self.logger.info("step_starting", step=4, description="Creating animated visualizations")

        try:
            self.animated_viz.create_all_animations(
                self.animation_data,
                output_dir=config.ANIMATED_OUTPUT_DIR
            )

            self.logger.info("animated_visualizations_complete", output_dir=config.ANIMATED_OUTPUT_DIR)
            return True

        except Exception as e:
            self.logger.error("error_creating_animated_visualizations",
                            error=str(e),
                            exc_info=True)
            return False

    def generate_outputs(self):
        """Generate additional outputs (reports, metadata)"""
        self.logger.info("step_starting", step=5, description="Generating outputs")

        try:
            # Generate text report
            report_path = os.path.join(config.OUTPUT_DIR, 'market_report.txt')
            generate_report(self.processed_data, self.sector_summary, report_path)

            # Calculate summary statistics for metadata
            latest_data = self.processed_data[self.processed_data['Date'] == self.processed_data['Date'].max()]
            total_market_cap = latest_data['Market_Cap'].sum()
            avg_ytd_return = latest_data['YTD_Return'].mean()
            avg_volatility = latest_data['Volatility_20'].mean()
            
            # Determine data source
            use_sample_data = os.environ.get('USE_SAMPLE_DATA', 'false').lower() == 'true'
            
            # Save metadata with summary
            metadata = {
                'run_date': datetime.now().isoformat(),
                'start_date': self.start_date,
                'end_date': self.end_date,
                'market': 'S&P 500',
                'data_source': 'sample' if use_sample_data else 'live',
                'total_stocks': self.processed_data['Symbol'].nunique(),
                'total_data_points': len(self.processed_data),
                'animation_periods': self.animation_data['Year_Month'].nunique(),
                'sectors': sorted(self.processed_data['Sector'].unique().tolist()),
                'summary': {
                    'total_stocks': self.processed_data['Symbol'].nunique(),
                    'total_market_cap': float(total_market_cap),
                    'avg_ytd_return': float(avg_ytd_return),
                    'avg_volatility': float(avg_volatility)
                }
            }
            save_metadata(metadata, os.path.join(config.OUTPUT_DIR, 'metadata.json'))
            
            # Copy dashboard assets
            self._copy_dashboard_assets()

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

            self.logger.info("outputs_generated_successfully")
            return True

        except Exception as e:
            self.logger.error("error_generating_outputs",
                            error=str(e),
                            exc_info=True)
            return False
    
    def _copy_dashboard_assets(self):
        """Copy dashboard HTML, CSS, and JS files to output directory"""
        import shutil
        
        try:
            # Create assets directory
            assets_dir = os.path.join(config.OUTPUT_DIR, 'assets')
            os.makedirs(assets_dir, exist_ok=True)
            
            # Source files from project root
            project_root = os.path.dirname(os.path.abspath(__file__))
            source_assets = os.path.join(project_root, 'outputs', 'assets')
            source_index = os.path.join(project_root, 'outputs', 'index.html')
            
            # Copy assets if they exist in source
            if os.path.exists(source_assets):
                for filename in ['styles.css', 'app.js']:
                    src = os.path.join(source_assets, filename)
                    dst = os.path.join(assets_dir, filename)
                    if os.path.exists(src):
                        shutil.copy2(src, dst)
                        self.logger.debug("file_copied", filename=filename, destination="assets/")
            
            # Copy index.html if it exists
            if os.path.exists(source_index):
                dst = os.path.join(config.OUTPUT_DIR, 'index.html')
                shutil.copy2(source_index, dst)
                self.logger.debug("file_copied", filename="index.html", destination="outputs/")
            
            self.logger.info("dashboard_assets_copied_successfully")
            
        except Exception as e:
            self.logger.warning("could_not_copy_dashboard_assets", error=str(e))

    def run(self, skip_static=False, skip_animated=False):
        """
        Run the complete pipeline

        Args:
            skip_static: Skip static visualizations
            skip_animated: Skip animated visualizations

        Returns:
            Boolean indicating success
        """
        self.logger.info("pipeline_starting",
                        start_date=self.start_date,
                        end_date=self.end_date,
                        max_stocks=self.max_stocks or 'All',
                        animation_period=self.animation_period,
                        skip_static=skip_static,
                        skip_animated=skip_animated)
        
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
                self.logger.warning("some_static_visualizations_failed")

        # Step 4: Create animated visualizations
        if not skip_animated:
            if not self.create_animated_visualizations():
                self.logger.warning("some_animated_visualizations_failed")

        # Step 5: Generate outputs
        self.generate_outputs()

        self.logger.info("pipeline_complete",
                        output_dir=config.OUTPUT_DIR,
                        static_dir=config.STATIC_OUTPUT_DIR,
                        animated_dir=config.ANIMATED_OUTPUT_DIR,
                        data_dir=config.DATA_DIR)
        
        print("\n" + "="*60)
        print("PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nOutputs saved to:")
        print(f"  - Main Dashboard: {os.path.join(config.OUTPUT_DIR, 'index.html')}")
        print(f"  - Static visualizations: {config.STATIC_OUTPUT_DIR}")
        print(f"  - Animated visualizations: {config.ANIMATED_OUTPUT_DIR}")
        print(f"  - Data files: {config.DATA_DIR}")
        print(f"  - Reports: {config.OUTPUT_DIR}")
        print("\n🚀 Open index.html in your browser for the full dashboard experience!")
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

    # Setup logging
    setup_logging(log_level=config.LOG_LEVEL, log_file=config.LOG_FILE)
    logger = get_logger(__name__)
    
    logger.info("application_started",
                start_date=args.start_date,
                end_date=args.end_date,
                max_stocks=args.max_stocks,
                animation_period=args.animation_period)

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
        logger.info("application_finished", success=success)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        logger.warning("application_interrupted_by_user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        logger.error("fatal_application_error", error=str(e), exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
