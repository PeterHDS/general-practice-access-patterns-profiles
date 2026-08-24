# GP Patient Survey interpretation

## 1. Purpose

GPAP² uses the GP Patient Survey (GPPS) to add a patient-reported perspective to profiles defined from recorded OCS and GPAD activity. The activity data describe how recorded online consultation and appointment activity was configured. GPPS describes how sampled patients reported selected aspects of their experience at the practice.

GPPS was linked only after the three national profiles had been fixed. It therefore helps interpret the profiles; it did not define the clusters or change any practice assignment. This separation matters because recorded activity volume, channel mix and booking configuration cannot on their own describe how patients experienced access.

### Evidence chain

| Stage | Evidence and operation | Repository authority |
|---|---|---|
| Source | NHS England GP Patient Survey 2026 practice estimates; fieldwork 2 January to 13 April 2026 and publication 9 July 2026 | [Source and reuse register](../DATA_LICENSE.md), [official sources](../references/official-sources.md) |
| Preparation | Official practice estimates were retained in percentage points, with question-specific evaluated denominators, suppression/status handling and response-base validity rules | [External-context reproduction authority](reproducibility-releases.md) |
| Linkage | Valid practice estimates were linked by practice identifier to the frozen 6,067-practice national profile assignments | [Canonical claim authority](../outputs/tables/claim_to_evidence_matrix.csv) |
| Comparison | Measure-specific profile medians and distributions were reported; primary comparisons used rank-based effect-size descriptions and unadjusted OLS with HC3 uncertainty, with prespecified sensitivity analyses | [Numeric profile summaries](../outputs/tables/numeric_profile_descriptive_summary.csv), [GPPS precision summary](../outputs/tables/gpps_precision_profile_summary.csv) |
| Presentation | The retained aggregate authorities are loaded and checksum-validated by the external-context notebook | [External-context notebook](../notebooks/06_interpret_profiles_with_external_context.ipynb), [patient-experience figure](../outputs/figures/patient_experience_by_profile.png) |
| Claim boundary | Patient-experience claims are classified as descriptive, associatively examinable, or requiring additional evidence | [Evidence Map](evidence-map.md#patient-experience) |

The public repository distributes aggregate profile summaries rather than the practice-level GPPS estimates. The complete controlled preparation and model evidence is preserved in the external-context reproduction package identified by filename and SHA-256 in the [reproducibility release register](reproducibility-releases.md).

## 2. GPPS measures used

The five primary outcomes below are the measures shown in the repository's patient-experience figure and profile summary. Values remain in their published percentage-point scale. Primary descriptive validity required an evaluated unweighted response base of at least 10; a base-at-least-30 sensitivity flag was retained. Suppressed or unavailable evidence was not interpreted as zero.

| GPPS measure | Repository variable | Meaning | Why included | Interpretation boundary |
|---|---|---|---|---|
| Overall practice experience | `gpps_overall_practice_experience_good_pct` | Percentage of evaluated Q32 respondents reporting a very good or fairly good overall experience of the practice | Provides a broad patient-reported experience measure | Not a complete measure of practice quality, objective performance or the effect of digital access |
| Contact experience | `gpps_contact_experience_good_pct` | Percentage of evaluated Q16 respondents reporting a very good or fairly good experience of contacting the practice | Relates most directly to the experience of making contact | Does not establish suitable care, request resolution or complete access quality |
| Preferred-professional continuity fulfilled | `gpps_preferred_professional_continuity_fulfilled_pct` | Percentage of eligible evaluated Q7 respondents who usually saw or spoke to their preferred healthcare professional when requested | Adds a continuity dimension conditional on having and requesting a preferred professional | Does not measure continuity for all patients or establish clinical quality; Q6 preferred-professional prevalence is descriptive context rather than the outcome itself |
| Support for managing long-term conditions | `gpps_long_term_condition_support_good_pct` | Percentage of eligible evaluated Q43 respondents reporting enough support from local services or organisations to manage their conditions | Adds experience of wider support for people managing long-term conditions | Is not limited to support from the GP practice and does not measure a clinical outcome, unmet appointment need or access success |
| Next-step clarity | `gpps_next_step_clarity_pct` | Percentage in the official evaluated Q12 denominator reporting that they knew the next step after contacting the practice | Captures clarity following contact | Does not establish that every respondent made contact, that the next step was appropriate or completed, or that care was obtained |

Two further GPPS evidence families provide bounded descriptive context in the Evidence Map:

- `gpps_unable_to_contact_pct` reports the percentage saying they could not contact the practice. It is not a measure of total unmet need.
- Q18 records whether respondents reported any, none, or one of eight overlapping actions before trying to obtain an appointment. These options were described separately and were not summed as though they were mutually exclusive outcomes.

## 3. Profile-level GPPS comparison

The table reports the practice-level median percentage for each valid measure, rounded to one decimal place from [`gpps_precision_profile_summary.csv`](../outputs/tables/gpps_precision_profile_summary.csv). The valid number of practices varies slightly by measure because the response-base and source-validity rules were applied separately.

| Profile | GPPS measure | Median (valid practices) | Interpretation |
|---|---|---:|---|
| Profile 1 | Overall practice experience | 76.9% (1,752) | Lower median than Profiles 2 and 3 in this cross-sectional practice comparison |
| Profile 1 | Contact experience | 73.7% (1,752) | Similar median to Profile 3 and lower than Profile 2 |
| Profile 1 | Preferred-professional continuity fulfilled | 42.2% (1,748) | Between Profiles 2 and 3 |
| Profile 1 | Support for managing long-term conditions | 67.7% (1,751) | Lower median than Profiles 2 and 3 |
| Profile 1 | Next-step clarity | 83.3% (1,752) | Lower median than Profiles 2 and 3 |
| Profile 2 | Overall practice experience | 81.6% (2,312) | Highest of the three profile medians |
| Profile 2 | Contact experience | 78.2% (2,312) | Highest of the three profile medians |
| Profile 2 | Preferred-professional continuity fulfilled | 44.4% (2,309) | Highest of the three profile medians |
| Profile 2 | Support for managing long-term conditions | 73.5% (2,312) | Highest of the three profile medians |
| Profile 2 | Next-step clarity | 87.1% (2,312) | Highest of the three profile medians |
| Profile 3 | Overall practice experience | 78.4% (2,002) | Between Profiles 1 and 2 |
| Profile 3 | Contact experience | 73.6% (2,002) | Similar median to Profile 1 and lower than Profile 2 |
| Profile 3 | Preferred-professional continuity fulfilled | 37.4% (1,997) | Lowest of the three profile medians |
| Profile 3 | Support for managing long-term conditions | 70.8% (2,002) | Between Profiles 1 and 2 |
| Profile 3 | Next-step clarity | 85.6% (2,002) | Between Profiles 1 and 2 |

![GP Patient Survey estimates by fixed national profile](../outputs/figures/patient_experience_by_profile.png)

These are profile-level descriptive comparisons, not a ranking exercise. The validated claim authority records small rank-based effect sizes for all five primary outcomes. The differences therefore add context to the recorded-activity profiles without turning them into quality grades.

## 4. What GPPS adds to interpretation

OCS, GPAD and CBT describe recorded activity: online submissions, appointment configuration and available telephony evidence. GPPS adds reported experience of the practice, contacting it, continuity, support and clarity after contact. Together, these sources allow the recorded-activity profiles to be interpreted alongside a distinct experience layer rather than treating operational intensity as a proxy for access quality.

The comparison shows that the activity profiles carry different patient-experience distributions, but those distributions do not follow directly from activity volume alone. For example, Profile 2 has lower recorded OCS activity and longer booking delays while showing the highest median for each of the five selected GPPS measures. This is a cross-sectional association and does not identify the mechanism behind the pattern.

GPPS also improves evidence discipline. It identifies which patient-experience propositions can be examined with the available practice-level data and which stronger propositions still require patient-level longitudinal evidence and a credible causal comparator.

## 5. Evidence boundaries

| GPPS can support | GPPS cannot establish |
|---|---|
| Differences in practice-level patient-reported experience across fixed profiles | That a profile caused better or worse patient experience |
| A patient-experience dimension that is separate from recorded activity | That recorded activity represents total demand, unmet need or access quality |
| Measure-specific distributions, medians, uncertainty and bounded practice-level associations | Individual patient pathways, outcomes or mechanisms |
| Descriptive context about inability to contact and actions before seeking an appointment | Total unmet need, successful resolution, avoidance or failed access |
| Evaluation of whether activity-profile interpretations are coherent with independent experience evidence | A complete quality ranking of practices or profiles |
| Ecological context for considering equity questions where the relevant evidence is present | Individual-level equity effects or causal improvement in equity |

Further limitations include survey non-response, residual confounding, measure-specific denominators and timing differences between GPPS fieldwork and the April 2025 to March 2026 activity window. Missing or suppressed survey evidence remains missing; it is not zero activity or zero experience.

## 6. Relationship to the Evidence Map

GPPS directly informs the Evidence Map's **patient experience** domain:

- B04–B08 assess the five primary outcomes as practice-level associations with fixed profiles.
- B09 and B10 retain unable-to-contact and pre-appointment-action measures as descriptive context.
- E02 records that the available evidence cannot establish that digital access improves patient experience.

GPPS also contributes to bounded **access interpretation** by preventing recorded activity from being read as patient experience. It may inform ecological **equity interpretation** when linked to supported contextual measures, but it does not supply individual characteristics, individual care journeys or a causal design.

The canonical wording, represented population and additional evidence required for each proposition remain governed by the [42-claim authority](../outputs/tables/claim_to_evidence_matrix.csv) and its reader-facing [Evidence Map](evidence-map/index.html).
