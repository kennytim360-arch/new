#!/usr/bin/env python3
"""
V4 Validation and Comparison Tool
Compares v3 vs v4 backtest results to validate Risk-Off fixes
"""

import pandas as pd
import numpy as np
from pathlib import Path
import sys

def load_latest_backtest():
    """Find and load the most recent backtest CSV."""
    csv_files = sorted(Path('.').glob('backtest_results_*.csv'), reverse=True)
    if not csv_files:
        print("❌ No backtest CSV files found!")
        print("Run: python main.py backtest")
        sys.exit(1)

    latest = csv_files[0]
    print(f"📊 Loading: {latest}")
    return pd.read_csv(latest)

def analyze_risk_off_performance(df):
    """Analyze MODERATE_RISK_OFF regime performance."""
    print("\n" + "="*80)
    print("RISK-OFF PERFORMANCE ANALYSIS (V4 FIX VALIDATION)")
    print("="*80)

    # MODERATE_RISK_OFF analysis
    moderate_risk_off = df[df['regime'] == 'MODERATE_RISK_OFF']

    if len(moderate_risk_off) > 0:
        avg_return = moderate_risk_off['strategy_return'].mean()
        volatility = moderate_risk_off['strategy_return'].std()
        count = len(moderate_risk_off)

        print(f"\n📉 MODERATE_RISK_OFF:")
        print(f"   Occurrences: {count}")
        print(f"   Avg Return: {avg_return:.3f}%")
        print(f"   Volatility: {volatility:.3f}%")

        # V4 TARGET: Should be 0% to +0.5%
        if avg_return >= 0 and avg_return <= 0.5:
            print(f"   ✅ SUCCESS! Within target range (0% to +0.5%)")
        elif avg_return >= 0:
            print(f"   ⚠️  Positive but high ({avg_return:.3f}%) - may be over-allocated to bonds")
        else:
            print(f"   ❌ STILL NEGATIVE! v4 fix didn't work - investigate further")

        # Show individual occurrences
        print(f"\n   Individual MODERATE_RISK_OFF periods:")
        for idx, row in moderate_risk_off.iterrows():
            print(f"      {row['date']}: {row['strategy_return']:+.2f}% | Score: {row['score']:.1f}")
    else:
        print(f"\n📉 MODERATE_RISK_OFF: No occurrences (may be good - harder to trigger)")

    # STRONG_RISK_OFF analysis
    strong_risk_off = df[df['regime'] == 'STRONG_RISK_OFF']

    if len(strong_risk_off) > 0:
        avg_return = strong_risk_off['strategy_return'].mean()
        count = len(strong_risk_off)

        print(f"\n📉 STRONG_RISK_OFF:")
        print(f"   Occurrences: {count}")
        print(f"   Avg Return: {avg_return:.3f}%")

        if avg_return >= -0.5:
            print(f"   ✅ Good - limited losses with -30% max shorts")
        else:
            print(f"   ⚠️  Still losing money - may need to remove all shorts")
    else:
        print(f"\n📉 STRONG_RISK_OFF: No occurrences (excellent - extreme fear didn't trigger)")

def compare_regime_distribution(df):
    """Compare how often each regime occurred."""
    print("\n" + "="*80)
    print("REGIME DISTRIBUTION (Should favor Risk-On)")
    print("="*80)

    regime_counts = df['regime'].value_counts()
    total_days = len(df)

    print(f"\nTotal Days: {total_days}")
    print("\nRegime              Count    % of Time    Target")
    print("-" * 80)

    targets = {
        'MODERATE_RISK_ON': '60-70%',
        'STRONG_RISK_ON': '10-20%',
        'NEUTRAL': '20-30%',
        'MODERATE_RISK_OFF': '5-10%',
        'STRONG_RISK_OFF': '<5%'
    }

    for regime in ['STRONG_RISK_ON', 'MODERATE_RISK_ON', 'NEUTRAL',
                   'MODERATE_RISK_OFF', 'STRONG_RISK_OFF']:
        count = regime_counts.get(regime, 0)
        pct = 100 * count / total_days
        target = targets.get(regime, 'N/A')
        print(f"{regime:20s} {count:5d}    {pct:5.1f}%      {target}")

