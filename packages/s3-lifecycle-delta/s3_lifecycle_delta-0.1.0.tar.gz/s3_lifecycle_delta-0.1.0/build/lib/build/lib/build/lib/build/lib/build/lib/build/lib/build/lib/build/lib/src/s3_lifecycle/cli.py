import argparse
import json
from policy import LifecyclePolicy
from manager import LifecycleManager

def main():
    parser = argparse.ArgumentParser(description="S3 Lifecycle Delta Tool")
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--policy-file", required=True)
    parser.add_argument("--apply", action="store_true", help="Actually apply instead of dry-run")
    args = parser.parse_args()

    with open(args.policy_file) as f:
        policy_dict = json.load(f)

    desired = LifecyclePolicy.from_dict(policy_dict)
    manager = LifecycleManager()
    delta = manager.compute(args.bucket, desired)
    manager.apply(args.bucket, delta, desired, dry_run=not args.apply)

if __name__ == "__main__":
    main()
