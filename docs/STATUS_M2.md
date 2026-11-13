# ViralOS M2 status — verified implementation scope

| Capability | Status | Evidence/limit |
|---|---|---|
| Current M0–M3 data and APIs | Retained | Existing pytest regression suite |
| M2 typed shot timeline | Implemented | Pydantic checks + tests |
| Timed text/image overlays (not video footage) | Implemented (text/diagram only) | Real Pillow → FFmpeg H.264 output |
| Rights-attested still PNG/JPEG | Implemented | Projects isolated; sha256 verification; NO legal guarantee |
| Rights-attested soundtrack WAV | Implemented | Gain mix; no auto rights clearance |
| Narration timing duration guard | Implemented | ±450 ms WAV-vs-timeline guard; NOT speech forced alignment |
| Hindi and English overlay text | Supported with system font | Font presence and Windows device tests pending |
| 12 category specialized video direction | Not implemented | Sports prototype only |
| Accurate auto-translated/dubbed multi-language | Not implemented | Manual caption texts only |
| Real cricket/NFL match footage legally fetched | Not implemented | No clip downloader provided |
| Automated professional video scoring | Not implemented | Technical quality checks only |
| Publishing/YouTube OAuth live upload | Disabled | Explicit authorization and rights gate pending |
| Local CUDA generative image/video | Not implemented | CPU-first adapter-friendly data design |
