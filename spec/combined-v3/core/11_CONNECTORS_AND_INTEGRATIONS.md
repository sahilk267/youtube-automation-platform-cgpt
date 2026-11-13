# CORE-11 — External Connector Engineering Contract (No Phantom APIs)

## 11.1 Contract all providers must implement

```
Connector.id / version / license_policy / source_class
Connector.discover_capabilities() -> verified methods, auth, regional coverage, provider terms
Connector.validate_access(credentials_ref, market, date) -> allowed | blocked(reason)
Connector.fetch(query, cursor, max_items, deadline) -> ObservationBatch + quota + errors
Connector.normalize(raw_item) -> TopicObservation + SourceVersion candidate
Connector.freshness_policy() -> max_age and update lag from provider/pilot
Connector.reconcile(updated_item) -> source revision/correction event
```

Every connector stores `provider_id, provider API version, documented endpoint URL, terms_approved_at, auth scopes, connection test evidence, official rate limits, pagination/cursors, time zone, query constraints, permitted storage/redistribution, quota resets, retry_after, last_success/failure, coverage status`. Human approval needed for paid/licensed providers and scraping legal questions. No model-generated private API URL as working fact.

## 11.2 Source-specific implementation routes

| Source | Launch route | Ultimate route | Do not assume |
|---|---|---|---|
| Manual URL/public file | Validate allowed URL, fetch if accessible, capture provenance and rights metadata | Rich archives/media and user-supplied document parsing | Link is a fact, or website permits redistribution |
| RSS/news | Feed parser with stable item IDs, time and syndication detection, server policy checks | Region/language and historical archive monitoring | Everything in a feed is independent evidence |
| Official cricket data | Record tested exact allowed provider; if no legal programmatic access use manual verified scorecard/source links | Per-format stats, score correction, licensed ball-by-ball where available | There is a free universal live cricket API |
| Official NFL | Use documented permitted stats/schedule if accessible; otherwise verified manual/public citation | Play-by-play/tactical adapter with verified access and venue/clock accuracy | Game broadcast/public recap constitutes rights grant |
| MLB/NBA/Soccer | Disabled until sport-specific contracts and permissions approved | League-specific adapter, model and tests | Common data shape alone sufficient across sports |
| YouTube public metadata | API key/OAuth as appropriate, quota health, source IDs, no view enumeration promise | Cross-market trend discovery where quotas allow | Unrestricted complete public content crawl |
| YouTube Studio/Analytics | **Owner-authorized OAuth only**, metrics availability flags | Cohort experiments and money ledger | Other channel's private analytics accessible |
| Google Trends | `NOT_CONFIGURED` until legitimate access method verified | Historical/geo samples with limited interpretation | 0–100 trend index = absolute search volume |
| Reddit | API scopes and terms + privacy filtering | Questions/communities and lead tracking | Comments represent proof of claims |
| Official filings/archives | Public documents and official search URLs, cache as terms allow | Dedicated newsroom/business/history case files | Every government document available/searchable |
| Open scientific archives | DOI/paper metadata, accessible paper versions | Retraction/consensus/metadata adapters | All preprints are peer reviewed |
| Other social providers | Disabled until legal documented access | Plugin hooks and coverage notes | Generic bypass scraper acceptable |

## 11.3 Shared network security

All requests through one `SafeFetcher`, which enforces allowed schemes `https` (http only for opt-in localhost test fixtures), DNS/IP recheck after redirects, blocks private/reserved IP ranges, byte/time limits, URL sanitization, provider rate/quota and user-agent policy. Never download executable assets from untrusted text and run them. Browser/page text is untrusted source content and may contain prompt injection; LLM summarizer sees marked passages, not instructions.

## 11.4 Freshness and integrity

Evidence is versioned per retrieval; preserve original publication timestamp distinct from fetched timestamp. When sport final score changes, create version and invalidate referencing content. A source 404/paywalled/banned after initial fetch remains cited to permissible archived hash or marked no longer accessible. `retrieved_at` can never be silently edited. Quota exhaustion source goes `DEGRADED/NO_DATA`, no AI-generated replacement. Support manual source entry with `HUMAN_VERIFICATION_REQUIRED` and explicit integrity check.

## 11.5 YouTube exact integration details

Use official YouTube Data API v3 `videos.insert` for authorized upload and YouTube Analytics API for allowed reports. Check live docs for endpoints, scopes, audit or verification requirements, upload limits, default privacy and quota rules before development and regularly thereafter. Upload manifests include `status.containsSyntheticMedia` when supported/required, declared made-for-kids decision and intended privacy. Thumbnail and playlist operations use only verified APIs/scopes, not undocumented scraping. Use `resumable` upload where documented; on ambiguous timeout reconcile first, do not replay blindly.

## 11.6 Connector contract tests

- Fake rate-limit 429 with `Retry-After`, correctly schedule and show quota.
- Redirect to localhost/private IP => deny even if initial host public.
- News RSS item copies another page => evidence independence not duplicated.
- Duplicate pagination cursor => stop and raise parser error, not infinite loop.
- Source field missing timestamp => store unknown and display warning, not fabricate current date.
- OAuth revoked => disable only affected channel and avoid storing token in logs.
- 200 OK with malformed JSON => fail with source parse error, preserve hash metadata.
- Provider terms changed => `NEEDS_EXTERNAL_VERIFICATION`; do not auto-switch to unauthorized scraping.

## 11.7 Dynamic policy references to review

https://developers.google.com/youtube/v3/docs/videos/insert ; https://developers.google.com/youtube/analytics ; https://support.google.com/youtube/answer/1311392 ; https://support.google.com/youtube/answer/14328491 ; https://support.google.com/youtube/answer/72851. These are official source URLs, **not** license grants. Agents must check contemporaneous policy when integrating and record dated review.
