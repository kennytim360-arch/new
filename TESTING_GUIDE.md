# V4 Testing Guide - Complete Walkthrough

**Date:** November 7, 2025
**Version:** v4.0
**Status:** Ready for Validation

---

## 📋 Pre-Flight Checklist

Before running the backtest, verify:

- [ ] You're on branch `claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w`
- [ ] All code is pulled from remote
- [ ] Python cache is cleared
- [ ] Virtual environment is activated
- [ ] All dependencies installed

---

## 🚀 Complete Testing Process

### Step 1: Environment Setup

```powershell
# Navigate to project directory
cd C:\Users\User\new\new

# Activate virtual environment
.venv\Scripts\Activate.ps1

# Verify you're in the right environment
python --version  # Should show Python 3.x
```

### Step 2: Pull Latest V4 Code

```powershell
# Check current branch
git branch

# Should show: * claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Pull latest changes
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Verify latest commit
git log --oneline -1

# Should show: fa2bf3b docs: Add CURRENT_STATUS summary document for v4 testing phase
```

### Step 3: Clear Python Cache (CRITICAL!)

**Why this matters:** Old cached bytecode from v3 will produce incorrect results!

```powershell
# Delete all __pycache__ directories
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse

# Delete all .pyc files
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# Verify cache is cleared
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force

# Should return nothing
```

### Step 4: Run Backtest

```powershell
# Run the backtest
python main.py backtest

# This will take 1-2 minutes and produce output like:
# - Fetching market data...
# - Calculating regime scores...
# - Running backtest...
# - Exporting results...
```

**Expected output file:** `backtest_results_YYYYMMDD_HHMMSS.csv`

### Step 5: Run Validation Analysis

```powershell
# Run automated validation
python V4_VALIDATION.py
```

**This tool will automatically:**
- ✅ Check MODERATE_RISK_OFF performance
- ✅ Analyze regime distribution
- ✅ Validate Q4 signal quality
- ✅ Calculate institutional metrics
- ✅ Provide pass/fail verdict
- ✅ Recommend next actions

### Step 6: Optional Deep Dive

```powershell
# Analyze Q4 signal quality specifically
python Q4_SIGNAL_DIAGNOSTIC.py

# Test the simplified 3-pillar backup
python SIMPLE_3PILLAR_PROTOTYPE.py
```

---

## 📊 What to Look For in Results

### Critical Metrics (Must Improve)

**1. MODERATE_RISK_OFF Performance**
```
v3 Result: -1.618% avg returns (CATASTROPHIC!)
v4 Target: 0% to +0.5% (PROTECTION)

Look for this section:
  MODERATE_RISK_OFF
    Occurrences: X
    Avg Return: ???%  ← Should be positive!
    Volatility: ???%
```

**2. Maximum Drawdown**
```
v3 Result: -16.88%
v4 Target: <-12%

Look for:
  Strategy Max Drawdown: ???%
  Benchmark Max Drawdown: -18.76%
```

**3. Success Criteria**
```
v3 Result: 4/6
v4 Target: 5/6 or 6/6

Look for:
  Success Criteria Met: ???/6

  Checklist:
    ✓/✗ MDD < Benchmark
    ✓/✗ Sharpe > 1.0
    ✓/✗ Calmar > 1.0
    ✓/✗ Beta < 1.0
    ✓/✗ Alpha > 0
    ✓/✗ Down Capture < 50%
```

### Secondary Metrics (Nice to Have)

**4. Regime Changes**
```
v3 Result: 9 (good!)
v4 Target: <10

Look for:
  Regime Changes: ???
```

**5. Q4 Signal Quality**
```
v3 Result: Q4 < Q3 (bad)
v4 Target: Q4 > Q3

Look for quartile breakdown:
  Q3 (50-75): ???% avg
  Q4 (75-100): ???% avg  ← Should be > Q3
```

---

## 🎯 Interpretation Guide

### Scenario A: Clear Success ✅

**If you see:**
- ✅ MODERATE_RISK_OFF: +0.2% (positive!)
- ✅ Max Drawdown: -10.5% (<-12%)
- ✅ Success Criteria: 5/6 or 6/6
- ✅ Sharpe: 1.15 (>1.0)

**Action:** 🎉 **Deploy v4!** You have an institutional-grade strategy!

**Next steps:**
1. Document final performance
2. Prepare for live testing
3. Optional: Fine-tune for 6/6 if at 5/6

---

### Scenario B: Close But Not There ⚠️

