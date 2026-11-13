# CORE-05 — Evidence Graph, Research Protocol and Investigative Trust

## 5.1 Central claim: language models are assistants, not sources

External verifiable sources and actual user-supplied data are evidence. LLM extraction, summarization, sentiment, source reputation and numerical predictions **never** become primary evidence. Every factual script sentence must be traceable to a source version + exact passage/page/timecode or a reproducible computation with source inputs. A fabricated citation is a release-blocking defect.

## 5.2 Research objects

`ResearchPlan {questions, scope, time/locale, source classes, search_queries, must_check, depth, stop_conditions, budget, state}`; `SourceVersion {source_id, canonical_url, retrieved_at, original_published_at, content_hash, content_type, captured_bytes_path, original_language, rights_constraints, provenance_group}`; `Claim {exact_proposition, attribution, time_scope, geography, qualifier, type, verification_status}`; `EvidenceEdge {claim_id, source_version_id, locator, quote_or_numeric_row, relation, independence_group, checked_by}`; `ResearchGap {question, attempted_queries, available_sources, missing_coverage, consequence}`.

**Admissibility invariant:** Only SourceVersions with actually captured and verified relevant text/data (and permitted use) can directly support a substantive factual claim. `METADATA_ONLY` can establish identity/date only where appropriate, and `FAILED` retrievals are never evidentiary support; they are source access gaps.

Claim classes: `FACT`, `QUOTE`, `POLICY`, `PREDICTION`, `OPINION`, `ALLEGATION`, `EXPLANATION`, `SATIRE`, `HYPOTHESIS`. Verification states: `UNREVIEWED`, `SUPPORTED`, `REFUTED`, `MIXED`, `UNVERIFIABLE`, `OUT_OF_CONTEXT`, `REQUIRES_HUMAN_REVIEW`. Evidence edge relation: `SUPPORTS`, `REFUTES`, `CONTEXT`, `ORIGIN`, `CORRECTION`.

## 5.3 Research executor algorithm

Input: topic, domain-specific question planner, research depth, source policy, maximum time/requests, channel locale. Output: `ResearchDossier`, **not** a forced final conclusion.

1. Break topic into atomic questions and assertions, include strongest plausible alternative interpretation and data-needed list.
2. Fetch original primary records first when available (official speech/video, regulation, scientific article, sports official result, audited filing, source code test). Preserve exact context and original language.
3. Collect independent perspectives based on *independent provenance*, not number of headlines. Group syndication/reposts and quotations from the same primary source.
4. Extract claims with exact offsets/page/timecodes; no claim can cite generic home page or unvisited URL.
5. Verify each through domain-specific deterministic calculators/checks, additional primary sources, methodological critique, contradictory evidence and independent records. Do not infer a contradiction from unrelated contexts.
6. Compute explicit gaps/unknowns and resource budgets; if essential evidence remains inaccessible, mark INCOMPLETE instead of inventing result.
7. Produce dossier with: sources, source conflicts, claim matrix, strongest counterevidence, missing information, human review flags, confidence **rationale**, and supported visualizable data.
8. Before final script, pass a line-by-line CitationLink validator; any high-impact unsupported fact blocks final approval.

## 5.4 Evidence scoring is an audit rubric, not ground truth probability

For each edge record factual proposition match (0/1/manual), exact locator availability (0/1), independence/provenance status, original primary class, temporal relevance, context completeness and correction status. A verdict requires:
- `SUPPORTED`: at least 1 directly relevant primary source **or** an appropriately justified set of independent corroborating sources, with source text matching the precise proposition, no unresolved decisive counterevidence. Serious allegations need heightened corroboration and human assessment.
- `REFUTED`: reliable source(s) directly contradict same proposition under comparable time/definitions; explain counterevidence.
- `MIXED`: credible supporting and counterevidence with substantive conflict or different legitimate scope.
- `UNVERIFIABLE`: inaccessible, unspecified, insufficient or privacy-restricted evidence.
- `OUT_OF_CONTEXT`: quoted content's meaning materially changed through omission, translation or incorrect time/location.