def analyze_q4_performance(df):
    """Check if Q4 signal quality improved."""
    print("\n" + "="*80)
    print("Q4 SIGNAL QUALITY (Should be positive now)")
    print("="*80)

    df['quartile'] = pd.cut(df['score'], bins=[0, 25, 50, 75, 100],
                           labels=['Q1', 'Q2', 'Q3', 'Q4'])

    print("\nQuartile    Avg Return    Volatility    Count    Status")
    print("-" * 80)

    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        q_data = df[df['quartile'] == q]
        if len(q_data) > 0:
            avg_ret = q_data['strategy_return'].mean()
            volatility = q_data['strategy_return'].std()
            count = len(q_data)

            status = "✅" if avg_ret > 0 else "❌"

            print(f"{q:10s}  {avg_ret:+8.3f}%    {volatility:8.3f}%    {count:5d}    {status}")

    # Check if Q4 > Q3
    q3_return = df[df['quartile'] == 'Q3']['strategy_return'].mean()
    q4_return = df[df['quartile'] == 'Q4']['strategy_return'].mean()

    print(f"\n📊 Q4 vs Q3 Comparison:")
    if q4_return > q3_return:
        print(f"   ✅ Q4 ({q4_return:.3f}%) > Q3 ({q3_return:.3f}%) - Signal quality fixed!")
    else:
        print(f"   ❌ Q4 ({q4_return:.3f}%) < Q3 ({q3_return:.3f}%) - Still needs work")

def analyze_regime_changes(df):
    """Count regime changes."""
    print("\n" + "="*80)
    print("REGIME STABILITY (Lower is better)")
    print("="*80)

    regime_changes = (df['regime'] != df['regime'].shift()).sum() - 1
    avg_duration = len(df) / (regime_changes + 1) if regime_changes > 0 else len(df)

    print(f"\nRegime Changes: {regime_changes}")
    print(f"Average Duration: {avg_duration:.1f} days")

    if regime_changes < 12:
        print(f"✅ Excellent - fewer than 12 changes per year")
    elif regime_changes < 15:
        print(f"⚠️  Good but could be better")
    else:
        print(f"❌ Too many regime changes - increase persistence")

