import re


class BehaviorDetector:
    def analyze(self, text: str) -> dict:
        text_lower = text.lower()
        word_count = max(1, len(text.split()))

        patterns = {
            "instruction_density": r"\b(step|first|then|next|finally|how.{0,5}to)\b",
            "imperative_commands": r"\b(target|exploit|bypass|create|build|inject)\b",
            "technical_specificity": r"\b(\d+\s*(mhz|khz)|\.exe|\.sh|api|endpoint|chemical)\b",
            "secrecy_language": r"\b(secret|undetected|dark.{0,5}web)\b",
            "violence_indicators": r"\b(kill|harm|attack|assault)\b",
            "minor_risk_indicators": r"\b(child|minor|underage)\b",
        }

        raw_counts = {
            key: len(re.findall(pattern, text_lower))
            for key, pattern in patterns.items()
        }

        normalized = {key: raw_counts[key] / word_count for key in raw_counts}

        # Calculate composite risk score
        risk = min(
            30
            * (
                normalized["instruction_density"] * 0.08
                + normalized["imperative_commands"] * 0.12
                + normalized["technical_specificity"] * 0.1
                + normalized["secrecy_language"] * 0.04
                + normalized["violence_indicators"] * 0.12
                + normalized["minor_risk_indicators"] * 0.16
            ),
            1.0,
        )

        return {
            "risk": risk,
            "raw": raw_counts,
            "norm": normalized,
            "is_high_risk": risk > 0.4,
        }
