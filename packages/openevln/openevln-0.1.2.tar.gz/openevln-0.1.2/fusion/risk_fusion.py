import math


def cap(value, min_val, max_val):
    """Clamp value between min and max bounds."""
    return max(min_val, min(max_val, value))


def fuse(pattern, behavior, semantic, context_score, threshold=0.3):
    """
    Fuse pattern, behavioral, and semantic signals into composite risk score.

    Args:
        pattern: Pattern detection results
        behavior: Behavioral analysis results
        semantic: Semantic similarity results
        context_score: Context adherence score
        threshold: Risk threshold for classification

    Returns:
        Tuple of (composite_risk, level, is_safe, active_threats, max_severity, max_breadth)
    """
    # Calculate base severity and breadth from patterns
    max_severity = max((v.get("base_severity", 0) for v in pattern.values()), default=0)
    max_breadth = max((v.get("base_breadth", 0) for v in pattern.values()), default=0)

    total_severity = 0
    total_breadth = 0
    active_threats = []

    # Process each category
    for category, data in pattern.items():
        count = data["count"]
        severity = data["base_severity"]
        breadth = data["base_breadth"]

        # Get semantic similarity boost
        similarity = 0.0
        if semantic:
            similarity = semantic.get(category, {"similarity": 0.0})["similarity"]

        # Apply semantic amplification
        severity = cap(severity * (1 + 0.8 * similarity) + 0.1 * count, 0, 10)
        breadth = cap(breadth * (1 + 0.6 * similarity) + 0.1 * count, 0, 10)

        # Track active threats
        if count > 0 or similarity > 0.6:
            active_threats.append(
                {
                    "category": category,
                    "severity": severity,
                    "breadth": breadth,
                    "count": count,
                }
            )

        # Accumulate totals
        total_severity += severity * count / 10
        total_breadth += breadth * count / 10
        max_severity = max(max_severity, severity)
        max_breadth = max(max_breadth, breadth)

    # Calculate component risks
    pattern_risk = sum((1 if v["count"] > 0 else 0) for v in pattern.values()) / max(
        1, len(pattern)
    )

    behavioral_risk = behavior["risk"]
    context_risk = 1 - context_score
    severity_impact = cap(total_severity / 50, 0, 1)
    breadth_impact = cap(total_breadth / 50, 0, 1)

    # Calculate composite risk
    composite = cap(
        pattern_risk * 0.22
        + behavioral_risk * 0.2
        + context_risk * 0.1
        + severity_impact * 0.28
        + breadth_impact * 0.2,
        0,
        1,
    )

    # Determine risk level
    if max_severity >= 10 or max_breadth >= 10:
        level = "CRITICAL"
    elif max_severity >= 5 or max_breadth >= 5 or composite > 0.7:
        level = "HIGH"
    elif composite > threshold:
        level = "MEDIUM"
    else:
        level = "LOW"

    is_safe = composite < threshold and max_severity < 5

    return composite, level, is_safe, active_threats, max_severity, max_breadth
