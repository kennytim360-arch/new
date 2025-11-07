# Complete Setup and Verification Guide

## Step 1: Fix All Issues

```bash
python FIX_ALL_ISSUES.py
```

This will:
- Fix dashboard exports
- Verify all configuration
- Test all imports
- Report any remaining issues

**Expected output:** "SUCCESS! All imports working"

---

## Step 2: Install Dependencies (if not already done)

```bash
pip install -r requirements.txt
```

**Note:** If TA-Lib fails, you can skip it:
```bash
pip install pandas numpy yfinance dash plotly dash-bootstrap-components scipy requests python-dotenv pyyaml python-dateutil
```

---

## Step 3: Test the System

```bash
python TEST_SYSTEM.py
```

This will:
- Import all modules
- Initialize engines
- Fetch REAL market data
- Calculate current regime
- Generate positioning recommendations
- Display alerts

**This is a full end-to-end test with live data!**

---

## Step 4: Run the Monitor

Once TEST_SYSTEM.py succeeds, you can run:

### Console Analysis
```bash
python main.py analyze
```

### Interactive Dashboard
```bash
python main.py dashboard
```
Then open: http://localhost:8050

### Historical Backtest
```bash
python main.py backtest
```

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'pandas'"
**Fix:** `pip install -r requirements.txt`

### "cannot import name 'run_dashboard'"
**Fix:** `python FIX_ALL_ISSUES.py`

### "DATA_CACHE_HOURS" not found
**Fix:** `python FIX_ALL_ISSUES.py`

### Network errors when fetching data
- Check internet connection
- Verify Yahoo Finance is accessible
- Check firewall settings

---

## What Each Script Does

| Script | Purpose |
|--------|---------|
| `install_data_module.py` | Creates missing data module files |
| `FIX_ALL_ISSUES.py` | Fixes all import/export issues |
| `TEST_SYSTEM.py` | Full end-to-end test with real data |
| `main.py analyze` | Production regime analysis |
| `main.py dashboard` | Web-based monitoring dashboard |
| `main.py backtest` | Historical validation |

---

## Success Criteria

✅ **FIX_ALL_ISSUES.py** shows "SUCCESS! All imports working"
✅ **TEST_SYSTEM.py** calculates a regime score (0-100)
✅ **TEST_SYSTEM.py** generates CFD recommendations
✅ **main.py analyze** runs without errors

Once all four pass, the system is fully operational!
