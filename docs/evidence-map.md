# GPAP² Evidence Map

This text view presents the same 42 claims as the interactive evidence map. The canonical machine-readable authority is [`claim_to_evidence_matrix.csv`](../outputs/tables/claim_to_evidence_matrix.csv).

## Access

What do recorded activity patterns and their robustness show?

### A01: National OCS–GPAD profiles exist.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Fixed three-profile membership derived from 14 annual OCS and GPAD features.
- **Population:** 6,067 practices with complete 12-month primary features
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** K-Means clustering; frozen assignment reconciliation
- **Main result:** 6,067 practices were assigned once to three profiles: 1,753, 2,312 and 2,002.
- **Permitted wording:** Three national practice-level recorded-activity profiles were identified.
- **Prohibited wording:** The profiles are performance tiers or direct measures of access quality.
- **Additional evidence required:** No additional data are required for the bounded descriptive statement.

### A02: Profiles are sufficiently stable for cautious descriptive use.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Assignment uncertainty across silhouette, GMM posterior evidence and resampling.
- **Population:** 6,067 practices
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** Silhouette, GMM posterior, algorithm disagreement and temporal resampling
- **Main result:** 1,966 practices (32.4%) carry an interpretive-caution flag.
- **Permitted wording:** The profiles support cautious descriptive use with explicit uncertainty.
- **Prohibited wording:** The profiles are definitive, permanent or equally certain for every practice.
- **Additional evidence required:** Longer longitudinal replication would test persistence beyond the study year.

### A03: Alternative algorithms recover related but non-identical structure.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Aligned membership comparison between primary K-Means and spherical GMM.
- **Population:** 6,067 practices
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** Aligned K-Means versus spherical-GMM assignment comparison
- **Main result:** 1,411 practices (23.3%) differed between aligned K-Means and GMM assignments.
- **Permitted wording:** Alternative algorithms recovered related but non-identical structure.
- **Prohibited wording:** Alternative algorithms reproduced identical membership.
- **Additional evidence required:** No additional longitudinal data are required to decide whether these observed assignments were identical.

### A04: Feature sensitivity supports a related, non-identical profile interpretation.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Quarter-1 14-feature versus 12-feature assignment comparison.
- **Population:** 5,677 quarter-eligible practices
- **Population scope:** Directly represents the stated shorter-period calculable cohort; it is smaller than the 6,067-practice annual population.
- **Method:** Assignment agreement and adjusted Rand index
- **Main result:** Q1 assignment agreement was 91.6% and ARI was 0.761.
- **Permitted wording:** The reduced feature set recovered broadly related structure with some reassignment.
- **Prohibited wording:** Feature choice had no effect on membership.
- **Additional evidence required:** Replication with future releases would test whether feature sensitivity persists.

### A05: Temporal robustness supports the annual solution with material within-year variation.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Half-year and quarterly recurrence of profile structure.
- **Population:** 5,924 half-year-eligible and 5,677 quarter-eligible practices
- **Population scope:** Directly represents the stated shorter-period calculable cohort; it is smaller than the 6,067-practice annual population.
- **Method:** Temporal resampling, adjusted Rand index and transition summaries
- **Main result:** Median reference ARI was 0.960 for H1 and 0.968 for H2; common-sample H1/H2 ARI was 0.464.
- **Permitted wording:** The annual profiles recur strongly within half-years, alongside meaningful within-year reassignment.
- **Prohibited wording:** Every practice retained the same profile throughout the year.
- **Additional evidence required:** Additional years are required for long-run persistence claims.

### A06: CBT inbound sensitivity produces a related profile structure in submitting practices.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Assignment change after adding recorded CBT inbound activity indicators.
- **Population:** 3,020 CBT inbound-submitting practices
- **Population scope:** Directly represents the 3,020-practice CBT inbound cohort; evidence availability is geographically concentrated.
- **Method:** Restricted-cohort aligned assignment sensitivity
- **Main result:** 571 of 3,020 practices changed aligned assignment after CBT inbound features were added.
- **Permitted wording:** Adding CBT inbound indicators altered some assignments within the submitting-practice cohort.
- **Prohibited wording:** CBT sensitivity represents all English practices or total telephone demand.
- **Additional evidence required:** Consistent national CBT submission would improve generalisability.

