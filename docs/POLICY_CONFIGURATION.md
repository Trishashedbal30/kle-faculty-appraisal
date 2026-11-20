# Configure the institutional API rubric

An authorised Dean or IQAC user uploads the approved policy document in **Source records** with category **policy**, then creates a version under **Scoring policy**. Each rule needs a clause/page reference. Inspect the draft against the uploaded source and approve it with the approval reference.

`INSTITUTIONAL_POLICY.template.json` intentionally contains `null` weights/caps and empty labels. It cannot be approved as-is. Fill these fields with institution-approved values; do not copy the synthetic demo rubric into real operation.

## Rule fields

| Field | Meaning |
|---|---|
| `kind` | Exact activity kind to which the rule applies; unique within a policy |
| `category` | `research`, `teaching` or `administrative` |
| `method` | `count`, `sum`, `mean` or `weighted_mean` |
| `weight` | Approved multiplier |
| `divisor` | Positive scaling divisor; use 100 to convert a percentage when specified |
| `cap` | Maximum points for that component |
| `citation` | Clause or page in the approved rubric |

Calculation: `min(raw_aggregate / divisor × weight, cap)`. Each component is rounded to two decimals, half up; rounded components are summed. The chosen rubric must permit that rounding convention. If it requires a different convention, change the arithmetic module and tests before approving the configuration.

- `count`: number of verified included activities of this kind.
- `sum`: sum of numeric `value` for these activities.
- `mean`: unweighted mean of `value`.
- `weighted_mean`: response-count-weighted mean of aggregate feedback percentages, using `students`. Each participating record must have a positive response count. This does not imply a count of unique students across courses.

A zero component is valid only within a complete, faculty-declared cycle. The application does not infer missing records to mean no activity. Every included kind must have a policy rule; otherwise the run is blocked. Deliberately unclaimed or inapplicable rows must have a reviewed exclusion reason.

## Available imported kinds

Research: `conference`, `journal`, `book_chapter`, `preprint`. Preprints cannot be scored as published work. Teaching: `feedback_formative`, `feedback_summative`.

Additional activities can use explicit kinds such as `teaching_load`, `learning_outcome`, `grant`, `phd_guidance`, `committee` or `event_coordination`. Enter evidence-backed numeric values with the unit stated in the activity title/locator and policy clause. Do not combine incompatible units under one kind.

## Authorship and specialised rules

The imported publication quantity is one record; the system does not invent a coauthor allocation. If your approved policy uses a fractional share, create an appropriately evidenced activity with that quantity, explicitly exclude the unadjusted imported claim and use `sum` with the approved rule. Duplicate DOI/title detection prevents silently counting both as included research. Complex nonlinear rules need a reviewed calculator extension, not arbitrary expressions entered into the application.

## Rating bands and versions

Bands need unique lower bounds and must include zero. The highest satisfied lower bound supplies the recommendation. A human can override only to a label present in the approved bands and must record a reason; the computed API total remains unchanged.

Approved policy versions are not edited in place. Create a new version for revisions. Each plan records the full approved policy hash and its selected track (`balanced`, `teaching`, `research` or `administrative`). Policies and plans must use the same cycle and track.
