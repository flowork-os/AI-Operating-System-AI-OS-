#!/usr/bin/env python3
"""
Flowork OS — Sovereign Headless Background Remover Engine (Node 03)
Offline CPU-optimized U2NetP + PyMatting Alpha Matting + Edge Color Decontamination
+ Automatic EXIF/XMP/C2PA/AI-Metadata Scrubber.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from typing import Callable, Optional

SUPPORTED_IMAGE_EXTS = {
    ".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"
}

IMAGE_ENGINE_PYTHON = "/opt/floworkos/runtime/venvs/bg_remove/bin/python3"
SYSTEM_U2NET_DIR = "/opt/floworkos/runtime/models/u2netp"


def get_pictures_dir() -> str:
    """
    Dynamically resolve the active user's Pictures directory without ever
    hardcoding any username. Portable across any Linux user/PC.
    """
    try:
        res = subprocess.run(
            ["xdg-user-dir", "PICTURES"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if res.returncode == 0:
            candidate = res.stdout.strip()
            if candidate and os.path.isdir(candidate):
                return candidate
    except Exception:
        pass

    home_pics = os.path.join(os.path.expanduser("~"), "Pictures")
    os.makedirs(home_pics, exist_ok=True)
    return home_pics


def open_pictures_dir(target_dir: Optional[str] = None) -> None:
    """Open the Pictures folder in the default file manager (detached)."""
    folder = target_dir or get_pictures_dir()
    try:
        subprocess.Popen(
            ["xdg-open", folder],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def build_unique_output_path(input_path: str, output_dir: Optional[str] = None) -> str:
    target_dir = output_dir or get_pictures_dir()
    os.makedirs(target_dir, exist_ok=True)
    stem = os.path.splitext(os.path.basename(input_path))[0]
    candidate = os.path.join(target_dir, f"{stem}_nobg.png")
    if not os.path.exists(candidate):
        return candidate
    idx = 2
    while True:
        candidate = os.path.join(target_dir, f"{stem}_nobg_{idx}.png")
        if not os.path.exists(candidate):
            return candidate
        idx += 1


def _resolve_u2net_home() -> str:
    if os.path.isfile(os.path.join(SYSTEM_U2NET_DIR, "u2netp.onnx")):
        return SYSTEM_U2NET_DIR
    user_u2net = os.path.join(os.path.expanduser("~"), ".u2net")
    if os.path.isfile(os.path.join(user_u2net, "u2netp.onnx")):
        return user_u2net
    return SYSTEM_U2NET_DIR


_WORKER_CODE = r'''
import json
import os
import sys
import numpy as np
from PIL import Image, ImageOps
from scipy.ndimage import distance_transform_edt
import rembg

def emit(p, stage):
    print(json.dumps({"progress": round(float(p), 4), "stage": stage}), flush=True)

def decontaminate_edges(rgba: np.ndarray) -> np.ndarray:
    """
    Replace background color bleed on semi-transparent edge pixels (0 < alpha < 245)
    with the nearest solid foreground pixel color (alpha >= 245).
    """
    alpha = rgba[:, :, 3]
    fg_mask = alpha >= 245
    edge_mask = (alpha > 0) & (alpha < 245)
    if not np.any(fg_mask) or not np.any(edge_mask):
        return rgba
    _, indices = distance_transform_edt(~fg_mask, return_indices=True)
    out = rgba.copy()
    nearest_y = indices[0][edge_mask]
    nearest_x = indices[1][edge_mask]
    out[edge_mask, :3] = rgba[nearest_y, nearest_x, :3]
    return out

def main():
    in_path = sys.argv[1]
    out_path = sys.argv[2]
    use_matting = sys.argv[3] == "1"
    use_defringe = sys.argv[4] == "1"

    emit(0.10, "LOADING")
    with Image.open(in_path) as raw_img:
        img = ImageOps.exif_transpose(raw_img)
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        else:
            img = img.copy()

    emit(0.30, "SEGMENTING")
    session = rembg.new_session("u2netp")
    out_img = None
    if use_matting:
        try:
            out_img = rembg.remove(
                img,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=8,
            )
        except Exception:
            out_img = None

    if out_img is None:
        out_img = rembg.remove(img, session=session, alpha_matting=False)

    rgba = np.array(out_img.convert("RGBA"), dtype=np.uint8)

    if use_defringe:
        emit(0.72, "DEFRINGING")
        rgba = decontaminate_edges(rgba)

    emit(0.90, "SCRUBBING")
    # Fresh Image.fromarray strips 100% of EXIF, XMP, IPTC, C2PA, and AI PNG chunks
    clean_img = Image.fromarray(rgba, mode="RGBA")
    clean_img.save(out_path, format="PNG", optimize=True)

    emit(1.0, "DONE")
    print(json.dumps({
        "status": "ok",
        "engine": "u2netp_pymatting_defringe",
        "input": os.path.abspath(in_path),
        "output": os.path.abspath(out_path),
        "output_dir": os.path.dirname(os.path.abspath(out_path)),
        "width": int(clean_img.width),
        "height": int(clean_img.height),
        "metadata_scrubbed": True,
        "bytes": os.path.getsize(out_path),
    }), flush=True)

if __name__ == "__main__":
    main()
'''


def remove_background_image(
    input_path: str,
    output_path: Optional[str] = None,
    alpha_matting: bool = True,
    decontaminate: bool = True,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    """
    Remove image background offline using U2NetP + PyMatting alpha matting +
    edge color decontamination, exporting a metadata-free transparent PNG.
    """
    if not os.path.isfile(input_path):
        raise FileNotFoundError(f"Input image file not found: {input_path}")

    ext = os.path.splitext(input_path)[1].lower()
    if ext not in SUPPORTED_IMAGE_EXTS:
        raise ValueError(
            f"Unsupported image format '{ext}'. Supported: {sorted(SUPPORTED_IMAGE_EXTS)}"
        )

    py_bin = IMAGE_ENGINE_PYTHON if os.path.isfile(IMAGE_ENGINE_PYTHON) else (shutil.which("python3") or sys.executable)
    out_path = output_path or build_unique_output_path(input_path)
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)

    env = os.environ.copy()
    env["U2NET_HOME"] = _resolve_u2net_home()
    env["NUMBA_CACHE_DIR"] = "/tmp/flowork_numba_cache"
    env["OMP_NUM_THREADS"] = str(max(1, min(8, os.cpu_count() or 4)))

    cmd = [
        py_bin,
        "-c",
        _WORKER_CODE,
        input_path,
        out_path,
        "1" if alpha_matting else "0",
        "1" if decontaminate else "0",
    ]

    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env,
        bufsize=1,
    )

    final_result = None
    if proc.stdout is not None:
        for raw_line in proc.stdout:
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except Exception:
                continue
            if "progress" in payload and "stage" in payload:
                if on_progress:
                    on_progress(float(payload["progress"]), str(payload["stage"]))
            elif payload.get("status") == "ok":
                final_result = payload

    stderr_text = proc.stderr.read() if proc.stderr is not None else ""
    rc = proc.wait()
    if rc != 0 or not final_result or not os.path.isfile(out_path):
        raise RuntimeError(f"Background removal failed (rc={rc}): {stderr_text.strip()[-400:]}")

    return final_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flowork OS Headless Background Remover Engine (Node 03)"
    )
    parser.add_argument("input", help="Input image file (.png, .jpg, .webp, .bmp, .tiff)")
    parser.add_argument("-o", "--output", help="Explicit output PNG path")
    parser.add_argument("--output-dir", help="Output directory (default: user Pictures folder)")
    parser.add_argument("--no-matting", action="store_true", help="Disable PyMatting alpha matting")
    parser.add_argument("--no-defringe", action="store_true", help="Disable edge color decontamination")
    parser.add_argument("--open-folder", action="store_true", help="Open Pictures folder when finished")
    parser.add_argument("--json-progress", action="store_true", help="Emit JSON progress lines")
    args = parser.parse_args()

    out_path = args.output
    if not out_path and args.output_dir:
        out_path = build_unique_output_path(args.input, args.output_dir)

    def _emit(p: float, stage: str) -> None:
        if args.json_progress:
            print(json.dumps({"progress": round(p, 4), "stage": stage}), flush=True)

    try:
        result = remove_background_image(
            args.input,
            output_path=out_path,
            alpha_matting=not args.no_matting,
            decontaminate=not args.no_defringe,
            on_progress=_emit,
        )
        if args.open_folder:
            open_pictures_dir(result["output_dir"])
        print(json.dumps(result), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "error", "error": str(exc)}), file=sys.stderr, flush=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
