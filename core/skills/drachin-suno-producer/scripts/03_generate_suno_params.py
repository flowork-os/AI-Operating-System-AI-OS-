#!/usr/bin/env python3
"""
03_generate_suno_params.py
Generate ready-to-paste Suno v6 Cover parameters (Styles, Exclude, Weirdness,
Style Influence, Title) for the 3 @JanganNontonDrachin OST re-genres.
"""
import argparse
import json

GENRES = {
    1: {
        "name": "Mandopop Balada Galau (Modern Heartbreak OST)",
        "ideal_bpm": "68-82 BPM",
        "default_bpm": 74,
        "styles": (
            "Cinematic Mandopop Ballad, Chinese Drama OST, Emotional Piano, Lush Orchestral Strings, "
            "Solo Cello, Subtle Guzheng Arpeggios, Breathy Intimate Vocals, Heartbreak Melancholy, "
            "Dynamic Chorus Swell, Studio Mastered, 4/4 Time"
        ),
        "exclude": "EDM, Trap, Heavy Metal, Rap, Hip-Hop, Auto-Tune, Lo-Fi Distortion, Upbeat Dance, Reggae",
        "weirdness": 35,
        "style_influence": 75,
    },
    2: {
        "name": "Sweet Pop & Akustik Ringan (Modern Rom-Com OST)",
        "ideal_bpm": "88-105 BPM",
        "default_bpm": 96,
        "styles": (
            "Sweet Mandopop Acoustic, Modern Chinese Rom-Com OST, Warm Fingerpicked Acoustic Guitar, "
            "Soft Rhodes Piano, Light Brush Percussion, Airy Sweet Vocals, Romantic Nostalgia, "
            "Clean Pop Production, Uplifting Chorus, 4/4 Time"
        ),
        "exclude": "Heavy Metal, Screamo, Dark Trap, Dubstep, Aggressive Rap, Industrial, Harsh Distortion",
        "weirdness": 30,
        "style_influence": 70,
    },
    3: {
        "name": "Gufeng Epik Wuxia & Xianxia (Colossal Fantasy OST)",
        "ideal_bpm": "72-92 BPM",
        "default_bpm": 78,
        "styles": (
            "Epic Guofeng Xianxia OST, Wuxia Chinese Drama Soundtrack, Soaring Dizi Flute, "
            "Dramatic Guzheng, Expressive Erhu Solo, Cinematic Taiko War Drums, Sweeping Orchestral Brass, "
            "Emotional Vibrato Vocals, Ethereal Choir Backing, Colossal Fantasy Atmosphere"
        ),
        "exclude": "Modern EDM, Trap Beats, Hip-Hop, Funk, Jazz Saxophone, Punk Rock, Auto-Tune, Synthwave",
        "weirdness": 40,
        "style_influence": 80,
    },
}


def main():
    parser = argparse.ArgumentParser(description="Generate Suno v6 Drachin OST parameters.")
    parser.add_argument("--genre", type=int, choices=[1, 2, 3], required=True, help="1=Balada Galau, 2=Sweet Pop, 3=Gufeng Epik")
    parser.add_argument("--title", required=True, help="Song title (e.g. 'Kangen (Xiang Nian)')")
    parser.add_argument("--bpm", type=int, help="Target BPM (optional, uses genre default)")
    parser.add_argument("--gender", choices=["male", "female"], default="male", help="Lead vocal gender")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    g = GENRES[args.genre]
    bpm = args.bpm or g["default_bpm"]
    vocal_tag = "Expressive Male Mandarin Vocal" if args.gender == "male" else "Expressive Female Mandarin Vocal"
    styles = f"{g['styles']}, {vocal_tag}, {bpm} BPM"

    out = {
        "genre": g["name"],
        "ideal_bpm_range": g["ideal_bpm"],
        "target_bpm": bpm,
        "title": args.title,
        "styles": styles,
        "exclude": g["exclude"],
        "weirdness_pct": g["weirdness"],
        "style_influence_pct": g["style_influence"],
    }

    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(f"=== SUNO V6 PARAMETERS: {out['genre']} ===")
        print(f"Title           : {out['title']}")
        print(f"Target BPM      : {out['target_bpm']} BPM (Ideal: {out['ideal_bpm_range']})")
        print(f"Weirdness       : {out['weirdness_pct']}%")
        print(f"Style Influence : {out['style_influence_pct']}%")
        print(f"\n[Styles]\n{out['styles']}")
        print(f"\n[Exclude]\n{out['exclude']}")


if __name__ == "__main__":
    main()
