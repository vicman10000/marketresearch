"""
Static Visualizer Module
Creates static bubble charts and other visualizations
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
from src.logging_config import get_logger


class StaticVisualizer:
    """Creates static visualizations for financial data"""

    def __init__(self):
        """Initialize StaticVisualizer"""
        self.logger = get_logger(__name__)
        self.sector_colors = config.SECTOR_COLORS
        
        # Professional financial theme configuration
        self.theme_config = {
            'template': 'plotly_white',
            'font': dict(
                family='Inter, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif',
                size=13,
                color='#1e293b'
            ),
            'title': dict(
                font=dict(size=20, family='Inter', weight=600, color='#1e293b'),
                x=0.5,
                xanchor='center',
                pad=dict(t=20, b=20)
            ),
            'plot_bgcolor': '#ffffff',
            'paper_bgcolor': '#ffffff',
            'margin': dict(l=60, r=40, t=80, b=60),
            'hovermode': 'closest',
            'hoverlabel': dict(
                bgcolor='white',
                font_size=12,
                font_family='Inter',
                bordercolor='#e2e8f0'
            ),
            'xaxis': dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#f1f5f9',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#e2e8f0',
                showline=True,
                linewidth=1,
                linecolor='#cbd5e1',
                title_font=dict(size=14, family='Inter', weight=600)
            ),
            'yaxis': dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#f1f5f9',
                zeroline=True,
                zerolinewidth=2,
                zerolinecolor='#e2e8f0',
                showline=True,
                linewidth=1,
                linecolor='#cbd5e1',
                title_font=dict(size=14, family='Inter', weight=600)
            ),
            'legend': dict(
                orientation='v',
                yanchor='top',
                y=1,
                xanchor='right',
                x=1,
                bgcolor='rgba(255, 255, 255, 0.9)',
                bordercolor='#e2e8f0',
                borderwidth=1,
                font=dict(size=12)
            )
        }
        
        # Enhanced color palette for professional look
        self.professional_colors = {
            'blue': '#0ea5e9',
            'green': '#10b981',
            'orange': '#f59e0b',
            'purple': '#8b5cf6',
            'red': '#ef4444',
            'teal': '#14b8a6',
            'indigo': '#6366f1',
            'pink': '#ec4899'
        }

    def create_bubble_chart(self, df, x_col='Volatility_20', y_col='YTD_Return',
                           size_col='Market_Cap', color_col='Sector',
                           hover_name='Security', title=None,
                           save_path=None, show=True):
        """
        Create a static bubble chart

        Args:
            df: DataFrame with data
            x_col: Column for x-axis
            y_col: Column for y-axis
            size_col: Column for bubble size
            color_col: Column for color grouping
            hover_name: Column for hover label
            title: Chart title
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        # Get latest date data
        latest_date = df['Date'].max()
        plot_df = df[df['Date'] == latest_date].copy()

        if title is None:
            title = f'Market Bubble Chart - {latest_date.strftime("%Y-%m-%d")}'

        # Create bubble chart
        fig = px.scatter(
            plot_df,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            hover_name=hover_name,
            hover_data={
                'Symbol': True,
                size_col: ':,.0f',
                x_col: ':.2f',
                y_col: ':.2f',
                color_col: True
            },
            color_discrete_map=self.sector_colors,
            size_max=config.BUBBLE_SIZE_MAX,
            title=title
        )

        # Update layout with professional theme
        fig.update_layout(
            title=dict(text=title, **self.theme_config['title']),
            xaxis_title=x_col.replace('_', ' '),
            yaxis_title=y_col.replace('_', ' ') + ' (%)',
            legend_title=color_col,
            template=self.theme_config['template'],
            font=self.theme_config['font'],
            plot_bgcolor=self.theme_config['plot_bgcolor'],
            paper_bgcolor=self.theme_config['paper_bgcolor'],
            margin=self.theme_config['margin'],
            hovermode=self.theme_config['hovermode'],
            hoverlabel=self.theme_config['hoverlabel'],
            xaxis=self.theme_config['xaxis'],
            yaxis=self.theme_config['yaxis'],
            legend=self.theme_config['legend'],
            height=700,
            width=None,  # Auto-width for responsive design
            autosize=True
        )

        # Update bubble style with professional look
        fig.update_traces(
            marker=dict(
                opacity=0.7,
                line=dict(width=1.5, color='rgba(255, 255, 255, 0.6)'),
                sizemode='diameter'
            ),
            textfont=dict(family='Inter', size=10)
        )

        # Add reference lines with professional styling
        fig.add_hline(y=0, line_dash="dash", line_color="#94a3b8", opacity=0.6, line_width=1.5)
        fig.add_vline(x=plot_df[x_col].median(), line_dash="dash",
                     line_color="#94a3b8", opacity=0.6, line_width=1.5,
                     annotation_text="Median", annotation_position="top")

        # Save if path provided
        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            self.logger.info("saved_bubble_chart", save_path=save_path)

        if show:
            fig.show()

        return fig

    def create_sector_performance_chart(self, sector_summary, save_path=None, show=True):
        """
        Create sector performance bar chart

        Args:
            sector_summary: DataFrame with sector summary stats
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        if sector_summary.empty:
            self.logger.warning("no_sector_summary_data_available")
            return None

        # Sort by average return
        sector_summary = sector_summary.sort_values('Avg_YTD_Return', ascending=True)

        # Create bar chart
        fig = go.Figure()

        fig.add_trace(go.Bar(
            y=sector_summary['Sector'],
            x=sector_summary['Avg_YTD_Return'],
            orientation='h',
            marker=dict(
                color=sector_summary['Sector'].map(self.sector_colors),
                line=dict(color='rgba(255, 255, 255, 0.6)', width=1.5),
                opacity=0.9
            ),
            text=sector_summary['Avg_YTD_Return'].round(2),
            texttemplate='%{text}%',
            textposition='outside',
            textfont=dict(family='Inter', size=12, weight=600),
            hovertemplate='<b>%{y}</b><br>' +
                         'Avg YTD Return: %{x:.2f}%<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title=dict(text='Average YTD Return by Sector', **self.theme_config['title']),
            xaxis_title='Average YTD Return (%)',
            yaxis_title='Sector',
            template=self.theme_config['template'],
            font=self.theme_config['font'],
            plot_bgcolor=self.theme_config['plot_bgcolor'],
            paper_bgcolor=self.theme_config['paper_bgcolor'],
            margin=self.theme_config['margin'],
            hoverlabel=self.theme_config['hoverlabel'],
            xaxis=self.theme_config['xaxis'],
            yaxis={**self.theme_config['yaxis'], 'showgrid': False},
            height=600,
            width=None,
            autosize=True,
            showlegend=False
        )

        # Add reference line at 0 with professional styling
        fig.add_vline(x=0, line_dash="solid", line_color="#1e293b", line_width=2, opacity=0.8)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            self.logger.info("saved_sector_performance_chart", save_path=save_path)

        if show:
            fig.show()

        return fig

    def create_market_cap_distribution(self, df, save_path=None, show=True):
        """
        Create market cap distribution by sector

        Args:
            df: DataFrame with stock data
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        # Get latest date data
        latest_date = df['Date'].max()
        plot_df = df[df['Date'] == latest_date].copy()

        # Calculate sector market caps
        sector_caps = plot_df.groupby('Sector')['Market_Cap'].sum().reset_index()
        sector_caps['Market_Cap_Billions'] = sector_caps['Market_Cap'] / 1e9
        sector_caps = sector_caps.sort_values('Market_Cap', ascending=False)

        # Create sunburst chart
        fig = go.Figure(go.Sunburst(
            labels=sector_caps['Sector'],
            parents=[''] * len(sector_caps),
            values=sector_caps['Market_Cap'],
            marker=dict(
                colors=sector_caps['Sector'].map(self.sector_colors)
            ),
            text=sector_caps['Market_Cap_Billions'].round(1),
            texttemplate='<b>%{label}</b><br>$%{text}B',
            hovertemplate='<b>%{label}</b><br>' +
                         'Market Cap: $%{value:,.0f}<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title=f'Market Capitalization by Sector - {latest_date.strftime("%Y-%m-%d")}',
            title_x=0.5,
            height=700,
            width=1000
        )

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            self.logger.info("saved_market_cap_distribution", save_path=save_path)

        if show:
            fig.show()

        return fig

    def create_top_performers_chart(self, df, n=20, save_path=None, show=True):
        """
        Create chart showing top N performing stocks

        Args:
            df: DataFrame with stock data
            n: Number of top performers to show
            save_path: Path to save HTML file
            show: Whether to display the chart

        Returns:
            Plotly figure object
        """
        # Get latest date data
        latest_date = df['Date'].max()
        plot_df = df[df['Date'] == latest_date].copy()

        # Get top performers
        top_performers = plot_df.nlargest(n, 'YTD_Return')

        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=top_performers['YTD_Return'],
            y=top_performers['Security'],
            orientation='h',
            marker=dict(
                color=top_performers['Sector'].map(self.sector_colors),
                line=dict(color='white', width=1)
            ),
            text=top_performers['YTD_Return'].round(2),
            texttemplate='%{text}%',
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>' +
                         'Symbol: %{customdata[0]}<br>' +
                         'Sector: %{customdata[1]}<br>' +
                         'YTD Return: %{x:.2f}%<br>' +
                         '<extra></extra>',
            customdata=top_performers[['Symbol', 'Sector']]
        ))

        fig.update_layout(
            title=f'Top {n} Performing Stocks - {latest_date.strftime("%Y-%m-%d")}',
            title_x=0.5,
            xaxis_title='YTD Return (%)',
            yaxis_title='',
            template='plotly_white',
            height=max(600, n * 25),
            width=1000,
            showlegend=False,
            yaxis=dict(autorange='reversed')
        )

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            self.logger.info("saved_top_performers_chart", save_path=save_path)

        if show:
            fig.show()

        return fig

    def create_dashboard(self, df, sector_summary, save_path=None, show=True):
        """
        Create comprehensive dashboard with multiple visualizations

        Args:
            df: DataFrame with stock data
            sector_summary: DataFrame with sector summary
            save_path: Path to save HTML file
            show: Whether to display

        Returns:
            Plotly figure object
        """
        from plotly.subplots import make_subplots

        # Get latest date data
        latest_date = df['Date'].max()
        plot_df = df[df['Date'] == latest_date].copy()

        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Return vs Volatility Bubble Chart',
                'Sector Performance',
                'Top 10 Performers',
                'Market Cap Distribution by Sector'
            ),
            specs=[
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "pie"}]
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.1
        )

        # 1. Bubble chart
        for sector in plot_df['Sector'].unique():
            sector_data = plot_df[plot_df['Sector'] == sector]
            fig.add_trace(
                go.Scatter(
                    x=sector_data['Volatility_20'],
                    y=sector_data['YTD_Return'],
                    mode='markers',
                    name=sector,
                    marker=dict(
                        size=np.sqrt(sector_data['Market_Cap']) / 5e5,
                        color=self.sector_colors.get(sector, '#999999'),
                        opacity=0.7,
                        line=dict(width=1, color='white')
                    ),
                    text=sector_data['Security'],
                    hovertemplate='<b>%{text}</b><br>' +
                                 'Volatility: %{x:.2f}<br>' +
                                 'YTD Return: %{y:.2f}%<br>' +
                                 '<extra></extra>',
                    showlegend=True
                ),
                row=1, col=1
            )

        # 2. Sector performance
        sector_sorted = sector_summary.sort_values('Avg_YTD_Return', ascending=False).head(10)
        fig.add_trace(
            go.Bar(
                x=sector_sorted['Sector'],
                y=sector_sorted['Avg_YTD_Return'],
                marker=dict(color=sector_sorted['Sector'].map(self.sector_colors)),
                showlegend=False,
                hovertemplate='<b>%{x}</b><br>Avg Return: %{y:.2f}%<extra></extra>'
            ),
            row=1, col=2
        )

        # 3. Top performers
        top_10 = plot_df.nlargest(10, 'YTD_Return')
        fig.add_trace(
            go.Bar(
                x=top_10['YTD_Return'],
                y=top_10['Symbol'],
                orientation='h',
                marker=dict(color=top_10['Sector'].map(self.sector_colors)),
                showlegend=False,
                hovertemplate='<b>%{y}</b><br>Return: %{x:.2f}%<extra></extra>'
            ),
            row=2, col=1
        )

        # 4. Market cap pie
        sector_caps = plot_df.groupby('Sector')['Market_Cap'].sum().reset_index()
        fig.add_trace(
            go.Pie(
                labels=sector_caps['Sector'],
                values=sector_caps['Market_Cap'],
                marker=dict(colors=sector_caps['Sector'].map(self.sector_colors)),
                showlegend=False,
                hovertemplate='<b>%{label}</b><br>%{percent}<extra></extra>'
            ),
            row=2, col=2
        )

        # Update layout
        fig.update_layout(
            title_text=f"Market Overview Dashboard - {latest_date.strftime('%Y-%m-%d')}",
            title_x=0.5,
            height=1000,
            width=1600,
            showlegend=True,
            template='plotly_white'
        )

        fig.update_xaxes(title_text="Volatility", row=1, col=1)
        fig.update_yaxes(title_text="YTD Return (%)", row=1, col=1)
        fig.update_yaxes(title_text="Avg YTD Return (%)", row=1, col=2)
        fig.update_xaxes(title_text="YTD Return (%)", row=2, col=1)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            fig.write_html(save_path)
            self.logger.info("saved_dashboard", save_path=save_path)

        if show:
            fig.show()

        return fig


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
    results = processor.process_complete_pipeline(raw_df)

    if not results:
        print("Failed to process data!")
        return

    # Create visualizations
    print("\nCreating visualizations...")
    visualizer = StaticVisualizer()

    output_dir = config.STATIC_OUTPUT_DIR

    # 1. Bubble chart
    visualizer.create_bubble_chart(
        results['processed'],
        save_path=os.path.join(output_dir, 'bubble_chart.html'),
        show=False
    )

    # 2. Sector performance
    visualizer.create_sector_performance_chart(
        results['sector_summary'],
        save_path=os.path.join(output_dir, 'sector_performance.html'),
        show=False
    )

    # 3. Market cap distribution
    visualizer.create_market_cap_distribution(
        results['processed'],
        save_path=os.path.join(output_dir, 'market_cap_distribution.html'),
        show=False
    )

    # 4. Top performers
    visualizer.create_top_performers_chart(
        results['processed'],
        n=20,
        save_path=os.path.join(output_dir, 'top_performers.html'),
        show=False
    )

    # 5. Dashboard
    visualizer.create_dashboard(
        results['processed'],
        results['sector_summary'],
        save_path=os.path.join(output_dir, 'dashboard.html'),
        show=False
    )

    print(f"\nAll visualizations saved to {output_dir}")


if __name__ == '__main__':
    main()
