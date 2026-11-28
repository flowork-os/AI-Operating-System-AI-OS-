#!/usr/bin/env python3
"""
Flowork OS — Sovereign Suno Cover Thumbnail Engine (Node 05)
Generates high-CTR 16:9 YouTube split-comparison cover thumbnails:
  - Left half: Original singer (Penyanyi Asli)
  - Right half: Cover singer (Penyanyi Cover)
  - Center: Glowing yellow lightning bolt divider + glowing 'VS' badge
  - Bottom: Bold italic yellow uppercase title with thick black outline & shadow
  - Optional: Small subtitle below main title (no flags, channel-agnostic)
  - Output: Saved dynamically to the active user's Pictures directory (never hardcoded)
"""

import argparse
import io
import os
import re
import subprocess
import sys
import time
from typing import Callable, Optional, Tuple

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps

SUPPORTED_IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tiff", ".tif"}

CANVAS_W = 1920
CANVAS_H = 1080
UI_SCALE = CANVAS_W / 1280.0

FONT_CANDIDATES_BLACK_ITALIC = [
    "/usr/share/fonts/opentype/inter/InterDisplay-BlackItalic.otf",
    "/usr/share/fonts/opentype/inter/Inter-BlackItalic.otf",
    "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBoldItalic.otf",
    "/usr/share/fonts/opentype/inter/Inter-ExtraBoldItalic.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
]

FONT_CANDIDATES_BOLD_ITALIC = [
    "/usr/share/fonts/opentype/inter/InterDisplay-BoldItalic.otf",
    "/usr/share/fonts/opentype/inter/Inter-BoldItalic.otf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-BoldItalic.ttf",
]


def get_pictures_dir() -> str:
    """
    Dynamically resolve the active user's Pictures directory without hardcoding
    any username. Works across any Flowork OS installation or Live ISO user.
    """
    try:
        res = subprocess.run(
            ["xdg-user-dir", "PICTURES"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        p = res.stdout.strip()
        if p and os.path.isabs(p):
            os.makedirs(p, exist_ok=True)
            return p
    except Exception:
        pass

    fallback = os.path.join(os.path.expanduser("~"), "Pictures")
    os.makedirs(fallback, exist_ok=True)
    return fallback


def open_pictures_dir(path: Optional[str] = None) -> None:
    target = path or get_pictures_dir()
    try:
        subprocess.Popen(["xdg-open", target], start_new_session=True)
    except Exception:
        pass


def _pick_font(candidates: list, size: int) -> ImageFont.FreeTypeFont:
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size=size)
            except Exception:
                continue
    return ImageFont.load_default()


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower()).strip("_")
    return cleaned[:40] if cleaned else "cover"


def _unique_output_path(out_dir: str, title: str, ext: str = ".jpg") -> str:
    slug = _slugify(title)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    base = f"suno_cover_{slug}_{stamp}"
    candidate = os.path.join(out_dir, f"{base}{ext}")
    idx = 2
    while os.path.exists(candidate):
        candidate = os.path.join(out_dir, f"{base}_{idx}{ext}")
        idx += 1
    return candidate


def _prepare_half(image_path: str, width: int, height: int) -> Image.Image:
    with Image.open(image_path) as raw:
        img = ImageOps.exif_transpose(raw).convert("RGB")
    src_w, src_h = img.size
    # Upper-center bias (0.5, 0.22) keeps singer faces/heads framed cleanly
    fitted = ImageOps.fit(img, (width, height), method=Image.Resampling.LANCZOS, centering=(0.5, 0.22))
    # Adaptive HD sharpening: stronger detail recovery when source photo is upscaled
    if src_w < width or src_h < height:
        fitted = fitted.filter(ImageFilter.UnsharpMask(radius=1.6, percent=145, threshold=3))
        fitted = ImageEnhance.Sharpness(fitted).enhance(1.12)
    else:
        fitted = fitted.filter(ImageFilter.UnsharpMask(radius=1.0, percent=85, threshold=3))
    fitted = ImageEnhance.Contrast(fitted).enhance(1.08)
    fitted = ImageEnhance.Color(fitted).enhance(1.10)
    return fitted.convert("RGBA")


def _build_bottom_vignette(width: int, height: int) -> Image.Image:
    grad = Image.new("L", (1, height), 0)
    start_y = int(height * 0.54)
    for y in range(start_y, height):
        t = (y - start_y) / max(1, height - start_y - 1)
        # Smooth ease-in curve up to ~220 alpha at bottom edge
        alpha = int(220 * (t ** 1.45))
        grad.putpixel((0, y), alpha)
    alpha_mask = grad.resize((width, height), Image.Resampling.BILINEAR)
    overlay = Image.new("RGBA", (width, height), (6, 8, 14, 255))
    overlay.putalpha(alpha_mask)
    return overlay


