
import pytest

from rollback.decision import (
    RollbackDecision,
    decide_rollback,
)


@pytest.mark.parametrize(
    "good_id,new_id,deployments,expected",
    [
        (
            "dep-good123",
            "dep-new456",
            [
                {"deploy": {"id": "dep-good123", "status": "live"}},
                {"deploy": {"id": "dep-new456", "status": "update_failed"}},
            ],
            RollbackDecision.NO_ROLLBACK,
        ),
        (
            "dep-good123",
            "dep-new456",
            [
                {"deploy": {"id": "dep-new456", "status": "live"}},
                {"deploy": {"id": "dep-good123", "status": "deactivated"}},
            ],
            RollbackDecision.ROLLBACK_CANDIDATE,
        ),
        (
            "dep-good123",
            "dep-new456",
            [
                {"deploy": {"id": "dep-new456", "status": "update_failed"}},
                {"deploy": {"id": "dep-good123", "status": "deactivated"}},
            ],
            RollbackDecision.MANUAL_REVIEW,
        ),
    ],
)
def test_rollback_decision(
    good_id, new_id, deployments, expected
):
    result = decide_rollback(
        good_id, new_id, deployments
    )

    assert result == expected
