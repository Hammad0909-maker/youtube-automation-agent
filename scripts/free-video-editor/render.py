#!/usr/bin/env python3
"""Render a simple scene-based YouTube video with free FFmpeg tools.

Manifest paths are relative to the manifest file. Each scene requires an image
and duration_seconds. Optional voiceover and subtitles can be provided.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path


def run(command: list[str]) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, check=True)


def probe_duration(path: Path) -> float:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return float(result.stdout.strip())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, help="Path to project JSON")
    parser.add_argument("--output", required=True, help="Output MP4 path")
    args = parser.parse_args()

    manifest_path = Path(args.manifest).resolve()
    output_path = Path(args.output).resolve()
    if not manifest_path.is_file():
        raise SystemExit(f"Manifest not found: {manifest_path}")
    if shutil.which("ffmpeg") is None or shutil.which("ffprobe") is None:
        raise SystemExit("FFmpeg and ffprobe must be installed.")

    project = json.loads(manifest_path.read_text(encoding="utf-8"))
    scenes = project.get("scenes")
    if not isinstance(scenes, list) or not scenes:
        raise SystemExit("Manifest must contain a non-empty 'scenes' array.")

    base = manifest_path.parent
    resolved_scenes = []
    total_duration = 0.0
    for index, scene in enumerate(scenes, start=1):
        image_value = scene.get("image")
        duration = scene.get("duration_seconds")
        if not image_value or not isinstance(duration, (int, float)) or duration <= 0:
            raise SystemExit(
                f"Scene {index} needs an image path and positive duration_seconds."
            )
        image_path = (base / image_value).resolve()
        if not image_path.is_file():
            raise SystemExit(f"Scene {index} image not found: {image_path}")
        resolved_scenes.append((image_path, float(duration)))
        total_duration += float(duration)

    voiceover = project.get("voiceover")
    voiceover_path = (base / voiceover).resolve() if voiceover else None
    if voiceover_path and not voiceover_path.is_file():
        raise SystemExit(f"Voice-over audio not found: {voiceover_path}")
    if voiceover_path:
        audio_duration = probe_duration(voiceover_path)
        if audio_duration > total_duration + 0.25:
            raise SystemExit(
                f"Voice-over is {audio_duration:.1f}s but scenes total "
                f"{total_duration:.1f}s. Increase scene durations to fit the narration."
            )

    subtitles = project.get("subtitles")
    subtitles_path = (base / subtitles).resolve() if subtitles else None
    if subtitles_path and not subtitles_path.is_file():
        raise SystemExit(f"Subtitle file not found: {subtitles_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="novara-render-") as temp_dir:
        temp = Path(temp_dir)
        clip_paths = []
        for index, (image_path, duration) in enumerate(resolved_scenes, start=1):
            clip_path = temp / f"scene-{index:03d}.mp4"
            clip_paths.append(clip_path)
            vf = (
                "scale=1920:1080:force_original_aspect_ratio=increase,"
                "crop=1920:1080,"
                "zoompan=z='min(zoom+0.0005,1.06)':"
                "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                "d=1:s=1920x1080:fps=30,"
                "format=yuv420p"
            )
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-loop", "1", "-framerate", "30", "-i", str(image_path),
                "-t", f"{duration:.3f}", "-vf", vf,
                "-an", "-c:v", "libx264", "-preset", "veryfast",
                "-crf", "20", "-pix_fmt", "yuv420p", str(clip_path),
            ])

        concat_file = temp / "concat.txt"
        concat_file.write_text(
            "".join(f"file '{p.as_posix()}'\n" for p in clip_paths),
            encoding="utf-8",
        )
        silent_video = temp / "silent.mp4"
        run([
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-f", "concat", "-safe", "0", "-i", str(concat_file),
            "-c", "copy", str(silent_video),
        ])

        current_video = silent_video
        if subtitles_path:
            subtitled_video = temp / "subtitled.mp4"
            # Runner paths use forward slashes; escape punctuation for FFmpeg filter syntax.
            subtitle_filter_path = (
                subtitles_path.as_posix()
                .replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("'", "\\'")
            )
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(current_video),
                "-vf", f"subtitles='{subtitle_filter_path}':force_style="
                      "'FontName=Arial,FontSize=22,Outline=2,Shadow=1,MarginV=45'",
                "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                "-pix_fmt", "yuv420p", "-an", str(subtitled_video),
            ])
            current_video = subtitled_video

        if voiceover_path:
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(current_video), "-i", str(voiceover_path),
                "-map", "0:v:0", "-map", "1:a:0",
                "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-shortest", "-movflags", "+faststart", str(output_path),
            ])
        else:
            run([
                "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                "-i", str(current_video), "-c:v", "copy",
                "-movflags", "+faststart", str(output_path),
            ])

    print(f"Finished video: {output_path}")
    print(f"Scene duration total: {total_duration:.1f} seconds")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
