# CORE-08 — Hardware Adaptive Compute, Model Registry, GPU and Distributed Scale

## 8.1 Runtime profiles

- `CPU_ONLY`: mandatory on user's current Intel i7 8th gen, 32GB RAM, no discrete GPU. Enables research, small quantized text models if benchmarked, TTS, STT if feasible, graphics, FFmpeg, manual upload. GPU-only text-to-video is `WAITING_FOR_CAPABILITY`.
- `AUTO`: preferred; choose compatible hardware automatically per job, without silent semantic-output substitution. Fallback only for tasks that explicitly declare permitted fallback.
- `CUDA_ONLY`: requires supported NVIDIA CUDA worker; on absent/insufficient hardware wait with capability error, never pretend GPU active.
- `HYBRID`: independent CPU research and GPU generation workers with resource reservations, checkpointing and max-concurrency limits.
- `REMOTE_WORKER` future: secure authenticated worker with artifact transfer, compatible model hashes and tenant boundaries; disabled in Launch.

**Future machines** may include RTX 3090 24GB, RTX A6000 48GB, multiple GPUs, other NVIDIA GPUs. An installed GPU's exact capability, VRAM available, drivers, model licensing and memory requirements must be tested. Neither 24GB nor 48GB guarantees every photorealistic video model or long 4K shots.

## 8.2 Capability and workload manifests

Worker capability: `worker_id, provider_type, device_name, driver, compute_runtime, cpu_cores, ram_total/available, gpu_count, vram_total/available, FFmpeg_encoders, installed_models_and_hashes, filesystem_space, supported_tasks, health, last_seen`.

Job request: `required_task, accepted_modalities, preferred_mode, estimated_ram_mb, estimated_vram_mb, estimated_disk_mb, CPU_threads, priority, cancellable, checkpoint_strategy, model_id, license_policy, source_revision, output_format, resource_cap_override`.

Model manifest: `model_id, architecture_family, version_tag, sha256, local_path, source_uri, license_name, commercial_status, allowed_uses, supported_tasks, precision, required_runtime, min_gpu_vram_estimate, RAM_estimate, max_frames_resolution_capability, safety_notes, benchmark_record`. Unknown license => blocked installation/generation, not inferred open source.

## 8.3 Scheduler algorithm

1. On worker registration verify executable binaries, GPU runtime/driver when present, FFmpeg supported encoders and model signatures.
2. Load job's capability/resource requirements and current mode. Reject tasks outside installed model capabilities. Estimate peak usage from benchmarks (not model-proclaimed guesses).
3. Reserve memory/disk/concurrency budget; default conservative margins (e.g. 15% memory headroom) with user-configured limits; if prediction uncertain, restrict concurrency and report risk.
4. Pick compatible worker by lowest expected completion cost and locality; `CPU_ONLY` filter excludes CUDA; GPU-only jobs cannot downgrade to CPU unless explicit compatible render mode approved.
5. Acquire durable job lease, run with monitored subprocess/process-group, progress logs, cancellation checkpoints.
6. On GPU out-of-memory: free resources, retry at most once with same quality only if transient; propose reduced batch/resolution/offload as an explicit **new quality profile** requiring approval.
7. Store actual CPU/RAM/VRAM/wall-time/disk metrics; improve estimates from empirically measured runs.
8. On failure release reservation, mark structured state, requeue only idempotent work.

## 8.4 Local model decisions

Optional text engine `Ollama` or `llama.cpp` with documented tested small quantized model selected through benchmark suite, not a fabricated guaranteed model. External facts must be checked through citations. Never stream unbounded research context into 32GB; retrieve chunks, extract and reassemble with source IDs. For visual models, register ComfyUI adapters when licensed/installed, reject unknown graph node requirements and select supported text-to-image, image-to-video or video-to-video per manifest. All model downloads require owner consent and disk/terms/license preflight.

## 8.5 Queue resource policy

CPU heavy inference/render defaults 1; source fetch concurrent 2/provider unless terms lower; I/O lightweight can overlap. No uncontrolled simultaneous 12-domain inference. Source check jobs and corrections prioritized over bulk video generation. GPU future queue allocates actual measured VRAM and reserves headroom; multi-GPU jobs must declare model parallelism support, not assume arbitrary distribution.

## 8.6 Windows install, health and upgrade

CPU install does not require CUDA, Docker, Node at runtime (after frontend built), or always-on internet for saved projects. Preflight: OS build, Python runtime, directory write permission, free SSD, FFmpeg, voices/fonts/optional local model. CPU-only sample video must pass. Hardware upgrade: detect GPU, install approved adapter/drivers/models with consent, re-run benchmarks, switch mode, rerender same saved project version, compare provenance and quality; no DB data-copy or reset.

## 8.7 Remote worker future security

If enabled later: mTLS or equivalent mutual auth, queue access scoped to job and artifact, encryption in transit, digest verification, no distributing plaintext OAuth tokens, least privilege, worker revocation, signed/verified model paths and sandboxed third-party dependencies. Multi-tenant SaaS must not put tenants' private sources on another tenant worker.

## 8.8 Hardware regression suite

- Boot, create research, narrate and export with no GPU and no CUDA DLL installed.
- Selecting GPU mode without GPU yields `WAITING_FOR_CAPABILITY` and preserves job.
- Fake GPU registry must not make UI claim physical GPU installed.
- Model file hash mismatch blocks execute.
- Runtime 24GB vs 48GB profile only changes compatible job admission; no promise to run unsupported model.
- Worker crash, disk full and OOM preserve content project and retry/cancel integrity.