**If you see:**
- ⚠️ MODERATE_RISK_OFF: +0.1% (slightly positive)
- ⚠️ Max Drawdown: -13.2% (close to -12%)
- ⚠️ Success Criteria: 4/6 (no improvement)
- ⚠️ Sharpe: 0.85 (close to 1.0)

**Action:** **Fine-tune v4.1** - One more iteration

**Potential adjustments:**
1. Increase Q4 reduction: 50% → 70%
2. Adjust Risk-On leverage: 145-185% → 160-200%
3. Remove all shorts (even STRONG_RISK_OFF)
4. Tighten regime persistence: 5 → 7 days

---

### Scenario C: Need to Pivot ❌

**If you see:**
- ❌ MODERATE_RISK_OFF: -1.2% (still negative!)
- ❌ Max Drawdown: -17.5% (worse!)
- ❌ Success Criteria: 3/6 (worse)
- ❌ Sharpe: 0.65 (worse)

**Action:** **Pivot to 3-Pillar System**

**Why:** The 5-pillar system may be over-engineered and overfitting.

**Next steps:**
1. Run `python SIMPLE_3PILLAR_PROTOTYPE.py`
2. Compare results
3. Deploy whichever performs better

---

## 📋 Quick Decision Matrix

```
┌─────────────────────────────────────────────────────────────┐
│         IS MODERATE_RISK_OFF NOW POSITIVE?                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  YES (0% to +0.5%)           NO (<0%)                       │
│  │                           │                              │
│  ├─ Are 5/6 criteria met?   └─ Did any metrics improve?    │
│  │                              │                           │
│  YES        NO                 YES          NO              │
│  │          │                  │            │               │
│  ✅         ⚠️                 ⚠️           ❌              │
│  DEPLOY     V4.1               V4.1         PIVOT           │
│  V4         FIX                FIX          3-PILLAR        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Common Issues & Solutions

### Issue 1: Results Identical to v3

**Symptom:** Backtest shows exact same numbers as before

**Cause:** Python cache not cleared

**Solution:**
```powershell
# Force clear cache
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# Restart Python interpreter
exit()
python main.py backtest
```

### Issue 2: Import Errors

**Symptom:** `ModuleNotFoundError` or `ImportError`

**Cause:** Virtual environment not activated or dependencies missing

**Solution:**
```powershell
# Activate venv
.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt

# Retry
python main.py backtest
```

### Issue 3: Data Fetch Failures

**Symptom:** `Failed to fetch data for ticker...`

**Cause:** Yahoo Finance API issues or network problems

**Solution:**
```powershell
# Check internet connection
ping google.com

# Retry with fresh data
python main.py backtest --fresh

# If persistent, check ticker list in:
# roro_monitor/config/tickers.py
```

### Issue 4: CSV File Not Found for Validation

**Symptom:** `V4_VALIDATION.py` says "No backtest CSV files found"

**Cause:** Backtest didn't complete successfully

**Solution:**
```powershell
# Check for CSV files
Get-ChildItem -Filter "backtest_results_*.csv"

# If none exist, backtest failed - check error logs
python main.py backtest 2>&1 | Tee-Object -FilePath backtest_log.txt

# Review backtest_log.txt for errors
```

---

## 📝 What to Report Back

### Minimum Required Information

**Copy and paste this section from V4_VALIDATION.py output:**

```
FINAL VERDICT
────────────────────────────────────────────────────────────
✅/⚠️/❌ [VERDICT HERE]

