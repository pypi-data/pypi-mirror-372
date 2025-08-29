import json
import boto3
import botocore

from .policy import LifecyclePolicy
from .diff import DiffResult, RuleChange
from .validators import validate_policy
from .exceptions import ApplyError, DiffError, FetchError


class LifecycleManager:
    def __init__(self, client=None):
        self.client = client or boto3.client("s3")

    def _get_current_policy(self, bucket: str) -> dict:
        try:
            return self.client.get_bucket_lifecycle_configuration(Bucket=bucket)
        except botocore.exceptions.ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code == "NoSuchLifecycleConfiguration":
                # No lifecycle set yet → treat as empty
                return {"Rules": []}
            elif error_code == "NoSuchBucket":
                raise FetchError(f"Bucket '{bucket}' does not exist", details=e.response)
            else:
                raise FetchError("Failed to fetch lifecycle configuration", details=e.response)

    def fetch_current(self, bucket: str) -> LifecyclePolicy:
        """Public method to fetch current lifecycle as LifecyclePolicy."""
        data = self._get_current_policy(bucket)
        return LifecyclePolicy.from_dict(data)

    @staticmethod
    def _normalize_dict(d: dict) -> dict:
        return json.loads(json.dumps(d, sort_keys=True))

    def compute(self, bucket_name: str, desired_policy: LifecyclePolicy) -> DiffResult:
        try:
            current = self.fetch_current(bucket_name)
        except Exception as e:
            raise DiffError(f"Failed to fetch current lifecycle for diff: {e}") from e

        to_add = []
        to_delete = []
        to_update = []

        current_rules = {r.ID: r for r in current.Rules}
        desired_rules = {r.ID: r for r in desired_policy.Rules}

        for rid, desired_rule in desired_rules.items():
            if rid not in current_rules:
                to_add.append(desired_rule)
            else:
                cur_norm = self._normalize_dict(current_rules[rid].model_dump())
                des_norm = self._normalize_dict(desired_rule.model_dump())
                if cur_norm != des_norm:
                    to_update.append({"before": current_rules[rid], "after": desired_rule})

        for rid, current_rule in current_rules.items():
            if rid not in desired_rules:
                to_delete.append(current_rule)

        rule_change = RuleChange(to_add=to_add, to_update=to_update, to_delete=to_delete)
        return DiffResult(rule_change)

    def apply(
            self,
            bucket_name: str,
            delta: DiffResult,
            desired_policy: LifecyclePolicy,
            dry_run: bool = True
    ) -> None:
        """
        Apply the lifecycle delta to the bucket.
        Automatically removes None values to comply with boto3 parameter validation.
        """
        validate_policy(desired_policy)
        # If you can try before
        if dry_run:
            print(f"Dry-run mode: would apply {delta.summary()} to bucket '{bucket_name}'")
            return

        def _sanitize_policy_for_boto3(policy_dict: dict) -> dict:
            """Remove None fields from policy dict that boto3 does not accept."""
            clean = {"Rules": []}
            for rule in policy_dict.get("Rules", []):
                clean_rule = {k: v for k, v in rule.items() if v is not None}
                if "Transitions" in clean_rule:
                    clean_rule["Transitions"] = [
                        {k: v for k, v in t.items() if v is not None}
                        for t in clean_rule["Transitions"]
                    ]
                if "Expiration" in clean_rule and clean_rule["Expiration"] is None:
                    del clean_rule["Expiration"]
                clean["Rules"].append(clean_rule)
            return clean

        try:
            clean_policy = _sanitize_policy_for_boto3(desired_policy.dict())
            self.client.put_bucket_lifecycle_configuration(
                Bucket=bucket_name,
                LifecycleConfiguration=clean_policy
            )
        except Exception as e:
            raise ApplyError(f"Failed to apply lifecycle policy: {e}") from e
