"""
Emergency diagnostic script to analyze backtest failures.

Analyzes:
1. Why upside capture dropped from 68% to 57%
2. Why downside capture is negative (-55.8%)
3. Regime stability issues (23 changes)
4. Q4 vs Q3 performance problem
"""

import pandas as pd
import numpy as np

# Load the backtest results
results = pd.read_csv('backtest_results_20251107_132027.csv')

print("="*80)
print("EMERGENCY DIAGNOSTIC ANALYSIS")
print("="*80)

# 1. Regime frequency analysis
print("\n1. REGIME FREQUENCY ANALYSIS")
print("─"*80)
regime_counts = results['regime'].value_counts()
print(f"\nRegime Distribution:")
for regime, count in regime_counts.items():
    pct = (count / len(results)) * 100
    print(f"  {regime}: {count} periods ({pct:.1f}%)")

# 2. Average return by regime
print("\n2. AVERAGE RETURN BY REGIME")
print("─"*80)
regime_returns = results.groupby('regime')['forward_return'].agg(['mean', 'std', 'count'])
print(regime_returns)

# 3. Regime duration analysis
print("\n3. REGIME DURATION ANALYSIS")
print("─"*80)
results['regime_change'] = results['regime'] != results['regime'].shift(1)
regime_changes = results['regime_change'].sum()
avg_duration = len(results) / regime_changes if regime_changes > 0 else 0
print(f"Total regime changes: {regime_changes}")
print(f"Average regime duration: {avg_duration:.1f} periods (should be >5)")

# Calculate actual durations
durations = []
current_regime = results['regime'].iloc[0]
duration = 1
for i in range(1, len(results)):
    if results['regime'].iloc[i] == current_regime:
        duration += 1
    else:
        durations.append(duration)
        current_regime = results['regime'].iloc[i]
        duration = 1
durations.append(duration)

print(f"Median regime duration: {np.median(durations):.1f} periods")
print(f"Shortest regime: {min(durations)} periods")
print(f"Longest regime: {max(durations)} periods")
print(f"\n⚠ Durations < 5 periods: {sum(1 for d in durations if d < 5)} out of {len(durations)}")

# 4. Score distribution analysis
print("\n4. SCORE DISTRIBUTION ANALYSIS")
print("─"*80)
print(f"Average score: {results['score'].mean():.1f}")
print(f"Score std dev: {results['score'].std():.1f}")
print(f"Score range: {results['score'].min():.1f} to {results['score'].max():.1f}")

# Check if scores are clustered in neutral zone
neutral_pct = ((results['score'] >= 40) & (results['score'] < 60)).sum() / len(results) * 100
print(f"\n% of time in NEUTRAL zone (40-59): {neutral_pct:.1f}%")
risk_on_pct = (results['score'] >= 60).sum() / len(results) * 100
print(f"% of time in RISK-ON zones (≥60): {risk_on_pct:.1f}%")
risk_off_pct = (results['score'] < 40).sum() / len(results) * 100
print(f"% of time in RISK-OFF zones (<40): {risk_off_pct:.1f}%")

# 5. Q4 vs Q3 problem analysis
print("\n5. QUARTILE PERFORMANCE PROBLEM")
print("─"*80)
results['score_quartile'] = pd.qcut(results['score'], q=4, labels=['Q1', 'Q2', 'Q3', 'Q4'])
quartile_perf = results.groupby('score_quartile')['forward_return'].agg(['mean', 'std', 'count'])
print(quartile_perf)
print("\n⚠ Q4 should outperform Q3 but doesn't - signal degradation detected")

# 6. Largest losses analysis
print("\n6. LARGEST LOSSES (Top 10 Worst Periods)")
print("─"*80)
worst_periods = results.nsmallest(10, 'forward_return')[['date', 'score', 'regime', 'forward_return']]
print(worst_periods.to_string())

# 7. Upside capture detailed analysis
print("\n7. UPSIDE CAPTURE PROBLEM")
print("─"*80)
# Approximate benchmark returns (would need actual benchmark data)
avg_positive_return = results[results['forward_return'] > 0]['forward_return'].mean()
positive_periods = (results['forward_return'] > 0).sum()
print(f"Periods with positive returns: {positive_periods} ({positive_periods/len(results)*100:.1f}%)")
print(f"Average positive return: {avg_positive_return:.3f}%")

# Check if strategy is too defensive (scores too low during rallies)
positive_return_periods = results[results['forward_return'] > 0]
avg_score_during_positive = positive_return_periods['score'].mean()
print(f"Average score during positive return periods: {avg_score_during_positive:.1f}")
print("⚠ If this is <60, the strategy is too defensive during rallies")

# 8. Downside capture analysis
print("\n8. DOWNSIDE CAPTURE ANALYSIS (Negative = Inverse Correlation)")
print("─"*80)
negative_return_periods = results[results['forward_return'] < 0]
if len(negative_return_periods) > 0:
    avg_score_during_negative = negative_return_periods['score'].mean()
    regime_during_declines = negative_return_periods['regime'].value_counts()
    print(f"Average score during negative return periods: {avg_score_during_negative:.1f}")
    print(f"\nRegimes during market declines:")
    for regime, count in regime_during_declines.items():
        pct = (count / len(negative_return_periods)) * 100
        print(f"  {regime}: {count} periods ({pct:.1f}%)")
    print("\n⚠ If NEUTRAL or RISK-ON regimes dominate during declines, signals are broken")

# 9. Critical issue summary
print("\n" + "="*80)
print("CRITICAL ISSUES SUMMARY")
print("="*80)

issues = []

if avg_duration < 5:
    issues.append(f"✗ Regime duration too short: {avg_duration:.1f} periods (need >5)")

if neutral_pct > 50:
    issues.append(f"✗ Too much time in NEUTRAL: {neutral_pct:.1f}% (strategy too cautious)")

if avg_score_during_positive < 60:
    issues.append(f"✗ Score too low during rallies: {avg_score_during_positive:.1f} (missing upside)")

if quartile_perf.loc['Q4', 'mean'] < quartile_perf.loc['Q3', 'mean']:
    issues.append("✗ Q4 underperforming Q3 (signal degradation)")

if len(issues) > 0:
    for issue in issues:
        print(issue)
else:
    print("✓ No critical issues found")

print("\n" + "="*80)
print("RECOMMENDED FIXES")
print("="*80)
print("1. Add regime stability filter (minimum 5-day duration)")
print("2. Increase Risk-On sensitivity (lower threshold or increase trend weight)")
print("3. Fix leading indicators (reduce weight or smooth signals)")
print("4. Review position sizing in NEUTRAL regime")
print("5. Add trend confirmation for regime changes")
print("="*80)
