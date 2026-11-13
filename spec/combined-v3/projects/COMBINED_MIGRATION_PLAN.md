# Combined Edition — One Codebase, Two Release Profiles

LAUNCH is an executable *milestone*, ULTIMATE a future superset. Both must use identical core IDs, database schema and service owners. Never copy an entire Launch app into a second Ultimate folder. The architecture only has one source registry, one evidence graph, one rights service, one media pipeline, one publication gateway and one analytics/ledger. Domain engines live in `domains/` plugin adapters.

**Upgrading Launch to Ultimate:** Take checksum backup, run migration dry-run and integrity check, compare API schema version 2.0.0 and known feature flags, enable domain plugins one by one after source/license tests, model/GPU capability checks and golden fixtures, ensure existing projects/analytics/revenue stay unchanged. Run rollback by restoring pre-migration backup if migration fails; don't downgrade production data destructively. Existing CPU-only projects remain exportable.

**Combined operator mode:** default LAUNCH. The owner can switch to ULTIMATE only after release gate evidence for a specific domain/compute feature. SaaS remains separately optional. README, tests and manifest must make installed/enabled/deferred distinct. Do not present a list of twelve as twelve implemented modules.

**Definition of compatibility:** source/claim/channel/project IDs same; URLs and asset hashes stable; histories and approvals never lost; old renders still playable; any material re-render triggers technical QC and revision approval; live upload intents never duplicated.
