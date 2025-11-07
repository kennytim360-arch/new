# 🎯 Institutional Risk-On/Risk-Off (RO/RO) Monitor

An institutional-grade, multi-dimensional market regime analysis system that identifies Risk-On vs Risk-Off conditions with probabilistic conviction weighting and generates actionable CFD positioning recommendations.

## 📊 Overview

The RO/RO Monitor transforms market analysis from binary classification into a sophisticated, conviction-weighted allocation system. It analyzes **5 fundamental pillars** across multiple timeframes to produce:

- **Master Regime Score (0-100)**: Quantitative measure of market risk appetite
- **Regime Classification**: STRONG_RISK_ON → MODERATE_RISK_ON → NEUTRAL → MODERATE_RISK_OFF → STRONG_RISK_OFF
- **Conviction Level**: HIGH, MEDIUM, or LOW confidence in the regime
- **CFD Positioning Matrix**: Dynamic, regime-based position recommendations
- **Multi-Level Alerts**: Real-time warnings for regime changes, credit spreads, and divergences

---

## 🏗️ System Architecture

### The 5 Pillars

#### Pillar A: Price Trend & Momentum (30% Weight)
- Moving Average Alignment (50/100/200-day)
- RSI Regime Analysis
- MACD Signal Quality
- Multi-timeframe confirmation

#### Pillar B: Market Breadth & Health (25% Weight)
- Sector Rotation (Cyclical vs Defensive)
- Small Cap vs Large Cap Leadership
- Risk Asset Dispersion
- Market Internal Health

#### Pillar C: Macro-Fundamental Drivers (25% Weight)
- Credit Spreads (HYG vs IEF)
- VIX Term Structure
- Safe-Haven Flows (TLT, GLD)
- Volatility Regime

#### Pillar D: Currency & Carry Trade (10% Weight)
- JPY Crosses (USDJPY, AUDJPY)
- Risk Currency Momentum
- Carry Trade Unwind Detection

#### Pillar E: Sentiment & Positioning (10% Weight)
- VIX Levels & Z-Scores
- Price Extremes
- Contrarian Indicators

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd new

# Install dependencies
pip install -r requirements.txt
```

### Running the System

#### 1. Interactive Dashboard (Recommended)
```bash
python main.py dashboard
```
Access at: `http://localhost:8050`

#### 2. Command-Line Analysis
```bash
python main.py analyze
```
Outputs current regime analysis to console.

#### 3. Historical Backtest
```bash
python main.py backtest
```
Runs historical validation and exports results.

---

## 📈 Dashboard Features

### Main Components

1. **Master Regime Gauge**
   - Real-time 0-100 score display
   - Color-coded regime classification
   - Conviction indicator

2. **Pillar Score Breakdown**
   - Individual pillar scores
   - Weighted contributions
   - Component drill-down

3. **Score History Chart**
   - 30-day regime timeline
   - Threshold visualizations
   - Trend identification

4. **Intermarket Heatmap**
   - Multi-asset performance (1D/1W/1M)
   - Visual correlation matrix
   - Quick market snapshot

5. **CFD Positioning Matrix**
   - Asset-specific recommendations
   - Dynamic sizing weights
   - Risk/reward rationale

6. **Alert System**
   - Regime change notifications
   - Credit spread warnings
   - Divergence alerts
   - VIX spike detection

---

## 🎯 CFD Positioning System

### Regime-Based Allocation

| Master Score | Regime | Equity CFDs | Bond CFDs | Conviction |
|--------------|--------|-------------|-----------|------------|
| 80-100 | STRONG RISK-ON | +100-150% | -30% | HIGH |
| 60-79 | MODERATE RISK-ON | +50-100% | 0% | MEDIUM |
| 40-59 | NEUTRAL/TRANSITION | 0-25% | 0-25% | LOW |
| 20-39 | MODERATE RISK-OFF | -50% | +75% | MEDIUM |
| 0-19 | STRONG RISK-OFF | -100% | +100% | HIGH |

### Dynamic Position Sizing

