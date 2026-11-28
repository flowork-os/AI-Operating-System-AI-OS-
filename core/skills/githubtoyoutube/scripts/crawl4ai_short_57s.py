#!/usr/bin/env python3
"""
🎬 SOVEREIGN YOUTUBE SHORT: CRAWL4AI (TRENDING GITHUB REPO)
Repository: unclecode/crawl4ai (87,600+ Stars)
Specs: 1080x1920 (9:16 Vertical Shorts), 30 fps, 57.0s (1710 frames)
Directorial Mandates:
  1. 100% English audio, typography, HUD, subtitles.
  2. Zero-overflow safe margins (X: 90-990, Y: 180-1680) via safe_render_tools.
  3. Persistent top GitHub URL pill + Full Outro Dual-CTA card with stars.
  4. Post-production viral SEO research package integration.
"""

import os
import sys
import math
import subprocess
import cairo

# Import safe render tools
sys.path.insert(0, "/opt/floworkos/skills/githubtoyoutube/scripts")
import safe_render_tools as srt

W, H = 1080, 1920
FPS = 30
DURATION_SEC = 57.0
TOTAL_FRAMES = int(FPS * DURATION_SEC)

AUDIO_WAV = "/opt/floworkos/documents/videos/crawl4ai-short/audio/mastered_voiceover.wav"
if not os.path.exists(AUDIO_WAV):
    AUDIO_WAV = "/tmp/crawl4ai_final_audio_mastered.wav"
OUTPUT_MP4 = "/opt/floworkos/documents/videos/crawl4ai-short/CRAWL4AI_GITHUB_CARTOON_SHORT.mp4"
REPO_OWNER = "unclecode"
REPO_NAME = "crawl4ai"
STARS_COUNT = 87652
REPO_SLUG = f"{REPO_OWNER}/{REPO_NAME}"

# Broadcast Palette
C_BG_DARK = (0.07, 0.08, 0.12)
C_CYAN = (0.12, 0.82, 0.95)
C_EMERALD = (0.18, 0.86, 0.45)
C_AMBER = (1.00, 0.76, 0.15)
C_CORAL = (1.00, 0.35, 0.35)
C_WHITE = (1.00, 1.00, 1.00)
C_CARD_BG = (0.11, 0.13, 0.20)
C_CARD_BORDER = (0.20, 0.25, 0.38)
FLOOR_Y = 1420

def draw_background(ctx, t, theme="dark"):
    ctx.set_source_rgb(*C_BG_DARK)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()

    # Ambient grid
    ctx.save()
    ctx.set_source_rgba(0.18, 0.24, 0.36, 0.22)
    ctx.set_line_width(1.5)
    grid_size = 90
    offset_y = (t * 25) % grid_size
    for x in range(0, W + grid_size, grid_size):
        ctx.move_to(x, 0)
        ctx.line_to(x, H)
    for y in range(0, H + grid_size, grid_size):
        ctx.move_to(0, y + offset_y)
        ctx.line_to(W, y + offset_y)
    ctx.stroke()
    ctx.restore()

    # Floor ground
    ctx.save()
    ctx.set_source_rgba(0.14, 0.18, 0.26, 0.8)
    ctx.rectangle(0, FLOOR_Y, W, H - FLOOR_Y)
    ctx.fill()
    ctx.set_source_rgb(0.12, 0.82, 0.95)
    ctx.set_line_width(4)
    ctx.move_to(0, FLOOR_Y)
    ctx.line_to(W, FLOOR_Y)
    ctx.stroke()
    ctx.restore()

