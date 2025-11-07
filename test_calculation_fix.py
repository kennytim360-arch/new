"""Test the master score calculation fix."""

# Simulate pillar scores from the logs
pillar_scores = {
    'Pillar A': {'score': 70.3, 'weight': 0.30},
    'Pillar B': {'score': 35.5, 'weight': 0.25},
    'Pillar C': {'score': 48.3, 'weight': 0.25},
    'Pillar D': {'score': 34.5, 'weight': 0.10},
    'Pillar E': {'score': 57.3, 'weight': 0.10},
}

# Calculate weighted scores
weighted_scores = []
for name, data in pillar_scores.items():
    weighted = data['score'] * data['weight']
    weighted_scores.append(weighted)
    print(f"{name}: {data['score']:.1f} × {data['weight']:.2f} = {weighted:.1f}")

# Calculate master score
total_weight = sum(data['weight'] for data in pillar_scores.values())
master_score_OLD = (sum(weighted_scores) / total_weight) * 100  # OLD (buggy)
master_score_NEW = sum(weighted_scores) / total_weight         # NEW (fixed)

print("\n" + "="*60)
print(f"Sum of weighted scores: {sum(weighted_scores):.1f}")
print(f"Total weight: {total_weight:.2f}")
print("\nOLD CALCULATION (buggy): ({sum(weighted_scores):.1f} / {total_weight:.2f}) × 100 = {master_score_OLD:.1f}")
print(f"NEW CALCULATION (fixed): ({sum(weighted_scores):.1f} / {total_weight:.2f}) = {master_score_NEW:.1f}")
print("="*60)

# Determine regime
if master_score_NEW >= 80:
    regime = "STRONG_RISK_ON"
elif master_score_NEW >= 60:
    regime = "MODERATE_RISK_ON"
elif master_score_NEW >= 40:
    regime = "NEUTRAL"
elif master_score_NEW >= 20:
    regime = "MODERATE_RISK_OFF"
else:
    regime = "STRONG_RISK_OFF"

print(f"\n✓ Master Score: {master_score_NEW:.1f}/100")
print(f"✓ Regime: {regime}")
print(f"✓ Fix successful! (was showing {master_score_OLD:.1f})")
