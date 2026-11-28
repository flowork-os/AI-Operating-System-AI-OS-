//! The Rust port of the glibc behavior behind `src/facade.c` ("C" locale).

#![forbid(unsafe_code)]

use std::ffi::{c_int, c_long};

/// C's `isspace` in the "C" locale.
fn space(b: u8) -> bool {
    matches!(b, b' ' | b'\t' | b'\n' | b'\x0b' | b'\x0c' | b'\r')
}

fn digit_value(b: u8) -> Option<u32> {
    (b as char).to_digit(36)
}

/// `strtol(text, NULL, base)`: leading space, a sign, `0x` for base 16 or 0, a leading `0`
/// meaning octal for base 0; clamps to `LONG_MIN`/`LONG_MAX`; 0 for a bad base.
pub fn parse_long(text: Option<&[u8]>, base: c_int) -> c_long {
    let Some(s) = text else { return 0 };
    if base != 0 && !(2..=36).contains(&base) {
        return 0;
    }
    let mut i = 0;
    while i < s.len() && space(s[i]) {
        i += 1;
    }
    let negative = match s.get(i) {
        Some(b'-') => {
            i += 1;
            true
        }
        Some(b'+') => {
            i += 1;
            false
        }
        _ => false,
    };
    let mut base = base as u32;
    let hex_prefix = s.get(i) == Some(&b'0')
        && matches!(s.get(i + 1), Some(b'x' | b'X'))
        && s.get(i + 2)
            .and_then(|&b| digit_value(b))
            .is_some_and(|d| d < 16);
    if (base == 0 || base == 16) && hex_prefix {
        i += 2;
        base = 16;
    } else if base == 0 {
        base = if s.get(i) == Some(&b'0') { 8 } else { 10 };
    }
    let mut value: i128 = 0;
    let mut overflow = false;
    while let Some(d) = s.get(i).and_then(|&b| digit_value(b)).filter(|&d| d < base) {
        value = value * i128::from(base) + i128::from(d);
        if value > i128::from(c_long::MAX) + 1 {
            overflow = true;
            value = i128::from(c_long::MAX) + 1;
        }
        i += 1;
    }
    let signed = if negative { -value } else { value };
    if overflow || signed > i128::from(c_long::MAX) || signed < i128::from(c_long::MIN) {
        return if negative { c_long::MIN } else { c_long::MAX };
    }
    signed as c_long
}

/// `atoi`: glibc's `(int) strtol(text, NULL, 10)`, truncating.
pub fn parse_int(text: Option<&[u8]>) -> c_int {
    parse_long(text, 10) as c_int
}

/// `strtod(text, NULL)`: the longest prefix that is a decimal or hex float, `inf[inity]` or
/// `nan[(...)]`, correctly rounded.
pub fn parse_double(text: Option<&[u8]>) -> f64 {
    let Some(s) = text else { return 0.0 };
    let mut i = 0;
    while i < s.len() && space(s[i]) {
        i += 1;
    }
    let sign = match s.get(i) {
        Some(b'-') => {
            i += 1;
            -1.0
        }
        Some(b'+') => {
            i += 1;
            1.0
        }
        _ => 1.0,
    };
    let rest = &s[i..];
    let lower: Vec<u8> = rest.iter().take(8).map(u8::to_ascii_lowercase).collect();
    if lower.starts_with(b"inf") {
        return sign * f64::INFINITY;
    }
    if lower.starts_with(b"nan") {
        return f64::NAN.copysign(sign);
    }
    if lower.starts_with(b"0x") {
        if let Some(v) = hex_float(&rest[2..]) {
            return sign * v;
        }
        return sign * 0.0;
    }
    // Decimal: digits, optional fraction, optional exponent with at least one digit.
    let mut j = 0;
    let mut digits = 0;
    while j < rest.len() && rest[j].is_ascii_digit() {
        j += 1;
        digits += 1;
    }
    if rest.get(j) == Some(&b'.') {
        j += 1;
        while j < rest.len() && rest[j].is_ascii_digit() {
            j += 1;
            digits += 1;
        }
    }
    if digits == 0 {
        // Nothing converted: strtod returns +0.0 whatever sign came before.
        return 0.0;
    }
    if matches!(rest.get(j), Some(b'e' | b'E')) {
        let mut k = j + 1;
        if matches!(rest.get(k), Some(b'+' | b'-')) {
            k += 1;
        }
        if rest.get(k).is_some_and(u8::is_ascii_digit) {
            while k < rest.len() && rest[k].is_ascii_digit() {
                k += 1;
            }
            j = k;
        }
    }
    let text = std::str::from_utf8(&rest[..j]).unwrap_or("0");
    let text = text.strip_suffix('.').unwrap_or(text);
    let text = text
        .strip_prefix('.')
        .map_or_else(|| text.to_string(), |t| format!("0.{t}"));
    sign * text.parse::<f64>().unwrap_or(0.0)
}

