# CORE-09 — YouTube Adapter, Policy, Publishing, Analytics and Revenue

## 9.1 Business constraint: owner's own channels only

Launch earns exclusively from own YouTube channels; no customer-service marketplace, B2B packages, drop shipping, guaranteed CPM/RPM or premature SaaS. Video view counts are not the same as income. Multiple active channels can be added once quality and operations demonstrate reliability.

## 9.2 Account authorization

Per channel official OAuth 2.0 scopes, separately stored account linkage, token validity and refresh, user consent, disconnect/revocation and account identity verification. Use Google/YouTube official APIs according to current docs; never scrape private Studio metrics. If credential not present, allow manual export but no fake API upload/analytics. Scope requests minimal; OAuth secrets protected in Windows Credential Manager/DPAPI-bound store, not plain config or logs.

## 9.3 Publishing state machine

`DRAFT -> QA_PASSED -> REVIEW_APPROVED -> EXPORT_READY -> UPLOAD_QUEUED -> UPLOADING -> UPLOAD_RECONCILING -> UPLOADED_PRIVATE -> SCHEDULED_OR_PUBLISHED -> OBSERVED`, with `BLOCKED` and correction paths. The default is **private/manual**; public upload and scheduled publication require separate channel policy opt-in and approved revision. Confirm remote video ID only from API response or reconciliation. Different scopes and provider verification limitations may restrict API-uploaded visibility; surface clearly.

Publication manifest: channel owner, approved project revision/hash, video path/hash, original title/description, attribution, thumbnail hash, target privacy, timezone-aware schedule, made-for-kids decision, synthetic-disclosure assessment, category, language, rights gate result, uploader account and API attempts. Do not allow an AI agent to arbitrarily set `made_for_kids`; owner/editorial decision required based on actual content.

## 9.4 Policies and external docs (snapshot; verify before use)

Official references as of 2026-11-09:
- Monetization/authenticity/reused content: https://support.google.com/youtube/answer/1311392
- YPP eligibility: https://support.google.com/youtube/answer/72851
- Expanded YPP access: https://support.google.com/youtube/answer/13429240
- Disclosure of realistic altered/synthetic media: https://support.google.com/youtube/answer/14328491
- YouTube upload API: https://developers.google.com/youtube/v3/docs/videos/insert
- YouTube Analytics API: https://developers.google.com/youtube/analytics

These are living policies. Agent MUST check current official page, quota, OAuth verification and API responses before implementation/deployment. Never hardcode quota costs/YPP thresholds permanently. YPP application is reviewed by YouTube; threshold attainment does not guarantee acceptance.

## 9.5 Originality and reused content

Original replay explanations, critical review, substantive commentary and original tactical diagrams may create value, but copyright and YouTube reused-content monetization review are independent. No assumption green screen face, cropping, watermarks, voiceover alone or quick jump cuts confer rights/monetization. Mass-produced interchangeable scripts are not the product goal. Upload QC must track percentage of self-created/third-party materials with human evaluation of substantive contribution; percentage alone does not define legality.

## 9.6 Automated metadata preparation

Inputs: approved factual script, content format, domain audience profile, source/correction metadata. Outputs: 2–5 title alternatives, description with relevant source citations and attributions, chapters where format supports, thumbnail spec and accessibility text, disclosure flags, honest content categorization. Hard gate: metadata claim must be in final video and backed by evidence; thumbnails must not depict fabricated sports scores or fake quotes. Never promise ranking through keyword stuffing or engagement manipulation.

## 9.7 Analytics import and distinction

Use official authorized reports and channel video association, with permissible metrics and scopes. `AnalyticsSnapshot` records data source, measurement date window, retrieval timestamp, units, currency, update lag, video ID, definitions, availability and incomplete/missing status. Shorts and long-form are separately analyzed; impressions/CTR vs Shorts feed metrics differ. Retention points are subject to API/data availability; no fabricated retention chart. When revenue reports unavailable, show `NOT_AUTHORIZED`/`NOT_ELIGIBLE`/`NOT_AVAILABLE` rather than zero.

## 9.8 Niche profitability evaluation

For pilot cricket India and NFL USA, track content pipeline effort by role/stage, source costs, original production time, publishing volume, watch-time quality, unique returning viewers, monetization status, rights claims, actual authorized income. No claimed RPM until observed. A/B tests require account-level platform support; observational title tests explicitly carry confounding warning.

## 9.9 GPU fund ledger

Entries: actual authorized revenue deposits, tax/reserve/operating expense records, net savings transfers, owner-entered target quote, current savings. Currency stored ISO code + integer minor units with explicit exchange conversion source/date when multi-currency. Dashboard shows actual amount, forecast scenario separately labelled, cumulative savings, and shortfall. **Never infer actual earnings from estimated views**. GPU cost includes PSU/cooling/other required system changes only when owner has quotes.

## 9.10 Failure handling and audits

Network failure while uploading -> reconcile via authorized API/account before retry; canceled upload may already exist remotely and must be checked. Privacy mismatches fail gate; token revocation blocks upload. Channel identity mismatch blocks cross-channel publish. Copyright complaint or content strike triggers issue workflow and stops related reuse pending review. Deleting/taking down public content requires explicit owner action and audit.

## 9.11 Release tests

Mock tests: stale token, quota exceeded, duplicate idempotency, channel A/B separation, legal disclosure required, changed script after approval, scheduled DST conversion, missing metric. Live tests only using owner-authorized test channel, explicit consent and safe/private visibility. Never count mock `video_id` as a completed real upload.