### A07: CBT outcome-complete sensitivity is composition-dependent within its restricted cohort.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Assignment change across CBT outcome representations.
- **Population:** 1,456 CBT outcome-complete practices
- **Population scope:** Directly represents the 1,456-practice outcome-complete CBT cohort; selection is strongly concentrated geographically.
- **Method:** Restricted-cohort raw-share and ILR assignment sensitivity
- **Main result:** 729 practices changed from 17 to raw-21 features, while 52 changed from 17 to ILR-20 features.
- **Permitted wording:** CBT outcome sensitivity depended on feature representation in the complete-outcome cohort.
- **Prohibited wording:** CBT outcomes produce a unique national profile solution.
- **Additional evidence required:** More complete CBT outcome reporting would improve generalisability.

### B01: OCS activity represents visible online-route activity.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Recorded OCS submissions and their clinical, administrative and residual composition.
- **Population:** 6,067 practices in the primary 12-month profile matrix
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** Validated annual feature construction and descriptive profile use
- **Main result:** OCS activity and composition contribute directly to the 14-feature primary matrix.
- **Permitted wording:** OCS measures visible recorded online-route activity.
- **Prohibited wording:** OCS submissions equal total demand, successful access or resolved need.
- **Additional evidence required:** Request-level linkage would be required for resolution and journey claims.

### B02: GPAD represents recorded appointment activity and configuration.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Recorded appointment rate, mode, DNA and mutually exclusive booking-delay shares.
- **Population:** 6,067 practices in the primary 12-month profile matrix
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** Validated annual feature construction and descriptive profile use
- **Main result:** GPAD appointment activity and configuration contribute directly to the 14-feature primary matrix.
- **Permitted wording:** GPAD measures recorded appointment activity and configuration.
- **Prohibited wording:** GPAD measures total demand or time from first request to resolution.
- **Additional evidence required:** Linked request and appointment journeys would be required for end-to-end access claims.

### B03: CBT provides recorded telephone-route activity indicators among submitting practices.

- **Evidence status:** ▲ Major qualification required
- **Observed construct:** Recorded inbound and outcome-related CBT indicators under supplier and completeness restrictions.
- **Population:** 3,020 inbound-submitting and 1,456 outcome-complete practices
- **Population scope:** Telephone-route evidence is available in nested cohorts: inbound indicators represent 3,020 practices, while outcome-composition evidence represents the 1,456-practice outcome-complete subset. Both are restricted reporting populations rather than national telephony coverage.
- **Method:** Restricted-cohort descriptive sensitivity; no GPPS regression
- **Main result:** CBT indicators changed 571 inbound-cohort assignments; outcome sensitivities were evaluated in 1,456 practices.
- **Permitted wording:** CBT provides recorded telephone-route activity indicators among submitting practices.
- **Prohibited wording:** CBT measures total telephone pressure or represents all practices.
- **Additional evidence required:** Consistent national submission plus call-journey linkage would support stronger claims.

### C01: Profiles differ by registered-list size.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Registered list size
- **Population:** 6,067 descriptively; 5,774 in the complete primary MNLogit cohort
- **Population scope:** The canonical cohort distinguishes the descriptive practice population from the smaller complete-case contextual model; each result represents its stated population.
- **Method:** Kruskal-Wallis/Dunn effect sizes; robust-covariance MNLogit and average marginal effects
- **Main result:** Log registered list size was included in the primary MNLogit model.
- **Permitted wording:** Registered-list size was associated with profile membership.
- **Prohibited wording:** The contextual characteristic caused profile membership or individual access outcomes.
- **Additional evidence required:** Longitudinal multilevel or quasi-experimental data are required for causal interpretation.