Never turn reviewer confidence into numerical legal guilt, medical efficacy, financial certainty or virality forecast. Source reliability is **claim-specific**, not permanent brand whitelist/blacklist.

## 5.5 Independence graph and source provenance

Store an `independence_group_id` for articles quoting or syndicating same original. A report repeating another article's allegation is not new independent verification. Unknown independence cannot be treated as confirmed independent; mark uncertain. Provenance edge types `REPRINTS, QUOTES, SUMMARIZES, REFERENCES, ORIGINAL_RECORD, UNKNOWN`. Audit any later correction/retraction, versioning and downstream invalidation.

## 5.6 Statement / contradiction engine (Newsroom)

Input: current full speech/citation, historical candidate speeches, structured claim proposition. Verify speaker identity, original transcript/timecodes, time/geography, audience, qualifiers, dates and actual promised actions.

Comparison classes: `CONSISTENT`, `POSITION_UPDATED`, `APPARENT_CONTRADICTION`, `SUBSTANTIATED_CONTRADICTION`, `UNVERIFIABLE`, `OUT_OF_CONTEXT`. `SUBSTANTIATED_CONTRADICTION` requires logically incompatible positions about same subject/conditions with verified text and no unresolved contextual qualifier. An altered policy position is not automatically a lie; differentiate speech contradictions from implementation failure and outcomes. Agent outputs claim-level findings, not moral judgment of person. Complete historical coverage is never claimed.

## 5.7 Media ownership, political influence and investigation safeguards

Ownership graph edges must link exact names/legal entities, filing IDs, dates, percentages or public documents. Public ad spending, political finance, regulation, media coverage patterns, takedown reports and documented network ties can be investigatory leads. Association or pattern is not proof of coordination, corrupt intent or government control. Record alternative explanations and uncertainty. Right-of-reply tracker for serious identifiable allegations: recipients and questions, attempts, timestamps, response deadline, response or nonresponse; do not fabricate outreach or imply user sent messages without user-approved channel/action. Human legal/editorial review always.

## 5.8 Research completeness and stop criteria

Completeness auditor compares research_plan.must_check against collected records; source search coverage by provider/geography/language/time; primary document provenance; unresolved rebuttals; known archive gaps; data changes. States `SUFFICIENT_FOR_DRAFT`, `NEEDS_MORE_RESEARCH`, `BLOCKED_EXTERNAL_SOURCE`, `HUMAN_ADJUDICATION_REQUIRED`. It cannot guarantee all sources searched. Quick brief: bound scope with explicit caveats; deep research: cross-check substantial facts; forensic: extensive archives, methods, adversarial review, human signoff.

## 5.9 Multimedia verification

Preserve original media URI, digest, container metadata, frame/timecode references, transcript version, subtitle language and creator. Verify full-context video before judging viral 10-second clip when possible. Synthetic media detectors can flag anomalies, not certify forgery/authenticity. Unverified identity/altered clip => review. Translations need original text retained; impactful quote discrepancy => bilingual review.

## 5.10 Corrections and cascading re-review

A source retraction/updated official score changes claim status, creates audit event, marks dependent scripts and scheduled videos `NEEDS_REAPPROVAL`, and triggers recommended correction for published videos. No stealth edits to immutable past citations. Owner chooses public correction or replacement; record outcome.

## 5.11 Negative tests

- Two copies of a single press release not independent verification.
- Quote from 2012 compared to 2026 without changed-law context -> not automatically contradiction.
- Satirical statement not interpreted as factual pledge.
- News article claiming wrongdoing without primary corroboration -> cannot present guilt as fact.
- Numeric claim cited only to LLM answer -> hard gate fail.
- Historical article paywalled -> `BLOCKED_EXTERNAL_SOURCE` not invented paragraph.
- Sport injuries marked confirmed from anonymous rumor -> reject claim.
- Edited synthetic clip -> evidence cannot be verified solely from appearance.
