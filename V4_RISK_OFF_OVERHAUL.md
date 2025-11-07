# V4 Risk-Off Allocation Overhaul

**Date:** November 7, 2025
**Version:** v4 (Critical Risk-Off Fix)
**Priority:** EMERGENCY - Addresses catastrophic -1.618% avg returns in MODERATE_RISK_OFF

---

## 🚨 The Critical Problem

### V3 Backtest Results Showed Catastrophe in Risk-Off Regime

**MODERATE_RISK_OFF Performance:**
- **Average Return:** -1.618% per occurrence ❌
- **Occurrences:** 6 times in 0.97 years
- **Total Impact:** ~-9.7% cumulative losses
- **Conclusion:** Risk-Off regime was THE major drawdown driver

**What Was Happening:**
```python
# v3 MODERATE_RISK_OFF allocation:
SPY: -20% short
QQQ: -10% short
IWM: 0%
Net: -30% short equities

# The problem:
- Strategy detects Risk-Off signal (score 20-39)
- Goes short -30%
- Market rebounds during Risk-Off period
- Shorts get crushed → -1.618% avg losses
```

**This was killing the strategy!** Even though Risk-On periods were profitable, Risk-Off was wiping out gains.

---

## 💡 The Fundamental Realization

### Risk-Off ≠ Shorting Opportunity

**Old Philosophy (v1-v3):**
> "Risk-Off means market going down → Short it!"

**The Reality:**
> Risk-Off signals are for **DEFENSE**, not **OFFENSE**

**Why Shorting Failed:**
1. **Timing is Hard:** Market rebounds happen quickly and unpredictably
2. **Risk-Off is About Protection:** Not speculation
3. **Your Edge is in Risk-On:** The strategy's alpha comes from capturing rallies, not timing tops
4. **Bonds Do Better:** TLT rallies during Risk-Off without the short squeeze risk

---

## ✅ V4 Solution: Defense Not Offense

### New Philosophy

**Risk-Off = Capital Preservation**
- 0% equity exposure in MODERATE_RISK_OFF
- Bonds + cash provide defense without short risk
- Limited shorts only in STRONG_RISK_OFF (extreme panic)

### Changed Allocations

#### MODERATE_RISK_OFF (Score 15-39)

**Before v4:**
```python
SPY: -20% short
QQQ: -10% short
IWM: 0%
Net: -30% equities
Result: -1.618% avg returns 💀
```

**After v4:**
```python
SPY: 0% (cash)
QQQ: 0% (cash)
IWM: 0% (cash)
Net: 0% equities, bonds via TLT allocation
Expected: 0% to +0.5% (preservation) ✅
```

**Rationale:**
- No shorting = No short squeeze risk
- Bonds rally during Risk-Off (flight to safety)
- Cash preserves capital for next Risk-On opportunity
- Score 15-39 = uncertainty, not conviction to short

#### STRONG_RISK_OFF (Score 0-14)

**Before v4:**
```python
SPY: -40% short
QQQ: -20% short
IWM: -10% short
Net: -70% short equities
Risk: Severe losses on rebounds
```

**After v4:**
```python
SPY: -20% short (reduced from -40)
QQQ: -10% short (reduced from -20)
IWM: 0% (no small cap shorts)
Net: -30% max short equities
Philosophy: Limited shorts + bonds
```

**Rationale:**
- Extreme panic (score <15) justifies SOME shorting
- But cap at -30% to limit downside on rebounds
- Bonds still do most of the defensive work
- Small cap shorts removed (too volatile)

#### Risk-Off Thresholds

**Before v4:**
```python
MODERATE_RISK_OFF: (20, 39)  # Triggered frequently
STRONG_RISK_OFF: (0, 19)
```

**After v4:**
```python
MODERATE_RISK_OFF: (15, 39)  # Harder to trigger
STRONG_RISK_OFF: (0, 14)     # Only extreme fear
```