### C08: Assignment uncertainty varied descriptively across ICBs.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** ICB composition of practice-level interpretive-caution flags.
- **Population:** 6,067 practices across 42 ICBs
- **Population scope:** Represents the 6,067 national practices aggregated across 42 March 2026 ICB organisations.
- **Method:** Descriptive ICB aggregation only
- **Main result:** The ICB-level share carrying interpretive caution was mapped descriptively.
- **Permitted wording:** Assignment uncertainty varied descriptively across ICBs.
- **Prohibited wording:** Assignment uncertainty is geographically patterned or shows spatial clustering.
- **Additional evidence required:** Additional algorithms and years would improve uncertainty characterisation.

### C09: Evidence availability differs across profiles.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Source-row presence and primary/sensitivity-valid coverage by profile and source family.
- **Population:** 6,067 practices with measure-specific validity
- **Population scope:** Directly represents the 6,067 practices in the national analytical cohort unless the claim records a narrower valid population.
- **Method:** Descriptive coverage and source-specific availability tests
- **Main result:** Coverage varies by source and profile; missing evidence was retained as missing rather than zero-filled.
- **Permitted wording:** External evidence availability differed for some source-profile combinations.
- **Prohibited wording:** Missing external evidence indicates low activity or poor performance.
- **Additional evidence required:** More complete source submission would reduce availability bias.

### D01: The sources measure total demand.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Total patient demand across all routes
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** The public sources record selected activities, not all demand.
- **Permitted wording:** The current data do not support the claim: The sources measure total demand.
- **Prohibited wording:** The sources measure total demand.
- **Additional evidence required:** linked demand and contact-attempt records

### D02: The profiles identify unmet need.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Unmet need
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** No direct unmet-need construct is present.
- **Permitted wording:** The current data do not support the claim: The profiles identify unmet need.
- **Prohibited wording:** The profiles identify unmet need.
- **Additional evidence required:** patient-reported unmet need and outcomes

### D06: Requests were resolved.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Request resolution
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** No request-resolution outcome is available.
- **Permitted wording:** The current data do not support the claim: Requests were resolved.
- **Prohibited wording:** Requests were resolved.
- **Additional evidence required:** request-level outcome and closure status

### D07: The data measure timeliness from first request to resolution.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Elapsed time from first request to resolution
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** The required start and resolution timestamps are absent.
- **Permitted wording:** The current data do not support the claim: The data measure timeliness from first request to resolution.
- **Prohibited wording:** The data measure timeliness from first request to resolution.
- **Additional evidence required:** time-stamped linked request-to-resolution journeys

### D11: Digital access causally changes outcomes.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Causal effect of digital access
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** The study is observational, aggregate and cross-sectional.
- **Permitted wording:** The current data do not support the claim: Digital access causally changes outcomes.
- **Prohibited wording:** Digital access causally changes outcomes.
- **Additional evidence required:** a credible causal design with exposure timing and counterfactual

### D12: Supplier products cause profile differences.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Causal supplier-product effect
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** Supplier association is confounded by selection and implementation.
- **Permitted wording:** The current data do not support the claim: Supplier products cause profile differences.
- **Prohibited wording:** Supplier products cause profile differences.
- **Additional evidence required:** product-level exposure, implementation timing and causal comparison

### E01: Digital access improves access.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Causal improvement in access
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-boundary assessment only
- **Main result:** GPAD/OCS activity and GPPS associations do not establish improvement.
- **Permitted wording:** The study does not establish that digital access improves access.
- **Prohibited wording:** Digital access improves access.
- **Additional evidence required:** request-level access outcomes, exposure timing and a credible comparator

## Patient experience

How do fixed profiles relate to reported patient experience?

### B04: Profiles differ in overall practice experience.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Overall practice experience rated good
- **Population:** 6,066 practices with a valid measure
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis effect-size description; unadjusted OLS HC3; prespecified sensitivities
- **Main result:** Overall-experience differences were small in rank-based effect-size terms.
- **Permitted wording:** Profiles were associated with differences in practice-level overall-experience estimates.
- **Prohibited wording:** The profile caused better or worse patient experience.
- **Additional evidence required:** Longitudinal patient-level linkage and a causal design are required for improvement claims.

