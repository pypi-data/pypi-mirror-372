import re
import yaml
from typing import Dict, Any


class RegexDetector:
    def __init__(self, patterns: Dict[str, Any], caps=(10, 10)):
        self.patterns = patterns
        self.caps = caps

    @classmethod
    def load_default(cls):
        import os

        current_dir = os.path.dirname(os.path.abspath(__file__))
        patterns_path = os.path.join(
            os.path.dirname(current_dir), "resources", "patterns.yml"
        )
        with open(patterns_path, "r") as f:
            patterns = yaml.safe_load(f)
        return cls(patterns)

    def analyze(self, text: str) -> Dict[str, Any]:
        results = {}
        text_lower = text.lower()

        for category, config in self.patterns.items():
            matches = []
            count = 0

            for pattern in config["patterns"]:
                found_matches = re.findall(pattern, text_lower)
                if found_matches:
                    matches += found_matches
                    count += len(found_matches)

            severity = config["base_severity"]
            breadth = config["base_breadth"]

            results[category] = {
                "count": count,
                "matches": matches,
                "base_severity": severity,
                "base_breadth": breadth,
            }

        return results