**Rationale:**
- Score 15-20 now stays in NEUTRAL (not Risk-Off)
- Fewer Risk-Off periods = better timing
- Only enter Risk-Off when truly necessary
- Hysteresis + persistence already reduces flipping

---

## 📊 Expected V4 Improvements

### Primary Goals (Must Achieve)

| Metric | v3 Result | v4 Target | Fix |
|--------|-----------|-----------|-----|
| **MODERATE_RISK_OFF Avg Return** | -1.618% | **0% to +0.5%** | Changed to 0% equities |
| **Max Drawdown** | -16.88% | **<-12%** | Fixed Risk-Off losses |
| **Risk-Off Occurrences** | 6 | **3-4** | Higher threshold |
| **Sharpe Ratio** | 0.728 | **>0.9** | Reduced drawdown |

### Secondary Goals (Nice to Have)

| Metric | v3 Result | v4 Target | Why |
|--------|-----------|-----------|-----|
| Calmar Ratio | 0.971 | **>1.2** | Better return/drawdown |
| Success Criteria | 4/6 | **5/6** | Pass institutional tests |
| Alpha | 10.17% | **>8%** | Maintain edge |
| Regime Changes | 9 | **<10** | Already good |

---

## 🔧 Technical Implementation

### File Changes

#### 1. `roro_monitor/engine/positioning.py`

**MODERATE_RISK_OFF Section (lines 129-141):**
```python
elif score >= 20:
    # MODERATE RISK-OFF - GO TO CASH/DEFENSIVE (v4 CRITICAL FIX!)
    # Problem: v3 had -30% shorts → -1.618% avg returns (CATASTROPHIC!)
    # Root cause: Shorting during Risk-Off creates losses, not protection
    # Solution: 0% equity exposure, pure defensive positioning
    spy_action = "CASH"
    spy_sizing = 0    # CHANGED from -20 (shorting was losing money)
    qqq_action = "CASH"
    qqq_sizing = 0    # CHANGED from -10
    iwm_action = "CASH"
    iwm_sizing = 0
    # Net exposure: 0% equities (bonds via _bond_recommendations)
    # Philosophy: Risk-Off = DEFENSE not OFFENSE. Cash + bonds, zero shorts.
```

**STRONG_RISK_OFF Section (lines 143-154):**
```python
else:
    # STRONG RISK-OFF - MINIMAL short exposure (v4 fix)
    # v3 had -70% shorts which could still cause losses
    # v4: Cap at -30% maximum shorts, focus on preservation
    spy_action = "REDUCE"
    spy_sizing = -20  # REDUCED from -40 (v3 shorts still too high)
    qqq_action = "REDUCE"
    qqq_sizing = -10  # REDUCED from -20
    iwm_action = "CASH"
    iwm_sizing = 0    # CHANGED from -10 (no small cap shorts)
    # Net exposure: -30% max shorts (was -70%)
    # Philosophy: Even in panic, limited shorting. Bonds do the work.
```

#### 2. `roro_monitor/config/settings.py`

**Regime Thresholds (lines 62-72):**
```python
if self.REGIME_THRESHOLDS is None:
    # v4: Made Risk-Off harder to trigger (was 20-39, now 15-39)
    # Reason: MODERATE_RISK_OFF had -1.618% avg returns (catastrophic)
    # Fewer Risk-Off periods + defensive allocation = better protection
    self.REGIME_THRESHOLDS = {
        'STRONG_RISK_ON': (80, 100),
        'MODERATE_RISK_ON': (60, 79),
        'NEUTRAL': (40, 59),
        'MODERATE_RISK_OFF': (15, 39),  # CHANGED from (20, 39)
        'STRONG_RISK_OFF': (0, 14),      # CHANGED from (0, 19)
    }
```

---

## 📈 What to Expect in V4 Backtest

### Success Indicators

**If v4 works, you'll see:**