def calculate_key_metrics(df):
    """Calculate and display key performance metrics."""
    print("\n" + "="*80)
    print("KEY PERFORMANCE METRICS")
    print("="*80)

    # Returns
    total_return = ((1 + df['strategy_return'] / 100).prod() - 1) * 100
    benchmark_return = ((1 + df['benchmark_return'] / 100).prod() - 1) * 100

    # Volatility (annualized)
    strategy_vol = df['strategy_return'].std() * np.sqrt(252)

    # Sharpe (assuming 0% risk-free rate)
    sharpe = (total_return / strategy_vol) if strategy_vol > 0 else 0

    # Max Drawdown
    cumulative = (1 + df['strategy_return'] / 100).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100
    max_dd = drawdown.min()

    # Upside/Downside Capture
    up_days = df[df['benchmark_return'] > 0]
    down_days = df[df['benchmark_return'] < 0]

    if len(up_days) > 0:
        upside_capture = (up_days['strategy_return'].sum() / up_days['benchmark_return'].sum()) * 100
    else:
        upside_capture = 0

    if len(down_days) > 0:
        downside_capture = (down_days['strategy_return'].sum() / down_days['benchmark_return'].sum()) * 100
    else:
        downside_capture = 0

    print(f"\n📈 Returns:")
    print(f"   Strategy: {total_return:+.2f}%")
    print(f"   Benchmark: {benchmark_return:+.2f}%")
    print(f"   Alpha: {total_return - benchmark_return:+.2f}%")

    print(f"\n📊 Risk Metrics:")
    print(f"   Max Drawdown: {max_dd:.2f}%")
    print(f"   Volatility: {strategy_vol:.2f}%")
    print(f"   Sharpe Ratio: {sharpe:.3f}")

    print(f"\n🎯 Capture Ratios:")
    print(f"   Upside: {upside_capture:.1f}%")
    print(f"   Downside: {downside_capture:.1f}%")

    # Success criteria
    print(f"\n✅ SUCCESS CRITERIA:")
    criteria_met = 0
    total_criteria = 6

    if max_dd > -18.76:
        print(f"   ✅ Max DD better than benchmark ({max_dd:.2f}% vs -18.76%)")
        criteria_met += 1
    else:
        print(f"   ❌ Max DD worse than benchmark")

    if sharpe > 1.0:
        print(f"   ✅ Sharpe > 1.0 ({sharpe:.3f})")
        criteria_met += 1
    else:
        print(f"   ❌ Sharpe < 1.0 ({sharpe:.3f})")

    calmar = abs(total_return / max_dd) if max_dd != 0 else 0
    if calmar > 1.0:
        print(f"   ✅ Calmar > 1.0 ({calmar:.3f})")
        criteria_met += 1
    else:
        print(f"   ❌ Calmar < 1.0 ({calmar:.3f})")

    # Calculate beta
    cov_matrix = np.cov(df['strategy_return'], df['benchmark_return'])
    beta = cov_matrix[0,1] / cov_matrix[1,1]

    if beta < 1.0:
        print(f"   ✅ Beta < 1.0 ({beta:.3f})")
        criteria_met += 1
    else:
        print(f"   ❌ Beta >= 1.0 ({beta:.3f})")

    if total_return > benchmark_return:
        print(f"   ✅ Alpha > 0 ({total_return - benchmark_return:+.2f}%)")
        criteria_met += 1
    else:
        print(f"   ❌ Alpha < 0")

    if downside_capture < 50:
        print(f"   ✅ Downside Capture < 50% ({downside_capture:.1f}%)")
        criteria_met += 1
    else:
        print(f"   ❌ Downside Capture >= 50%")

    print(f"\n🎯 FINAL SCORE: {criteria_met}/{total_criteria}")

    if criteria_met >= 5:
        print(f"   ✅✅✅ INSTITUTIONAL GRADE! Strategy is ready!")
    elif criteria_met >= 4:
        print(f"   ⚠️  Close but needs refinement")
    else:
        print(f"   ❌ Significant work needed")

    return {
        'total_return': total_return,
        'max_dd': max_dd,
        'sharpe': sharpe,
        'upside_capture': upside_capture,
        'downside_capture': downside_capture,
        'criteria_met': criteria_met
    }

def main():
    print("\n" + "="*80)
    print("V4 BACKTEST VALIDATION TOOL")
    print("="*80)
    print("\nValidating v4 fixes:")
    print("1. MODERATE_RISK_OFF should be 0% to +0.5% (was -1.618%)")
    print("2. Max Drawdown should be <-12% (was -16.88%)")
    print("3. Success criteria should be 5/6 (was 4/6)")

    # Load data
    df = load_latest_backtest()

    # Run analyses
    analyze_risk_off_performance(df)
    compare_regime_distribution(df)
    analyze_q4_performance(df)
    analyze_regime_changes(df)
    metrics = calculate_key_metrics(df)

    # Final verdict
    print("\n" + "="*80)
    print("FINAL VERDICT")
    print("="*80)

    if metrics['criteria_met'] >= 5:
        print("\n✅✅✅ V4 IS A SUCCESS!")
        print("\nThe strategy is now institutional-grade and ready for live deployment.")
        print("Consider fine-tuning for marginal improvements, but core issues are solved.")
    elif metrics['criteria_met'] == 4:
        print("\n⚠️  V4 SHOWS IMPROVEMENT BUT NOT THERE YET")
        print("\nRecommendations:")
        if metrics['max_dd'] < -12:
            print("- Max drawdown still high - investigate remaining loss sources")
        if metrics['sharpe'] < 1.0:
            print("- Sharpe ratio needs work - reduce volatility or increase returns")
        if metrics['upside_capture'] < 70:
            print("- Upside capture low - consider more Risk-On aggression")
    else:
        print("\n❌ V4 STILL HAS MAJOR ISSUES")
        print("\nRecommend pivoting to simplified 3-pillar approach:")
        print("1. Market Breadth (A/D line)")
        print("2. Credit Spreads (HYG/TLT)")
        print("3. Volatility Structure (VIX term structure)")
        print("\nComplex 5-pillar system may be over-engineered.")

if __name__ == "__main__":
    main()
