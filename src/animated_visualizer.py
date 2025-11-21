"""
Animated Visualizer Module
Creates animated bubble charts with time-based transitions
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


class AnimatedVisualizer:
    """Creates animated visualizations for financial data"""

    def __init__(self):
        """Initialize AnimatedVisualizer"""
        self.sector_colors = config.SECTOR_COLORS

    def create_animated_bubble_chart(self, df, x_col='Volatility_20', y_col='YTD_Return',
                                     size_col='Market_Cap', color_col='Sector',
                                     animation_frame='Year_Month',
                                     hover_name='Security', title=None,
                                     save_path=None, show=True):
        """
        Create animated bubble chart (Chartfleau-style)

        Args:
            df: DataFrame with time-series data
            x_col: Column for x-axis
            y_col: Column for y-axis
            size_col: Column for bubble size
            color_col: Column for color grouping
            animation_frame: Column for animation timeline
            hover_name: Column for hover label
            title: Chart title
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        if title is None:
            title = 'Animated Market Performance Over Time'

        # Ensure animation frame column exists
        if animation_frame not in df.columns:
            print(f"Warning: {animation_frame} column not found. Creating from Date...")
            df[animation_frame] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m')

        # Calculate fixed axis ranges for consistent animation
        x_min = df[x_col].min()
        x_max = df[x_col].max()
        y_min = df[y_col].min()
        y_max = df[y_col].max()

        # Add padding
        x_padding = (x_max - x_min) * 0.1
        y_padding = (y_max - y_min) * 0.1

        # Create animated scatter plot
        fig = px.scatter(
            df,
            x=x_col,
            y=y_col,
            animation_frame=animation_frame,
            animation_group='Symbol',  # Track individual stocks
            size=size_col,
            color=color_col,
            hover_name=hover_name,
            hover_data={
                'Symbol': True,
                size_col: ':,.0f',
                x_col: ':.2f',
                y_col: ':.2f',
                color_col: True,
                animation_frame: False
            },
            color_discrete_map=self.sector_colors,
            size_max=config.BUBBLE_SIZE_MAX,
            range_x=[x_min - x_padding, x_max + x_padding],
            range_y=[y_min - y_padding, y_max + y_padding],
            title=title
        )

        # Update layout for better animation
        fig.update_layout(
            title_x=0.5,
            xaxis_title=x_col.replace('_', ' '),
            yaxis_title=y_col.replace('_', ' ') + ' (%)',
            legend_title=color_col,
            hovermode='closest',
            template='plotly_white',
            font=dict(size=12, family='Arial'),
            height=700,
            width=1200,
            # Animation settings
            updatemenus=[{
                'buttons': [
                    {
                        'args': [None, {
                            'frame': {'duration': config.ANIMATION_FRAME_DURATION, 'redraw': True},
                            'fromcurrent': True,
                            'transition': {'duration': config.ANIMATION_TRANSITION_DURATION, 'easing': 'cubic-in-out'}
                        }],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': True},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }],
            sliders=[{
                'active': 0,
                'yanchor': 'top',
                'y': -0.1,
                'xanchor': 'left',
                'currentvalue': {
                    'prefix': 'Date: ',
                    'visible': True,
                    'xanchor': 'right'
                },
                'transition': {'duration': config.ANIMATION_TRANSITION_DURATION, 'easing': 'cubic-in-out'},
                'pad': {'b': 10, 't': 50},
                'len': 0.9,
                'x': 0.1,
            }]
        )

        # Update bubble style
        fig.update_traces(
            marker=dict(
                opacity=config.BUBBLE_OPACITY,
                line=dict(width=config.BUBBLE_BORDER_WIDTH, color='white')
            )
        )

        # Add reference lines
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        # Update frame durations
        for frame in fig.frames:
            frame['layout'].update(
                transition={'duration': config.ANIMATION_TRANSITION_DURATION, 'easing': 'cubic-in-out'}
            )

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            print(f"Saved animated bubble chart to {save_path}")

        if show:
            fig.show()

        return fig

    def create_animated_sector_race(self, df, save_path=None, show=True):
        """
        Create animated bar chart race showing sector performance over time

        Args:
            df: DataFrame with time-series data
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        # Calculate sector average returns by period
        sector_performance = df.groupby(['Year_Month', 'Sector']).agg({
            'YTD_Return': 'mean',
            'Market_Cap': 'sum'
        }).reset_index()

        sector_performance = sector_performance.sort_values(['Year_Month', 'YTD_Return'])

        # Create animated bar chart
        fig = px.bar(
            sector_performance,
            y='Sector',
            x='YTD_Return',
            animation_frame='Year_Month',
            color='Sector',
            orientation='h',
            range_x=[
                sector_performance['YTD_Return'].min() - 5,
                sector_performance['YTD_Return'].max() + 5
            ],
            color_discrete_map=self.sector_colors,
            title='Sector Performance Race Over Time'
        )

        fig.update_layout(
            title_x=0.5,
            xaxis_title='Average YTD Return (%)',
            yaxis_title='',
            template='plotly_white',
            height=600,
            width=1000,
            showlegend=False,
            yaxis={'categoryorder': 'total ascending'}
        )

        # Add reference line at 0
        fig.add_vline(x=0, line_dash="solid", line_color="black", line_width=1)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            print(f"Saved animated sector race to {save_path}")

        if show:
            fig.show()

        return fig

    def create_animated_swarm_plot(self, df, save_path=None, show=True):
        """
        Create animated swarm plot (similar to Chartfleau's signature style)
        Groups stocks by sector horizontally, positions by return vertically

        Args:
            df: DataFrame with time-series data
            save_path: Path to save HTML file
            show: Whether to display

        Returns:
            Plotly figure object
        """
        # Prepare data: assign x-position based on sector
        sectors = sorted(df['Sector'].unique())
        sector_positions = {sector: i for i, sector in enumerate(sectors)}

        df = df.copy()
        df['Sector_Position'] = df['Sector'].map(sector_positions)

        # Add small random jitter to x position to prevent overlap
        np.random.seed(42)
        df['X_Jitter'] = df['Sector_Position'] + np.random.uniform(-0.3, 0.3, len(df))

        # Calculate fixed ranges
        y_min = df['YTD_Return'].min()
        y_max = df['YTD_Return'].max()
        y_padding = (y_max - y_min) * 0.1

        # Create animated scatter
        fig = px.scatter(
            df,
            x='X_Jitter',
            y='YTD_Return',
            animation_frame='Year_Month',
            animation_group='Symbol',
            size='Market_Cap',
            color='Sector',
            hover_name='Security',
            hover_data={
                'Symbol': True,
                'Market_Cap': ':,.0f',
                'YTD_Return': ':.2f',
                'Sector': True,
                'X_Jitter': False,
                'Sector_Position': False,
                'Year_Month': False
            },
            color_discrete_map=self.sector_colors,
            size_max=config.BUBBLE_SIZE_MAX,
            range_x=[-0.5, len(sectors) - 0.5],
            range_y=[y_min - y_padding, y_max + y_padding],
            title='Animated Swarm Plot - Stock Performance by Sector'
        )

        # Update layout
        fig.update_layout(
            title_x=0.5,
            xaxis_title='Sector',
            yaxis_title='YTD Return (%)',
            legend_title='Sector',
            hovermode='closest',
            template='plotly_white',
            font=dict(size=12, family='Arial'),
            height=700,
            width=1400,
            xaxis=dict(
                tickmode='array',
                tickvals=list(range(len(sectors))),
                ticktext=sectors,
                tickangle=-45
            )
        )

        # Update bubble style
        fig.update_traces(
            marker=dict(
                opacity=config.BUBBLE_OPACITY,
                line=dict(width=config.BUBBLE_BORDER_WIDTH, color='white')
            )
        )

        # Add reference line at y=0
        fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            print(f"Saved animated swarm plot to {save_path}")

        if show:
            fig.show()

        return fig

    def create_animated_3d_visualization(self, df, save_path=None, show=True):
        """
        Create 3D animated visualization with volatility, return, and market cap

        Args:
            df: DataFrame with time-series data
            save_path: Path to save HTML file
            show: Whether to display

        Returns:
            Plotly figure object
        """
        # Create 3D scatter
        fig = px.scatter_3d(
            df,
            x='Volatility_20',
            y='YTD_Return',
            z='Market_Cap_Billions',
            animation_frame='Year_Month',
            animation_group='Symbol',
            color='Sector',
            size='Market_Cap',
            hover_name='Security',
            hover_data={
                'Symbol': True,
                'Volatility_20': ':.2f',
                'YTD_Return': ':.2f',
                'Market_Cap_Billions': ':.2f',
                'Sector': True,
                'Year_Month': False
            },
            color_discrete_map=self.sector_colors,
            size_max=50,
            title='3D Animated Market Visualization'
        )

        fig.update_layout(
            title_x=0.5,
            scene=dict(
                xaxis_title='Volatility (%)',
                yaxis_title='YTD Return (%)',
                zaxis_title='Market Cap (Billions)',
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.3)
                )
            ),
            template='plotly_white',
            height=800,
            width=1200
        )

        fig.update_traces(
            marker=dict(
                opacity=0.8,
                line=dict(width=0.5, color='white')
            )
        )

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            print(f"Saved 3D animated visualization to {save_path}")

        if show:
            fig.show()

        return fig

    def create_all_animations(self, animation_df, output_dir=None):
        """
        Create all animation types

        Args:
            animation_df: Prepared animation DataFrame
            output_dir: Directory to save outputs

        Returns:
            Dictionary of figure objects
        """
        if output_dir is None:
            output_dir = config.ANIMATED_OUTPUT_DIR

        os.makedirs(output_dir, exist_ok=True)

        print("\n" + "="*50)
        print("CREATING ANIMATED VISUALIZATIONS")
        print("="*50)

        figures = {}

        # 1. Standard animated bubble chart
        print("\n1. Creating animated bubble chart...")
        figures['bubble'] = self.create_animated_bubble_chart(
            animation_df,
            save_path=os.path.join(output_dir, 'animated_bubble_chart.html'),
            show=False
        )

        # 2. Sector race
        print("\n2. Creating animated sector race...")
        figures['sector_race'] = self.create_animated_sector_race(
            animation_df,
            save_path=os.path.join(output_dir, 'animated_sector_race.html'),
            show=False
        )

        # 3. Swarm plot
        print("\n3. Creating animated swarm plot...")
        figures['swarm'] = self.create_animated_swarm_plot(
            animation_df,
            save_path=os.path.join(output_dir, 'animated_swarm_plot.html'),
            show=False
        )

        # 4. 3D visualization
        print("\n4. Creating 3D animated visualization...")
        # Add Market_Cap_Billions if not present
        if 'Market_Cap_Billions' not in animation_df.columns:
            animation_df['Market_Cap_Billions'] = animation_df['Market_Cap'] / 1e9

        figures['3d'] = self.create_animated_3d_visualization(
            animation_df,
            save_path=os.path.join(output_dir, 'animated_3d_visualization.html'),
            show=False
        )

        print("\n" + "="*50)
        print(f"ALL ANIMATIONS SAVED TO: {output_dir}")
        print("="*50)

        return figures


def main():
    """Example usage"""
    from data_fetcher import DataFetcher
    from data_processor import DataProcessor
    from datetime import datetime, timedelta

    # Fetch and process data
    print("Fetching data...")
    fetcher = DataFetcher()
    raw_df = fetcher.fetch_complete_dataset(
        start_date=(datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d'),
        max_stocks=30,
        use_cache=True
    )

    print("\nProcessing data...")
    processor = DataProcessor()
    results = processor.process_complete_pipeline(raw_df, animation_period='M')

    if not results:
        print("Failed to process data!")
        return

    # Create animations
    print("\nCreating animations...")
    animator = AnimatedVisualizer()
    figures = animator.create_all_animations(results['animation'])

    print("\nDone! Open the HTML files in your browser to view the animations.")


if __name__ == '__main__':
    main()
