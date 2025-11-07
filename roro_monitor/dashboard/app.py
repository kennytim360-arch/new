"""
Main Dashboard Application

Interactive Plotly Dash dashboard for the Institutional RO/RO Monitor.
"""

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc
from datetime import datetime
import logging

from ..engine import RegimeEngine, PositioningEngine
from ..data import DataFetcher
from .components import DashboardComponents
from .alerts import AlertSystem
from ..config import settings

logger = logging.getLogger(__name__)


def create_dashboard(debug: bool = None, port: int = None):
    """
    Create and configure the dashboard application.

    Args:
        debug: Debug mode (default from settings)
        port: Port number (default from settings)

    Returns:
        Dash app instance
    """
    if debug is None:
        debug = settings.DASHBOARD_DEBUG
    if port is None:
        port = settings.DASHBOARD_PORT

    # Initialize components
    regime_engine = RegimeEngine()
    positioning_engine = PositioningEngine()
    alert_system = AlertSystem()
    dashboard_components = DashboardComponents()

    # Create Dash app with Bootstrap theme
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        title="RO/RO Monitor"
    )

    # Dashboard Layout
    app.layout = dbc.Container([
        # Header
        dbc.Row([
            dbc.Col([
                html.H1("🎯 Institutional Risk-On/Risk-Off Monitor",
                       className="text-center mb-4 mt-4",
                       style={'color': '#1f77b4', 'font-weight': 'bold'})
            ])
        ]),

        # Last Update Time
        dbc.Row([
            dbc.Col([
                html.Div(id='last-update', className='text-center text-muted mb-3')
            ])
        ]),

        # Alerts Section
        dbc.Row([
            dbc.Col([
                html.Div(id='alert-banner')
            ])
        ], className='mb-3'),

        # Main Dashboard Row 1: Master Gauge + Summary
        dbc.Row([
            # Master Gauge
            dbc.Col([
                dcc.Graph(id='master-gauge')
            ], width=6),

            # Summary Stats
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Current Status")),
                    dbc.CardBody([
                        html.Div(id='status-summary')
                    ])
                ])
            ], width=6)
        ], className='mb-4'),

        # Row 2: Pillar Scores + Score History
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='pillar-bars')
            ], width=6),

            dbc.Col([
                dcc.Graph(id='score-history')
            ], width=6)
        ], className='mb-4'),

        # Row 3: Heatmap
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='heatmap')
            ], width=12)
        ], className='mb-4'),

        # Row 4: CFD Positioning Matrix
        dbc.Row([
            dbc.Col([
                html.H3("CFD Positioning Recommendations", className='mb-3'),
                html.Div(id='positioning-summary', className='mb-3'),
                dcc.Graph(id='positioning-table')
            ], width=12)
        ], className='mb-4'),

        # Row 5: Detailed Pillar Breakdown
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Detailed Pillar Analysis")),
                    dbc.CardBody([
                        html.Div(id='pillar-details')
                    ])
                ])
            ], width=12)
        ], className='mb-4'),

        # Control Section
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "🔄 Refresh Data",
                    id='refresh-button',
                    color='primary',
                    size='lg',
                    className='w-100'
                )
            ], width=3),

            dbc.Col([
                dbc.Button(
                    "📊 Export Report",
                    id='export-button',
                    color='secondary',
                    size='lg',
                    className='w-100',
                    disabled=True
                )
            ], width=3),

            dbc.Col([
                html.Div([
                    html.Label("Auto-refresh:"),
                    dcc.Dropdown(
                        id='refresh-interval',
                        options=[
                            {'label': 'Off', 'value': 0},
                            {'label': '1 minute', 'value': 60},
                            {'label': '5 minutes', 'value': 300},
                            {'label': '15 minutes', 'value': 900},
                        ],
                        value=0,
                        clearable=False
                    )
                ])
            ], width=3)
        ], className='mb-4'),

        # Hidden div to store data
        dcc.Store(id='regime-data'),
        dcc.Store(id='market-data-store'),
        dcc.Store(id='previous-regime-data'),

        # Interval component for auto-refresh
        dcc.Interval(
            id='interval-component',
            interval=300*1000,  # Default 5 minutes
            n_intervals=0,
            disabled=True
        )

    ], fluid=True, style={'backgroundColor': '#f8f9fa'})

    # Callbacks
    @app.callback(
        [
            Output('regime-data', 'data'),
            Output('market-data-store', 'data'),
            Output('previous-regime-data', 'data'),
            Output('last-update', 'children')
        ],
        [
            Input('refresh-button', 'n_clicks'),
            Input('interval-component', 'n_intervals')
        ],
        [
            State('regime-data', 'data'),
        ],
        prevent_initial_call=False
    )
    def update_regime_data(n_clicks, n_intervals, previous_data):
        """Fetch fresh data and calculate regime."""
        logger.info("Calculating regime...")

        try:
            # Calculate regime
            regime_data = regime_engine.calculate_regime(fetch_fresh=False)

            # Store market data flag (we'll fetch it separately if needed)
            market_data_flag = {'fetched': True}

            # Update timestamp
            timestamp_str = f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

            return regime_data, market_data_flag, previous_data, timestamp_str

        except Exception as e:
            logger.error(f"Error updating regime: {e}", exc_info=True)
            return None, None, previous_data, f"Error: {str(e)}"

    @app.callback(
        Output('master-gauge', 'figure'),
        Input('regime-data', 'data')
    )
    def update_master_gauge(regime_data):
        """Update master gauge."""
        if not regime_data:
            return dashboard_components.create_master_gauge(50, 'NEUTRAL')

        score = regime_data.get('master_score', 50)
        regime = regime_data.get('regime', 'NEUTRAL')

        return dashboard_components.create_master_gauge(score, regime)

    @app.callback(
        Output('status-summary', 'children'),
        Input('regime-data', 'data')
    )
    def update_status_summary(regime_data):
        """Update status summary."""
        if not regime_data:
            return html.P("Loading...")

        score = regime_data.get('master_score', 50)
        regime = regime_data.get('regime', 'NEUTRAL')
        conviction = regime_data.get('conviction', 'LOW')
        summary = regime_data.get('summary', '')
        key_drivers = regime_data.get('key_drivers', [])

        return html.Div([
            html.H5(f"Score: {score:.1f}/100", className='mb-2'),
            html.H5(f"Conviction: {conviction}", className='mb-3'),
            html.Hr(),
            html.H6("Summary:", className='mb-2'),
            html.P(summary, className='mb-3'),
            html.H6("Key Drivers:", className='mb-2'),
            html.Ul([html.Li(driver) for driver in key_drivers])
        ])

    @app.callback(
        Output('pillar-bars', 'figure'),
        Input('regime-data', 'data')
    )
    def update_pillar_bars(regime_data):
        """Update pillar bars."""
        if not regime_data or 'pillar_scores' not in regime_data:
            return {}

        return dashboard_components.create_pillar_bars(regime_data['pillar_scores'])

    @app.callback(
        Output('score-history', 'figure'),
        Input('regime-data', 'data')
    )
    def update_score_history(regime_data):
        """Update score history."""
        if not regime_data or 'score_history' not in regime_data:
            return {}

        return dashboard_components.create_score_history(regime_data['score_history'])

    @app.callback(
        Output('heatmap', 'figure'),
        Input('market-data-store', 'data')
    )
    def update_heatmap(market_data_flag):
        """Update heatmap."""
        if not market_data_flag:
            return {}

        # Fetch market data
        data_fetcher = DataFetcher(use_cache=True)
        market_data = data_fetcher.fetch_all_universe(period='1mo', interval='1d')

        return dashboard_components.create_heatmap(market_data)

    @app.callback(
        [
            Output('positioning-table', 'figure'),
            Output('positioning-summary', 'children')
        ],
        Input('regime-data', 'data')
    )
    def update_positioning(regime_data):
        """Update positioning recommendations."""
        if not regime_data:
            return {}, ""

        recommendations = positioning_engine.generate_recommendations(regime_data)
        summary = positioning_engine.get_summary()

        fig = dashboard_components.create_positioning_table(recommendations)

        summary_html = html.Div([
            html.H5("Portfolio Exposure Summary:", className='mb-2'),
            html.P(summary, style={'font-size': '1.1em', 'font-weight': 'bold'})
        ])

        return fig, summary_html

    @app.callback(
        Output('pillar-details', 'children'),
        Input('regime-data', 'data')
    )
    def update_pillar_details(regime_data):
        """Update detailed pillar breakdown."""
        if not regime_data or 'pillar_scores' not in regime_data:
            return html.P("No data available")

        pillar_scores = regime_data['pillar_scores']
        details = []

        for pillar_name, pillar_data in pillar_scores.items():
            details.append(
                html.Div([
                    html.H5(pillar_name, className='mt-3'),
                    html.P(f"Score: {pillar_data['score']:.1f} | Status: {pillar_data['status']}"),
                    html.P(f"Weight: {pillar_data['weight']:.1%} | Weighted Score: {pillar_data['weighted_score']:.1f}"),
                    html.Hr()
                ])
            )

        return details

    @app.callback(
        Output('alert-banner', 'children'),
        [
            Input('regime-data', 'data'),
            Input('previous-regime-data', 'data')
        ]
    )
    def update_alerts(regime_data, previous_regime_data):
        """Update alert banner."""
        if not regime_data:
            return ""

        alerts = alert_system.check_alerts(regime_data, previous_regime_data)
        return html.Div([
            html.Div(dashboard_components.create_alert_banner(alerts),
                    dangerously_allow_html=True)
        ], dangerously_allow_html=True)

    @app.callback(
        [
            Output('interval-component', 'disabled'),
            Output('interval-component', 'interval')
        ],
        Input('refresh-interval', 'value')
    )
    def update_refresh_interval(interval_seconds):
        """Update auto-refresh interval."""
        if interval_seconds == 0:
            return True, 300*1000  # Disabled

        return False, interval_seconds * 1000

    logger.info(f"Dashboard created. Ready to run on port {port}")

    return app


def run_dashboard(debug: bool = None, port: int = None):
    """
    Run the dashboard server.

    Args:
        debug: Debug mode
        port: Port number
    """
    app = create_dashboard(debug, port)

    if port is None:
        port = settings.DASHBOARD_PORT
    if debug is None:
        debug = settings.DASHBOARD_DEBUG

    logger.info("="*60)
    logger.info("STARTING RO/RO MONITOR DASHBOARD")
    logger.info(f"Access at: http://localhost:{port}")
    logger.info("="*60)

    app.run_server(debug=debug, port=port, host='0.0.0.0')
