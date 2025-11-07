# 🚀 Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If you encounter issues installing TA-Lib, use:
```bash
# On Ubuntu/Debian
sudo apt-get install ta-lib
pip install TA-Lib

# On macOS
brew install ta-lib
pip install TA-Lib

# Or skip TA-Lib (system will work without it)
pip install -r requirements.txt --no-deps
pip install pandas numpy yfinance pandas-ta dash plotly dash-bootstrap-components scipy requests alpha-vantage python-dotenv pyyaml python-dateutil
```

### Step 2: Run Your First Analysis
```bash
python main.py analyze
```

Expected output:
```
====================================================
INSTITUTIONAL RO/RO MONITOR - ANALYSIS
====================================================

Fetching market data and calculating regime...

Master Score: 67.3/100
Regime: MODERATE_RISK_ON
Conviction: MEDIUM

Summary: Markets in moderate risk-on mode. Conviction level: MEDIUM

--- Pillar Scores ---
Pillar A: Price Trend & Momentum: 72.1 (Slightly Bullish)
Pillar B: Market Breadth & Health: 65.8 (Slightly Bullish)
Pillar C: Macro-Fundamental Drivers: 58.2 (NEUTRAL)
Pillar D: Currency & Carry Trade: 71.5 (BULLISH)
Pillar E: Sentiment & Positioning: 63.0 (Slightly Bullish)

--- CFD Positioning Recommendations ---
SPY    | BUY          | Sizing:  +75% | Large Cap US Equities
QQQ    | BUY          | Sizing:  +35% | Tech-heavy Nasdaq
TLT    | NEUTRAL      | Sizing:    0% | Long-term Treasuries

Net Equity Exposure: +110% | Risk Bias: LONG
```

### Step 3: Launch the Dashboard
```bash
python main.py dashboard
```

Open browser to: **http://localhost:8050**

You'll see:
- 🎯 **Master Regime Gauge**: Real-time score (0-100)
- 📊 **Pillar Breakdown**: Individual component scores
- 📈 **Score History**: 30-day regime timeline
- 🔥 **Heatmap**: Multi-asset performance
- 💼 **CFD Positioning**: Dynamic recommendations
- 🔔 **Alerts**: Live regime warnings

---

## 30-Second Test

```bash
# Quick validation (no dependencies needed)
python -c "print('RO/RO Monitor structure: '); import os; os.system('find roro_monitor -name \"*.py\" | wc -l')"
```

Should show: **28 files** ✓

---

## Usage Modes

### 1. Dashboard Mode (Interactive)
```bash
python main.py dashboard
```
- Real-time regime monitoring
- Interactive charts and gauges
- Auto-refresh capability
- Alert notifications

### 2. Analysis Mode (Command-Line)
```bash
python main.py analyze
```
- One-time regime calculation
- Console output
- Quick market snapshot
- CFD recommendations

### 3. Backtest Mode (Historical)
```bash
python main.py backtest
```
- Historical validation
- Performance metrics
- Signal quality analysis
- Exports to CSV

---

## Configuration

### Adjust Pillar Weights
Edit `roro_monitor/config/settings.py`:

```python
PILLAR_WEIGHTS = {
    'pillar_a': 0.35,  # Increase trend weight
    'pillar_b': 0.25,
    'pillar_c': 0.20,  # Decrease macro weight
    'pillar_d': 0.10,
    'pillar_e': 0.10,
}
```

### Change Regime Thresholds
```python
REGIME_THRESHOLDS = {
    'STRONG_RISK_ON': (75, 100),    # More conservative
    'MODERATE_RISK_ON': (55, 74),
    'NEUTRAL': (45, 54),
    'MODERATE_RISK_OFF': (25, 44),
    'STRONG_RISK_OFF': (0, 24),
}
```

### Add/Remove Assets
Edit `roro_monitor/config/tickers.py`:

```python
EQUITIES_RISK = AssetClass(
    name="Equities (Risk)",
    tickers=["SPY", "QQQ", "IWM", "EEM", "VTI"],  # Added VTI
    purpose="Core Risk Assets"
)
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'pandas'"
**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "TA-Lib installation failed"
**Solution**: Skip TA-Lib or install system package
```bash
# Skip TA-Lib (optional dependency)
grep -v "ta-lib" requirements.txt > requirements_no_talib.txt
pip install -r requirements_no_talib.txt
```

### Issue: Dashboard shows "Error fetching data"
**Solution**: Check internet connection (Yahoo Finance API access)
```bash
# Test connectivity
python -c "import yfinance as yf; print(yf.Ticker('SPY').history(period='5d'))"
```

### Issue: Cache directory errors
**Solution**: Create cache directory
```bash
mkdir -p .cache
```

---

## Next Steps

1. ✅ **Run analysis** to see current regime
2. ✅ **Launch dashboard** for interactive monitoring
3. ✅ **Run backtest** to validate performance
4. ✅ **Customize settings** to match your strategy
5. ✅ **Set up alerts** (future: email/SMS)

---

## Support & Documentation

- **Full Documentation**: See `README.md`
- **Strategic Blueprint**: Reference the original plan
- **Code Structure**: Browse `roro_monitor/` modules

---

## Example Workflow

```bash
# Morning routine
python main.py analyze          # Quick regime check

# Deep dive
python main.py dashboard        # Interactive analysis
# Open http://localhost:8050

# Weekly validation
python main.py backtest         # Performance review
```

---

**Ready to monitor institutional risk flows!** 🎯📊

For questions: Open an issue or review the comprehensive `README.md`
