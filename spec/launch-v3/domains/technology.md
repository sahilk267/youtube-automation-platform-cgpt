# DOMAIN-TECHNOLOGY — AI/Software/Hardware Product Testing OS

**ID:** `technology` | **Edition:** Launch optional control + Ultimate depth | **Goal:** demonstrable, reproducible technology analysis rather than paraphrased press releases.

## Domain entities

Product, model/software version, release date, changelog, official documentation, runtime/OS, test environment, hardware, benchmark task, dataset, observed metric, vendor claim, bug reproduction, privacy/security disclosure, license/cost terms, supported locale. Formats: tutorials, verified comparisons, benchmarks, feature announcements with hands-on validation.

## Engines and steps

| Engine | Inputs -> procedure -> outputs |
|---|---|
| Release Monitor | Official repos/docs -> versioned change list and source hash; track known issues -> release candidate |
| Claims vs Evidence | Vendor release note -> extract testable claim, scope, benchmarks and hardware assumptions -> test matrix |
| Reproducible Test Harness | Tested software and dataset -> run under versioned, isolated environment with authorized resources; capture commands and measured logs -> observation manifest |
| Benchmark Normalizer | Multiple products -> same task/hardware/versions/seed/setup where possible; report non-comparability explicitly -> table and caveats |
| Security/Privacy Examiner | Documentation, explicit test -> review permission, data flow, vulnerability claims with authorized safe testing only -> risk report |
| Cost/License Analyzer | Official pricing/terms with retrieval date -> usage scenario calculations, free tier and expiration -> transparent comparison |
| Tutorial Compiler | Actual successful workflow -> screen capture, command sequence, prerequisites and troubleshooting -> reproducible lesson |
| Version Drift Monitor | Follow-up official changes -> mark demos/guides outdated and schedule revision -> correction tasks |

## Algorithmic constraints

Never claim to have installed/tested a product when only documentation was read. No fabricated speed/accuracy benchmark. User-owned CPU i7/32GB/no GPU is default test environment; tests requiring stronger hardware flagged `NOT_TESTED_HARDWARE`. Software exploitation/unauthorized security probing prohibited; handle responsible security reports carefully. UI has reproducibility card showing OS, version, CPU/GPU, model, input, run count, median/variance when sample exists, timestamp, failure count.

## Creative and automation

Prefer original screen recordings, diagrams, side-by-side results, own code outputs, time-lapse recordings. New tool claims -> verify docs -> test if safe/compatible -> synthesize script with test labels -> capture -> edit -> review -> post. User action required for destructive installation, paid subscription, login, secret access and high-risk tool commands. Model can write test plans but actual observed outputs required.

## Tests

Incorrect version title, incompatible benchmark hardware, unlicensed software model, nonexistent command, pricing page change, self-reported benchmark as measurement, test output from fixture shown as real, interrupted software installation. All must fail or be labelled accordingly.
