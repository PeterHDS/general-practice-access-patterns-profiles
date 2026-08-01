"""Immutable names in the GPAP² analytical contract.

Feature lists and model controls are loaded from the reference configuration.
Only semantic names that define the outcome-composition API live here.
"""

IDENTIFIER = "practice_code_standardised"

OUTCOME_SHARE_COLUMNS = (
    "cbt_answered_share_cbt003",
    "cbt_missed_share",
    "cbt_ivr_share",
    "cbt_callback_request_share",
)

NHS_OUTCOME_ILR_NAMES = (
    "ilr_dealt_vs_missed",
    "ilr_answered_vs_ivr_callback",
    "ilr_ivr_vs_callback",
)

FORBIDDEN_HISTORICAL_FEATURES = ("gpad_1_to_7_days_share",)
REQUIRED_BOOKING_FEATURES = ("gpad_1_day_share", "gpad_2_to_7_days_share")
