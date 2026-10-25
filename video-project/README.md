# Free scene-based video editor

This repository now includes a free FFmpeg-based render workflow. It assembles still-image scenes into a 16:9 1080p MP4, applies a gentle zoom effect, optionally burns in SRT captions, and adds a narration track.

## Prepare a project

1. Create a folder under `video-project/`, for example `video-project/kidney-health/`.
2. Copy the example manifest into that folder and rename it `manifest.json`.
3. Add one image per scene, a narration file such as `voiceover.mp3`, and optionally an SRT subtitle file such as `captions.srt`.
4. Edit the manifest so every scene has an image filename and a duration in seconds. The total scene duration must be at least as long as the narration.
5. Commit the project assets and manifest to your repository.

Example manifest:

```json
{
  "voiceover": "voiceover.mp3",
  "subtitles": "captions.srt",
  "scenes": [
    { "image": "scene-01.jpg", "duration_seconds": 8 },
    { "image": "scene-02.jpg", "duration_seconds": 12 }
  ]
}
```

All paths are relative to the manifest file. Leave out `voiceover` or `subtitles` if you do not have those files.

## Render through GitHub

1. Open the repository's **Actions** tab.
2. Select **Free Video Editor (FFmpeg)**.
3. Click **Run workflow**.
4. Enter the path to your manifest, for example `video-project/kidney-health/manifest.json`, and choose an MP4 output filename.
5. When the run completes, download the `rendered-youtube-video` artifact from the run summary.

The workflow runs only when manually triggered. It does not publish anything to YouTube. GitHub Actions usage limits apply, and uploaded artifacts are retained for seven days.

## Render locally

Install FFmpeg, then run:

```bash
python3 scripts/free-video-editor/render.py \
  --manifest video-project/manifest.example.json \
  --output rendered/novara-video.mp4
```

This renderer is designed for image-based explainers and slideshow documentaries. It is not a replacement for a full timeline editor such as Kdenlive or Shotcut, and it does not generate source images or narration for you.
