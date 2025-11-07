#!/usr/bin/env python3
"""
Q4 Signal Quality Diagnostic
Analyzes why highest conviction signals (75-100) are losing money
"""

import pandas as pd
import numpy as np
from pathlib import Path

def analyze_q4_failure(csv_path: str):
    """Deep dive into Q4 signal failure."""

    print("="*80)
    print("Q4 SIGNAL FAILURE ANALYSIS")
    print("="*80)

    df = pd.read_csv(csv_path)

    # Quartile breakdown
    df['quartile'] = pd.cut(df['score'], bins=[0, 25, 50, 75, 100],
                           labels=['Q1', 'Q2', 'Q3', 'Q4'])

    print("\n1. QUARTILE PERFORMANCE BREAKDOWN")
    print("-" * 80)
    for q in ['Q1', 'Q2', 'Q3', 'Q4']:
        q_data = df[df['quartile'] == q]
        if len(q_data) > 0:
            avg_ret = q_data['strategy_return'].mean()
            volatility = q_data['strategy_return'].std()
            count = len(q_data)
            print(f"{q}: {avg_ret:.3f}% avg return | {volatility:.3f}% vol | {count} days")

    # Q4 deep dive
    q4_data = df[df['quartile'] == 'Q4'].copy()

    print("\n2. Q4 SCORE DISTRIBUTION (75-100 range)")
    print("-" * 80)
    if len(q4_data) > 0:
        print(f"Q4 Score Range: {q4_data['score'].min():.1f} - {q4_data['score'].max():.1f}")
        print(f"Q4 Average Score: {q4_data['score'].mean():.1f}")
        print(f"Q4 Days: {len(q4_data)}")

        # Break Q4 into sub-ranges
        for lower in [75, 80, 85, 90, 95]:
            upper = lower + 5
            subset = q4_data[(q4_data['score'] >= lower) & (q4_data['score'] < upper)]
            if len(subset) > 0:
                avg_ret = subset['strategy_return'].mean()
                print(f"  {lower}-{upper}: {avg_ret:.3f}% avg return ({len(subset)} days)")

    print("\n3. Q4 WORST DAYS (Largest Losses)")
    print("-" * 80)
    if len(q4_data) > 0:
        worst_q4 = q4_data.nsmallest(5, 'strategy_return')
        for idx, row in worst_q4.iterrows():
            print(f"  {row['date']}: Score {row['score']:.1f} → {row['strategy_return']:.2f}% | "
                  f"SPY: {row['benchmark_return']:.2f}%")

    print("\n4. REGIME ANALYSIS DURING Q4 SCORES")
    print("-" * 80)
    if len(q4_data) > 0:
        regime_perf = q4_data.groupby('regime').agg({
            'strategy_return': ['mean', 'count'],
            'exposure': 'mean'
        }).round(3)
        print(regime_perf)

    print("\n5. EXPOSURE DURING Q4 vs MARKET PERFORMANCE")
    print("-" * 80)
    if len(q4_data) > 0:
        print(f"Average Q4 Exposure: {q4_data['exposure'].mean():.1f}%")
        print(f"Average Q4 Benchmark Return: {q4_data['benchmark_return'].mean():.3f}%")
        print(f"Average Q4 Strategy Return: {q4_data['strategy_return'].mean():.3f}%")

        # Check if Q4 occurs at market tops
        q4_data['is_market_positive'] = q4_data['benchmark_return'] > 0
        positive_days = q4_data['is_market_positive'].sum()
        print(f"\nQ4 on positive market days: {positive_days}/{len(q4_data)} ({100*positive_days/len(q4_data):.1f}%)")

        q4_positive = q4_data[q4_data['is_market_positive']]
        q4_negative = q4_data[~q4_data['is_market_positive']]

        if len(q4_positive) > 0:
            print(f"  Q4 + Positive Market: {q4_positive['strategy_return'].mean():.3f}% avg")
        if len(q4_negative) > 0:
            print(f"  Q4 + Negative Market: {q4_negative['strategy_return'].mean():.3f}% avg")

    print("\n6. TIMING ANALYSIS - WHEN DO Q4 SCORES OCCUR?")
    print("-" * 80)
    if len(q4_data) > 0:
        q4_data['date'] = pd.to_datetime(q4_data['date'])
        q4_data['month'] = q4_data['date'].dt.month
        monthly = q4_data.groupby('month')['strategy_return'].agg(['count', 'mean'])
        print("Q4 Scores by Month:")
        print(monthly)

    print("\n7. DIAGNOSIS: ROOT CAUSE ANALYSIS")
    print("="*80)
    if len(q4_data) > 0:
        avg_q4_ret = q4_data['strategy_return'].mean()
        avg_q3_ret = df[df['quartile'] == 'Q3']['strategy_return'].mean()

        print(f"\n❌ Q4 underperforms Q3 by {avg_q3_ret - avg_q4_ret:.3f}%")

        # Hypothesis testing
        print("\nLIKELY CAUSES:")

        # 1. Over-leveraged at market tops?
        avg_exposure_q4 = q4_data['exposure'].mean()
        avg_exposure_q3 = df[df['quartile'] == 'Q3']['exposure'].mean()
        if avg_exposure_q4 > avg_exposure_q3:
            print(f"  ⚠️  Q4 is over-leveraged: {avg_exposure_q4:.1f}% vs Q3 {avg_exposure_q3:.1f}%")

        # 2. Mean reversion at extremes?
        q4_positive_days = (q4_data['benchmark_return'] > 0).sum()
        q4_total_days = len(q4_data)
        if q4_positive_days / q4_total_days < 0.5:
            print(f"  ⚠️  Q4 scores trigger at market tops (only {100*q4_positive_days/q4_total_days:.1f}% positive days)")

        # 3. Lagging signals at extremes?
        if q4_data['strategy_return'].std() > df['strategy_return'].std() * 1.5:
            print(f"  ⚠️  Q4 signals are too volatile/noisy")

        print("\n✅ RECOMMENDED FIXES:")
        print("  1. Add momentum confirmation before taking extreme positions")
        print("  2. Reduce position sizing at Q4 (>75 scores) by 30-50%")
        print("  3. Check for overbought conditions (RSI > 70) as contra-signal")
        print("  4. Implement mean reversion check at extremes")

if __name__ == "__main__":
    # Find most recent backtest CSV
    csv_files = sorted(Path('.').glob('backtest_results_*.csv'), reverse=True)

    if csv_files:
        latest_csv = str(csv_files[0])
        print(f"\nAnalyzing: {latest_csv}\n")
        analyze_q4_failure(latest_csv)
    else:
        print("No backtest CSV files found. Run: python main.py backtest")
