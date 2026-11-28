#!/usr/bin/env python3
# ==============================================================================
# FLOWORK OS - 4K UHD AUDIO-VISUAL MASTER ENGINE (NODE 07)
# Module: /opt/floworkos/engine/renderer_4k/renderer_4k.py
# Version: 1.0.0 (Sovereign Rust-Kernel Linux 7.3 Integration)
# Hardware: NVIDIA RTX 4060 NVENC Hardware Acceleration + CPU Fallback
# ==============================================================================

import os
import sys
import json
import time
import shutil
import argparse
import threading
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

DEFAULT_WIDTH = 3840
DEFAULT_HEIGHT = 2160
DEFAULT_FPS = 30
DEFAULT_AUDIO_BITRATE = "320k"

# ------------------------------------------------------------------------------
# 1. HARDWARE & ENCODER DETECTION
# ------------------------------------------------------------------------------

def detect_best_encoder() -> str:
    """Detect whether NVIDIA NVENC is available and functional; fallback to libx264."""
    try:
        cmd = [
            "ffmpeg", "-hide_banner", "-f", "lavfi", "-i", "color=c=black:s=256x256:d=0.1",
            "-c:v", "h264_nvenc", "-f", "null", "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if res.returncode == 0:
            return "h264_nvenc"
    except Exception:
        pass
    return "libx264"


# ------------------------------------------------------------------------------
# 2. MEDIA PROBING
# ------------------------------------------------------------------------------

def probe_audio_info(file_path: str) -> Dict[str, Any]:
    """Extract audio duration (seconds), sample rate, channels, bitrate, and metadata."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")

    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,bit_rate,size:stream=codec_name,sample_rate,channels,duration",
        "-of", "json", file_path
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(proc.stdout)
        
        format_info = data.get("format", {})
        streams = data.get("streams", [])
        audio_stream = next((s for s in streams if s.get("codec_name") not in ["png", "mjpeg", "bmp"]), streams[0] if streams else {})
        
        # Duration priority: stream duration -> format duration
        dur_str = audio_stream.get("duration") or format_info.get("duration") or "0"
        duration = float(dur_str)
        
        sample_rate = int(audio_stream.get("sample_rate", 44100))
        channels = int(audio_stream.get("channels", 2))
        codec = audio_stream.get("codec_name", "unknown")
        bit_rate = int(format_info.get("bit_rate") or audio_stream.get("bit_rate") or 0)
        
        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "duration": duration,
            "duration_str": format_duration(duration),
            "sample_rate": sample_rate,
            "channels": channels,
            "codec": codec,
            "bit_rate": bit_rate,
            "size_bytes": int(format_info.get("size", 0)),
        }
    except Exception as e:
        raise RuntimeError(f"Gagal menganalisis file audio '{file_path}': {e}")


def probe_image_info(file_path: str) -> Dict[str, Any]:
    """Extract image width, height, and format."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Image file not found: {file_path}")

    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,codec_name:format=size",
        "-of", "json", file_path
    ]
    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(proc.stdout)
        streams = data.get("streams", [])
        if not streams:
            raise ValueError("No video/image stream found")
        s = streams[0]
        w = int(s.get("width", 0))
        h = int(s.get("height", 0))
        codec = s.get("codec_name", "")
        return {
            "path": file_path,
            "filename": os.path.basename(file_path),
            "width": w,
            "height": h,
            "aspect": (w / h) if h > 0 else 1.0,
            "codec": codec,
        }
    except Exception as e:
        raise RuntimeError(f"Gagal membaca metadata gambar '{file_path}': {e}")