def draw_stickman(ctx, x, y, scale=1.0, pose="idle", t=0.0):
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)

    # Bobbing
    bob = math.sin(t * 8) * 4 if pose in ["panic", "dance"] else math.sin(t * 4) * 2

    # Head
    head_y = -140 + bob
    ctx.set_source_rgb(0.95, 0.85, 0.72)
    ctx.arc(0, head_y, 32, 0, 2 * math.pi)
    ctx.fill_preserve()
    ctx.set_source_rgb(0.08, 0.08, 0.12)
    ctx.set_line_width(5)
    ctx.stroke()

    # Eyes & Expression
    if pose == "panic":
        ctx.set_source_rgb(0.08, 0.08, 0.12)
        # Wide panic eyes
        ctx.arc(-11, head_y - 4, 7, 0, 2 * math.pi)
        ctx.fill()
        ctx.arc(11, head_y - 4, 7, 0, 2 * math.pi)
        ctx.fill()
        # Wavy scream mouth
        ctx.arc(0, head_y + 16, 12, 0, math.pi)
        ctx.stroke()
        # Sweat drops
        ctx.set_source_rgb(*C_CYAN)
        ctx.arc(36, head_y - 10, 6, 0, 2 * math.pi)
        ctx.fill()
    else:
        # Happy eyes
        ctx.set_source_rgb(0.08, 0.08, 0.12)
        ctx.arc(-10, head_y - 4, 5, 0, 2 * math.pi)
        ctx.fill()
        ctx.arc(10, head_y - 4, 5, 0, 2 * math.pi)
        ctx.fill()
        # Big smile
        ctx.arc(0, head_y + 10, 10, 0.1 * math.pi, 0.9 * math.pi)
        ctx.stroke()

    # Body spine
    ctx.set_line_width(6)
    ctx.set_source_rgb(0.08, 0.08, 0.12)
    ctx.move_to(0, head_y + 32)
    ctx.line_to(0, -30 + bob)
    ctx.stroke()

    # Arms
    if pose == "panic":
        ctx.move_to(0, head_y + 55)
        ctx.line_to(-45, head_y + 20 + math.sin(t * 15) * 15)
        ctx.line_to(-60, head_y - 20)
        ctx.stroke()

        ctx.move_to(0, head_y + 55)
        ctx.line_to(45, head_y + 20 - math.sin(t * 15) * 15)
        ctx.line_to(60, head_y - 20)
        ctx.stroke()
    elif pose == "point_right":
        ctx.move_to(0, head_y + 55)
        ctx.line_to(-35, head_y + 85)
        ctx.stroke()

        ctx.move_to(0, head_y + 55)
        ctx.line_to(65, head_y + 40)
        ctx.line_to(95, head_y + 35)
        ctx.stroke()
    elif pose == "victory":
        ctx.move_to(0, head_y + 55)
        ctx.line_to(-50, head_y - 15 + math.sin(t * 6) * 10)
        ctx.stroke()
        ctx.move_to(0, head_y + 55)
        ctx.line_to(50, head_y - 15 - math.sin(t * 6) * 10)
        ctx.stroke()
    else:
        ctx.move_to(0, head_y + 55)
        ctx.line_to(-35, head_y + 90)
        ctx.stroke()
        ctx.move_to(0, head_y + 55)
        ctx.line_to(35, head_y + 90)
        ctx.stroke()

    # Legs
    ctx.move_to(0, -30 + bob)
    ctx.line_to(-30, 0)
    ctx.stroke()
    ctx.move_to(0, -30 + bob)
    ctx.line_to(30, 0)
    ctx.stroke()

    ctx.restore()

