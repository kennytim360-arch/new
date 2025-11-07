"""
Dashboard UI Components

Reusable Plotly/Dash components for the RO/RO Monitor.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, Any, List
from datetime import datetime

from ..config import settings


class DashboardComponents:
    """Collection of reusable dashboard components."""

    @staticmethod
    def create_master_gauge(score: float, regime: str) -> go.Figure:
        """
        Create the main regime score gauge.

        Args:
            score: Master regime score (0-100)
            regime: Regime classification

        Returns:
            Plotly figure
        """
        color = settings.regime_colors.get(regime, '#FFFF00')

        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"<b>{regime}</b><br><span style='font-size:0.8em'>Master Regime Score</span>",
                   'font': {'size': 24}},
            delta={'reference': 50, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color, 'thickness': 0.75},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 20], 'color': '#FFE6E6'},
                    {'range': [20, 40], 'color': '#FFF4E6'},
                    {'range': [40, 60], 'color': '#FFFEE6'},
                    {'range': [60, 80], 'color': '#E6FFE6'},
                    {'range': [80, 100], 'color': '#E6F7E6'}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': score
                }
            }
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=20, r=20, t=80, b=20),
            paper_bgcolor="white",
            font={'color': "darkblue", 'family': "Arial"}
        )

        return fig

    @staticmethod
    def create_pillar_bars(pillar_scores: Dict[str, Any]) -> go.Figure:
        """
        Create pillar score bar chart.

        Args:
            pillar_scores: Dictionary of pillar scores

        Returns:
            Plotly figure
        """
        pillars = []
        scores = []
        weights = []
        weighted_scores = []

        for name, data in pillar_scores.items():
            pillars.append(name.replace('Pillar ', '').replace(': ', '<br>'))
            scores.append(data['score'])
            weights.append(data['weight'])
            weighted_scores.append(data['weighted_score'])

        fig = go.Figure()

        # Raw scores
        fig.add_trace(go.Bar(
            name='Raw Score',
            x=pillars,
            y=scores,
            marker_color='lightblue',
            text=[f"{s:.1f}" for s in scores],
            textposition='auto',
        ))

        # Weighted scores
        fig.add_trace(go.Bar(
            name='Weighted Score',
            x=pillars,
            y=weighted_scores,
            marker_color='darkblue',
            text=[f"{s:.1f}" for s in weighted_scores],
            textposition='auto',
        ))

        fig.update_layout(
            title="<b>Pillar Score Breakdown</b>",
            xaxis_title="",
            yaxis_title="Score",
            yaxis=dict(range=[0, 100]),
            barmode='group',
            height=400,
            margin=dict(l=20, r=20, t=60, b=100),
            legend=dict(x=0.7, y=1.1, orientation='h'),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_score_history(score_history: List[Dict[str, Any]]) -> go.Figure:
        """
        Create score history time series.

        Args:
            score_history: List of historical scores

        Returns:
            Plotly figure
        """
        if not score_history:
            # Empty figure
            fig = go.Figure()
            fig.add_annotation(text="No historical data available",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            return fig

        df = pd.DataFrame(score_history)

        fig = go.Figure()

        # Score line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['score'],
            mode='lines+markers',
            name='Master Score',
            line=dict(color='darkblue', width=3),
            marker=dict(size=6),
            hovertemplate='<b>%{x}</b><br>Score: %{y:.1f}<extra></extra>'
        ))

        # Regime threshold lines
        fig.add_hline(y=80, line_dash="dash", line_color="green",
                     annotation_text="Strong Risk-On", annotation_position="right")
        fig.add_hline(y=60, line_dash="dot", line_color="lightgreen")
        fig.add_hline(y=40, line_dash="dot", line_color="orange")
        fig.add_hline(y=20, line_dash="dash", line_color="red",
                     annotation_text="Strong Risk-Off", annotation_position="right")

        fig.update_layout(
            title="<b>Regime Score History (30 Days)</b>",
            xaxis_title="Date",
            yaxis_title="Master Score",
            yaxis=dict(range=[0, 100]),
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            hovermode='x unified',
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_heatmap(market_data: Dict[str, pd.DataFrame]) -> go.Figure:
        """
        Create intermarket performance heatmap.

        Args:
            market_data: Dictionary of ticker -> DataFrame

        Returns:
            Plotly figure
        """
        # Calculate returns for key assets
        key_assets = ['SPY', 'QQQ', 'IWM', 'TLT', 'HYG', 'GLD', '^VIX']
        periods = ['1D', '1W', '1M']

        data = []
        for ticker in key_assets:
            if ticker not in market_data or market_data[ticker].empty:
                continue

            df = market_data[ticker]

            if len(df) < 21:
                continue

            row = {'Asset': ticker}

            # 1-day
            if len(df) >= 2:
                row['1D'] = ((df['close'].iloc[-1] / df['close'].iloc[-2]) - 1) * 100

            # 1-week (5 days)
            if len(df) >= 6:
                row['1W'] = ((df['close'].iloc[-1] / df['close'].iloc[-6]) - 1) * 100

            # 1-month (21 days)
            if len(df) >= 22:
                row['1M'] = ((df['close'].iloc[-1] / df['close'].iloc[-22]) - 1) * 100

            data.append(row)

        if not data:
            fig = go.Figure()
            fig.add_annotation(text="Insufficient data for heatmap",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            return fig

        heatmap_df = pd.DataFrame(data)
        heatmap_df = heatmap_df.set_index('Asset')

        fig = go.Figure(data=go.Heatmap(
            z=heatmap_df.values,
            x=heatmap_df.columns,
            y=heatmap_df.index,
            colorscale='RdYlGn',
            zmid=0,
            text=heatmap_df.values,
            texttemplate='%{text:.2f}%',
            textfont={"size": 12},
            colorbar=dict(title="Return %")
        ))

        fig.update_layout(
            title="<b>Intermarket Performance Heatmap</b>",
            height=400,
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_positioning_table(recommendations: List[Dict[str, Any]]) -> go.Figure:
        """
        Create CFD positioning recommendations table.

        Args:
            recommendations: List of position recommendations

        Returns:
            Plotly figure
        """
        if not recommendations:
            fig = go.Figure()
            fig.add_annotation(text="No recommendations available",
                             xref="paper", yref="paper",
                             x=0.5, y=0.5, showarrow=False)
            return fig

        df = pd.DataFrame(recommendations)

        # Color code the actions
        action_colors = {
            'STRONG BUY': '#00CC00',
            'BUY': '#90EE90',
            'NEUTRAL': '#FFFF00',
            'SELL': '#FFB347',
            'STRONG SELL': '#FF6B6B'
        }

        cell_colors = [action_colors.get(action, '#FFFFFF') for action in df['action']]

        fig = go.Figure(data=[go.Table(
            header=dict(
                values=['<b>Asset</b>', '<b>Class</b>', '<b>Action</b>',
                       '<b>Sizing (%)</b>', '<b>Rationale</b>'],
                fill_color='darkblue',
                align='left',
                font=dict(color='white', size=12)
            ),
            cells=dict(
                values=[df['asset'], df['asset_class'], df['action'],
                       df['sizing'], df['rationale']],
                fill_color=['white', 'white', [cell_colors], 'white', 'white'],
                align='left',
                font=dict(size=11),
                height=30
            )
        )])

        fig.update_layout(
            title="<b>CFD Positioning Matrix</b>",
            height=max(400, len(recommendations) * 40 + 100),
            margin=dict(l=20, r=20, t=60, b=20),
            paper_bgcolor="white"
        )

        return fig

    @staticmethod
    def create_alert_banner(alerts: List[Dict[str, Any]]) -> str:
        """
        Create HTML alert banner.

        Args:
            alerts: List of active alerts

        Returns:
            HTML string
        """
        if not alerts:
            return """
            <div style='padding: 10px; background-color: #E6F7E6; border-left: 5px solid green;'>
                <strong>✓ No Active Alerts</strong> - System operating normally
            </div>
            """

        severity_colors = {
            'CRITICAL': '#8B0000',
            'HIGH': '#FF0000',
            'MEDIUM': '#FFA500',
            'LOW': '#FFD700'
        }

        html_parts = []

        for alert in alerts:
            color = severity_colors.get(alert['severity'], '#FFA500')
            html_parts.append(f"""
            <div style='padding: 10px; margin: 5px 0; background-color: {color}22; border-left: 5px solid {color};'>
                <strong>{alert['severity']}: {alert['title']}</strong><br>
                {alert['message']}
            </div>
            """)

        return "".join(html_parts)
