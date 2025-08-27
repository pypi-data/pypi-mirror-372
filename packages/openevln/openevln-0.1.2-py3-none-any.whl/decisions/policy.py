def recommend(level, max_severity, max_breadth):
    """
    Generate action recommendations based on risk level and threat characteristics.

    Args:
        level: Risk level ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')
        max_severity: Maximum severity score
        max_breadth: Maximum breadth score

    Returns:
        Dictionary with recommended actions and escalation flags
    """
    # Determine primary action
    if level in {"CRITICAL", "HIGH"}:
        action = "BLOCK"
    elif level == "MEDIUM":
        action = "REVIEW"
    else:
        action = "ALLOW"

    # Determine severity-based action
    if max_severity >= 10:
        severity_action = "CRITICAL_ESCALATION"
    elif max_severity >= 5:
        severity_action = "HIGH_PRIORITY"
    else:
        severity_action = "STANDARD"

    # Determine breadth-based action
    if max_breadth >= 10:
        breadth_action = "MASS_IMPACT_ALERT"
    elif max_breadth >= 5:
        breadth_action = "POPULATION_RISK"
    else:
        breadth_action = "LIMITED_SCOPE"

    return {
        "action": action,
        "human_review": max_severity >= 5 or max_breadth >= 5,
        "immediate_escalation": max_severity >= 10 or max_breadth >= 10,
        "severity_action": severity_action,
        "breadth_action": breadth_action,
    }