### B05: Profiles differ in contact experience.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Experience of contacting the practice rated good
- **Population:** 6,066 practices with a valid measure
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis effect-size description; unadjusted OLS HC3; prespecified sensitivities
- **Main result:** Contact-experience differences were small in rank-based effect-size terms.
- **Permitted wording:** Profiles were associated with differences in practice-level contact-experience estimates.
- **Prohibited wording:** The profile caused better or worse patient experience.
- **Additional evidence required:** Longitudinal patient-level linkage and a causal design are required for improvement claims.

### B06: Profiles differ in continuity fulfilment.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Preferred-professional continuity fulfilled, interpreted with Q6 preferred-professional prevalence as descriptive context
- **Population:** 6,054 practices with a valid measure
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis effect-size description; unadjusted OLS HC3; prespecified sensitivities
- **Main result:** Continuity-fulfilment differences were small and Q6 prevalence was retained as context only.
- **Permitted wording:** Profiles were associated with differences in practice-level continuity fulfilment; Q6 prevalence is descriptive context.
- **Prohibited wording:** The profile caused better or worse patient experience.
- **Additional evidence required:** Longitudinal patient-level linkage and a causal design are required for improvement claims.

### B07: Profiles differ in next-step clarity.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Reported clarity about the next step
- **Population:** 6,066 practices with a valid measure
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis effect-size description; unadjusted OLS HC3; prespecified sensitivities
- **Main result:** Next-step-clarity differences were small in rank-based effect-size terms.
- **Permitted wording:** Profiles were associated with differences in practice-level next-step clarity.
- **Prohibited wording:** The profile caused better or worse patient experience.
- **Additional evidence required:** Longitudinal patient-level linkage and a causal design are required for improvement claims.

### B08: Profiles differ in long-term-condition support.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Long-term-condition support rated good
- **Population:** 6,065 practices with a valid measure
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis effect-size description; unadjusted OLS HC3; prespecified sensitivities
- **Main result:** Long-term-condition-support differences were small in rank-based effect-size terms.
- **Permitted wording:** Profiles were associated with differences in practice-level long-term-condition support.
- **Prohibited wording:** The profile caused better or worse patient experience.
- **Additional evidence required:** Longitudinal patient-level linkage and a causal design are required for improvement claims.

### B09: Unable-to-contact prevalence provides descriptive contact context.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Practice-level percentage reporting inability to contact the practice.
- **Population:** 6,066 practices with valid unable-to-contact context
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Descriptive medians and bootstrap intervals only
- **Main result:** Profile-specific medians and bootstrap intervals were reported without a formal profile test.
- **Permitted wording:** Unable-to-contact prevalence provides bounded descriptive context.
- **Prohibited wording:** Unable-to-contact prevalence measures total unmet need.
- **Additional evidence required:** Patient-level contact-attempt and outcome linkage is needed for unmet-need claims.

### B10: Q18 describes reported pre-appointment actions.

- **Evidence status:** ● Descriptively supported
- **Observed construct:** Any/none and eight overlapping reported actions before trying to obtain an appointment.
- **Population:** 6,065 primary-valid practices; 6,063 base-at-least-30 sensitivity records
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Descriptive medians, bootstrap intervals and complement validation only
- **Main result:** Ten Q18 measures were summarised across three profiles; overlapping options were not summed.
- **Permitted wording:** Q18 describes reported actions before trying to obtain an appointment.
- **Prohibited wording:** Q18 actions measure unmet need or resolved demand.
- **Additional evidence required:** Patient-level reasons, outcomes and subsequent care are needed for stronger interpretation.

### E02: Digital access improves patient experience.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Causal improvement in patient experience
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-boundary assessment only
- **Main result:** GPPS supports practice-level association, not causal patient-experience improvement.
- **Permitted wording:** The study does not establish that digital access improves patient experience.
- **Prohibited wording:** Digital access improves patient experience.
- **Additional evidence required:** longitudinal patient-level experience linked to exposure and a causal comparator