The system automatically adjusts exposure based on:
- Current regime score
- Conviction level
- Asset-specific factors
- Sector rotation signals

**Example Output:**
```
SPY   | STRONG BUY  | Sizing: +100% | Large Cap US Equities
QQQ   | BUY         | Sizing:  +50% | Tech-heavy Nasdaq
TLT   | NEUTRAL     | Sizing:    0% | Long-term Treasuries
XLF   | BUY         | Sizing:  +40% | Financials - Risk-On leader

Net Equity Exposure: +190% | Net Bond Exposure: 0% | Risk Bias: LONG
```

---

## 🔧 Configuration

### Customize Settings

Edit `roro_monitor/config/settings.py`:

```python
# Pillar Weights (must sum to 1.0)
PILLAR_WEIGHTS = {
    'pillar_a': 0.30,  # Price Trend & Momentum
    'pillar_b': 0.25,  # Market Breadth
    'pillar_c': 0.25,  # Macro Fundamentals
    'pillar_d': 0.10,  # Currency Carry
    'pillar_e': 0.10,  # Sentiment
}

# Regime Thresholds
REGIME_THRESHOLDS = {
    'STRONG_RISK_ON': (80, 100),
    'MODERATE_RISK_ON': (60, 79),
    'NEUTRAL': (40, 59),
    'MODERATE_RISK_OFF': (20, 39),
    'STRONG_RISK_OFF': (0, 19),
}

# Technical Indicator Parameters
MA_SHORT = 50
MA_MEDIUM = 100
MA_LONG = 200
RSI_PERIOD = 14
```

### Asset Universe

Customize tracked assets in `roro_monitor/config/tickers.py`:

```python
EQUITIES_RISK = ["SPY", "QQQ", "IWM", "EEM"]
GOVERNMENT_BONDS = ["IEF", "TLT"]
CREDIT = ["HYG", "LQD"]
COMMODITIES = ["GLD", "USO"]
CURRENCIES = ["USDJPY=X", "AUDJPY=X"]
```

---

## 📊 Data Sources

### Current Implementation
- **Primary**: Yahoo Finance (yfinance) - Free, reliable, real-time
- **Caching**: 1-hour local cache to minimize API calls
- **Fallback**: Robust error handling with graceful degradation

### Future Enhancements
- Bloomberg API integration
- Alpha Vantage for advanced breadth indicators
- Custom WebSocket feeds for real-time updates

---

## 🧪 Backtesting

### Run Historical Validation

```bash
python main.py backtest
```

### Output Metrics
- Regime classification accuracy
- Score-return correlation
- Performance by regime
- Signal quality analysis
- Optimal weight calibration

### Example Results
```
BACKTEST RESULTS SUMMARY
========================================
Total Signals: 120
Average Score: 62.3
Score-Return Correlation: 0.45

Performance by Regime:
  STRONG_RISK_ON: +1.2% avg forward return
  MODERATE_RISK_ON: +0.8%
  NEUTRAL: +0.2%
  MODERATE_RISK_OFF: -0.3%
  STRONG_RISK_OFF: -0.9%
```

---

## 🔔 Alert System

### Alert Types & Severity

| Alert Type | Severity | Trigger Condition |
|------------|----------|-------------------|
| Regime Change | HIGH | Regime classification changes |
| Score Movement | MEDIUM | Score moves >10 points |
| Credit Spread Warning | HIGH | HY spreads widen >2σ |
| VIX Spike | HIGH | VIX z-score >2.0 |
| Breadth Divergence | MEDIUM | Price-breadth gap >30 points |

### Alert Configuration

Alerts are automatically displayed in the dashboard and can be configured for:
- Email notifications (future)
- SMS alerts (future)
- Webhook integrations (future)

---

## 📁 Project Structure

```
new/
├── roro_monitor/
│   ├── config/          # Configuration & asset universe
│   ├── data/            # Data fetching & caching
│   ├── indicators/      # Technical & macro indicators
│   ├── pillars/         # 5 pillar analysis modules
│   ├── engine/          # Regime & positioning engines
│   ├── dashboard/       # Interactive web dashboard
│   ├── backtest/        # Backtesting & calibration
│   └── tests/           # Unit tests
├── main.py              # Main entry point
├── requirements.txt     # Dependencies
└── README.md           # This file
```