KEY METRICS:
1. MODERATE_RISK_OFF: ???% (target: 0-0.5%)
2. Max Drawdown: ???% (target: <-12%)
3. Success Criteria: ???/6 (target: 5/6)
4. Sharpe Ratio: ??? (target: >1.0)
```

### Full Output (If Possible)

Share the entire `V4_VALIDATION.py` output for comprehensive analysis.

---

## 🎓 Understanding the Results

### What MODERATE_RISK_OFF Tells You

**If positive (0-0.5%):**
- ✅ v4 fix worked!
- ✅ Risk-Off now provides protection
- ✅ Bonds doing their job
- ✅ No more catastrophic short losses

**If still negative (<0%):**
- ❌ v4 fix didn't work
- ❌ Fundamental issue remains
- ❌ May need to pivot to simpler approach

### What Max Drawdown Tells You

**If <-12%:**
- ✅ Risk management working
- ✅ Fixed Risk-Off catastrophe
- ✅ Better capital preservation

**If >-15%:**
- ❌ Risk management failing
- ❌ Need to investigate other loss sources
- ❌ May need to reduce Risk-On leverage

### What Success Criteria Tell You

**If 5/6 or 6/6:**
- ✅ Institutional grade!
- ✅ Ready for deployment
- ✅ Strategy validated

**If 4/6:**
- ⚠️ Close but needs work
- ⚠️ Identify which criteria failed
- ⚠️ Implement targeted fixes

**If 3/6 or worse:**
- ❌ Major issues remain
- ❌ Consider simplification
- ❌ Pivot to 3-pillar likely best

---

## 🚀 After Testing - Next Steps

### Path A: Deploy v4 (If Successful)

**Checklist before live deployment:**
- [ ] Backtest validated (5/6 or 6/6)
- [ ] All metrics meet targets
- [ ] Code reviewed and tested
- [ ] Risk parameters documented
- [ ] Emergency procedures defined
- [ ] Monitoring dashboard configured
- [ ] Paper trading completed (optional)

### Path B: Fine-Tune v4.1 (If Close)

**Adjustment options:**
1. Q4 sizing: 50% → 70% reduction
2. Risk-On: Increase to 160-200%
3. Shorts: Remove entirely
4. Persistence: 5 → 7 days
5. Hysteresis: Widen buffers

### Path C: Pivot to 3-Pillar (If Failed)

**Implementation steps:**
1. Test `SIMPLE_3PILLAR_PROTOTYPE.py`
2. Backtest simplified approach
3. Compare 5-pillar vs 3-pillar
4. Deploy best performer

---

## 📚 Reference Documentation

**Quick links to documentation:**

1. **CURRENT_STATUS.md** - Current state summary
2. **NEXT_STEPS_DECISION_TREE.md** - Strategic pathways
3. **V4_RISK_OFF_OVERHAUL.md** - v4 changes explained
4. **V3_SIGNAL_QUALITY_FIXES.md** - v3 changes explained

**Tools:**
- `V4_VALIDATION.py` - Automated verdict
- `Q4_SIGNAL_DIAGNOSTIC.py` - Q4 analysis
- `SIMPLE_3PILLAR_PROTOTYPE.py` - Backup system

---

## ⚠️ Critical Reminders

1. **ALWAYS clear cache before testing**
   - Old bytecode = wrong results
   - Use commands provided above

2. **v4 core change is simple but powerful**
   - MODERATE_RISK_OFF: -30% → 0%
   - This single change should fix everything

3. **Be ready to pivot**
   - 5-pillar is complex
   - 3-pillar backup is ready
   - Both approaches are valid

4. **Trust the validation tool**
   - It will tell you exactly what to do
   - Clear verdict provided
   - Follow the recommendations

---

## 🎯 Expected Timeline

**Total testing time: ~10 minutes**

1. Environment setup: 2 min
2. Pull code + clear cache: 1 min
3. Run backtest: 2-3 min
4. Run validation: 1-2 min
5. Review results: 2-3 min
6. Decide next action: 1 min

---

## 📞 Need Help?

**If stuck, check:**
1. This guide (TESTING_GUIDE.md)
2. Current status (CURRENT_STATUS.md)
3. Decision tree (NEXT_STEPS_DECISION_TREE.md)

**Common questions:**

**Q: Backtest taking forever?**
A: Should take 2-3 minutes. If longer, check network or kill and restart.

**Q: Results look wrong?**
A: Did you clear cache? This is #1 cause of issues.

**Q: Which path should I take?**
A: Run V4_VALIDATION.py - it will tell you exactly what to do.

**Q: Should I pivot to 3-pillar?**
A: Only if v4 shows NO improvement. Try v4 first.

---

## ✅ Testing Checklist

**Before starting:**
- [ ] Virtual environment activated
- [ ] On correct git branch
- [ ] Latest code pulled
- [ ] Python cache cleared

**During testing:**
- [ ] Backtest completed successfully
- [ ] CSV file generated
- [ ] Validation tool ran
- [ ] Results documented

**After testing:**
- [ ] Verdict understood
- [ ] Next action identified
- [ ] Results shared (if needed)
- [ ] Decision made

---

**Good luck with testing!** 🚀

The v4 fix is simple but powerful - changing MODERATE_RISK_OFF from -30% shorts to 0% cash/bonds should transform the entire strategy.

**Run the 5 commands and share the V4_VALIDATION.py output!**

---

**Last Updated:** November 7, 2025
**Version:** v4.0 Testing Guide
**Status:** Ready for Validation