## Workload

What can recorded activity and workforce context say about workload?

### C03: Profiles differ by GP workforce capacity.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Fully qualified GP FTE per 10,000 registered patients
- **Population:** 5,801 descriptively; 5,774 in the complete primary MNLogit cohort
- **Population scope:** The canonical cohort distinguishes the descriptive practice population from the smaller complete-case contextual model; each result represents its stated population.
- **Method:** Kruskal-Wallis/Dunn effect sizes; robust-covariance MNLogit and average marginal effects
- **Main result:** GP workforce capacity was included in the primary MNLogit model.
- **Permitted wording:** GP workforce capacity was associated with profile membership.
- **Prohibited wording:** The contextual characteristic caused profile membership or individual access outcomes.
- **Additional evidence required:** Longitudinal multilevel or quasi-experimental data are required for causal interpretation.

### C04: Profiles differ by non-GP workforce.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Direct patient care, nurse and other non-GP workforce capacity measures.
- **Population:** Nurse 5,615; direct patient care 5,265; administrative/non-clinical 5,711
- **Population scope:** Uses the measure-specific valid practice population recorded in the claim authority.
- **Method:** Kruskal-Wallis/Dunn effect sizes and bootstrap descriptive intervals
- **Main result:** Non-GP workforce measures were described and tested separately; they were not primary MNLogit predictors.
- **Permitted wording:** Non-GP workforce capacity differed across profiles in descriptive practice-level comparisons.
- **Prohibited wording:** Non-GP workforce caused profile membership or reduced workload.
- **Additional evidence required:** Longitudinal staffing, workload and activity linkage would support mechanism testing.

### D03: Digital access reduces workload.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Change in clinical and administrative workload
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** No workload outcome or causal counterfactual is present.
- **Permitted wording:** The current data do not support the claim: Digital access reduces workload.
- **Prohibited wording:** Digital access reduces workload.
- **Additional evidence required:** longitudinal staff-time and workload measures with a comparator

### D04: The profiles reveal hidden administrative workload.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Unrecorded administrative work
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** Hidden administrative work is not observed.
- **Permitted wording:** The current data do not support the claim: The profiles reveal hidden administrative workload.
- **Prohibited wording:** The profiles reveal hidden administrative workload.
- **Additional evidence required:** workflow logs, staff time and task-level administrative records

### D05: The data measure repeat contact.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Repeated contacts for the same episode
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** Records are not linked into patient episodes.
- **Permitted wording:** The current data do not support the claim: The data measure repeat contact.
- **Prohibited wording:** The data measure repeat contact.
- **Additional evidence required:** linked pseudonymised request/contact episodes

## Equity

Which practice-level inequalities can be examined with available context?

### C02: Profiles differ by age composition.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Registered population aged 65 years and over
- **Population:** 6,067 descriptively; 5,774 in the complete primary MNLogit cohort
- **Population scope:** The canonical cohort distinguishes the descriptive practice population from the smaller complete-case contextual model; each result represents its stated population.
- **Method:** Kruskal-Wallis/Dunn effect sizes; robust-covariance MNLogit and average marginal effects
- **Main result:** Age composition showed a large omnibus rank effect and was included in MNLogit.
- **Permitted wording:** Registered age composition was associated with profile membership.
- **Prohibited wording:** The contextual characteristic caused profile membership or individual access outcomes.
- **Additional evidence required:** Longitudinal multilevel or quasi-experimental data are required for causal interpretation.

### C05: Profiles differ by deprivation.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Patient-weighted average IMD 2025 score
- **Population:** 6,035 descriptively; 5,774 in the complete primary MNLogit cohort
- **Population scope:** The canonical cohort distinguishes the descriptive practice population from the smaller complete-case contextual model; each result represents its stated population.
- **Method:** Kruskal-Wallis/Dunn effect sizes; robust-covariance MNLogit and average marginal effects
- **Main result:** Deprivation was included in the primary MNLogit model.
- **Permitted wording:** Patient-weighted average IMD 2025 score was associated with profile membership.
- **Prohibited wording:** The contextual characteristic caused profile membership or individual access outcomes.
- **Additional evidence required:** Longitudinal multilevel or quasi-experimental data are required for causal interpretation.