---

## 🛠️ Development

### Running Tests
```bash
pytest roro_monitor/tests/
```

### Code Quality
```bash
# Linting
flake8 roro_monitor/

# Type checking
mypy roro_monitor/
```

### Adding Custom Pillars

1. Create new pillar in `roro_monitor/pillars/`
2. Inherit from `BasePillar`
3. Implement `calculate_score()` and `get_details()`
4. Add to `RegimeEngine` initialization
5. Update pillar weights in settings

---

## 📝 Usage Examples

### Programmatic Access

```python
from roro_monitor import RegimeEngine, PositioningEngine

# Initialize engines
regime_engine = RegimeEngine()
positioning_engine = PositioningEngine()

# Calculate current regime
regime_data = regime_engine.calculate_regime()

print(f"Score: {regime_data['master_score']:.1f}")
print(f"Regime: {regime_data['regime']}")

# Generate positions
recommendations = positioning_engine.generate_recommendations(regime_data)

for rec in recommendations:
    print(f"{rec['asset']}: {rec['action']} ({rec['sizing']:+}%)")
```

### Custom Analysis

```python
from roro_monitor import DataFetcher
from roro_monitor.pillars import PillarA_PriceTrend

# Fetch specific data
fetcher = DataFetcher()
data = fetcher.fetch_multiple_tickers(['SPY', 'QQQ', 'TLT'])

# Run individual pillar
pillar_a = PillarA_PriceTrend()
score = pillar_a.calculate_score(data)
details = pillar_a.get_details()

print(f"Trend Score: {score:.1f}")
print(f"Components: {details['components']}")
```

---

## 🎓 Methodology

### Scoring Philosophy

The system uses a **0-100 continuous scale** rather than binary classification:

- **0-19**: Strong defensive positioning required
- **20-39**: Cautious, risk-off bias
- **40-59**: Neutral, market-neutral strategies
- **60-79**: Constructive, risk-on bias
- **80-100**: Aggressive long positioning

### Conviction Weighting

Position sizing scales with conviction:
- **HIGH Conviction** (scores 0-19 or 80-100): Maximum exposure
- **MEDIUM Conviction** (scores 20-39 or 60-79): Moderate exposure
- **LOW Conviction** (scores 40-59): Minimal exposure, focus on hedging

### Multi-Timeframe Confirmation

Pillars analyze multiple timeframes:
- **Daily**: Tactical signals
- **Weekly**: Intermediate trends
- **Monthly**: Strategic positioning

---

## 🚧 Roadmap

### Version 1.1 (Planned)
- [ ] Real-time WebSocket data feeds
- [ ] Email/SMS alert delivery
- [ ] Enhanced backtesting (Monte Carlo)
- [ ] Machine learning weight optimization

### Version 1.2 (Planned)
- [ ] Bloomberg Terminal integration
- [ ] Options positioning analysis
- [ ] Crypto market regime tracking
- [ ] Mobile dashboard app

### Version 2.0 (Future)
- [ ] Multi-asset class expansion
- [ ] Portfolio optimizer integration
- [ ] Automated trade execution
- [ ] Risk management module

---

## 📄 License

Copyright © 2024 RO/RO Monitor Team. All rights reserved.

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

---

## 📧 Support

For questions, issues, or feature requests:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

## ⚠️ Disclaimer

This system is for **informational and educational purposes only**. It does not constitute financial advice. Trading CFDs and leveraged instruments carries substantial risk of loss. Always conduct your own research and consult with qualified financial advisors before making investment decisions.

**Past performance does not guarantee future results.**

---

## 🙏 Acknowledgments

Built with:
- Python 3.8+
- Plotly/Dash for visualization
- yfinance for market data
- pandas/numpy for analysis
- Institutional trading methodology

---

**© 2024 Institutional RO/RO Monitor | Version 1.0.0**
