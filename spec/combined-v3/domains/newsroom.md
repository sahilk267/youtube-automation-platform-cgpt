# DOMAIN-NEWSROOM — Investigative Journalism OS

**ID:** `newsroom` | **Edition:** Ultimate; Launch may use evidence tooling on sports and tech without fully activating newsroom | **Owner:** Domain plugin only; common sources, rights and publishing remain CORE services.

## Goals, inputs and outputs

Investigate important claims/events/speeches through multi-source, multilingual, historically contextual research. Input may be viral 20-second clip, full speech link, policy announcement, allegation, official notice, public finance disclosure or user-supplied question. Output is `NewsroomDossier` with exact sources and gaps, possible factual contradictions **between statements**, action/outcome evaluation, counterevidence and legally reviewed original script. Never preselect a partisan conclusion. Audience: regional and national explainers, long documentaries and short verified updates.

## Domain engines and contracts

| Engine | Inputs | Operation -> output | Block/negative path |
|---|---|---|---|
| Event Verification | Clip URL, metadata, original broadcast/source | Match origin speaker/date/venue; capture original length and transcript timecodes; mark cuts, translations and uncertain identity | Original unavailable -> no categorical context claim |
| Full Speech Parser | Original recording/text, language | STT/OCR with timecode, manual alignment, distinguish direct quotation from interpretation, multilingual quote map | Translation uncertainty -> bilingual review |
| Claim Atomizer | Full transcript/policy text | Split exact subjects, predicates, qualifiers, time periods, promises, predictions, opinions; create claim IDs | Satire/rhetoric classified, not automatically factual |
| Historical Statement Memory | Claim, person/entity/time/place variants | Search dated archives/official videos/interviews/documents; capture retrieved set and known blind spots | Never claim all historical statements found |
| Consistency/Contradiction | Comparable verified claims | Evaluate same proposition/scope/time, qualifiers and changed circumstances; output six-class review | Context mismatch/translation drift => APPARENT or UNVERIFIABLE, not proven lie |
| Policy/Action/Outcome | Promise, institutions, legislation, budgets, dates | Join official orders/gazettes, court/parliament/budget records, implementation evidence, observable outcomes; separately label intention/action/effect | Avoid causality from correlation |
| Source Independence | Record graph | Trace syndicated/reporting relationships and primary document; de-duplicate evidentiary independence | Uncertain group => do not count as independent |
| Perspective/Counterevidence | Claim and candidate alternative views | Retrieve strongest good-faith rebuttal and verified evidence; weigh proportionally, avoid false balance | Missing opposition response -> show gap |
| Influence & Ownership Graph | Media organization/company/official filings | Legal ownership, directorship, recorded funding, advertising/coverage patterns, institutional link dates and alternate explanations | Association ≠ covert control or corruption proof |
| Right of Reply | Serious named allegations | Draft exact fair questions, log owner-approved outreach, response deadline and published response if authenticated | NEVER pretend emails/contacts were sent |
| Editorial/Legal Review | Dossier and narrative | Severity classification, privacy, defamation review, disclosure, corrections and human signoff | Sensitive public allegation always requires human approval |
| Investigative Memory | Verified case versions | Index provenance, prior speech comparisons and corrections for future reuse | Corrected/retracted source invalidates memory inference |

## Forensic pipeline

1. Intake event, record origin claim and whether identity/source original is known.
2. Locate full primary speech, historical record, original-language transcript and video timestamp. A clipped original with missing context is a **lead**, never conclusive proof.
3. Decompose into atomic claims and assign explicit date/time and actor.
4. Search historical candidate statements with multilingual aliases and variants. Store all search queries attempted and results; run coverage completeness audit.
5. Compare prior and current claims only where same proposition, circumstance and temporal scope; detect changed policy vs contradictions vs implementation shortfall.
6. Examine policy/financial/public records, independent journalism and counters; record original documents + source families; avoid assuming sources with common origin are independent.
7. For allegations involving identifiable people/institutions, document counterevidence and right-of-reply work with human approval. No fabricated outreach.
8. Build original script: question, documentary record, historical timeline, competing explanations, supported conclusion, uncertainty, corrections route.
9. News-specific visual policy: primary source documents, timestamped speech excerpts with rights review, maps, data animations; AI scenes explicitly identified as reconstructions, never faux evidence.
10. Run human editorial/legal gate; publish only authorized revisions; monitor corrections and late-breaking official records.

## Classification protocol

Consistency outcomes: `CONSISTENT`, `POSITION_UPDATED`, `APPARENT_CONTRADICTION`, `SUBSTANTIATED_CONTRADICTION`, `UNVERIFIABLE`, `OUT_OF_CONTEXT`. Store compared quotations and source locators, logical relation, historical context, alternate meaning and review reason. Serious allegation cannot use automatic `SUBSTANTIATED_CONTRADICTION` as moral/intent label.

## Research depth

`QUICK_VERIFIED_BRIEF`: limited questions and explicit caveats, never high-stakes automated publish. `DEEP_INVESTIGATION`: historical context, multiple provenance groups and policy comparison. `EXTENDED_FORENSIC`: extensive public archives, method appendix, legal/specialist review and source challenge. Time spent cannot be fixed from spec; stop when agreed sufficiency criteria satisfied or report gap.

## Quality and automation

Must maintain statement-to-source citation coverage, date-context precision, unanswered relevant question inventory, source-independence caveats, translation status, right-of-reply log and approval status. Research, transcription, archiving, contradiction candidate retrieval and dossier drafting automate; ultimate conclusions, high-risk publication and legal determinations remain human-reviewed.

## Mandatory fixture tests

- Clipped statement misrepresents full speech; label out of context.
- Old and new policy positions differ but contexts changed; `POSITION_UPDATED`, not automatic dishonesty.
- Ten sites copy one unsupported accusation; independence count one.
- Affiliated media owner overlaps with another firm, but no documented editorial control; no conspiracy claim.
- Contradictory court/official document emerges after approval; invalidate scheduled video and flag published correction.
- Original language and translated quote differ; require manual bilingual review.
- Right-of-reply work not actually sent; no false claim of attempted contact.
