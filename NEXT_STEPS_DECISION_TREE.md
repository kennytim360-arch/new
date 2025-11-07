# Next Steps Decision Tree - Post V4 Backtest

**Created:** November 7, 2025
**Purpose:** Guide decision-making based on v4 backtest results

---

## 🧪 Step 1: Run V4 Validation

### Commands to Execute

```powershell
# 1. Pull v4 code
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w

# 2. Clear Python cache (CRITICAL!)
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force

# 3. Run backtest
python main.py backtest

# 4. Run validation analysis
python V4_VALIDATION.py
```

---

## 🎯 Step 2: Evaluate Results (Decision Points)

### Decision Point A: MODERATE_RISK_OFF Performance

**v4 Fix Target:** -1.618% → 0% to +0.5%

#### ✅ **If MODERATE_RISK_OFF is now positive (0% to +0.5%):**
- **Conclusion:** v4 fix worked! Risk-Off allocation is correct
- **Action:** Proceed to Decision Point B

#### ⚠️ **If MODERATE_RISK_OFF is still slightly negative (-0.5% to 0%):**
- **Conclusion:** Improvement but not perfect
- **Action:** Consider removing ALL shorts (even in STRONG_RISK_OFF)
- **Next:** Test v4.1 with 0% shorts everywhere

#### ❌ **If MODERATE_RISK_OFF is still catastrophic (<-0.5%):**
- **Conclusion:** Fundamental issue with Risk-Off signals
- **Action:** Skip to Step 3 - Consider 3-Pillar Approach

---

### Decision Point B: Overall Success Criteria

**Target:** 5/6 or 6/6 institutional tests passed

#### ✅ **If 5/6 or 6/6 criteria met:**
- **Conclusion:** Strategy is institutional-grade!
- **Action:** Proceed to Step 4 - Fine-Tuning & Deployment

#### ⚠️ **If 4/6 criteria met (same as v3):**
- **Conclusion:** v4 didn't improve overall performance
- **Action:** Analyze which criteria failed, proceed to Step 3

#### ❌ **If <4/6 criteria met:**
- **Conclusion:** Strategy getting worse, not better
- **Action:** Proceed to Step 3 - Pivot to 3-Pillar Approach

---

### Decision Point C: Max Drawdown

**Target:** <-12% (was -16.88% in v3)

#### ✅ **If Max DD <-12%:**
- **Conclusion:** Risk management working
- **Action:** Proceed to Decision Point D

#### ⚠️ **If Max DD -12% to -15%:**
- **Conclusion:** Improved but not enough
- **Action:** Investigate non-Risk-Off sources of losses
- **Diagnostic:** Run `python Q4_SIGNAL_DIAGNOSTIC.py` to find other issues

#### ❌ **If Max DD >-15%:**
- **Conclusion:** Risk management failing
- **Action:** Reduce leverage in Risk-On regimes OR pivot to 3-Pillar

---

### Decision Point D: Q4 Signal Quality

**Target:** Q4 returns > Q3 returns (signal quality fixed)

#### ✅ **If Q4 > Q3:**
- **Conclusion:** Extreme signal handling working
- **Action:** Strategy fundamentals are sound

#### ❌ **If Q4 < Q3:**
- **Conclusion:** Still have signal inversion at extremes
- **Action:** Consider increasing Q4 reduction from 50% to 70%
- **Alternative:** Disable positions entirely for scores >85

---

## 📊 Step 3: Pathway Decision Based on Results

### Pathway A: **Continue with 5-Pillar System** ✅

**Choose this if:**
- ✅ MODERATE_RISK_OFF is now positive
- ✅ Max DD improved to <-13%
- ✅ At least 4/6 criteria met
- ✅ Clear path to improvement visible

**Next Actions:**
1. Fine-tune remaining issues (Q4, upside capture, etc.)
2. Implement v4.1 micro-adjustments
3. Run another backtest iteration
4. Target: 6/6 criteria met

**v4.1 Potential Adjustments:**
- Increase Q4 reduction: 50% → 70%
- Adjust Risk-On leverage: 145-185% → 160-200%
- Tighten regime persistence: 5 days → 7 days
- Optimize pillar weights based on Q4 diagnostic

---

### Pathway B: **Pivot to 3-Pillar Simplified System** 🔄

**Choose this if:**
- ❌ v4 didn't improve MODERATE_RISK_OFF (<-0.5% still)
- ❌ Success criteria still 4/6 or worse
- ❌ Max DD not improved or got worse
- ❌ Q4 signal quality still failing
- ❌ Spending too much time debugging complex system

**Next Actions:**
1. **Prototype the 3-Pillar system** (already prepared: `SIMPLE_3PILLAR_PROTOTYPE.py`)
2. **Backtest the simplified approach**
3. **Compare 5-pillar vs 3-pillar performance**
4. **Deploy whichever performs better**

**3-Pillar System Benefits:**
- ✅ Uses institutional-grade LEADING indicators
- ✅ Simpler to understand and execute
- ✅ Less prone to overfitting
- ✅ Clear binary output (Risk-On vs Risk-Off)
- ✅ Faster iteration cycles

**3-Pillar Components:**
1. **Market Breadth** (NYSE A/D Line) - The truth teller
2. **Credit Spreads** (HYG/TLT) - The crystal ball (leads equities)
3. **Volatility Structure** (VIX term structure) - The fear gauge

---

### Pathway C: **Hybrid Approach** 🔀