/// The value of hex float digits after `0x`: `h.hhhp±d`. `None` without a hex digit.
fn hex_float(s: &[u8]) -> Option<f64> {
    let mut mantissa: u128 = 0;
    let mut exp: i64 = 0;
    let mut any = false;
    let mut i = 0;
    let mut frac = false;
    while i < s.len() {
        match s[i] {
            b'.' if !frac => frac = true,
            b => match (b as char).to_digit(16) {
                Some(d) => {
                    any = true;
                    if mantissa >> 120 == 0 {
                        mantissa = mantissa * 16 + u128::from(d);
                        if frac {
                            exp -= 4;
                        }
                    } else if !frac {
                        exp += 4;
                    }
                }
                None => break,
            },
        }
        i += 1;
    }
    if !any {
        return None;
    }
    if matches!(s.get(i), Some(b'p' | b'P')) {
        let mut k = i + 1;
        let negative = s.get(k) == Some(&b'-');
        if matches!(s.get(k), Some(b'+' | b'-')) {
            k += 1;
        }
        if s.get(k).is_some_and(u8::is_ascii_digit) {
            let mut e: i64 = 0;
            while let Some(d) = s.get(k).filter(|b| b.is_ascii_digit()) {
                e = (e * 10 + i64::from(d - b'0')).min(100_000);
                k += 1;
            }
            exp += if negative { -e } else { e };
        }
    }
    Some(mantissa as f64 * 2f64.powi(exp.clamp(-2000, 2000) as i32))
}

/// `strspn`: the length of the prefix made of bytes in `accept`.
pub fn span(text: Option<&[u8]>, accept: Option<&[u8]>) -> usize {
    let (Some(s), Some(accept)) = (text, accept) else {
        return 0;
    };
    s.iter().take_while(|b| accept.contains(b)).count()
}

/// The sign of `strcmp`: bytes compare as unsigned char.
pub fn compare(a: Option<&[u8]>, b: Option<&[u8]>) -> c_int {
    match a.unwrap_or_default().cmp(b.unwrap_or_default()) {
        std::cmp::Ordering::Less => -1,
        std::cmp::Ordering::Equal => 0,
        std::cmp::Ordering::Greater => 1,
    }
}

/// glibc's tables cover -128..=255; a negative `char` reads like its unsigned byte.
fn byte(c: c_int) -> Option<u8> {
    match c {
        0..=255 => Some(c as u8),
        -128..=-2 => Some((c + 256) as u8),
        _ => None,
    }
}

/// `isalpha` in the "C" locale. Outside -128..=255 C's behavior is undefined.
pub fn is_alpha(c: c_int) -> c_int {
    c_int::from(byte(c).is_some_and(|b| b.is_ascii_alphabetic()))
}

/// `isspace` in the "C" locale.
pub fn is_space(c: c_int) -> c_int {
    c_int::from(byte(c).is_some_and(space))
}

/// `ispunct` in the "C" locale.
pub fn is_punct(c: c_int) -> c_int {
    c_int::from(byte(c).is_some_and(|b| b.is_ascii_punctuation()))
}

/// `toupper` in the "C" locale: glibc maps a negative `char` to its unsigned byte.
pub fn to_upper(c: c_int) -> c_int {
    match byte(c) {
        Some(b) if c != -1 => c_int::from(b.to_ascii_uppercase()),
        _ => c,
    }
}
