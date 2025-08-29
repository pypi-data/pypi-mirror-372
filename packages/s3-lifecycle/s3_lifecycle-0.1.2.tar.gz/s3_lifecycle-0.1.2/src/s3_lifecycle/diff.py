from typing import List, Dict, Any
from .policy import Rule
from dataclasses import dataclass


@dataclass
class RuleChange:
    to_add: List[Rule]
    to_update: List[Dict[str, Any]]  # includes {"before": Rule, "after": Rule}
    to_delete: List[Rule]

    def summary(self) -> str:
        parts = []
        if self.to_add:
            parts.append(f"Add {len(self.to_add)} rule(s): {[r.ID for r in self.to_add]}")
        if self.to_update:
            update_ids = [u["after"].ID for u in self.to_update]
            parts.append(f"Update {len(self.to_update)} rule(s): {update_ids}")
        if self.to_delete:
            parts.append(f"Delete {len(self.to_delete)} rule(s): {[r.ID for r in self.to_delete]}")
        return "; ".join(parts) if parts else "No changes"


class DiffResult:
    def __init__(self, rule_change: RuleChange):
        self.rule_change = rule_change

    def summary(self) -> str:
        return self.rule_change.summary()

    @staticmethod
    def _normalize_rule(rule: Rule) -> Dict[str, Any]:
        """
        Convert Rule object to dict and recursively remove None values.
        Ensures that all lifecycle fields are compared correctly.
        """
        def clean(d):
            if isinstance(d, dict):
                return {k: clean(v) for k, v in d.items() if v is not None}
            elif isinstance(d, list):
                return [clean(i) for i in d]
            else:
                return d

        return clean(rule.model_dump())

    @classmethod
    def from_rules(cls, current_rules: List[Rule], desired_rules: List[Rule]) -> "DiffResult":
        to_add = []
        to_update = []
        to_delete = []

        # Index rules by ID
        current_map = {r.ID: r for r in current_rules}
        desired_map = {r.ID: r for r in desired_rules}

        # Detect added or updated rules
        for rid, desired_rule in desired_map.items():
            if rid not in current_map:
                to_add.append(desired_rule)
            else:
                cur_norm = cls._normalize_rule(current_map[rid])
                des_norm = cls._normalize_rule(desired_rule)
                if cur_norm != des_norm:
                    to_update.append({"before": current_map[rid], "after": desired_rule})

        # Detect deleted rules
        for rid, cur_rule in current_map.items():
            if rid not in desired_map:
                to_delete.append(cur_rule)

        return cls(RuleChange(to_add=to_add, to_update=to_update, to_delete=to_delete))
