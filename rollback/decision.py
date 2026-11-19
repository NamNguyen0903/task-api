
from enum import Enum


class RollbackDecision(str, Enum):
    NO_ROLLBACK = "no_rollback"
    ROLLBACK_CANDIDATE = "rollback_candidate"
    MANUAL_REVIEW = "manual_review"


def decide_rollback(
    good_deploy_id: str,
    new_deploy_id: str,
    deployments: list[dict],
) -> RollbackDecision:

    if not good_deploy_id or not new_deploy_id:
        return RollbackDecision.MANUAL_REVIEW

    live_ids = [
        item.get("deploy", item).get("id")
        for item in deployments
        if item.get("deploy", item).get("status") == "live"
    ]

    if len(live_ids) != 1:
        return RollbackDecision.MANUAL_REVIEW

    live_id = live_ids[0]

    if live_id == good_deploy_id:
        return RollbackDecision.NO_ROLLBACK

    if live_id == new_deploy_id:
        return RollbackDecision.ROLLBACK_CANDIDATE

    return RollbackDecision.MANUAL_REVIEW
