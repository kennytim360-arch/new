# 🔧 V4 Testing - Troubleshooting Guide

**Quick reference for common issues during v4 testing**

---

## 🚨 Issue #1: Results Identical to v3

**Symptoms:**
- Backtest shows exact same numbers as before
- MODERATE_RISK_OFF still shows -1.618%
- Success criteria still 4/6

**Root Cause:** Python cache not properly cleared

**Solution:**
```powershell
# Force clear cache
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# Verify cache is cleared
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force
# Should return nothing

# Exit Python if it's running
exit()

# Re-run backtest
python main.py backtest
```

**Prevention:** Always clear cache before every backtest run.

---

## 🚨 Issue #2: Import Errors / ModuleNotFoundError

**Symptoms:**
```
ModuleNotFoundError: No module named 'yfinance'
ImportError: cannot import name 'RegimeEngine'
```

**Root Cause:** Virtual environment not activated or dependencies missing

**Solution:**

**Windows:**
```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Verify activation (should show (.venv) in prompt)
python --version

# Reinstall dependencies if needed
pip install -r requirements.txt

# Retry
python main.py backtest
```

**Linux/Mac:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Retry
python main.py backtest
```

**Prevention:** Always activate venv before running commands.

---

## 🚨 Issue #3: Data Fetch Failures

**Symptoms:**
```
Failed to fetch data for ticker SPY
HTTP Error 404: Not Found
possibly delisted; no price data found
```

**Root Cause:** Yahoo Finance API issues or network problems

**Solution:**

**Step 1: Check internet connection**
```powershell
ping google.com
ping finance.yahoo.com
```

**Step 2: Retry with fresh data**
```powershell
python main.py backtest --fresh
```

**Step 3: Check ticker list**
```powershell
# Edit roro_monitor/config/tickers.py
# Remove any delisted tickers
```

**Step 4: Use longer timeout**
```python
# In roro_monitor/data/fetcher.py
# Increase timeout parameter if needed
```

**Prevention:** Yahoo Finance is free but can be flaky. If persistent issues, consider paid data provider.

---

## 🚨 Issue #4: V4_VALIDATION.py Says "No CSV Found"

**Symptoms:**
```
❌ No backtest CSV files found!
Run: python main.py backtest
```

**Root Cause:** Backtest didn't complete successfully or CSV not generated

**Solution:**

**Step 1: Check for CSV files**
```powershell
Get-ChildItem -Filter "backtest_results_*.csv"
```

**Step 2: If none exist, check backtest errors**
```powershell
# Run backtest with error logging
python main.py backtest 2>&1 | Tee-Object -FilePath backtest_log.txt

# Review log
Get-Content backtest_log.txt
```

**Step 3: Check common errors**
- Import errors? → See Issue #2
- Data fetch failures? → See Issue #3
- Memory errors? → Close other applications

**Prevention:** Always verify backtest completed successfully before running validation.

---

## 🚨 Issue #5: Backtest Takes Forever (>5 minutes)

**Symptoms:**
- Backtest running for more than 5-10 minutes
- No output or progress indicators
- Python process consuming high CPU

**Root Cause:** Network timeouts, infinite loops, or data issues

**Solution:**

**Step 1: Kill the process**
```powershell
# Press Ctrl+C to stop
# Or close the terminal
```

**Step 2: Check network**
```powershell
ping finance.yahoo.com
# Should respond in <100ms
```

**Step 3: Run with shorter period**
```python
# Temporarily edit main.py backtest command
# Change period='1y' to period='3mo' for testing
```

**Step 4: Check for infinite loops**
```powershell
# Enable debug logging
# Edit main.py to add verbose output
```

**Prevention:** Backtest should complete in 2-3 minutes for 1 year of data.

---

## 🚨 Issue #6: Git Pull Fails

**Symptoms:**
```
fatal: unable to access
remote: Proxy error
Error 502: Service Unavailable
```

**Root Cause:** Temporary network or git proxy issues

**Solution:**

**Step 1: Retry with exponential backoff**
```powershell
# Retry 1 (wait 2 seconds)
Start-Sleep -Seconds 2
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Retry 2 (wait 4 seconds)
Start-Sleep -Seconds 4
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Retry 3 (wait 8 seconds)
Start-Sleep -Seconds 8
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w
```

**Step 2: Check if you're already up to date**
```powershell
git log --oneline -1
# Should show: f97bfa5 docs: Add complete delivery inventory and final summary
```

**Prevention:** Git proxy errors are usually temporary. Wait and retry.

---

## 🚨 Issue #7: Validation Shows "Worse Than v3"

**Symptoms:**
- V4_VALIDATION.py says "❌ V4 STILL HAS MAJOR ISSUES"
- Metrics worse than v3
- MODERATE_RISK_OFF still negative

**Root Cause:** Either cache not cleared OR v4 genuinely failed

**Solution:**

**Step 1: Verify cache was cleared**
```powershell
# Look for any __pycache__ directories
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force