**Choose this if:**
- ⚠️ 5-pillar shows promise but incomplete
- ⚠️ Want best of both worlds
- ⚠️ Willing to invest more time

**Next Actions:**
1. **Extract best pillars from 5-pillar system**
   - Pillar A (Price Trend): Keep momentum components
   - Pillar B (Market Breadth): Already in 3-pillar
   - Pillar C (Macro): Use credit spreads (already in 3-pillar)

2. **Build 4-Pillar Hybrid:**
   - Market Breadth (NYSE A/D)
   - Credit Spreads (HYG/TLT)
   - Volatility Structure (VIX)
   - Price Momentum (SPY 50/200 MA, MACD)

3. **Simplify regime structure:**
   - Only 3 regimes: RISK-ON, NEUTRAL, RISK-OFF
   - Clear thresholds: >65 = Risk-On, 35-65 = Neutral, <35 = Risk-Off

---

## 🛠️ Step 4: Fine-Tuning (If v4 Success)

### If v4 met 5/6 criteria, implement micro-adjustments:

#### **Adjustment A: Optimize Upside Capture** (if <70%)
```python
# Increase Risk-On sizing
if score >= 80:
    spy_sizing = 110  # Was 100
    qqq_sizing = 55   # Was 50
    # Net: 200% long (more aggressive)
```

#### **Adjustment B: Perfect Q4 Handling** (if Q4 still underperforming)
```python
# Increase Q4 reduction
if score > 75:
    q4_multiplier = 0.3  # Was 0.5 (70% reduction instead of 50%)

# OR disable extreme signals entirely
if score > 85:
    spy_sizing = 0  # No positions at extreme overbought
```

#### **Adjustment C: Optimize Sharpe Ratio** (if <1.0)
```python
# Reduce volatility via tighter stops or less leverage
# OR increase returns via better timing (hysteresis tuning)
```

---

## 📈 Step 5: Deployment Readiness Checklist

### Before deploying strategy live, verify:

**Performance Criteria:**
- ✅ Success criteria: 5/6 or better
- ✅ Sharpe ratio: >1.0
- ✅ Max drawdown: <-12%
- ✅ Upside capture: >70%
- ✅ Downside capture: <40%
- ✅ Q4 > Q3 (signal quality validated)

**Operational Criteria:**
- ✅ Code tested and validated
- ✅ Clear execution rules documented
- ✅ Risk management parameters defined
- ✅ Position sizing logic verified
- ✅ Regime change alerts working
- ✅ Daily monitoring process established

**Risk Management:**
- ✅ Maximum position size: 200% long, 30% short
- ✅ Stop-loss rules defined (if applicable)
- ✅ Emergency exit procedures documented
- ✅ Drawdown limits set (-15% max before pause)

---

## 🚀 Recommended Path Forward

### **If v4 Results Show:**

| MODERATE_RISK_OFF | Max DD | Criteria | Recommended Path |
|-------------------|--------|----------|------------------|
| ✅ Positive (0-0.5%) | ✅ <-12% | ✅ 5/6+ | **Deploy v4** or fine-tune to v4.1 |
| ⚠️ Near 0% (-0.3-0.3%) | ⚠️ -12 to -14% | ⚠️ 4/6 | **Fine-tune v4.1** → test again |
| ❌ Negative (<-0.5%) | ❌ >-14% | ❌ 3/6 | **Pivot to 3-Pillar** system |

---

## 🎯 Success Definitions

### **Institutional Grade (Ready for Deployment):**
- Success Criteria: 5/6 or 6/6 ✅
- Sharpe: >1.0 ✅
- Max DD: <-12% ✅
- Alpha: >5% ✅

### **Acceptable (Fine-tune before deploy):**
- Success Criteria: 4/6 ⚠️
- Sharpe: 0.8-1.0 ⚠️
- Max DD: -12% to -15% ⚠️
- Clear improvement path visible

### **Needs Rethink (Pivot to 3-Pillar):**
- Success Criteria: <4/6 ❌
- No improvement from v3 ❌
- Spending >3 iterations without progress ❌
- Simpler approach likely better

---

## 📋 Quick Decision Matrix

```
┌─────────────────────────────────────────────────────────────────┐
│                  V4 BACKTEST DECISION TREE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─── Is MODERATE_RISK_OFF now positive? ───┐                 │
│  │                                            │                 │
│  YES                                         NO                 │
│  │                                            │                 │
│  ├─── Are 5/6 criteria met? ───┐            │                 │
│  │                               │            │                 │
│  YES                            NO           │                 │
│  │                               │            │                 │
│  ✅ DEPLOY V4                  ⚠️ V4.1       ❌ PIVOT          │
│  (Institutional                (Fine-tune)   (3-Pillar)        │
│   Grade!)                                                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📞 What to Report Back

### After running v4 backtest, share:

**Critical Metrics:**
1. **MODERATE_RISK_OFF returns:** ??? % (target: 0-0.5%)
2. **Max Drawdown:** ??? % (target: <-12%)
3. **Success Criteria:** ???/6 (target: 5/6)
4. **Q4 vs Q3:** Q4 ??? % vs Q3 ??? % (target: Q4 > Q3)

**Secondary Metrics:**
5. Sharpe Ratio: ??? (target: >1.0)
6. Upside Capture: ??? % (target: >70%)
7. Regime Changes: ??? (target: <12)

**Then we'll make the call:**
- ✅ **Deploy v4** if institutional grade
- ⚠️ **Fine-tune v4.1** if close
- 🔄 **Pivot to 3-Pillar** if not improving

---

**End of Decision Tree**
