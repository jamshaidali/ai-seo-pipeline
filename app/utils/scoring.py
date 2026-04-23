def calculate_opportunity_score(search_volume: int, difficulty: int, domain_visible: bool, query_text: str) -> float:
    """
    Calculate the Opportunity Score scalar in range [0.0, 1.0].
    
    Formula Weights:
    - Volume: 30%
    - Difficulty: 30%
    - Visibility Gap: 30%
    - Commercial Intent Bonus: 10%
    """
    
    # Normalize Volume (Cap at 10,000 for standardisation)
    # E.g. Vol 5000 -> 0.5. Vol 20000 -> 1.0
    vol_cap = 10000
    norm_vol = min(max(search_volume, 0) / vol_cap, 1.0)
    
    # Normalize Difficulty
    # E.g. Diff 100 -> 0.0 (Hard). Diff 20 -> 0.8 (Easy).
    norm_diff = max(0.0, (100 - difficulty)) / 100.0
    
    # Visibility Gap
    # If not visible -> high score (1.0). If visible -> low score (0.0).
    vis_gap = 1.0 if not domain_visible else 0.0
    
    # Intent Bonus (If 'vs', 'best', 'review' are in query)
    lower_query = query_text.lower()
    intent_keywords = ['vs', 'versus', 'best', 'review', 'compare', 'alternative', 'how to']
    intent_bonus = 1.0 if any(kw in lower_query for kw in intent_keywords) else 0.0
    
    # Final Weighted calculation
    score = (0.3 * norm_vol) + (0.3 * norm_diff) + (0.3 * vis_gap) + (0.1 * intent_bonus)
    
    return round(min(max(score, 0.0), 1.0), 3)
