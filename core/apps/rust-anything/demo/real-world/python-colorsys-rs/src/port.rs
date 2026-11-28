//! The Rust port of Python's `colorsys` (CPython 3.13, `Lib/colorsys.py`).
//! Translated from CPython (PSF License Version 2).
//!
//! `colorsys` has no type hints and Python callers pass ints as often as floats; ints stay ints
//! through `+`, `-` and `*` and come back out (`hsv_to_rgb(0, 0, 7)` is `(7, 7, 7)`). So the port
//! computes with `Num`, Python's int-or-float.

#![forbid(unsafe_code)]

use crate::pynum::Num;

const ONE_THIRD: f64 = 1.0 / 3.0;
const ONE_SIXTH: f64 = 1.0 / 6.0;
const TWO_THIRD: f64 = 2.0 / 3.0;

fn n(x: f64) -> Num {
    Num::Float(x)
}

/// Port of `rgb_to_yiq` (`colorsys.py:40`).
pub fn rgb_to_yiq(r: Num, g: Num, b: Num) -> Result<(Num, Num, Num), String> {
    let y = n(0.30) * r + n(0.59) * g + n(0.11) * b;
    let i = n(0.74) * (r - y) - n(0.27) * (b - y);
    let q = n(0.48) * (r - y) + n(0.41) * (b - y);
    Ok((y, i, q))
}

/// Port of `yiq_to_rgb` (`colorsys.py:46`): clamps like the source, so NaN passes through.
pub fn yiq_to_rgb(y: Num, i: Num, q: Num) -> Result<(Num, Num, Num), String> {
    let clamp = |v: Num| {
        let v = if v < n(0.0) { n(0.0) } else { v };
        if v > n(1.0) { n(1.0) } else { v }
    };
    let r = y + n(0.946_882_217_090_069_3) * i + n(0.623_556_581_986_143_3) * q;
    let g = y - n(0.274_787_646_298_978_34) * i - n(0.635_691_079_187_380_1) * q;
    let b = y - n(1.108_545_034_642_032_2) * i + n(1.709_006_928_406_466_6) * q;
    Ok((clamp(r), clamp(g), clamp(b)))
}

/// The hue shared by `rgb_to_hls` and `rgb_to_hsv`.
fn hue(r: Num, g: Num, b: Num, maxc: Num, rangec: Num) -> Result<Num, String> {
    let rc = (maxc - r).true_div(rangec)?;
    let gc = (maxc - g).true_div(rangec)?;
    let bc = (maxc - b).true_div(rangec)?;
    let h = if r == maxc {
        bc - gc
    } else if g == maxc {
        n(2.0) + rc - bc
    } else {
        n(4.0) + gc - rc
    };
    h.true_div(n(6.0))?.modulo(n(1.0))
}

/// Port of `rgb_to_hls` (`colorsys.py:76`).
pub fn rgb_to_hls(r: Num, g: Num, b: Num) -> Result<(Num, Num, Num), String> {
    let maxc = Num::max(&[r, g, b]);
    let minc = Num::min(&[r, g, b]);
    let sumc = maxc + minc;
    let rangec = maxc - minc;
    let l = sumc.true_div(n(2.0))?;
    if minc == maxc {
        return Ok((n(0.0), l, n(0.0)));
    }
    let s = if l <= n(0.5) {
        rangec.true_div(sumc)?
    } else {
        rangec.true_div(n(2.0) - maxc - minc)?
    };
    Ok((hue(r, g, b, maxc, rangec)?, l, s))
}

/// Port of `hls_to_rgb` (`colorsys.py:99`).
pub fn hls_to_rgb(h: Num, l: Num, s: Num) -> Result<(Num, Num, Num), String> {
    if s == n(0.0) {
        return Ok((l, l, l));
    }
    let m2 = if l <= n(0.5) {
        l * (n(1.0) + s)
    } else {
        l + s - (l * s)
    };
    let m1 = n(2.0) * l - m2;
    Ok((
        v(m1, m2, h + n(ONE_THIRD))?,
        v(m1, m2, h)?,
        v(m1, m2, h - n(ONE_THIRD))?,
    ))
}

fn v(m1: Num, m2: Num, hue: Num) -> Result<Num, String> {
    let hue = hue.modulo(n(1.0))?;
    Ok(if hue < n(ONE_SIXTH) {
        m1 + (m2 - m1) * hue * n(6.0)
    } else if hue < n(0.5) {
        m2
    } else if hue < n(TWO_THIRD) {
        m1 + (m2 - m1) * (n(TWO_THIRD) - hue) * n(6.0)
    } else {
        m1
    })
}

/// Port of `rgb_to_hsv` (`colorsys.py:126`).
pub fn rgb_to_hsv(r: Num, g: Num, b: Num) -> Result<(Num, Num, Num), String> {
    let maxc = Num::max(&[r, g, b]);
    let minc = Num::min(&[r, g, b]);
    let rangec = maxc - minc;
    if minc == maxc {
        return Ok((n(0.0), n(0.0), maxc));
    }
    let s = rangec.true_div(maxc)?;
    Ok((hue(r, g, b, maxc, rangec)?, s, maxc))
}

/// Port of `hsv_to_rgb` (`colorsys.py:145`).
pub fn hsv_to_rgb(h: Num, s: Num, v: Num) -> Result<(Num, Num, Num), String> {
    if s == n(0.0) {
        return Ok((v, v, v));
    }
    let scaled = (h * n(6.0)).f();
    if scaled.is_nan() {
        return Err("ValueError: cannot convert float NaN to integer".into());
    }
    if scaled.is_infinite() {
        return Err("OverflowError: cannot convert float infinity to integer".into());
    }
    let i = scaled.trunc();
    let f = n(scaled - i);
    let p = v * (n(1.0) - s);
    let q = v * (n(1.0) - s * f);
    let t = v * (n(1.0) - s * (n(1.0) - f));
    // Python's `i % 6` on an int is never negative.
    Ok(match (i % 6.0 + 6.0) % 6.0 {
        0.0 => (v, t, p),
        1.0 => (q, v, p),
        2.0 => (p, v, t),
        3.0 => (p, q, v),
        4.0 => (t, p, v),
        _ => (v, p, q),
    })
}