def _build_center_seam_shadow(width: int, height: int) -> Image.Image:
    seam = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(seam)
    cx = width // 2
    draw.line([(cx, 0), (cx, height)], fill=(0, 0, 0, 190), width=26)
    return seam.filter(ImageFilter.GaussianBlur(radius=14))


def _draw_sharp_polyline(draw: ImageDraw.ImageDraw, pts: list, fill: tuple, width: int) -> None:
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=fill, width=width)
    r = width / 2.0
    for px, py in pts[1:-1]:
        draw.ellipse((px - r, py - r, px + r, py + r), fill=fill)


def _build_lightning_and_question(width: int, height: int) -> Image.Image:
    """
    Render the glowing yellow lightning bolt divider and upper-center 'VS' badge
    at 2x supersampling for crisp anti-aliased edges.
    """
    scale = 2
    sw, sh = width * scale, height * scale
    s = scale * (width / 1280.0)
    cx = sw // 2

    # Jagged vertical lightning bolt path from top down behind the title zone
    bolt_pts = [
        (cx + int(round(22 * s)), int(round(-10 * s))),
        (cx - int(round(30 * s)), int(round(110 * s))),
        (cx + int(round(18 * s)), int(round(132 * s))),
        (cx - int(round(38 * s)), int(round(270 * s))),
        (cx + int(round(26 * s)), int(round(292 * s))),
        (cx - int(round(32 * s)), int(round(440 * s))),
        (cx + int(round(18 * s)), int(round(462 * s))),
        (cx - int(round(20 * s)), int(round(595 * s))),
        (cx + int(round(8 * s)), int(round(640 * s))),
    ]

    # 1. Outer warm orange-gold glow
    glow_outer = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d_go = ImageDraw.Draw(glow_outer)
    _draw_sharp_polyline(d_go, bolt_pts, fill=(255, 135, 0, 225), width=max(2, int(round(36 * s))))
    glow_outer = glow_outer.filter(ImageFilter.GaussianBlur(radius=20 * s))

    # 2. Inner bright yellow glow
    glow_inner = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d_gi = ImageDraw.Draw(glow_inner)
    _draw_sharp_polyline(d_gi, bolt_pts, fill=(255, 228, 0, 245), width=max(2, int(round(18 * s))))
    glow_inner = glow_inner.filter(ImageFilter.GaussianBlur(radius=7 * s))

    # 3. Crisp bolt body + white-hot core
    bolt_core = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d_bc = ImageDraw.Draw(bolt_core)
    _draw_sharp_polyline(d_bc, bolt_pts, fill=(25, 14, 0, 230), width=max(2, int(round(16 * s))))
    _draw_sharp_polyline(d_bc, bolt_pts, fill=(255, 234, 0, 255), width=max(2, int(round(11 * s))))
    _draw_sharp_polyline(d_bc, bolt_pts, fill=(255, 254, 232, 255), width=max(1, int(round(4 * s))))

    bolt_layer = Image.alpha_composite(glow_outer, glow_inner)
    bolt_layer = Image.alpha_composite(bolt_layer, bolt_core)

    # Smoothly fade the bottom tip of the bolt behind the title area
    fade_mask = Image.new("L", (1, sh), 255)
    fade_start = int(sh * 0.74)
    fade_end = int(sh * 0.92)
    for y in range(fade_start, sh):
        if y >= fade_end:
            a = 0
        else:
            t = (y - fade_start) / max(1, fade_end - fade_start)
            a = int(255 * (1.0 - t))
        fade_mask.putpixel((0, y), a)
    bolt_alpha = bolt_layer.getchannel("A")
    fade_full = fade_mask.resize((sw, sh), Image.Resampling.BILINEAR)
    from PIL import ImageChops
    bolt_layer.putalpha(ImageChops.multiply(bolt_alpha, fade_full))

    # 4. Upper-center glowing 'VS' badge
    vs_font = _pick_font(FONT_CANDIDATES_BLACK_ITALIC, int(round(155 * s)))
    vs_x = cx
    vs_y = int(round(195 * s))

    vs_glow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d_vg = ImageDraw.Draw(vs_glow)
    d_vg.text(
        (vs_x, vs_y),
        "VS",
        font=vs_font,
        anchor="mm",
        fill=(255, 85, 0, 245),
        stroke_width=max(2, int(round(20 * s))),
        stroke_fill=(255, 65, 0, 245),
    )
    vs_glow = vs_glow.filter(ImageFilter.GaussianBlur(radius=16 * s))

    vs_fg = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    d_vf = ImageDraw.Draw(vs_fg)
    # Drop shadow
    d_vf.text(
        (vs_x + int(round(5 * s)), vs_y + int(round(8 * s))),
        "VS",
        font=vs_font,
        anchor="mm",
        fill=(0, 0, 0, 230),
        stroke_width=max(2, int(round(13 * s))),
        stroke_fill=(0, 0, 0, 230),
    )
    # Dark red-brown outline + vivid yellow fill
    d_vf.text(
        (vs_x, vs_y),
        "VS",
        font=vs_font,
        anchor="mm",
        fill=(255, 234, 0, 255),
        stroke_width=max(2, int(round(10 * s))),
        stroke_fill=(125, 22, 0, 255),
    )

    layer = Image.alpha_composite(bolt_layer, vs_glow)
    layer = Image.alpha_composite(layer, vs_fg)
    return layer.resize((width, height), Image.Resampling.LANCZOS)