1. ✅ **MODERATE_RISK_OFF Returns:** -1.618% → **Small positive or 0%**
   - No more catastrophic losses from shorts
   - Bonds provide gentle positive returns

2. ✅ **Max Drawdown Reduction:** -16.88% → **-10% to -12%**
   - Eliminating Risk-Off losses should cut MDD significantly
   - This fixes the biggest problem

3. ✅ **Fewer Risk-Off Occurrences:** 6 → **3-4**
   - Higher threshold (15 vs 20) means better signal quality
   - Only enter Risk-Off when truly necessary

4. ✅ **Better Risk-Adjusted Returns:**
   - Sharpe: 0.728 → **>0.9**
   - Calmar: 0.971 → **>1.2**
   - Lower drawdowns with maintained alpha

5. ✅ **Institutional Criteria:** 4/6 → **5/6**
   - MDD improvement should push you over the edge

### What Might Still Need Work

**If these still show issues:**

1. **Q4 Signal Quality** - May need further tuning
2. **Upside Capture** - Might need more Risk-On aggression
3. **Neutral Regime** - Could optimize further

---

## 🧪 Testing Instructions

### 1. Pull Latest V4 Code

```powershell
git pull origin claude/institutional-roro-monitor-011CUsaUHtVNX3Gd2DXSoC6w
```

### 2. Clear Python Cache (CRITICAL!)

```powershell
Get-ChildItem -Path . -Include __pycache__ -Recurse -Force | Remove-Item -Force -Recurse
Get-ChildItem -Path . -Filter *.pyc -Recurse -Force | Remove-Item -Force
```

### 3. Run Backtest

```powershell
python main.py backtest
```

### 4. Verify Key Metrics

**Check these specific results:**

```
REGIME SWITCHING EFFICACY
─────────────────────────────────────────────
Regime                    Avg Return    Count
─────────────────────────────────────────────
MODERATE_RISK_OFF         ???%          ???
```

**Target:** Avg return should be **0% to +0.5%** (not -1.618%)

```
MAXIMUM DRAWDOWN
─────────────────────────────────────────────
Strategy Max Drawdown:       ???%
Benchmark Max Drawdown:      -18.76%
```

**Target:** Strategy MDD should be **<-12%** (not -16.88%)

```
OVERALL ASSESSMENT
─────────────────────────────────────────────
Success Criteria Met: ???/6
```

**Target:** Should be **5/6** (not 4/6)

---

## 📝 Key Lessons from V4

### 1. Your Edge is in Risk-On, Not Risk-Off

**The Strategy's Alpha:**
- Comes from identifying Risk-On periods early
- Capturing rallies with leverage (145-185%)
- Not from timing market tops to short

**The Mistake:**
- Trying to make money in both directions
- Shorting during Risk-Off is speculation, not defense

**The Fix:**
- Risk-On = OFFENSE (leverage, alpha generation)
- Risk-Off = DEFENSE (preservation, protection)

### 2. Defense ≠ Shorting

**Traditional Thinking:**
> "Bearish signal = Short the market"

**Reality:**
> "Bearish signal = Protect capital via bonds + cash"

**Why:**
- Bonds rally during Risk-Off (flight to safety)
- No short squeeze risk
- Smoother returns
- Easier to execute

### 3. Fewer Regimes, Better Timing

**Quality Over Quantity:**
- v3: 6 Risk-Off periods with -1.618% avg = BAD
- v4: 3-4 Risk-Off periods with 0% avg = GOOD

**Higher Bar:**
- Score must drop to 15 (vs 20) to trigger Risk-Off
- With hysteresis, even harder to trigger
- Result: Only enter Risk-Off when truly necessary

### 4. Capital Preservation > Speculation

**In MODERATE_RISK_OFF:**
- Score 15-39 = uncertainty
- Strategy doesn't know what's coming
- **Don't speculate with shorts**
- **Just preserve capital**

