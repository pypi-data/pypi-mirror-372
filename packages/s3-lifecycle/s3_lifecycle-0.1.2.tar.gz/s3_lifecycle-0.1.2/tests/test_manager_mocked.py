from unittest.mock import MagicMock

from src.s3_lifecycle import LifecycleManager
from src.s3_lifecycle.policy import LifecyclePolicy

def test_fetch_current_empty():
    mock_client = MagicMock()
    mock_client.get_bucket_lifecycle_configuration.side_effect = \
        mock_client.exceptions.NoSuchLifecycleConfiguration = Exception()

    mgr = LifecycleManager()
    mgr.fetch_current = lambda b: LifecyclePolicy(Rules=[])
    result = mgr.fetch_current("fake-bucket")
    assert isinstance(result, LifecyclePolicy)
    assert result.Rules == []

def test_apply_dry_run(capsys):
    desired = LifecyclePolicy.from_dict({
        "Rules": [
            {
                "ID": "ruleX",
                "Filter": {"Prefix": "data/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 60, "StorageClass": "GLACIER"}]
            }
        ]
    })
    mgr = LifecycleManager()
    mgr.fetch_current = lambda b: LifecyclePolicy(Rules=[])
    delta = mgr.compute("bucket", desired)
    mgr.apply("bucket", delta, desired, dry_run=True)
    captured = capsys.readouterr()
    assert "Dry-run mode" in captured.out
