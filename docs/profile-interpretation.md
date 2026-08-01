# National access-pressure profiles

## Selected specification

The primary specification uses K-Means with three clusters on fourteen validated OCS and GPAD features. Activity-volume and change measures receive `log1p`; all features receive robust median/IQR scaling. The reference fit uses seed 2026, 100 initialisations, a maximum of 500 iterations and the Lloyd algorithm.

## Profile descriptions

### Profile 1: Lower recorded activity, higher DNA and shorter-delay shares

This group contains 1,753 practices. Its defining medians combine lower recorded OCS and GPAD activity, a comparatively higher did-not-attend share and greater weight in the shorter booking-delay bands, including next day and two to seven days.

### Profile 2: Higher face-to-face share, longer delay and lower OCS activity

This group contains 2,312 practices. It combines a stronger face-to-face appointment pattern with longer booking intervals and lower recorded OCS activity.

### Profile 3: Higher recorded activity, higher same-day share and greater variation

This group contains 2,002 practices. It combines higher recorded activity, more same-day appointments and greater month-to-month variation.

The descriptions summarise cluster medians in original units. They are not quality grades or performance rankings.

![Relative median characteristics and assignment-uncertainty signals for the three national profiles](../outputs/figures/national_profile_characteristics_and_uncertainty.png)

## Stability and uncertainty

Across 100 seeded K-Means repetitions, the median adjusted Rand index against the reference solution was 0.9599 and the fifth percentile was 0.9165. Median pairwise agreement was 0.9409. The minimum cluster-retention value was 0.9295.

Alternative algorithms and temporal reconstructions recover related but non-identical structure. Assignment uncertainty is retained for interpretation; no practice is removed solely because its profile assignment is less secure.
