# ViralOS v3.0 — CANONICAL PRECEDENCE, STATUS AND CONFLICT RULES

**Status:** project specification, not source-code implementation. This document supersedes v2.1 `SPEC_PRECEDENCE.md` and prior instructions for v3 package. No silent guesses or self-created extra services.

1. **Actual law/platform/source access and owner permission**, as verified at execution time, govern all external actions. Unknown rights/authorization -> HOLD.
2. `configs/default_policy.json` (existing hard gates), this file, and `core/21`–`core/26` (v3 creative requirements) with `contracts/v3` typed schemas and `configs/creative_operation_registry_v3.json` govern v3 media creation. If code/API cannot implement required schema, BLOCK and create ADR; do not fabricate compatibility.
3. Existing `core/00`–`core/20`, `configs/engine_registry.json`, `contracts/*.schema.json`, `database/schema.sql` and `002_operational_controls.sql` govern inherited *non-creative* source/evidence/jobs/rights/compute/publishing operations; v3 is additive and never erases them.
4. Each `creative/directors/*.md` controls domain-specific fact/visual rules, `creative/formats/*.md` controls format rhythm/structure, `ChannelBrandPack` controls channel identity, and `LocalizationVariant` controls language/region. When any preference conflicts with evidence/rights/hardware policy, the hard gate wins.
5. `research/` and samples are non-normative desk research unless linked to actual observed creator video. ADR-001 in `research` originally said PROPOSED; its **selected architecture is now ADOPTED as v3 specification** by `core/24`, not proof of deployment.

## Frozen compatibility
Original v2 `contract_version=2.0.0` and requirement IDs preserved. V3 creative contracts use 3.0.0 and distinct artifact IDs. All packs represent one future codebase; edition packaging does not create three independent running programs. Do not mutate legacy signed approval or source records.

## Missing data semantics
`UNKNOWN` is neither `FALSE` nor `ZERO` nor `NOT_APPLICABLE`. Consent, rights, source API, language access, hardware, real public metrics and account-enabled features are not granted by the brief. Any unresolved case becomes durable `BLOCKED` / `WAITING_FOR_APPROVAL` with operator action. Other jobs may continue.

## Completion rule
Structural validation != implemented operation != Windows render != genuine source validation != copyright clearance != channel monetization. Both package validators validate documents/contracts/SQL fixtures; human evaluation of final videos and real API/hardware testing remain required.