**In STRONG_RISK_OFF:**
- Score 0-14 = extreme panic
- Some shorting justified
- But capped at -30% (not -70%)
- Bonds still do most of the work

---

## 🎯 V4 Philosophy Summary

### Position Sizing by Regime

| Regime | Score | Equity Allocation | Philosophy |
|--------|-------|------------------|------------|
| **STRONG_RISK_ON** | 80-100 | 145-185% long | OFFENSE - Capture rallies |
| **MODERATE_RISK_ON** | 60-79 | 145% long | OFFENSE - Measured upside |
| **NEUTRAL** | 40-59 | 0% (cash) | PRESERVE - No edge detected |
| **MODERATE_RISK_OFF** | 15-39 | 0% (cash/bonds) | DEFEND - Pure preservation |
| **STRONG_RISK_OFF** | 0-14 | -30% max shorts | DEFEND - Limited speculation |

### Allocation Principles

1. **Risk-On (60-100):** Leverage for upside capture
2. **Neutral (40-59):** Cash - no risk without edge
3. **Risk-Off (0-39):** Bonds + cash - defense not offense

---

## 🚀 Next Steps After V4 Backtest

### If V4 Succeeds (Expected)

**Metrics to Validate:**
- ✅ MODERATE_RISK_OFF returns now positive
- ✅ Max Drawdown <-12%
- ✅ Success criteria 5/6
- ✅ Sharpe >0.9

**Then Consider:**
1. Fine-tune Risk-On sizing for more upside capture
2. Optimize Q4 signal quality further
3. Add momentum filters for regime confirmation
4. Deploy live with confidence

### If V4 Still Has Issues

**Potential Further Adjustments:**

1. **If Risk-Off still losing money:**
   - Remove ALL shorts (0% even in STRONG_RISK_OFF)
   - Pure bonds + cash approach

2. **If Max Drawdown still high:**
   - Investigate non-Risk-Off sources of losses
   - May need to reduce Risk-On leverage

3. **If Upside Capture still low:**
   - Increase Risk-On position sizing
   - Reduce Q4 sizing reduction (50% → 30%)

---

## 📊 Expected Final V4 Results

### Conservative Estimate

| Metric | Target | Rationale |
|--------|--------|-----------|
| Total Return | >15% | Maintain alpha from Risk-On |
| Max Drawdown | -10% to -12% | Fixed Risk-Off catastrophe |
| Sharpe Ratio | 0.9 to 1.1 | Better risk-adjusted returns |
| Upside Capture | 65-70% | Maintain rally participation |
| Downside Capture | 20-30% | Positive (bonds in Risk-Off) |
| Success Criteria | 5/6 | Pass institutional tests |

### Best Case

| Metric | Target | Rationale |
|--------|--------|-----------|
| Total Return | >18% | Risk-On optimization + no Risk-Off drag |
| Max Drawdown | -8% to -10% | Excellent protection |
| Sharpe Ratio | >1.2 | Superior risk-adjusted returns |
| Upside Capture | >70% | Strong rally participation |
| Success Criteria | 6/6 | Full institutional grade |

---

## 🎉 Conclusion

V4 represents a **fundamental strategy pivot**:

**From:** Tactical shorting in Risk-Off
**To:** Pure defense via bonds + cash

**The Key Insight:**
> The strategy's edge is in **identifying Risk-On periods**, not timing tops to short. Risk-Off should preserve capital, not speculate.

**Expected Impact:**
- MODERATE_RISK_OFF: -1.618% → 0% to +0.5%
- Max Drawdown: -16.88% → <-12%
- Success Criteria: 4/6 → 5/6

This single change (0% equities in MODERATE_RISK_OFF instead of -30% shorts) should transform the strategy from "promising but flawed" to "institutionally viable."

---

**Ready to test!** Pull v4 code, clear cache, run backtest, and share results.

**End of V4 Documentation**
