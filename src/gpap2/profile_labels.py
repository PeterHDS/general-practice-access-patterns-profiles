"""Authoritative reader-facing labels for the frozen national profiles."""

PROFILE_LABELS = {
    1: "Lower recorded activity, higher DNA and shorter-delay shares",
    2: "Higher face-to-face share, longer delay and lower OCS activity",
    3: "Higher recorded activity, higher same-day share and greater variation",
}

PROFILE_SHORT_LABELS = {
    profile: f"Profile {profile}: {label}" for profile, label in PROFILE_LABELS.items()
}

SUPERSEDED_PUBLIC_PHRASES = ("intermediate delay", "intermediate-delay")
