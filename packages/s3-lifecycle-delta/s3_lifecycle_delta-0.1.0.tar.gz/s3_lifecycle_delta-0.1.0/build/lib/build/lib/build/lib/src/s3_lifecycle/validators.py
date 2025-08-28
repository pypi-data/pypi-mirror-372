from .policy import LifecyclePolicy
from .exceptions import ValidationError


def validate_policy(policy: LifecyclePolicy) -> None:
    """
    Validates the s3_lifecycle policy according to AWS constraints.
    Raises ValidationError if invalid.
    """
    for rule in policy.Rules:
        if not rule.Transitions and not rule.Expiration:
            raise ValidationError(
                f"Rule '{rule.ID}' must have at least Transitions or Expiration",
                details={"rule_id": rule.ID}
            )
