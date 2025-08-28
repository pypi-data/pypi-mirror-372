from src.s3_lifecycle.policy import LifecyclePolicy
from src.s3_lifecycle import LifecycleManager

class DummyManager(LifecycleManager):
    def __init__(self, current_policy_dict):
        super().__init__()
        self._current = LifecyclePolicy.from_dict(current_policy_dict)

    def fetch_current(self, bucket_name: str):
        return self._current

def test_diff_no_change():
    desired = {
        "Rules": [
            {
                "ID": "rule1",
                "Filter": {"Prefix": "logs/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
            }
        ]
    }
    mgr = DummyManager(desired)
    delta = mgr.compute("bucket", LifecyclePolicy.from_dict(desired))
    assert delta.summary() == "No changes"

def test_diff_add_rule():
    current = {"Rules": []}
    desired = {
        "Rules": [
            {
                "ID": "rule1",
                "Filter": {"Prefix": "logs/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
            }
        ]
    }
    mgr = DummyManager(current)
    delta = mgr.compute("bucket", LifecyclePolicy.from_dict(desired))
    assert "Add 1 rule" in delta.summary()

def test_diff_update_rule():
    current = {
        "Rules": [
            {
                "ID": "rule1",
                "Filter": {"Prefix": "logs/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 30, "StorageClass": "STANDARD_IA"}]
            }
        ]
    }
    desired = {
        "Rules": [
            {
                "ID": "rule1",
                "Filter": {"Prefix": "logs/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
            }
        ]
    }
    mgr = DummyManager(current)
    delta = mgr.compute("bucket", LifecyclePolicy.from_dict(desired))
    assert "Update 1 rule" in delta.summary()

def test_diff_delete_rule():
    current = {
        "Rules": [
            {
                "ID": "rule1",
                "Filter": {"Prefix": "logs/"},
                "Status": "Enabled",
                "Transitions": [{"Days": 30, "StorageClass": "GLACIER"}]
            }
        ]
    }
    desired = {"Rules": []}
    mgr = DummyManager(current)
    delta = mgr.compute("bucket", LifecyclePolicy.from_dict(desired))
    assert "Delete 1 rule" in delta.summary()