def draw_crawl4ai_spider_bot(ctx, x, y, scale=1.0, t=0.0, stealth=False):
    """Draws Crawl4AI's signature high-tech cyber-spider bot."""
    ctx.save()
    ctx.translate(x, y)
    ctx.scale(scale, scale)

    hover = math.sin(t * 6) * 12
    ctx.translate(0, hover)

    color_primary = (0.2, 0.4, 0.5) if stealth else C_CYAN
    color_accent = (0.3, 0.7, 0.4) if stealth else C_EMERALD

    # Robotic Spider Legs (6 high-tech articulated limbs)
    ctx.set_line_width(6)
    ctx.set_source_rgb(*color_primary)
    for side in [-1, 1]:
        for i, angle_deg in enumerate([25, 60, 110]):
            leg_wave = math.sin(t * 8 + i * 1.2) * 10
            ctx.save()
            ctx.scale(side, 1)
            ctx.move_to(40, -10 + i * 15)
            knee_x = 90 + leg_wave
            knee_y = -40 + i * 35
            foot_x = 135
            foot_y = 60 + i * 20
            ctx.line_to(knee_x, knee_y)
            ctx.line_to(foot_x, foot_y)
            ctx.stroke()

            # Joint circles
            ctx.set_source_rgb(*color_accent)
            ctx.arc(knee_x, knee_y, 5, 0, 2 * math.pi)
            ctx.fill()
            ctx.arc(foot_x, foot_y, 4, 0, 2 * math.pi)
            ctx.fill()
            ctx.set_source_rgb(*color_primary)
            ctx.restore()

    # Bot Shell / Chassis
    ctx.set_source_rgb(0.08, 0.12, 0.18)
    ctx.arc(0, 0, 55, 0, 2 * math.pi)
    ctx.fill_preserve()
    ctx.set_source_rgb(*color_primary)
    ctx.set_line_width(5)
    ctx.stroke()

    # Cyber Eyes / Sensor Visor
    ctx.set_source_rgb(*color_accent)
    eye_glow = (math.sin(t * 10) + 1) * 0.5
    ctx.arc(-20, -10, 12, 0, 2 * math.pi)
    ctx.arc(20, -10, 12, 0, 2 * math.pi)
    ctx.arc(0, -22, 9, 0, 2 * math.pi)
    ctx.fill()

    # Turbo Jet / Thruster on top
    ctx.set_source_rgb(0.15, 0.20, 0.30)
    ctx.rectangle(-25, -55, 50, 18)
    ctx.fill_preserve()
    ctx.set_source_rgb(*color_primary)
    ctx.set_line_width(3)
    ctx.stroke()

    # Jet flame
    flame_h = 25 + math.sin(t * 20) * 15
    ctx.set_source_rgb(1.0, 0.6, 0.1)
    ctx.move_to(-18, -55)
    ctx.line_to(0, -55 - flame_h)
    ctx.line_to(18, -55)
    ctx.close_path()
    ctx.fill()

    # Chest Emblem: "C4AI"
    ctx.set_source_rgb(1.0, 1.0, 1.0)
    ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(20)
    ext = ctx.text_extents("C4AI")
    ctx.move_to(-ext.width / 2, 22)
    ctx.show_text("C4AI")

    ctx.restore()