def _wrap_title_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_w: int) -> list:
    words = text.split()
    if len(words) <= 1:
        return [text]
    best_split = None
    best_diff = 10**9
    for i in range(1, len(words)):
        l1 = " ".join(words[:i])
        l2 = " ".join(words[i:])
        w1 = draw.textbbox((0, 0), l1, font=font)[2]
        w2 = draw.textbbox((0, 0), l2, font=font)[2]
        if max(w1, w2) <= max_w:
            diff = abs(w1 - w2)
            if diff < best_diff:
                best_diff = diff
                best_split = [l1, l2]
    if best_split:
        return best_split
    return [text]


def _fit_title_layout(
    draw: ImageDraw.ImageDraw, title: str, max_w: int
) -> Tuple[list, ImageFont.FreeTypeFont, int]:
    # Try single line first from 94px down to 66px
    for size in range(94, 64, -2):
        font = _pick_font(FONT_CANDIDATES_BLACK_ITALIC, size)
        bbox = draw.textbbox((0, 0), title, font=font, stroke_width=max(6, int(size * 0.11)))
        if (bbox[2] - bbox[0]) <= max_w:
            return [title], font, size

    # Wrap into 2 balanced lines from 76px down to 44px
    for size in range(76, 42, -2):
        font = _pick_font(FONT_CANDIDATES_BLACK_ITALIC, size)
        lines = _wrap_title_lines(draw, title, font, max_w - 20)
        if len(lines) == 2:
            stroke = max(5, int(size * 0.11))
            w_max = max(
                draw.textbbox((0, 0), ln, font=font, stroke_width=stroke)[2]
                for ln in lines
            )
            if w_max <= max_w:
                return lines, font, size

    font = _pick_font(FONT_CANDIDATES_BLACK_ITALIC, 44)
    return _wrap_title_lines(draw, title, font, max_w), font, 44


