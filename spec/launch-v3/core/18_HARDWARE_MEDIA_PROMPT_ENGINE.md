# CORE-18 — CPU/GPU MEDIA, MODEL CAPABILITIES, SCENE SAFETY & PROMPT ENGINE

## 32GB CPU-first production
Detect actual i7 8th-gen feature set, RAM, OS and disk before benchmarking; no unconditional 1080p speed guarantee. Default one CPU-heavy job, quantized LLM optional, FFmpeg/Piper diagrams, screenshots/creator-provided rights-cleared media, deterministic SVG/PNG charts, timed captions and intro/outro. If the selected TTS/model isn't installed, offer manual narration/import or hold job. An offline video project requires no YouTube credentials.

## GPU and 48GB workstation evolution
Every render job records `required_capabilities`, preferred backend, expected RAM/VRAM/temp disk, reserve headroom, fallback compatibility and device-specific settings. Device AUTO can choose CPU render only if full scene intent is preserved; it must **not** silently replace requested photorealistic diffusion with generic static output. GPU mode is capability-gated by driver, backend, model hash, license and measured working run. `WAITING_FOR_CAPABILITY` is a valid honest state. Later multi-GPU/remote workers require authenticated artifact transfer and per-job content hashes.

## Deep prompt compiler contract
SceneSpec is intermediate representation: shot purpose, evidence IDs, context/era, fictional-vs-documentary, actor/prop/location references, camera, movement, lighting, duration, lens, resolution, aspect, narration alignment, rights, disclosure and model constraints. Prompt compiler emits **model-specific** prompt/negative prompt/control references/seed/steps/guidance/version/license. Do not claim one universal optimal prompt. Keep generation experiment results and manual visual comparisons. Character consistency needs documented reference image rights and continuity bible; actual physics/identity correctness validated post-generation.

## Multi-shot automation
Research-script -> storyboard -> per-scene asset plan -> license/disclosure -> budget/capability check -> render scene -> visual temporal QA + factual QA -> human review if sensitive -> FFmpeg composition -> audio/caption/blank-frame/codec QC -> revision hash approval -> export. Failed scene reruns only with safe deterministic inputs; cross-scene continuity is not inferred from unrelated seeds.

## Reconstruction truthfulness
Political/news scenes labeled synthetic reconstruction visibly and in metadata where required; no synthetic scene may be used as purported primary evidence. Historical/scientific simulation has explicit assumptions and uncertainty; gaming gameplay must originate from authorized genuine captures or licensed sources, not undisclosed simulation claiming real play.

## Windows process safety
Workspace canonical paths on Windows, safe UTF-8/Unicode handling, path length tests, ffmpeg list arguments with constrained demux/probe, file-size and frame-rate limits, temp directories under controlled root, signal-safe cancellation, free disk threshold and checksum before promoting final artifact.