def format_duration(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    total_sec = int(round(seconds))
    m, s = divmod(total_sec, 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    return f"{m:02d}:{s:02d}"


# ------------------------------------------------------------------------------
# 3. FILTERGRAPH BUILDER FOR 4K RENDERING
# ------------------------------------------------------------------------------

def build_4k_render_graph(
    images: List[str],
    total_duration: float,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    fit_style: str = "smart_blur",        # smart_blur | crop | pad_black
    motion_style: str = "ken_burns",     # ken_burns | crossfade | still
    visualizer_style: str = "neon_wave", # neon_wave | spectrum_bars | subtle_pulse | none
    audio_mastering: str = "youtube_lufs", # youtube_lufs | clarity_boost | original
) -> Dict[str, Any]:
    """
    Constructs an optimized FFmpeg filtergraph for single or multiple images
    with audio-reactive visualizer and 4K UHD smart scaling.
    """
    num_images = len(images)
    inputs = []
    filter_complex_parts = []
    
    # Audio input will always be input 0
    # Images will be input 1 to N
    
    # 1. Image Canvas Scaling Template per image index
    def get_canvas_filter(img_input_idx: int, out_label: str) -> str:
        in_tag = f"[{img_input_idx}:v]"
        if fit_style == "smart_blur":
            # High-performance blurred background: downscale to 360p, fast boxblur, upscale bilinear + crisp foreground
            return (
                f"{in_tag}split=2[fg_raw_{img_input_idx}][bg_raw_{img_input_idx}];"
                f"[bg_raw_{img_input_idx}]scale=640:360:force_original_aspect_ratio=increase,"
                f"crop=640:360,boxblur=15:5,scale={width}:{height}:flags=bilinear,eq=brightness=-0.18[bg_{img_input_idx}];"
                f"[fg_raw_{img_input_idx}]scale={width}:{height}:force_original_aspect_ratio=decrease[fg_{img_input_idx}];"
                f"[bg_{img_input_idx}][fg_{img_input_idx}]overlay=(W-w)/2:(H-h)/2[{out_label}]"
            )
        elif fit_style == "crop":
            return (
                f"{in_tag}scale={width}:{height}:force_original_aspect_ratio=increase,"
                f"crop={width}:{height}[{out_label}]"
            )
        else:  # pad_black
            return (
                f"{in_tag}scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black[{out_label}]"
            )

    # A. SINGLE IMAGE SCENARIO
    if num_images == 1:
        # One image
        canvas_filter = get_canvas_filter(1, "base_canvas")
        filter_complex_parts.append(canvas_filter)

        if motion_style == "ken_burns":
            # Smooth slow zoom in from 1.0 to 1.06
            total_frames = max(1, int(total_duration * fps))
            # Smooth zoom step
            zoom_step = 0.06 / total_frames if total_frames > 0 else 0.0001
            ken_filter = (
                f"[base_canvas]zoompan=z='min(zoom+{zoom_step:.7f},1.06)':"
                f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={width}x{height}:fps={fps}[video_canvas]"
            )
            filter_complex_parts.append(ken_filter)
        else:
            # Still mode or default
            filter_complex_parts.append(f"[base_canvas]copy[video_canvas]")

    # B. MULTIPLE IMAGES SCENARIO
    else:
        # Prepare each image canvas
        for i in range(num_images):
            img_idx = i + 1
            filter_complex_parts.append(get_canvas_filter(img_idx, f"canvas_{i}"))

        if motion_style == "crossfade":
            # Calculate transition duration and slide durations
            trans_sec = min(1.2, (total_duration / num_images) * 0.3)
            slide_sec = (total_duration + (num_images - 1) * trans_sec) / num_images
            
            # Trim/loop each canvas to slide_sec
            for i in range(num_images):
                filter_complex_parts.append(
                    f"[canvas_{i}]loop=-1:size=1:start=0,trim=duration={slide_sec:.3f},"
                    f"setpts=PTS-STARTPTS[slide_{i}]"
                )

            # Chain xfade transitions
            last_tag = "[slide_0]"
            for i in range(1, num_images):
                offset = i * slide_sec - i * trans_sec
                out_tag = f"[xf_{i}]" if i < num_images - 1 else "[video_canvas]"
                filter_complex_parts.append(
                    f"{last_tag}[slide_{i}]xfade=transition=fade:duration={trans_sec:.2f}:offset={offset:.3f}{out_tag}"
                )
                last_tag = out_tag
        else:
            # Equal time slice without fade or simple concat
            slide_sec = total_duration / num_images
            concat_tags = []
            for i in range(num_images):
                filter_complex_parts.append(
                    f"[canvas_{i}]loop=-1:size=1:start=0,trim=duration={slide_sec:.3f},"
                    f"setpts=PTS-STARTPTS[slide_{i}]"
                )
                concat_tags.append(f"[slide_{i}]")
            
            filter_complex_parts.append(
                f"{''.join(concat_tags)}concat=n={num_images}:v=1:a=0[video_canvas]"
            )

    # 2. AUDIO PROCESSING & MASTERING
    audio_filters = []
    if audio_mastering == "youtube_lufs":
        audio_filters.append("loudnorm=I=-14:TP=-1.5:LRA=11")
    elif audio_mastering == "clarity_boost":
        audio_filters.append("highpass=f=35,bass=g=2.2:f=110:w=0.6,treble=g=1.8:f=7500:w=0.6,loudnorm=I=-14:TP=-1.5:LRA=11")
    else:  # original
        audio_filters.append("anull")

    audio_chain_str = ",".join(audio_filters)
    filter_complex_parts.append(f"[0:a]{audio_chain_str},asplit=2[master_audio][vis_audio]")

    # 3. AUDIO-REACTIVE VISUALIZER
    if visualizer_style == "neon_wave":
        # Cyan neon wave with slight glow overlay at bottom margin (optimized 1080p wave upscaled to 4K)
        filter_complex_parts.append(
            f"[vis_audio]showwaves=s=1920x240:mode=line:colors=0x00e5ff@0.9:scale=sqrt,"
            f"scale={width}:240:flags=bilinear,format=rgba[wave_raw];"
            f"[video_canvas][wave_raw]overlay=0:H-260:format=auto,format=yuv420p[final_v]"
        )
    elif visualizer_style == "spectrum_bars":
        # Equalizer frequency bars at bottom with gradient cyan/purple
        filter_complex_parts.append(
            f"[vis_audio]showfreqs=s=1920x320:mode=bar:fscale=log:ascale=cbrt:"
            f"colors=0x00e5ff|0x9945ff@0.85,scale={width}:320:flags=bilinear,format=rgba[freq_raw];"
            f"[video_canvas][freq_raw]overlay=0:H-340:format=auto,format=yuv420p[final_v]"
        )
    elif visualizer_style == "subtle_pulse":
        # Gentle audio wave in middle with semi-transparency
        filter_complex_parts.append(
            f"[vis_audio]showwaves=s=1920x180:mode=cline:colors=0xffd200@0.75:scale=log,"
            f"scale={width}:180:flags=bilinear,format=rgba[wave_raw];"
            f"[video_canvas][wave_raw]overlay=0:H-200:format=auto,format=yuv420p[final_v]"
        )
    else:  # none
        filter_complex_parts.append(f"[video_canvas]format=yuv420p[final_v]")

    full_filter_complex = ";\n".join(filter_complex_parts)
    return {
        "filter_complex": full_filter_complex,
        "v_out": "[final_v]",
        "a_out": "[master_audio]"
    }


# ------------------------------------------------------------------------------
# 4. RENDER EXECUTION ENGINE WITH TELEMETRY
# ------------------------------------------------------------------------------

def render_4k_bundle(
    audio_file: str,
    image_files: List[str],
    output_path: Optional[str] = None,
    width: int = DEFAULT_WIDTH,
    height: int = DEFAULT_HEIGHT,
    fps: int = DEFAULT_FPS,
    fit_style: str = "smart_blur",
    motion_style: str = "ken_burns",
    visualizer_style: str = "neon_wave",
    audio_mastering: str = "youtube_lufs",
    encoder: Optional[str] = None,
    progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
) -> Dict[str, Any]:
    """
    Renders 4K UHD video from 1 Audio + 1 or more Images with full telemetry.
    """
    start_time = time.time()
    
    # Validate inputs
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file '{audio_file}' tidak ditemukan.")
    if not image_files:
        raise ValueError("Minimal satu file gambar diperlukan untuk render.")
    for img in image_files:
        if not os.path.exists(img):
            raise FileNotFoundError(f"File gambar '{img}' tidak ditemukan.")

    # Probe Audio
    audio_meta = probe_audio_info(audio_file)
    total_duration = audio_meta["duration"]
    if total_duration <= 0:
        raise ValueError("Durasi audio terdeteksi 0 detik.")

    # Determine Output Path
    if not output_path:
        audio_stem = Path(audio_file).stem
        target_dir = "/opt/floworkos/documents" if os.path.exists("/opt/floworkos/documents") else os.path.dirname(audio_file)
        output_path = os.path.join(target_dir, f"{audio_stem}_4K_UHD.mp4")

    # Ensure output directory exists
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

    # Determine Encoder
    if not encoder or encoder == "auto":
        encoder = detect_best_encoder()

    # Build Filtergraph
    fg_data = build_4k_render_graph(
        images=image_files,
        total_duration=total_duration,
        width=width,
        height=height,
        fps=fps,
        fit_style=fit_style,
        motion_style=motion_style,
        visualizer_style=visualizer_style,
        audio_mastering=audio_mastering
    )

    # Assemble FFmpeg Command
    cmd = ["ffmpeg", "-y", "-hide_banner"]

    # Input 0: Audio
    cmd.extend(["-i", audio_file])

    # Inputs 1..N: Images
    for img in image_files:
        if len(image_files) == 1 and motion_style != "ken_burns":
            # Fast single still loop
            cmd.extend(["-loop", "1", "-t", str(total_duration), "-i", img])
        else:
            cmd.extend(["-loop", "1", "-i", img])

    # Filter Complex
    cmd.extend(["-filter_complex", fg_data["filter_complex"]])
    cmd.extend(["-map", fg_data["v_out"], "-map", fg_data["a_out"]])

    # Video Encoding Flags
    if encoder == "h264_nvenc":
        cmd.extend([
            "-c:v", "h264_nvenc",
            "-preset", "p4",
            "-cq", "19",
            "-b:v", "38M",
            "-maxrate", "55M",
            "-bufsize", "55M",
            "-pix_fmt", "yuv420p"
        ])
    else:  # libx264
        cmd.extend([
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "18",
            "-pix_fmt", "yuv420p"
        ])

    # Audio Encoding Flags
    cmd.extend([
        "-c:a", "aac",
        "-b:a", DEFAULT_AUDIO_BITRATE,
        "-ar", "48000"
    ])

    # Master Duration & MP4 Metadata
    cmd.extend([
        "-t", f"{total_duration:.3f}",
        "-movflags", "+faststart",
        "-progress", "pipe:1",
        output_path
    ])

    # Execute and monitor progress with dedicated background stderr drainer
    # Prevents pipe buffer deadlock when FFmpeg outputs large filter/encode logs
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    stderr_lines = []
    def _drain_stderr(pipe):
        try:
            for s_line in iter(pipe.readline, ''):
                if not s_line:
                    break
                stderr_lines.append(s_line)
                if len(stderr_lines) > 250:
                    stderr_lines.pop(0)
        except Exception:
            pass
        finally:
            try:
                pipe.close()
            except Exception:
                pass

    t_stderr = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
    t_stderr.start()

    fps_current = 0.0
    speed_current = "0.0x"
    pct_current = 0.0

    while True:
        line = proc.stdout.readline()
        if not line:
            if proc.poll() is not None:
                break
            continue
        line = line.strip()
        if not line:
            continue

        if "=" in line:
            k, v = line.split("=", 1)
            k = k.strip()
            v = v.strip()
            if k == "out_time_ms":
                try:
                    out_ms = int(v)
                    cur_sec = out_ms / 1_000_000.0
                    pct_current = min(99.9, (cur_sec / total_duration) * 100.0)
                except ValueError:
                    pass
            elif k == "fps":
                try:
                    fps_current = float(v)
                except ValueError:
                    pass
            elif k == "speed":
                speed_current = v
            elif k == "progress" and v == "end":
                pct_current = 100.0

            if progress_callback:
                progress_callback({
                    "percent": pct_current,
                    "fps": fps_current,
                    "speed": speed_current,
                    "encoder": encoder,
                    "duration": total_duration,
                    "output_path": output_path,
                })

    try:
        proc.stdout.close()
    except Exception:
        pass
    proc.wait()
    t_stderr.join(timeout=2.0)
    stderr_output = "".join(stderr_lines)

    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg render gagal (code {proc.returncode}):\n{stderr_output[-800:]}")

    elapsed = time.time() - start_time
    file_size_mb = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0.0

    result = {
        "success": True,
        "output_path": output_path,
        "filename": os.path.basename(output_path),
        "duration": total_duration,
        "duration_str": format_duration(total_duration),
        "resolution": f"{width}x{height}",
        "encoder": encoder,
        "file_size_mb": round(file_size_mb, 2),
        "render_time_sec": round(elapsed, 2),
        "avg_fps": round((total_duration * fps) / elapsed, 1) if elapsed > 0 else 0.0,
        "motion_style": motion_style,
        "visualizer_style": visualizer_style,
        "audio_mastering": audio_mastering
    }

    if progress_callback:
        progress_callback({
            "percent": 100.0,
            "fps": result["avg_fps"],
            "speed": "Done",
            "encoder": encoder,
            "duration": total_duration,
            "output_path": output_path,
            "done": True,
            "result": result
        })

    return result


# ------------------------------------------------------------------------------
# 5. CLI INTERFACE
# ------------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Flowork OS 4K UHD Audio-Visual Master Engine (Node 07)")
    parser.add_argument("--audio", "-a", required=True, help="Path ke file audio (.mp3, .wav, .flac, etc.)")
    parser.add_argument("--image", "-i", action="append", dest="images", required=True, help="Path ke gambar (bisa diulang untuk multi-image)")
    parser.add_argument("--output", "-o", default=None, help="Path file output MP4 4K")
    parser.add_argument("--motion", choices=["ken_burns", "crossfade", "still"], default="ken_burns", help="Gaya pergerakan gambar")
    parser.add_argument("--fit", choices=["smart_blur", "crop", "pad_black"], default="smart_blur", help="Penyesuaian rasio gambar ke 4K")
    parser.add_argument("--visualizer", choices=["neon_wave", "spectrum_bars", "subtle_pulse", "none"], default="neon_wave", help="Efek visual reaktif audio")
    parser.add_argument("--mastering", choices=["youtube_lufs", "clarity_boost", "original"], default="youtube_lufs", help="Tuning audio mastering")
    parser.add_argument("--encoder", choices=["auto", "h264_nvenc", "libx264"], default="auto", help="Pilihan hardware encoder")
    
    args = parser.parse_args()

    print("=================================================================")
    print(" 👑 FLOWORK OS - 4K UHD AUDIO-VISUAL MASTER (NODE 07) ")
    print("=================================================================")
    print(f"🎵 Audio     : {args.audio}")
    print(f"🖼️ Images    : {len(args.images)} file(s)")
    print(f"🎬 Motion    : {args.motion}")
    print(f"🎨 Fit Mode  : {args.fit}")
    print(f"✨ Visualizer: {args.visualizer}")
    print(f"🎚️ Mastering : {args.mastering}")
    print("-----------------------------------------------------------------")

    def cli_progress(p):
        pct = p.get("percent", 0.0)
        fps = p.get("fps", 0.0)
        speed = p.get("speed", "")
        enc = p.get("encoder", "")
        sys.stdout.write(f"\r⏳ Rendering 4K [{enc}]: {pct:5.1f}% | {fps:5.1f} FPS | Speed: {speed}  ")
        sys.stdout.flush()

    try:
        res = render_4k_bundle(
            audio_file=args.audio,
            image_files=args.images,
            output_path=args.output,
            motion_style=args.motion,
            fit_style=args.fit,
            visualizer_style=args.visualizer,
            audio_mastering=args.mastering,
            encoder=args.encoder,
            progress_callback=cli_progress
        )
        print("\n\n✅ RENDER 4K SELESAI BERHASIL!")
        print(f"📁 Output File : {res['output_path']}")
        print(f"⏱️ Durasi Video: {res['duration_str']}")
        print(f"💾 Ukuran File : {res['file_size_mb']} MB")
        print(f"⚡ Waktu Render: {res['render_time_sec']} detik (Rata-rata {res['avg_fps']} FPS)")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