def _draw_titles(canvas: Image.Image, title: str, subtitle: str = "") -> Image.Image:
    title_clean = " ".join(title.strip().split()).upper()
    if not title_clean:
        raise ValueError("Judul cover tidak boleh kosong.")
    sub_clean = " ".join(subtitle.strip().split())

    txt_shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d_sh = ImageDraw.Draw(txt_shadow)
    txt_fg = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d_fg = ImageDraw.Draw(txt_fg)

    max_w = CANVAS_W - 110
    lines, font, font_size = _fit_title_layout(d_fg, title_clean, max_w)
    stroke_w = max(6, int(font_size * 0.115))

    line_heights = []
    for ln in lines:
        bb = d_fg.textbbox((0, 0), ln, font=font, stroke_width=stroke_w)
        line_heights.append(bb[3] - bb[1])

    line_gap = int(font_size * 0.14)
    total_title_h = sum(line_heights) + line_gap * (len(lines) - 1)

    sub_font = _pick_font(FONT_CANDIDATES_BOLD_ITALIC, 28) if sub_clean else None
    sub_h = 34 if sub_clean else 0
    sub_gap = 12 if sub_clean else 0

    bottom_margin = 34 if sub_clean else 42
    start_y = CANVAS_H - bottom_margin - sub_h - sub_gap - total_title_h

    cur_y = start_y
    for idx, ln in enumerate(lines):
        lh = line_heights[idx]
        cy = cur_y + lh // 2
        cx = CANVAS_W // 2

        # Heavy drop shadow
        d_sh.text(
            (cx, cy + 7),
            ln,
            font=font,
            anchor="mm",
            fill=(0, 0, 0, 235),
            stroke_width=stroke_w + 3,
            stroke_fill=(0, 0, 0, 235),
        )
        # Crisp black outline + vivid yellow fill
        d_fg.text(
            (cx, cy),
            ln,
            font=font,
            anchor="mm",
            fill=(255, 230, 0, 255),
            stroke_width=stroke_w,
            stroke_fill=(8, 8, 10, 255),
        )
        cur_y += lh + line_gap

    if sub_clean and sub_font is not None:
        sub_y = CANVAS_H - bottom_margin - (sub_h // 2)
        d_sh.text(
            (CANVAS_W // 2, sub_y + 3),
            sub_clean,
            font=sub_font,
            anchor="mm",
            fill=(0, 0, 0, 220),
            stroke_width=5,
            stroke_fill=(0, 0, 0, 220),
        )
        d_fg.text(
            (CANVAS_W // 2, sub_y),
            sub_clean,
            font=sub_font,
            anchor="mm",
            fill=(255, 255, 255, 255),
            stroke_width=4,
            stroke_fill=(8, 8, 10, 255),
        )

    txt_shadow = txt_shadow.filter(ImageFilter.GaussianBlur(radius=4))
    out = Image.alpha_composite(canvas, txt_shadow)
    out = Image.alpha_composite(out, txt_fg)
    return out


def generate_suno_cover(
    left_image: str,
    right_image: str,
    title: str,
    subtitle: str = "",
    output_path: Optional[str] = None,
    on_progress: Optional[Callable[[float, str], None]] = None,
) -> dict:
    """
    Compose a 1280x720 split-comparison YouTube cover thumbnail and save it
    into the active user's Pictures directory (or explicit output_path).
    """
    if not os.path.isfile(left_image):
        raise FileNotFoundError(f"Gambar kiri (penyanyi asli) tidak ditemukan: {left_image}")
    if not os.path.isfile(right_image):
        raise FileNotFoundError(f"Gambar kanan (penyanyi cover) tidak ditemukan: {right_image}")
    if not title or not title.strip():
        raise ValueError("Judul cover wajib diisi.")

    def _prog(pct: float, stage: str):
        if on_progress:
            on_progress(pct, stage)

    _prog(0.15, "FRAMING SINGERS")
    half_w = CANVAS_W // 2
    left_half = _prepare_half(left_image, half_w, CANVAS_H)
    right_half = _prepare_half(right_image, CANVAS_W - half_w, CANVAS_H)

    canvas = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 255))
    canvas.paste(left_half, (0, 0))
    canvas.paste(right_half, (half_w, 0))

    _prog(0.40, "LIGHTING & VIGNETTE")
    canvas = Image.alpha_composite(canvas, _build_center_seam_shadow(CANVAS_W, CANVAS_H))
    canvas = Image.alpha_composite(canvas, _build_bottom_vignette(CANVAS_W, CANVAS_H))

    _prog(0.65, "LIGHTNING & BADGE")
    canvas = Image.alpha_composite(canvas, _build_lightning_and_question(CANVAS_W, CANVAS_H))

    _prog(0.82, "RENDERING TITLE")
    canvas = _draw_titles(canvas, title, subtitle=subtitle)

    _prog(0.92, "SAVING TO PICTURES")
    if output_path:
        out_file = os.path.abspath(os.path.expanduser(output_path))
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
    else:
        pic_dir = get_pictures_dir()
        out_file = _unique_output_path(pic_dir, title, ext=".jpg")

    ext = os.path.splitext(out_file)[1].lower()
    if ext == ".png":
        canvas.convert("RGB").save(out_file, format="PNG", optimize=True)
    else:
        canvas.convert("RGB").save(
            out_file,
            format="JPEG",
            quality=95,
            subsampling=0,
            optimize=True,
        )

    _prog(1.0, "SAVED TO PICS")
    return {
        "output_path": out_file,
        "pictures_dir": os.path.dirname(out_file),
        "width": CANVAS_W,
        "height": CANVAS_H,
        "size_bytes": os.path.getsize(out_file),
        "title": " ".join(title.strip().split()).upper(),
        "subtitle": " ".join(subtitle.strip().split()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Flowork OS Suno Cover Thumbnail Generator (Node 05)"
    )
    parser.add_argument("left_image", help="Path to left image (Penyanyi Asli)")
    parser.add_argument("right_image", help="Path to right image (Penyanyi Cover)")
    parser.add_argument("-t", "--title", required=True, help="Main cover title text")
    parser.add_argument("-s", "--subtitle", default="", help="Optional small subtitle below title")
    parser.add_argument("-o", "--output", default=None, help="Optional explicit output path")
    args = parser.parse_args()

    try:
        res = generate_suno_cover(
            args.left_image,
            args.right_image,
            title=args.title,
            subtitle=args.subtitle,
            output_path=args.output,
        )
        print(
            f"[✓] Suno Cover generated: {res['output_path']} "
            f"({res['width']}x{res['height']}, {res['size_bytes'] // 1024} KB)"
        )
        return 0
    except Exception as exc:
        print(f"[✗] Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