### C06: Profiles differ by rurality.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Patient-weighted rural share
- **Population:** 6,051 descriptively; 5,774 in the complete primary MNLogit cohort
- **Population scope:** The canonical cohort distinguishes the descriptive practice population from the smaller complete-case contextual model; each result represents its stated population.
- **Method:** Kruskal-Wallis/Dunn effect sizes; robust-covariance MNLogit and average marginal effects
- **Main result:** Rurality was included in the primary MNLogit model.
- **Permitted wording:** Patient-weighted rural share was associated with profile membership.
- **Prohibited wording:** The contextual characteristic caused profile membership or individual access outcomes.
- **Additional evidence required:** Longitudinal multilevel or quasi-experimental data are required for causal interpretation.

### C07: Region and ICB profile composition varies.

- **Evidence status:** ◆ Associatively examinable
- **Observed construct:** Practice profile composition across seven regions and 42 March 2026 reference-period ICBs.
- **Population:** 6,067 practices across seven regions and 42 ICBs
- **Population scope:** Represents the 6,067 national practices aggregated across 42 March 2026 ICB organisations.
- **Method:** Bias-corrected Cramér’s V, bootstrap interval and fixed-margin permutation
- **Main result:** Bias-corrected Cramér’s V was 0.272 for region and 0.332 for ICB.
- **Permitted wording:** Profile composition varied across the frozen reference-period geographies.
- **Prohibited wording:** ICBs are ranked or the maps show performance.
- **Additional evidence required:** Patient-residence geography is needed for population-prevalence interpretation.

### D10: The analysis demonstrates individual-level equity.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Individual-level differential access and outcomes
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** Practice aggregates cannot establish individual equity.
- **Permitted wording:** The current data do not support the claim: The analysis demonstrates individual-level equity.
- **Prohibited wording:** The analysis demonstrates individual-level equity.
- **Additional evidence required:** individual-level protected characteristics, need, access and outcomes

### E03: Digital access improves equity.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Causal improvement in individual-level equity
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-boundary assessment only
- **Main result:** Deprivation, rurality and age provide ecological context, not individual-level equity improvement.
- **Permitted wording:** The study does not establish that digital access improves equity.
- **Prohibited wording:** Digital access improves equity.
- **Additional evidence required:** individual-level need, protected characteristics, access journeys, outcomes and a causal design

## Safety

Which safety claims require linked outcomes or pathway evidence?

### D08: The profiles identify safer access.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Safety outcomes attributable to access
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** No safety outcome is present.
- **Permitted wording:** The current data do not support the claim: The profiles identify safer access.
- **Prohibited wording:** The profiles identify safer access.
- **Additional evidence required:** linked safety incidents, clinical outcomes and risk adjustment

### D09: The profiles identify clinical quality.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Clinical quality
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** Recorded activity is not a clinical-quality measure.
- **Permitted wording:** The current data do not support the claim: The profiles identify clinical quality.
- **Prohibited wording:** The profiles identify clinical quality.
- **Additional evidence required:** validated clinical-quality outcomes and risk adjustment

## Value

Which value claims require cost and outcome evidence?

### D13: The profiles demonstrate economic value or cost-effectiveness.

- **Evidence status:** ○ Additional evidence required
- **Observed construct:** Costs, consequences and incremental value
- **Population:** No valid analytical cohort for this construct
- **Population scope:** No valid analytical cohort exists for this construct in the available evidence.
- **Method:** Evidence-gap assessment only
- **Main result:** No cost or outcome valuation is present.
- **Permitted wording:** The current data do not support the claim: The profiles demonstrate economic value or cost-effectiveness.
- **Prohibited wording:** The profiles demonstrate economic value or cost-effectiveness.
- **Additional evidence required:** resource use, costs, outcomes and an economic comparator
