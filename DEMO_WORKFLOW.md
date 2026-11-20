# KLE Faculty Appraisal — Reviewer Demonstration Guide

## Start

From the `kle-faculty-appraisal` directory in VS Code PowerShell:

```powershell
.\.venv\Scripts\python.exe manage.py run
```

Open the localhost URL printed in the terminal. If the `.venv` folder is absent, use a supported installed Python version to create it, then install `requirements.txt`.

## Roles and the exact order

1. **Administrator:** Sign in with the credentials created using `manage.py setup`. In **Faculty directory**, inspect the official teaching staff directory and verify only a proven identity match. In **Access management**, create named accounts for the actual authorised faculty, HoD and Dean/IQAC reviewers. Review decisions are not available to the admin role by design.
2. **Dean / IQAC:** Sign in to **Scoring policy**. Create and approve a policy based on the institution's real authorised API rubric and citations. The supplied documents do not establish universal scoring weights. Do not invent them.
3. **Faculty:** Sign in to **Source records** and grant consent for appropriate sources. Inspect and, if needed, add documented activities. In **Appraisal workspace**, create a plan, describe research/teaching/administrative completeness (including a truthful nil declaration where appropriate), select the approved policy, then lock the plan.
4. **HoD / Dean / IQAC:** Sign in and open **Activities & evidence**. Select the faculty and click **Review** on each record. Check the actual document, authorship, DOI, academic cycle, source locator and any caveats. Choose **Verified**, **Flagged** or **Excluded**, enter a factual review note and click **Record decision**. A verified source file checksum is not the same as verified faculty authorship.
5. **Faculty:** In **Appraisal workspace**, open the locked plan and start the appraisal run. The system may block processing until evidence, policy and consent requirements are satisfied.
6. **Dean / IQAC → HoD → Dean / IQAC:** Use **Review desk** to examine the generated calculation, acceptance checks and evidence trail; record each required human decision. A returned or blocked run is not a released appraisal.
7. **Reports & appeals:** After final approval, open the released report and download the PDF. Confirm source citations, score breakdown, named approvals and version history. An appeal must be resolved by authorised reviewers.

## Identity matching: important caveat

Imported author names and names in a staff directory can be incomplete, abbreviated, or similar without identifying the same person. Do not infer identity from a name match alone. A publication in an imported workbook is not automatically approved evidence. If a match cannot be established using independent institutional evidence, keep the identity unresolved and flag the relevant claim.

## What the status counts mean

`<verified>/<total>` reports how many records have approved evidence reviews. Identity `Verified` is a separate status. `No plans yet` means no appraisal plan has been created. `No appraisals to review` means there is no started appraisal run. A released-report count reflects appraisals that have passed all required approvals.

## Troubleshooting

- **Only Details, no Review:** Logged in as admin/faculty; use a named HoD, Dean or IQAC account for evidence decisions.
- **No Create plan:** Only the faculty role can create a plan, and an approved policy is required.
- **No scoring policy tab:** Only Dean/IQAC sees it.
- **No appraisal runs:** The faculty must lock and start a plan first.
- **Blocked or failed run:** Open Review desk, read exceptions, correct actual source/policy/consent issues; never force approval.

This guide documents the intended workflow and access rules; real end-to-end success requires correctly configured institutional policy, accounts, consent and verified evidence.