def render_scene(ctx, t):
    # Mandatory persistent header pill (Act 1-5, t < 49s)
    if t < 49.0:
        draw_background(ctx, t)
        srt.draw_github_repo_header_pill(
            ctx,
            repo_slug=REPO_SLUG,
            stars_count=STARS_COUNT,
            t=t
        )

    # -------------------------------------------------------------
    # SCENE 0: [0.0 - 5.0s] The Hook - Stop getting blocked!
    # -------------------------------------------------------------
    if t < 5.0:
        # Giant red alert headline
        srt.draw_safe_text_centered(
            ctx,
            text="STOP GETTING BLOCKED!",
            center_x=W / 2,
            baseline_y=360,
            font_size=68,
            font_family="Impact",
            color_rgb=C_CORAL,
            stroke_rgb=(0, 0, 0),
            stroke_width=6
        )

        # 403 Forbidden Shield Banner
        box_w, box_h = 760, 240
        box_x, box_y = (W - box_w) / 2, 430
        ctx.save()
        srt._rounded_rect(ctx, box_x, box_y, box_w, box_h, 24)
        ctx.set_source_rgb(0.20, 0.05, 0.08)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_CORAL)
        ctx.set_line_width(5)
        ctx.stroke()

        pulse = (math.sin(t * 12) + 1) * 0.5
        ctx.set_source_rgba(1.0, 0.2, 0.2, 0.2 * pulse)
        srt._rounded_rect(ctx, box_x, box_y, box_w, box_h, 24)
        ctx.fill()

        srt.draw_safe_text_centered(
            ctx,
            text="🚫 403 FORBIDDEN",
            center_x=W / 2,
            baseline_y=520,
            font_size=60,
            font_family="Impact",
            color_rgb=C_CORAL
        )
        srt.draw_safe_text_centered(
            ctx,
            text="CLOUDFLARE BOT SHIELD ACTIVE",
            center_x=W / 2,
            baseline_y=590,
            font_size=32,
            font_family="DejaVu Sans",
            color_rgb=C_WHITE
        )
        ctx.restore()

        # Screaming panicked dev stickman
        draw_stickman(ctx, W / 2, FLOOR_Y - 80, scale=1.4, pose="panic", t=t)

        # Subtitle
        srt.draw_safe_kinetic_caption(ctx, "Stop letting websites block your AI agents!", t)

    # -------------------------------------------------------------
    # SCENE 1: [5.0 - 13.8s] The Problem - HTML Bloat & Burning Tokens
    # -------------------------------------------------------------
    elif t < 13.8:
        srt.draw_safe_text_centered(
            ctx,
            text="MESSY HTML = BURNING TOKENS!",
            center_x=W / 2,
            baseline_y=360,
            font_size=58,
            font_family="Impact",
            color_rgb=C_AMBER,
            stroke_rgb=(0, 0, 0),
            stroke_width=5
        )

        # Code Bloat Waterfall Card
        card_w, card_h = 840, 520
        card_x, card_y = (W - card_w) / 2, 420
        ctx.save()
        srt._rounded_rect(ctx, card_x, card_y, card_w, card_h, 20)
        ctx.set_source_rgb(0.08, 0.10, 0.15)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_CARD_BORDER)
        ctx.set_line_width(4)
        ctx.stroke()

        # Simulated raw HTML junk
        raw_lines = [
            '<div class="min-h-screen bg-slate-900 overflow-hidden flex flex-col">',
            '  <script type="text/javascript" src="/_next/static/chunks/main-8f3a.js"></script>',
            '  <style data-styled="active">.css-19xa28{display:none;visibility:hidden;}</style>',
            '  <noscript><iframe src="https://tracking.ad-server.com/pixel"></iframe></noscript>',
            '  <!-- 500,000 BYTES OF USELESS CSS, COOKIE BANNERS & TRACKING SCRIPTS -->',
            '  <div id="target-data">Actual data is 12 bytes here!</div>'
        ]
        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(21)
        for i, line in enumerate(raw_lines):
            line_y = card_y + 70 + i * 45
            ctx.set_source_rgb(0.8, 0.3, 0.3) if i in [1, 2, 3, 4] else ctx.set_source_rgb(0.4, 0.8, 0.4)
            ctx.move_to(card_x + 35, line_y)
            ctx.show_text(line[:52])

        # Token cost meter
        burn_amount = min(5000, int((t - 5.0) * 600) + 1200)
        ctx.set_source_rgb(1.0, 0.25, 0.25)
        ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(44)
        ext = ctx.text_extents(f"🔥 WASTED TOKENS: {burn_amount:,} / PAGE")
        ctx.move_to(W / 2 - ext.width / 2, card_y + 460)
        ctx.show_text(f"🔥 WASTED TOKENS: {burn_amount:,} / PAGE")
        ctx.restore()

        # Panicked Dev Stickman pointing at screen
        draw_stickman(ctx, 240, FLOOR_Y - 80, scale=1.2, pose="panic", t=t)

        # Kinetic Subtitle
        if t < 9.5:
            srt.draw_safe_kinetic_caption(ctx, "Raw HTML is burning your LLM tokens and breaking scrapers!", t)
        else:
            srt.draw_safe_kinetic_caption(ctx, "Traditional tools choke on JavaScript and dump bloated code!", t)

    # -------------------------------------------------------------
    # SCENE 2: [13.8 - 25.0s] The Solution - Meet Crawl4AI
    # -------------------------------------------------------------
    elif t < 25.0:
        # Title Card
        srt.draw_safe_text_centered(
            ctx,
            text="MEET CRAWL4AI",
            center_x=W / 2,
            baseline_y=360,
            font_size=72,
            font_family="Impact",
            color_rgb=C_CYAN,
            stroke_rgb=(0, 0, 0),
            stroke_width=6
        )

        srt.draw_safe_text_centered(
            ctx,
            text="THE OPEN-SOURCE AI WEB CRAWLER",
            center_x=W / 2,
            baseline_y=425,
            font_size=36,
            font_family="DejaVu Sans",
            color_rgb=C_EMERALD
        )

        # Glowing Superhero Card for Crawl4AI
        card_w, card_h = 860, 480
        card_x, card_y = (W - card_w) / 2, 460
        ctx.save()
        srt._rounded_rect(ctx, card_x, card_y, card_w, card_h, 24)
        ctx.set_source_rgb(0.08, 0.12, 0.20)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_CYAN)
        ctx.set_line_width(5)
        ctx.stroke()

        # Features Bullets inside card
        features = [
            ("⚡ Blazing Fast Asynchronous Engine", C_CYAN),
            ("🤖 Built Specially for LLMs & AI Agents", C_EMERALD),
            ("🌐 Full Dynamic JavaScript Rendering", C_WHITE),
            ("🛡️ Advanced Stealth Bot Protection Bypass", C_AMBER)
        ]
        for f_idx, (f_text, f_col) in enumerate(features):
            fy = card_y + 80 + f_idx * 75
            srt.draw_safe_text_centered(
                ctx,
                text=f_text,
                center_x=W / 2,
                baseline_y=fy,
                font_size=32,
                font_family="DejaVu Sans",
                color_rgb=f_col
            )
        ctx.restore()

        # Characters: Crawl4AI Spider Bot & Happy Dev Stickman
        draw_crawl4ai_spider_bot(ctx, 740, FLOOR_Y - 260, scale=1.3, t=t)
        draw_stickman(ctx, 280, FLOOR_Y - 80, scale=1.2, pose="point_right", t=t)

        # Kinetic Subtitle
        if t < 19.5:
            srt.draw_safe_kinetic_caption(ctx, "Meet Crawl4AI: the open-source web crawler built for AI agents!", t)
        else:
            srt.draw_safe_kinetic_caption(ctx, "Engineered specifically for LLMs with lightning-fast extraction!", t)

    # -------------------------------------------------------------
    # SCENE 3: [25.0 - 37.0s] Core Superpower - JS to Clean Markdown
    # -------------------------------------------------------------
    elif t < 37.0:
        srt.draw_safe_text_centered(
            ctx,
            text="DYNAMIC JS ➔ CLEAN MARKDOWN",
            center_x=W / 2,
            baseline_y=360,
            font_size=58,
            font_family="Impact",
            color_rgb=C_EMERALD,
            stroke_rgb=(0, 0, 0),
            stroke_width=5
        )

        # Split comparison card
        card_w, card_h = 880, 560
        card_x, card_y = (W - card_w) / 2, 420
        ctx.save()
        srt._rounded_rect(ctx, card_x, card_y, card_w, card_h, 24)
        ctx.set_source_rgb(0.08, 0.11, 0.17)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_EMERALD)
        ctx.set_line_width(4)
        ctx.stroke()

        # Left Column: Raw Heavy Web (Red tint)
        col_w = 400
        srt._rounded_rect(ctx, card_x + 25, card_y + 30, col_w, 400, 16)
        ctx.set_source_rgb(0.18, 0.08, 0.10)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_CORAL)
        ctx.set_line_width(2)
        ctx.stroke()

        ctx.set_source_rgb(*C_CORAL)
        ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(28)
        ctx.move_to(card_x + 45, card_y + 75)
        ctx.show_text("❌ MESSY WEB DOM (2.4 MB)")

        dirty_lines = ["<script>eval()</script>", "<div class='ad-wrap'>", "<svg viewBox='...'>", "<style>css-junk{}</style>", "<!-- Tracking pixel -->"]
        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        ctx.set_font_size(18)
        ctx.set_source_rgb(0.7, 0.4, 0.4)
        for d_i, d_line in enumerate(dirty_lines):
            ctx.move_to(card_x + 45, card_y + 130 + d_i * 45)
            ctx.show_text(d_line)

        # Right Column: Pristine Clean Markdown (Green tint)
        srt._rounded_rect(ctx, card_x + 455, card_y + 30, col_w, 400, 16)
        ctx.set_source_rgb(0.06, 0.18, 0.12)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_EMERALD)
        ctx.set_line_width(2)
        ctx.stroke()

        ctx.set_source_rgb(*C_EMERALD)
        ctx.select_font_face("Impact", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(28)
        ctx.move_to(card_x + 475, card_y + 75)
        ctx.show_text("✅ CRAWL4AI OUTPUT (1.2 KB)")

        clean_lines = ["# Product Highlights", "- 94% Token Reduction", "- Instant Vector RAG", "- Extracted JSON Tables", "- Zero Noise / Pure Data"]
        ctx.select_font_face("DejaVu Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(19)
        ctx.set_source_rgb(0.9, 1.0, 0.9)
        for c_i, c_line in enumerate(clean_lines):
            ctx.move_to(card_x + 475, card_y + 130 + c_i * 45)
            ctx.show_text(c_line)

        # Bottom stat bar
        srt.draw_safe_text_centered(
            ctx,
            text="⚡ REDUCES LLM CONTEXT SIZE BY UP TO 95%",
            center_x=W / 2,
            baseline_y=card_y + 500,
            font_size=32,
            font_family="Impact",
            color_rgb=C_AMBER
        )
        ctx.restore()

        # Crawl4AI Spider scanning with laser
        draw_crawl4ai_spider_bot(ctx, W / 2, FLOOR_Y - 240, scale=1.2, t=t)

        # Kinetic Subtitle
        if t < 31.0:
            srt.draw_safe_kinetic_caption(ctx, "Renders dynamic pages and executes browser actions seamlessly!", t)
        else:
            srt.draw_safe_kinetic_caption(ctx, "Converts any web page into pure, clean markdown in milliseconds!", t)

    # -------------------------------------------------------------
    # SCENE 4: [37.0 - 48.0s] Stealth Mode, Local Speed & 87K Stars
    # -------------------------------------------------------------
    elif t < 48.0:
        srt.draw_safe_text_centered(
            ctx,
            text="100% LOCAL & STEALTH SPEED",
            center_x=W / 2,
            baseline_y=360,
            font_size=62,
            font_family="Impact",
            color_rgb=C_CYAN,
            stroke_rgb=(0, 0, 0),
            stroke_width=5
        )

        # Terminal Telemetry Card
        card_w, card_h = 860, 520
        card_x, card_y = (W - card_w) / 2, 420
        ctx.save()
        srt._rounded_rect(ctx, card_x, card_y, card_w, card_h, 24)
        ctx.set_source_rgb(0.06, 0.08, 0.12)
        ctx.fill_preserve()
        ctx.set_source_rgb(*C_CYAN)
        ctx.set_line_width(4)
        ctx.stroke()

        terminal_rows = [
            ("user@flowork:~$ crawl4ai --stealth --url https://target.ai", C_WHITE),
            ("[✓] Stealth Fingerprint Spoofing: ACTIVE", C_EMERALD),
            ("[✓] Cloudflare / PerimeterX: BYPASSED", C_EMERALD),
            ("[✓] Playwright Chromium headless: 140ms", C_CYAN),
            ("[✓] Chunking & Markdown extraction: 4.2ms", C_CYAN),
            ("[★] 87,600+ GitHub Stars & 100% Free Open Source", C_AMBER)
        ]
        ctx.select_font_face("Monospace", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        ctx.set_font_size(23)
        for r_i, (r_text, r_color) in enumerate(terminal_rows):
            ctx.set_source_rgb(*r_color)
            ctx.move_to(card_x + 40, card_y + 70 + r_i * 65)
            ctx.show_text(r_text)
        ctx.restore()

        # Crawl4AI Spider in stealth ninja mode
        draw_crawl4ai_spider_bot(ctx, 760, FLOOR_Y - 260, scale=1.3, t=t, stealth=True)
        draw_stickman(ctx, 240, FLOOR_Y - 80, scale=1.2, pose="victory", t=t)

        # Kinetic Subtitle
        if t < 43.0:
            srt.draw_safe_kinetic_caption(ctx, "Runs entirely local with stealth bot protection bypass!", t)
        else:
            srt.draw_safe_kinetic_caption(ctx, "Over 87,000 developers rely on Crawl4AI right now!", t)

    # -------------------------------------------------------------
    # SCENE 5: [48.0 - 57.0s] The Grand Outro & Star CTA
    # -------------------------------------------------------------
    else:
        # Dedicated Full Outro Dual-CTA Card (Law 3 + Flowork branding)
        draw_background(ctx, t, theme="victory")

        srt.draw_github_cta_card(
            ctx,
            repo_owner=REPO_OWNER,
            repo_name=REPO_NAME,
            stars_count=STARS_COUNT,
            t=t
        )

        # Characters celebrating
        draw_stickman(ctx, 220, FLOOR_Y - 80, scale=1.1, pose="victory", t=t)
        draw_crawl4ai_spider_bot(ctx, 840, FLOOR_Y - 220, scale=1.1, t=t)

        # Final kinetic CTA subtitle
        srt.draw_safe_kinetic_caption(ctx, "Star unclecode/crawl4ai on GitHub & visit floworkos.com!", t)


def render_all():
    print(f"🎬 Starting render of Crawl4AI short ({TOTAL_FRAMES} frames, {DURATION_SEC}s)...")
    temp_mp4 = "/tmp/crawl4ai_raw_video.mp4"

    cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-vcodec", "rawvideo",
        "-s", f"{W}x{H}",
        "-pix_fmt", "bgra",
        "-r", str(FPS),
        "-i", "-",
        "-i", AUDIO_WAV,
        "-c:v", "h264_nvenc",
        "-preset", "p4",
        "-b:v", "2200k",
        "-maxrate", "3500k",
        "-bufsize", "5000k",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        temp_mp4
    ]

    try:
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    except Exception:
        # Fallback to libx264 if NVENC is unavailable
        cmd[cmd.index("h264_nvenc")] = "libx264"
        cmd[cmd.index("-preset") + 1] = "fast"
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)

    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)

    for frame_idx in range(TOTAL_FRAMES):
        t = frame_idx / FPS
        render_scene(ctx, t)
        surface.flush()
        data = surface.get_data()
        proc.stdin.write(data)

        if frame_idx % 150 == 0:
            print(f"⏳ Frame {frame_idx}/{TOTAL_FRAMES} ({t:.1f}s / {DURATION_SEC:.1f}s)...")

    proc.stdin.close()
    ret = proc.wait()
    if ret != 0:
        err = proc.stderr.read().decode('utf-8', errors='ignore')
        print(f"❌ Error during rendering: {ret}\n{err}")
        sys.exit(ret)

    # Move to final deliverable path
    shutil.move(temp_mp4, OUTPUT_MP4)
    file_size = os.path.getsize(OUTPUT_MP4)
    print(f"✅ Render complete! Deliverable saved to: {OUTPUT_MP4} ({file_size:,} bytes)")


if __name__ == "__main__":
    render_all()
