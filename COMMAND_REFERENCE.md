# 📋 V4 Testing - Command Reference Card

**Version:** v4.0 | **Date:** November 7, 2025

---

## 🚀 **TESTING COMMANDS (Copy & Paste)**

### Windows PowerShell:
```powershell
# Step 1: Pull latest code
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Step 2: Clear Python cache (CRITICAL!)
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse; Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# Step 3: Run backtest
python main.py backtest

# Step 4: Run validation
python V4_VALIDATION.py

# Step 5: Optional diagnostics
python Q4_SIGNAL_DIAGNOSTIC.py
python SIMPLE_3PILLAR_PROTOTYPE.py
```

### Linux/Mac:
```bash
# Step 1: Pull latest code
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# Step 2: Clear Python cache (CRITICAL!)
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -name "*.pyc" -delete

# Step 3: Run backtest
python main.py backtest

# Step 4: Run validation
python V4_VALIDATION.py
```

---

## 📊 **EXPECTED V4 RESULTS**

| Metric | v3 Result | v4 Target | Status |
|--------|-----------|-----------|--------|
| MODERATE_RISK_OFF | -1.618% | 0-0.5% | ❓ |
| Max Drawdown | -16.88% | <-12% | ❓ |
| Success Criteria | 4/6 | 5/6 | ❓ |
| Sharpe Ratio | 0.728 | >0.9 | ❓ |

---

## 🔀 **DECISION MATRIX**

```
V4_VALIDATION.py verdict:

✅ V4 IS A SUCCESS!
   → Deploy v4 immediately

⚠️  V4 SHOWS IMPROVEMENT BUT NOT THERE YET
   → Fine-tune v4.1 (one more iteration)

❌ V4 STILL HAS MAJOR ISSUES
   → Pivot to 3-pillar simplified system
```

---

## 🐛 **QUICK TROUBLESHOOTING**

**Problem:** Results identical to v3
**Fix:** Clear cache again, restart terminal

**Problem:** Import errors
**Fix:** Activate venv: `.venv\Scripts\Activate.ps1`

**Problem:** Data fetch failures
**Fix:** Check internet, retry backtest

**Problem:** V4_VALIDATION.py not found
**Fix:** Ensure you pulled latest code (step 1)

---

## 📁 **KEY FILES REFERENCE**

**Documentation:**
- `QUICK_START.md` - Ultra-concise 5 commands
- `TESTING_GUIDE.md` - Complete walkthrough
- `CURRENT_STATUS.md` - Current state summary
- `NEXT_STEPS_DECISION_TREE.md` - Strategic pathways

**Tools:**
- `V4_VALIDATION.py` - Automated verdict
- `Q4_SIGNAL_DIAGNOSTIC.py` - Signal analysis
- `SIMPLE_3PILLAR_PROTOTYPE.py` - Backup system

**Technical:**
- `V4_RISK_OFF_OVERHAUL.md` - v4 explained
- `V3_SIGNAL_QUALITY_FIXES.md` - v3 explained

---

## 💡 **KEY V4 CHANGE**

**MODERATE_RISK_OFF:**
- **OLD:** -30% short equities
- **NEW:** 0% equities (cash + bonds)
- **Why:** Defense via bonds, not speculation

**Expected Impact:** -1.618% → +0.5% = **+2.1% improvement**

---

## 📞 **WHAT TO SHARE**

**Minimum:**
```
From V4_VALIDATION.py:

FINAL VERDICT: [✅/⚠️/❌]

KEY METRICS:
- MODERATE_RISK_OFF: ???%
- Max Drawdown: ???%
- Success Criteria: ???/6
- Sharpe Ratio: ???
```

**Ideal:** Full V4_VALIDATION.py output

---

## ⚠️ **CRITICAL REMINDER**

**ALWAYS clear Python cache before testing!**

Old bytecode from v3 = wrong results

Use Step 2 commands every time.

---

## 🎯 **CONFIDENCE: 85%+**

Why v4 will likely succeed:
1. Root cause identified (MODERATE_RISK_OFF shorts)
2. Fix is simple (0% vs -30%)
3. Impact is clear (-9.7% drag eliminated)
4. Philosophy is sound (defense ≠ speculation)
5. Other components working (9 regime changes)

---

**Branch:** `claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w`
**Latest Commit:** `f97bfa5`
**Status:** Ready for Testing