# Should return NOTHING
# If it returns directories, clear again
```

**Step 2: Verify latest code**
```powershell
git log --oneline -1
# Must show: f97bfa5 or later
```

**Step 3: Check positioning.py directly**
```powershell
# Check line 129-140 in positioning.py
# Should show:
# elif score >= 20:
#     # MODERATE RISK-OFF - GO TO CASH/DEFENSIVE (v4 CRITICAL FIX!)
#     spy_sizing = 0
#     qqq_sizing = 0
```

**Step 4: If everything is correct and results still bad**
→ V4 genuinely failed - Pivot to 3-pillar system
```powershell
python SIMPLE_3PILLAR_PROTOTYPE.py
```

**Prevention:** Always verify cache clearing worked before running backtest.

---

## 🚨 Issue #8: Results Look Suspicious

**Symptoms:**
- Numbers seem unrealistic (e.g., 500% returns)
- Negative scores or impossible values
- Validation throws errors

**Root Cause:** Data quality issues or calculation bugs

**Solution:**

**Step 1: Check backtest CSV manually**
```powershell
# Open CSV in Excel or text editor
Get-Content backtest_results_*.csv | Select-Object -First 10

# Verify columns and values look reasonable
```

**Step 2: Check score range**
```powershell
# Scores should be 0-100
# Check in CSV: score column should be in this range
```

**Step 3: Re-run with fresh data**
```powershell
# Delete any cached data
Remove-Item -Path "data_cache.pkl" -ErrorAction SilentlyContinue

# Re-run backtest
python main.py backtest
```

**Prevention:** Validate data quality before analysis.

---

## 🚨 Issue #9: Can't Find Documentation

**Symptoms:**
- "Which file should I read?"
- "Where is the testing guide?"
- "How do I know what to do next?"

**Solution:**

**Start here:**
1. `QUICK_START.md` - 5 commands (fastest)
2. `TESTING_GUIDE.md` - Complete walkthrough
3. `COMMAND_REFERENCE.md` - Quick reference card

**For decisions:**
- `NEXT_STEPS_DECISION_TREE.md` - What to do after results

**For understanding:**
- `CURRENT_STATUS.md` - Current state
- `V4_RISK_OFF_OVERHAUL.md` - What v4 changed
- `DELIVERY_COMPLETE.md` - Full inventory

**Prevention:** Start with QUICK_START.md, read others as needed.

---

## 🚨 Issue #10: Unsure Which Path to Take

**Symptoms:**
- Backtest complete but confused about next steps
- Unclear if results are good or bad
- Don't know whether to deploy, iterate, or pivot

**Solution:**

**Trust V4_VALIDATION.py - it will tell you exactly what to do:**

```
✅ V4 IS A SUCCESS!
   → Deploy v4
   → You're done!

⚠️  V4 SHOWS IMPROVEMENT BUT NOT THERE YET
   → Fine-tune v4.1
   → One more iteration

❌ V4 STILL HAS MAJOR ISSUES
   → Pivot to 3-pillar
   → Simpler approach
```

**If still unsure, share these 4 numbers:**
1. MODERATE_RISK_OFF: ???%
2. Max Drawdown: ???%
3. Success Criteria: ???/6
4. Sharpe Ratio: ???

**Prevention:** Always run V4_VALIDATION.py - don't try to interpret raw backtest output manually.

---

## 📋 **Troubleshooting Checklist**

Before asking for help, verify:

- [ ] Virtual environment activated
- [ ] Latest code pulled (commit f97bfa5 or later)
- [ ] Python cache completely cleared
- [ ] Internet connection working
- [ ] Backtest completed successfully
- [ ] CSV file exists
- [ ] Validation tool ran without errors

If all checked and still having issues, share:
1. Exact error message
2. Steps you took
3. Which issue number (from this guide) you tried
4. Results of troubleshooting steps

---

## 🆘 **Emergency Contact Points**

**For code issues:**
- Check git log: `git log --oneline -5`
- Verify file exists: `Get-Item <filename>`
- Check imports: `python -c "import roro_monitor"`

**For result interpretation:**
- Run: `python V4_VALIDATION.py`
- Read: `NEXT_STEPS_DECISION_TREE.md`
- Follow the verdict

**For strategic decisions:**
- Read: `CURRENT_STATUS.md`
- Review: `V4_RISK_OFF_OVERHAUL.md`
- Consider: `SIMPLE_3PILLAR_PROTOTYPE.py`

---

## ✅ **Quick Fixes Summary**

| Issue | Quick Fix |
|-------|-----------|
| Same results as v3 | Clear cache, restart |
| Import errors | Activate venv |
| Data fetch fails | Check internet, retry |
| No CSV found | Check backtest errors |
| Too slow | Check network, kill and retry |
| Git fails | Wait 2s, retry |
| Worse than v3 | Verify cache cleared |
| Suspicious results | Re-run with fresh data |
| Can't find docs | Start with QUICK_START.md |
| Unsure of path | Run V4_VALIDATION.py |

---

**Remember:** 90% of issues are from not clearing Python cache properly!

**Always run Step 2 from QUICK_START.md before every backtest.**

---

**Last Updated:** November 7, 2025
**Version:** v4.0
