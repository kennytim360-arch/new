# 🎯 RO/RO Monitor - Installation Guide

## ⚡ Quick Start (3 Commands)

```bash
# 1. Fix all issues
python FINAL_SETUP.py

# 2. Install dependencies  
pip install -r requirements.txt

# 3. Run the monitor
python main.py analyze
```

**That's it!** You'll get:
- Live regime score (0-100)
- 5 pillar analysis
- CFD recommendations
- Market alerts

---

## 📋 What You'll See

```
Master Score: 67.3/100
Regime: MODERATE_RISK_ON
Conviction: MEDIUM

Pillar Scores:
  A: Price Trend & Momentum: 72.1 (Slightly Bullish)
  B: Market Breadth: 65.8
  C: Macro Fundamentals: 58.2
  D: Currency Carry: 71.5 (BULLISH)
  E: Sentiment: 63.0

CFD Recommendations:
  SPY | BUY | +75% | Large Cap US Equities
  QQQ | BUY | +35% | Tech-heavy Nasdaq
  TLT | NEUTRAL | 0%

Net Exposure: +110% LONG
```

---

## 🚀 After Installation

### Console Analysis (Recommended)
```bash
python main.py analyze
```
- Fast
- Clear output
- Live regime score
- Position recommendations

### Web Dashboard
```bash
python main.py dashboard
```
Then open: **http://localhost:8050**
- Interactive charts
- Real-time updates
- Visual gauges
- Heatmaps

### Historical Backtest
```bash
python main.py backtest
```
- Tests strategy on historical data
- Performance metrics
- Exports to CSV

---

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"

**Fix:**
```bash
pip install -r requirements.txt
```

### "cannot import name 'run_dashboard'"

**Fix:**
```bash
python FINAL_SETUP.py
```

### Network errors when fetching data

**Causes:**
- No internet connection
- Yahoo Finance down
- Firewall blocking Python

**Fix:**
- Check internet
- Try again in a few minutes
- Check firewall settings

---

## 📁 Files Explained

| File | Purpose |
|------|---------|
| `FINAL_SETUP.py` | **⭐ Run this first** - Fixes everything |
| `install_data_module.py` | Creates missing data files |
| `main.py` | Main application |
| `requirements.txt` | Python dependencies |
| `SIMPLE_INSTALL.txt` | Text instructions |

---

## ✅ Verification

System is working when:

1. ✅ `python FINAL_SETUP.py` shows "SYSTEM READY TO RUN"
2. ✅ `python main.py analyze` fetches data without errors
3. ✅ You see a Master Score between 0-100
4. ✅ CFD recommendations are displayed

---

## 🎓 What It Does

The RO/RO Monitor analyzes 5 dimensions of market conditions:

1. **Price Trend & Momentum (30%)** - Moving averages, RSI, MACD
2. **Market Breadth (25%)** - Sector rotation, leadership
3. **Macro Fundamentals (25%)** - Credit spreads, VIX, safe havens
4. **Currency Carry (10%)** - JPY crosses, risk currencies
5. **Sentiment (10%)** - VIX levels, positioning

Combines them into:
- **Master Score (0-100)** - Overall risk appetite
- **Regime** - STRONG_RISK_ON → NEUTRAL → STRONG_RISK_OFF  
- **Conviction** - HIGH, MEDIUM, or LOW
- **CFD Positions** - Specific recommendations with sizing

---

## 🌐 Data Sources

- **Yahoo Finance** - All price data
- **Real-time** - Live market feeds
- **Free** - No API keys needed
- **Reliable** - Institutional-grade data

---

## 💡 Tips

- Run `python main.py analyze` daily for regime updates
- Use dashboard for deeper analysis
- Adjust position sizing based on conviction level
- Pay attention to regime changes (alerts)

---

## 🚀 Ready to Start?

```bash
python FINAL_SETUP.py
pip install -r requirements.txt  
python main.py analyze
```

You'll have a working institutional-grade RO/RO monitor in under 2 minutes!

---

**Questions?** Check `SIMPLE_INSTALL.txt` for text-only instructions.
