# Quick Start - V4 Testing

**Just run these 5 commands:**

## Windows PowerShell

```powershell
# 1. Pull code
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# 2. Clear cache
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse; Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# 3. Run backtest
python main.py backtest

# 4. Run validation
python V4_VALIDATION.py

# 5. Follow the verdict
```

---

## Expected Result

**V4_VALIDATION.py will show:**

```
FINAL VERDICT
────────────────────────────────────────────────────────────
✅ V4 IS A SUCCESS! (Deploy v4)
⚠️  V4 SHOWS IMPROVEMENT BUT NOT THERE YET (Fine-tune v4.1)
❌ V4 STILL HAS MAJOR ISSUES (Pivot to 3-pillar)
```

**Share this output and we'll know what to do next!**

---

## Key Metrics to Check

1. **MODERATE_RISK_OFF:** Should be 0-0.5% (was -1.618%)
2. **Max Drawdown:** Should be <-12% (was -16.88%)
3. **Success Criteria:** Should be 5/6 (was 4/6)
4. **Sharpe Ratio:** Should be >0.9 (was 0.728)

---

## If Something Goes Wrong

**Results look identical to before?**
→ You didn't clear cache properly. Re-run command #2.

**Import errors?**
→ Activate virtual environment: `.venv\Scripts\Activate.ps1`

**Can't find CSV?**
→ Backtest failed. Check for errors in step #3.

---

**That's it! 5 commands and you're done.** 🚀

See `TESTING_GUIDE.md` for detailed explanations.
