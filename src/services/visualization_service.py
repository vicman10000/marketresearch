"""
Visualization Service

Coordinates visualization creation and export operations.
"""
from typing import Optional, List, Dict
import pandas as pd
import os


class VisualizationService:
    """
    High-level service for visualization operations
    
    Coordinates between static and animated visualizers.
    """
    
    def __init__(self, static_visualizer, animated_visualizer, output_dir: str, logger=None):
        """
        Initialize visualization service
        
        Args:
            static_visualizer: StaticVisualizer instance
            animated_visualizer: AnimatedVisualizer instance
            output_dir: Base output directory
            logger: Optional logger instance
        """
        self.static_viz = static_visualizer
        self.animated_viz = animated_visualizer
        self.output_dir = output_dir
        self.logger = logger
    
    def create_all_visualizations(
        self,
        processed_data: pd.DataFrame,
        animation_data: pd.DataFrame,
        sector_summary: pd.DataFrame,
        skip_static: bool = False,
        skip_animated: bool = False
    ) -> Dict:
        """
        Create all visualizations
        
        Args:
            processed_data: Processed stock data
            animation_data: Animation-ready data
            sector_summary: Sector summary statistics
            skip_static: Skip static visualizations
            skip_animated: Skip animated visualizations
            
        Returns:
            Dictionary with creation results
        """
        results = {
            'static': {},
            'animated': {},
            'success': True
        }
        
        # Create static visualizations
        if not skip_static:
            results['static'] = self._create_static_visualizations(
                processed_data,
                sector_summary
            )
        
        # Create animated visualizations
        if not skip_animated:
            results['animated'] = self._create_animated_visualizations(
                animation_data
            )
        
        return results
    
    def _create_static_visualizations(
        self,
        processed_data: pd.DataFrame,
        sector_summary: pd.DataFrame
    ) -> Dict:
        """Create all static visualizations"""
        static_dir = os.path.join(self.output_dir, 'static')
        os.makedirs(static_dir, exist_ok=True)
        
        results = {}
        
        try:
            # Bubble chart
            if self.logger:
                self.logger.info("creating_visualization", type="bubble_chart")
            self.static_viz.create_bubble_chart(
                processed_data,
                save_path=os.path.join(static_dir, 'bubble_chart.html'),
                show=False
            )
            results['bubble_chart'] = 'success'
        except Exception as e:
            results['bubble_chart'] = f'error: {str(e)}'
            if self.logger:
                self.logger.error("visualization_error", type="bubble_chart", error=str(e))
        
        try:
            # Sector performance
            if self.logger:
                self.logger.info("creating_visualization", type="sector_performance")
            self.static_viz.create_sector_performance_chart(
                sector_summary,
                save_path=os.path.join(static_dir, 'sector_performance.html'),
                show=False
            )
            results['sector_performance'] = 'success'
        except Exception as e:
            results['sector_performance'] = f'error: {str(e)}'
        
        try:
            # Market cap distribution
            if self.logger:
                self.logger.info("creating_visualization", type="market_cap_distribution")
            self.static_viz.create_market_cap_distribution(
                processed_data,
                save_path=os.path.join(static_dir, 'market_cap_distribution.html'),
                show=False
            )
            results['market_cap_distribution'] = 'success'
        except Exception as e:
            results['market_cap_distribution'] = f'error: {str(e)}'
        
        try:
            # Top performers
            if self.logger:
                self.logger.info("creating_visualization", type="top_performers")
            self.static_viz.create_top_performers_chart(
                processed_data,
                n=20,
                save_path=os.path.join(static_dir, 'top_performers.html'),
                show=False
            )
            results['top_performers'] = 'success'
        except Exception as e:
            results['top_performers'] = f'error: {str(e)}'
        
        try:
            # Dashboard
            if self.logger:
                self.logger.info("creating_visualization", type="dashboard")
            self.static_viz.create_dashboard(
                processed_data,
                sector_summary,
                save_path=os.path.join(static_dir, 'dashboard.html'),
                show=False
            )
            results['dashboard'] = 'success'
        except Exception as e:
            results['dashboard'] = f'error: {str(e)}'
        
        return results
    
    def _create_animated_visualizations(self, animation_data: pd.DataFrame) -> Dict:
        """Create all animated visualizations"""
        animated_dir = os.path.join(self.output_dir, 'animated')
        os.makedirs(animated_dir, exist_ok=True)
        
        results = {}
        
        try:
            if self.logger:
                self.logger.info("creating_animations")
            figures = self.animated_viz.create_all_animations(
                animation_data,
                output_dir=animated_dir
            )
            
            for key in figures.keys():
                results[key] = 'success'
        except Exception as e:
            results['all_animations'] = f'error: {str(e)}'
            if self.logger:
                self.logger.error("animation_error", error=str(e))
        
        return results

