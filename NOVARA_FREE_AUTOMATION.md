# NOVARA — Free / Open-Source Video Automation Setup

This guide configures the existing AgentTube project for a **local-first, low-cost workflow**. It does not promise unlimited free AI video generation: hosted video models may require credits or paid API access, and free-tier limits can change.

## What can be free

- **Workflow and video assembly:** Node.js + FFmpeg (the project already bundles FFmpeg).
- **Captions/transcription:** faster-whisper can run locally if Python and model storage are available.
- **Visuals:** use your own licensed images, public-domain assets, or locally generated stills; assemble them into a real MP4.
- **Research and scripts:** use a provider only when its current free tier is available to your account. Check provider limits before each run.
- **YouTube upload:** YouTube Data API access has no direct per-video fee, but Google Cloud quota and OAuth setup apply.

## Important limitation: Google Flow

Google Flow is a separate creation interface. Do not assume it has a supported public API or that this repository can automatically operate Flow. If you create clips/stills in Flow, export them and add them as assets to AgentTube. Automation can then assemble, caption, review, and prepare the video. Full end-to-end Flow generation requires an officially supported integration.

## Recommended NOVARA workflow

1. Open the AgentTube dashboard and set the channel name to `NOVARA`, target audience to international English viewers, and region to `US` if that matches the intended YouTube audience.
2. Choose local slideshow / FFmpeg assembly as the default video method. Do not enable paid video providers or paid-media probes.
3. Add approved visual assets and narration to the production, or use an available free-tier text/TTS provider after checking its limits.
4. Generate the MP4 and captions; verify that the output is a real, decodable MP4 with audible narration.
5. Review every health/science claim against reliable sources. Confirm asset licenses and YouTube synthetic/altered-media disclosure where applicable.
6. Keep privacy set to **private** for initial tests. Only schedule or publish after the factual, rights, quality, and human-approval gates pass.

## Optional local captions with faster-whisper

Install Python 3.10+ and FFmpeg on the machine running the project, then install faster-whisper in a virtual environment:

```bash
python -m venv .venv
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell:
# .venv\Scripts\Activate.ps1
pip install faster-whisper
```

Transcribe an audio file with a small model (the first run downloads model weights):

```python
from faster_whisper import WhisperModel

model = WhisperModel("small", device="cpu", compute_type="int8")
segments, info = model.transcribe("narration.wav", vad_filter=True)
with open("captions.srt", "w", encoding="utf-8") as f:
    for i, segment in enumerate(segments, 1):
        def stamp(seconds):
            ms = round(seconds * 1000)
            h, ms = divmod(ms, 3_600_000)
            m, ms = divmod(ms, 60_000)
            s, ms = divmod(ms, 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"
        f.write(f"{i}\n{stamp(segment.start)} --> {stamp(segment.end)}\n{segment.text.strip()}\n\n")
```

This is optional; the project may already provide its own caption workflow. Do not add a second caption path unless needed.

## Android-only setup

GitHub stores the code, but GitHub itself does not provide an always-on free video-rendering computer. On Android, use GitHub Codespaces only if your account has available quota, or run the project on a computer you control. Free quotas and availability can change. A phone can review and manage the workflow, but long local renders may be slow.

## Safety and publishing

- Keep API keys in environment variables or repository Actions secrets—never commit keys, OAuth files, or `.env`.
- Keep `DEFAULT_PRIVACY_STATUS=private` for testing.
- Do not allow generated or simulated placeholder videos to publish.
- Never auto-publish health claims without source review, rights confirmation, and explicit approval.
- Check the current license and requirements of every external repository, model, voice, and asset before commercial use.

## Existing project

Repository: https://github.com/Hammad0909-maker/youtube-automation-agent

Start the dashboard using the project's existing Quick Start instructions in `README.md`. Run the project's Production Readiness check before enabling any autonomous generation or publishing.
