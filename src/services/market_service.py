"""
Market Analysis Service

Coordinates data fetching, processing, and analysis operations.
"""
from typing import Optional, List, Dict
import pandas as pd
from datetime import datetime


class MarketAnalysisService:
    """
    High-level service for market analysis operations
    
    Encapsulates business logic and coordinates between data fetcher,
    processor, and storage components.
    """
    
    def __init__(self, data_fetcher, data_processor, data_store=None, logger=None):
        """
        Initialize market analysis service
        
        Args:
            data_fetcher: DataFetcher instance
            data_processor: DataProcessor instance
            data_store: Optional DataStore instance
            logger: Optional logger instance
        """
        self.data_fetcher = data_fetcher
        self.data_processor = data_processor
        self.data_store = data_store
        self.logger = logger
    
    def analyze_market(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        max_stocks: Optional[int] = None,
        use_cache: bool = True,
        animation_period: str = 'M'
    ) -> Dict:
        """
        Perform complete market analysis
        
        Args:
            start_date: Analysis start date (YYYY-MM-DD)
            end_date: Analysis end date (YYYY-MM-DD)
            max_stocks: Maximum number of stocks to analyze
            use_cache: Whether to use cached data
            animation_period: Period for animation data ('D', 'W', 'M')
            
        Returns:
            Dictionary with analysis results
        """
        if self.logger:
            self.logger.info("starting_market_analysis",
                           start_date=start_date,
                           end_date=end_date,
                           max_stocks=max_stocks)
        
        # Step 1: Fetch data
        raw_data = self.data_fetcher.fetch_complete_dataset(
            start_date=start_date,
            end_date=end_date,
            max_stocks=max_stocks,
            use_cache=use_cache
        )
        
        if raw_data.empty:
            if self.logger:
                self.logger.error("no_data_fetched")
            return {'success': False, 'error': 'Failed to fetch data'}
        
        # Step 2: Process data
        results = self.data_processor.process_complete_pipeline(
            raw_data,
            animation_period=animation_period
        )
        
        if not results:
            if self.logger:
                self.logger.error("data_processing_failed")
            return {'success': False, 'error': 'Data processing failed'}
        
        # Step 3: Optionally store in database
        if self.data_store:
            self._store_results(results)
        
        if self.logger:
            self.logger.info("market_analysis_complete",
                           stocks=results['processed']['Symbol'].nunique(),
                           data_points=len(results['processed']))
        
        return {
            'success': True,
            'processed_data': results['processed'],
            'animation_data': results['animation'],
            'sector_summary': results['sector_summary'],
            'metadata': {
                'start_date': start_date,
                'end_date': end_date,
                'total_stocks': results['processed']['Symbol'].nunique(),
                'total_data_points': len(results['processed']),
                'animation_periods': results['animation']['Year_Month'].nunique(),
                'timestamp': datetime.now().isoformat()
            }
        }
    
    def get_stock_analysis(
        self,
        symbol: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Analyze a single stock
        
        Args:
            symbol: Stock ticker symbol
            start_date: Analysis start date
            end_date: Analysis end date
            
        Returns:
            Dictionary with stock analysis
        """
        if self.logger:
            self.logger.info("analyzing_stock", symbol=symbol)
        
        # Fetch data for single stock
        raw_data = self.data_fetcher.fetch_stock_data(
            [symbol],
            start_date=start_date,
            end_date=end_date
        )
        
        if raw_data.empty:
            return {'success': False, 'error': f'No data found for {symbol}'}
        
        # Process
        processed = self.data_processor.calculate_returns(raw_data)
        processed = self.data_processor.calculate_fundamentals(processed)
        
        latest = processed[processed['Date'] == processed['Date'].max()].iloc[0]
        
        return {
            'success': True,
            'symbol': symbol,
            'latest_price': float(latest['Close']),
            'ytd_return': float(latest['YTD_Return']),
            'volatility': float(latest['Volatility_20']),
            'market_cap': float(latest.get('Market_Cap', 0)),
            'data': processed
        }
    
    def get_sector_analysis(self, sector: str, date: Optional[str] = None) -> Dict:
        """
        Analyze a specific sector
        
        Args:
            sector: Sector name
            date: Optional date for analysis (default: latest)
            
        Returns:
            Dictionary with sector analysis
        """
        if self.logger:
            self.logger.info("analyzing_sector", sector=sector)
        
        # This is a simplified version - in production, you'd fetch sector-specific data
        return {
            'success': True,
            'sector': sector,
            'message': 'Sector analysis not yet implemented'
        }
    
    def _store_results(self, results: Dict):
        """Store analysis results in database"""
        if not self.data_store:
            return
        
        try:
            # Store stock info
            stock_info = results['processed'][['Symbol', 'Security', 'Sector']].drop_duplicates()
            self.data_store.save_stock_info(stock_info)
            
            # Store prices for each stock
            for symbol in results['processed']['Symbol'].unique():
                stock_data = results['processed'][results['processed']['Symbol'] == symbol]
                self.data_store.save_stock_prices(symbol, stock_data)
            
            if self.logger:
                self.logger.info("results_stored_in_database")
        except Exception as e:
            if self.logger:
                self.logger.error("failed_to_store_results", error=str(e))

