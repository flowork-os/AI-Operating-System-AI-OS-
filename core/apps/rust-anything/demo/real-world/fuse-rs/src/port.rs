//! The Rust port of `src/rust/relevance.ts`: Fuse.js's Bitap search and string-list scoring.
//! Fuse.js is Copyright Kiro Risk, Apache License 2.0 (https://github.com/krisk/Fuse).
//!
//! Text is compared in UTF-16 code units, as JS does, and every bit operation keeps JS's
//! 32-bit integer semantics, so scores match Fuse's to the last bit.

#![forbid(unsafe_code)]

use std::collections::HashMap;

use rayon::prelude::*;
use serde_json::Value;
use unicode_normalization::UnicodeNormalization;

use crate::js::math_round;

const MAX_BITS: usize = 32;

/// The options `relevance` takes, with Fuse's defaults.
#[derive(Clone, Debug)]
struct Options {
    is_case_sensitive: bool,
    ignore_diacritics: bool,
    ignore_location: bool,
    find_all_matches: bool,
    ignore_field_norm: bool,
    threshold: f64,
    location: f64,
    distance: f64,
    min_match_char_length: f64,
    field_norm_weight: f64,
}

impl Default for Options {
    fn default() -> Self {
        Self {
            is_case_sensitive: false,
            ignore_diacritics: false,
            ignore_location: false,
            find_all_matches: false,
            ignore_field_norm: false,
            threshold: 0.6,
            location: 0.0,
            distance: 100.0,
            min_match_char_length: 1.0,
            field_norm_weight: 1.0,
        }
    }
}

fn marker(v: &Value) -> Option<(&str, &Value)> {
    match v {
        Value::Object(m) if m.len() == 1 => {
            let (k, x) = m.iter().next()?;
            k.starts_with('$').then_some((k.as_str(), x))
        }
        _ => None,
    }
}

/// A JS number as the bridge carries it: plain, or a `{"$num": ...}` marker.
fn number(v: &Value) -> Option<f64> {
    if let Some(n) = v.as_f64() {
        return Some(n);
    }
    match marker(v)? {
        ("$num", Value::String(s)) => match s.as_str() {
            "NaN" => Some(f64::NAN),
            "Infinity" => Some(f64::INFINITY),
            "-Infinity" => Some(f64::NEG_INFINITY),
            "-0" => Some(-0.0),
            _ => None,
        },
        _ => None,
    }
}

fn is_undefined(v: &Value) -> bool {
    matches!(marker(v), Some(("$undefined", _)))
}

fn type_error(message: impl std::fmt::Display) -> String {
    format!("TypeError: {message}")
}

/// `checkOptions` and the defaults of `BitapSearch` and `relevance`.
fn parse_options(options: &Value) -> Result<Options, String> {
    let not_object = || type_error("options must be an object");
    let entries = match options {
        Value::Object(m) => match marker(options) {
            Some(("$undefined" | "$num" | "$bigint" | "$utf16", _)) => return Err(not_object()),
            Some(("$bytes" | "$buffer", Value::Array(bytes))) if !bytes.is_empty() => {
                return Err(type_error("unsupported option 0"));
            }
            Some(("$date" | "$map" | "$set" | "$bytes" | "$buffer", _)) => {
                return Ok(Options::default());
            }
            _ => m,
        },
        _ => return Err(not_object()),
    };
    let mut o = Options::default();
    for (key, value) in entries {
        if is_undefined(value) {
            continue;
        }
        let flag = match key.as_str() {
            "isCaseSensitive" => Some(&mut o.is_case_sensitive),
            "ignoreDiacritics" => Some(&mut o.ignore_diacritics),
            "ignoreLocation" => Some(&mut o.ignore_location),
            "findAllMatches" => Some(&mut o.find_all_matches),
            "ignoreFieldNorm" => Some(&mut o.ignore_field_norm),
            _ => None,
        };
        if let Some(flag) = flag {
            *flag = value
                .as_bool()
                .ok_or_else(|| type_error(format!("{key} must be a boolean")))?;
            continue;
        }
        let slot = match key.as_str() {
            "threshold" => &mut o.threshold,
            "location" => &mut o.location,
            "distance" => &mut o.distance,
            "minMatchCharLength" => &mut o.min_match_char_length,
            "fieldNormWeight" => &mut o.field_norm_weight,
            _ => return Err(type_error(format!("unsupported option {key}"))),
        };
        let n = number(value)
            .filter(|n| n.is_finite())
            .ok_or_else(|| type_error(format!("{key} must be a finite number")))?;
        if key == "location" && n.fract() != 0.0 {
            return Err(type_error("location must be an integer"));
        }
        *slot = n;
    }
    Ok(o)
}

/// `String.prototype.trim` is empty: JS whitespace and line terminators only.
fn is_blank(text: &str) -> bool {
    text.chars().all(|c| {
        matches!(
            c,
            '\u{9}'..='\u{D}'
                | ' '
                | '\u{A0}'
                | '\u{1680}'
                | '\u{2000}'..='\u{200A}'
                | '\u{2028}'
                | '\u{2029}'
                | '\u{202F}'
                | '\u{205F}'
                | '\u{3000}'
                | '\u{FEFF}'
        )
    })
}

/// Fuse's field-length norm: `round(1000 / tokens^(0.5 * weight)) / 1000`.
fn field_norm(tokens: usize, weight: f64) -> f64 {
    math_round(1000.0 / (tokens as f64).powf(0.5 * weight)) / 1000.0
}

/// Words separated by ASCII whitespace or NBSP, at least 1.
fn token_count(units: &[u16]) -> usize {
    let mut tokens = 0;
    let mut in_word = false;
    for &c in units {
        if (9..=13).contains(&c) || c == 32 || c == 160 {
            in_word = false;
        } else if !in_word {
            tokens += 1;
            in_word = true;
        }
    }
    tokens.max(1)
}

fn combining(c: char) -> bool {
    const RANGES: &[(u32, u32)] = &[
        (0x300, 0x36F),
        (0x483, 0x489),
        (0x591, 0x5BD),
        (0x5BF, 0x5BF),
        (0x5C1, 0x5C2),
        (0x5C4, 0x5C5),
        (0x5C7, 0x5C7),
        (0x610, 0x61A),
        (0x64B, 0x65F),
        (0x670, 0x670),
        (0x6D6, 0x6DC),
        (0x6DF, 0x6E4),
        (0x6E7, 0x6E8),
        (0x6EA, 0x6ED),
        (0x711, 0x711),
        (0x730, 0x74A),
        (0x7A6, 0x7B0),
        (0x7EB, 0x7F3),
        (0x7FD, 0x7FD),
        (0x816, 0x819),
        (0x81B, 0x823),
        (0x825, 0x827),
        (0x829, 0x82D),
        (0x859, 0x85B),
        (0x8D3, 0x8E1),
        (0x8E3, 0x903),
        (0x93A, 0x93C),
        (0x93E, 0x94F),
        (0x951, 0x957),
        (0x962, 0x963),
        (0x981, 0x983),
        (0x9BC, 0x9BC),
        (0x9BE, 0x9C4),
        (0x9C7, 0x9C8),
        (0x9CB, 0x9CD),
        (0x9D7, 0x9D7),
        (0x9E2, 0x9E3),
        (0x9FE, 0x9FE),
        (0xA01, 0xA03),
        (0xA3C, 0xA3C),
        (0xA3E, 0xA42),
        (0xA47, 0xA48),
        (0xA4B, 0xA4D),
        (0xA51, 0xA51),
        (0xA70, 0xA71),
        (0xA75, 0xA75),
        (0xA81, 0xA83),
        (0xABC, 0xABC),
        (0xABE, 0xAC5),
        (0xAC7, 0xAC9),
        (0xACB, 0xACD),
        (0xAE2, 0xAE3),
        (0xAFA, 0xAFF),
        (0xB01, 0xB03),
        (0xB3C, 0xB3C),
        (0xB3E, 0xB44),
        (0xB47, 0xB48),
        (0xB4B, 0xB4D),
        (0xB56, 0xB57),
        (0xB62, 0xB63),
        (0xB82, 0xB82),
        (0xBBE, 0xBC2),
        (0xBC6, 0xBC8),
        (0xBCA, 0xBCD),
        (0xBD7, 0xBD7),
        (0xC00, 0xC04),
        (0xC3E, 0xC44),
        (0xC46, 0xC48),
        (0xC4A, 0xC4D),
        (0xC55, 0xC56),
        (0xC62, 0xC63),
        (0xC81, 0xC83),
        (0xCBC, 0xCBC),
        (0xCBE, 0xCC4),
        (0xCC6, 0xCC8),
        (0xCCA, 0xCCD),
        (0xCD5, 0xCD6),
        (0xCE2, 0xCE3),
        (0xD00, 0xD03),
        (0xD3B, 0xD3C),
        (0xD3E, 0xD44),
        (0xD46, 0xD48),
        (0xD4A, 0xD4D),
        (0xD57, 0xD57),
        (0xD62, 0xD63),
        (0xD82, 0xD83),
        (0xDCA, 0xDCA),
        (0xDCF, 0xDD4),
        (0xDD6, 0xDD6),
        (0xDD8, 0xDDF),
        (0xDF2, 0xDF3),
        (0xE31, 0xE31),
        (0xE34, 0xE3A),
        (0xE47, 0xE4E),
        (0xEB1, 0xEB1),
        (0xEB4, 0xEB9),
        (0xEBB, 0xEBC),
        (0xEC8, 0xECD),
        (0xF18, 0xF19),
        (0xF35, 0xF35),
        (0xF37, 0xF37),
        (0xF39, 0xF39),
        (0xF3E, 0xF3F),
        (0xF71, 0xF84),
        (0xF86, 0xF87),
        (0xF8D, 0xF97),
        (0xF99, 0xFBC),
        (0xFC6, 0xFC6),
        (0x102B, 0x103E),
        (0x1056, 0x1059),
        (0x105E, 0x1060),
        (0x1062, 0x1064),
        (0x1067, 0x106D),
        (0x1071, 0x1074),
        (0x1082, 0x108D),
        (0x108F, 0x108F),
        (0x109A, 0x109D),
        (0x135D, 0x135F),
        (0x1712, 0x1714),
        (0x1732, 0x1734),
        (0x1752, 0x1753),
        (0x1772, 0x1773),
        (0x17B4, 0x17D3),
        (0x17DD, 0x17DD),
        (0x180B, 0x180D),
        (0x1885, 0x1886),
        (0x18A9, 0x18A9),
        (0x1920, 0x192B),
        (0x1930, 0x193B),
        (0x1A17, 0x1A1B),
        (0x1A55, 0x1A5E),
        (0x1A60, 0x1A7C),
        (0x1A7F, 0x1A7F),
        (0x1AB0, 0x1ABE),
        (0x1B00, 0x1B04),
        (0x1B34, 0x1B44),
        (0x1B6B, 0x1B73),
        (0x1B80, 0x1B82),
        (0x1BA1, 0x1BAD),
        (0x1BE6, 0x1BF3),
        (0x1C24, 0x1C37),
        (0x1CD0, 0x1CD2),
        (0x1CD4, 0x1CE8),
        (0x1CED, 0x1CED),
        (0x1CF2, 0x1CF4),
        (0x1CF7, 0x1CF9),
        (0x1DC0, 0x1DF9),
        (0x1DFB, 0x1DFF),
        (0x20D0, 0x20F0),
        (0x2CEF, 0x2CF1),
        (0x2D7F, 0x2D7F),
        (0x2DE0, 0x2DFF),
        (0x302A, 0x302F),
        (0x3099, 0x309A),
        (0xA66F, 0xA672),
        (0xA674, 0xA67D),
        (0xA69E, 0xA69F),
        (0xA6F0, 0xA6F1),
        (0xA802, 0xA802),
        (0xA806, 0xA806),
        (0xA80B, 0xA80B),
        (0xA823, 0xA827),
        (0xA880, 0xA881),
        (0xA8B4, 0xA8C5),
        (0xA8E0, 0xA8F1),
        (0xA8FF, 0xA8FF),
        (0xA926, 0xA92D),
        (0xA947, 0xA953),
        (0xA980, 0xA983),
        (0xA9B3, 0xA9C0),
        (0xA9E5, 0xA9E5),
        (0xAA29, 0xAA36),
        (0xAA43, 0xAA43),
        (0xAA4C, 0xAA4D),
        (0xAA7B, 0xAA7D),
        (0xAAB0, 0xAAB0),
        (0xAAB2, 0xAAB4),
        (0xAAB7, 0xAAB8),
        (0xAABE, 0xAABF),
        (0xAAC1, 0xAAC1),
        (0xAAEB, 0xAAEF),
        (0xAAF5, 0xAAF6),
        (0xABE3, 0xABEA),
        (0xABEC, 0xABED),
        (0xFB1E, 0xFB1E),
        (0xFE00, 0xFE0F),
        (0xFE20, 0xFE2F),
    ];
    let c = c as u32;
    RANGES.iter().any(|&(a, b)| (a..=b).contains(&c))
}

/// Fuse's `stripDiacritics`: NFD, combining marks dropped, a few letters spelled out.
fn strip_diacritics(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    for c in s.nfd().filter(|c| !combining(*c)) {
        match c {
            '\u{142}' => out.push('l'),
            '\u{141}' => out.push('L'),
            '\u{111}' => out.push('d'),
            '\u{110}' => out.push('D'),
            '\u{F8}' => out.push('o'),
            '\u{D8}' => out.push('O'),
            '\u{127}' => out.push('h'),
            '\u{126}' => out.push('H'),
            '\u{167}' => out.push('t'),
            '\u{166}' => out.push('T'),
            '\u{131}' => out.push('i'),
            '\u{DF}' => out.push_str("ss"),
            c => out.push(c),
        }
    }
    out
}

/// What `BitapSearch` does to a string before comparing it.
fn prepare(s: &str, o: &Options) -> Vec<u16> {
    let lowered;
    let s = if o.is_case_sensitive {
        s
    } else {
        lowered = s.to_lowercase();
        &lowered
    };
    if o.ignore_diacritics {
        strip_diacritics(s).encode_utf16().collect()
    } else {
        s.encode_utf16().collect()
    }
}

struct Chunk {
    pattern: Vec<u16>,
    alphabet: HashMap<u16, i32>,
    ascii: [i32; 128],
    start_index: usize,
}

impl Chunk {
    fn new(pattern: &[u16], start_index: usize) -> Self {
        let len = pattern.len();
        let mut alphabet: HashMap<u16, i32> = HashMap::new();
        for (i, &c) in pattern.iter().enumerate() {
            *alphabet.entry(c).or_insert(0) |= 1i32.wrapping_shl((len - i - 1) as u32);
        }
        let mut ascii = [0i32; 128];
        for (&c, &m) in &alphabet {
            if c < 128 {
                ascii[c as usize] = m;
            }
        }
        Self {
            pattern: pattern.to_vec(),
            alphabet,
            ascii,
            start_index,
        }
    }

    fn char_match(&self, c: u16) -> i32 {
        if c < 128 {
            self.ascii[c as usize]
        } else {
            self.alphabet.get(&c).copied().unwrap_or(0)
        }
    }
}

/// `BitapSearch`: a prepared pattern, searched in many texts.
struct Searcher {
    options: Options,
    pattern: Vec<u16>,
    chunks: Vec<Chunk>,
}

impl Searcher {
    fn new(pattern: &str, options: &Options) -> Self {
        let pattern = prepare(pattern, options);
        let mut chunks = Vec::new();
        let len = pattern.len();
        if len > MAX_BITS {
            let remainder = len % MAX_BITS;
            let end = len - remainder;
            let mut i = 0;
            while i < end {
                chunks.push(Chunk::new(&pattern[i..i + MAX_BITS], i));
                i += MAX_BITS;
            }
            if remainder > 0 {
                let start = len - MAX_BITS;
                chunks.push(Chunk::new(&pattern[start..], start));
            }
        } else if len > 0 {
            chunks.push(Chunk::new(&pattern, 0));
        }
        Self {
            options: options.clone(),
            pattern,
            chunks,
        }
    }

    /// `searchIn` on a text already prepared: whether it matches, and its score.
    fn search_in(&self, text: &[u16]) -> (bool, f64) {
        if self.pattern == text {
            if (text.len() as f64) < self.options.min_match_char_length {
                return (false, 1.0);
            }
            return (true, 0.0);
        }
        let mut total = 0.0;
        let mut any = false;
        for chunk in &self.chunks {
            let (matched, score) = bitap(text, chunk, &self.options);
            any |= matched;
            total += score;
        }
        if any {
            (true, total / self.chunks.len() as f64)
        } else {
            (false, 1.0)
        }
    }
}

fn index_of(text: &[u16], pattern: &[u16], from: usize) -> Option<usize> {
    if from > text.len() || pattern.len() > text.len() - from {
        return None;
    }
    text[from..]
        .windows(pattern.len())
        .position(|w| w == pattern)
        .map(|p| p + from)
}

/// Fuse's `search` (Bitap with a location and distance penalty) for one chunk.
fn bitap(text: &[u16], chunk: &Chunk, o: &Options) -> (bool, f64) {
    let pattern = &chunk.pattern;
    let pattern_len = pattern.len() as i64;
    let text_len = text.len() as i64;
    let location = o.location + chunk.start_index as f64;
    let expected = location.min(text_len as f64).max(0.0) as i64;
    let mut threshold = o.threshold;
    let calc = |errors: i64, current: i64| -> f64 {
        let accuracy = errors as f64 / pattern_len as f64;
        if o.ignore_location {
            return accuracy;
        }
        let proximity = (expected - current).abs() as f64;
        if o.distance == 0.0 {
            return if proximity != 0.0 { 1.0 } else { accuracy };
        }
        accuracy + proximity / o.distance
    };
    let compute_matches = o.min_match_char_length > 1.0;
    let mut match_mask = if compute_matches {
        vec![false; text.len()]
    } else {
        Vec::new()
    };

    let mut best_location = expected;
    while let Some(index) = usize::try_from(best_location)
        .ok()
        .and_then(|from| index_of(text, pattern, from))
    {
        let index = index as i64;
        threshold = threshold.min(calc(0, index));
        best_location = index + pattern_len;
        if compute_matches {
            for k in 0..pattern_len {
                match_mask[(index + k) as usize] = true;
            }
        }
    }

    BUFFERS
        .with_borrow_mut(|(bits, last)| {
            last.clear();
            search_errors(text, chunk, o, &calc, expected, threshold, bits, last)
        })
        .finish(text, chunk, o, compute_matches, &mut match_mask)
}

thread_local! {
    static BUFFERS: std::cell::RefCell<(Vec<i32>, Vec<i32>)> =
        const { std::cell::RefCell::new((Vec::new(), Vec::new())) };
}

/// Where the best match is, after the exact-match scan.
struct Found {
    best_location: i64,
    best_errors: i64,
    final_score: f64,
}

impl Found {
    fn finish(
        self,
        text: &[u16],
        chunk: &Chunk,
        o: &Options,
        compute_matches: bool,
        match_mask: &mut [bool],
    ) -> (bool, f64) {
        let Self {
            best_location,
            best_errors,
            final_score,
        } = self;
        let pattern_len = chunk.pattern.len() as i64;
        let text_len = text.len() as i64;
        if compute_matches && best_location >= 0 {
            let end = (text_len - 1).min(best_location + pattern_len - 1 + best_errors);
            let mut k = best_location;
            while k <= end {
                if chunk.char_match(text[k as usize]) != 0 {
                    match_mask[k as usize] = true;
                }
                k += 1;
            }
        }
        let mut is_match = best_location >= 0;
        let score = final_score.max(0.001);
        if compute_matches && !has_indices(match_mask, o.min_match_char_length) {
            is_match = false;
        }
        (is_match, score)
    }
}

/// The Bitap scan, one error level at a time, in two reused bit arrays.
#[allow(clippy::too_many_arguments)]
fn search_errors(
    text: &[u16],
    chunk: &Chunk,
    o: &Options,
    calc: &impl Fn(i64, i64) -> f64,
    expected: i64,
    mut threshold: f64,
    bits: &mut Vec<i32>,
    last: &mut Vec<i32>,
) -> Found {
    let pattern_len = chunk.pattern.len() as i64;
    let text_len = text.len() as i64;
    let mut best_location = -1;
    let mut final_score = 1.0;
    let mut best_errors = 0;
    let mut bin_max = pattern_len + text_len;
    let mask = 1i32.wrapping_shl((pattern_len - 1) as u32);

    for i in 0..pattern_len {
        let mut bin_min = 0;
        let mut bin_mid = bin_max;
        while bin_min < bin_mid {
            if calc(i, expected + bin_mid) <= threshold {
                bin_min = bin_mid;
            } else {
                bin_max = bin_mid;
            }
            bin_mid = bin_min + (bin_max - bin_min).div_euclid(2);
        }
        bin_max = bin_mid;

        let mut start = (expected - bin_mid + 1).max(1);
        let finish = if o.find_all_matches {
            text_len
        } else {
            (expected + bin_mid).min(text_len) + pattern_len
        };
        bits.clear();
        bits.resize((finish + 2) as usize, 0);
        bits[(finish + 1) as usize] = ((1i32.wrapping_shl(i as u32) as i64) - 1) as i32;
        let last_at = |k: i64| last.get(k as usize).copied().unwrap_or(0);

        let mut j = finish;
        while j >= start {
            let current = j - 1;
            let char_match = if current < text_len {
                chunk.char_match(text[current as usize])
            } else {
                0
            };
            let ju = j as usize;
            let mut b = (bits[ju + 1].wrapping_shl(1) | 1) & char_match;
            if i > 0 {
                b |= ((last_at(j + 1) | last_at(j)).wrapping_shl(1)) | 1 | last_at(j + 1);
            }
            bits[ju] = b;
            if b & mask != 0 {
                final_score = calc(i, current);
                if final_score <= threshold {
                    threshold = final_score;
                    best_location = current;
                    best_errors = i;
                    if best_location <= expected {
                        break;
                    }
                    start = (2 * expected - best_location).max(1);
                }
            }
            j -= 1;
        }

        if calc(i + 1, expected) > threshold {
            break;
        }
        std::mem::swap(bits, last);
    }
    Found {
        best_location,
        best_errors,
        final_score,
    }
}

/// Whether `convertMaskToIndices` finds a run of at least `min` matched units.
fn has_indices(mask: &[bool], min: f64) -> bool {
    let mut start: i64 = -1;
    for (i, &m) in mask.iter().enumerate() {
        let i = i as i64;
        if m && start == -1 {
            start = i;
        } else if !m && start != -1 {
            if (i - start) as f64 >= min {
                return true;
            }
            start = -1;
        }
    }
    let len = mask.len() as i64;
    len > 0 && mask[mask.len() - 1] && (len - start) as f64 >= min
}

/// One string of a list, prepared for searching.
struct Item {
    blank: bool,
    tokens: usize,
    text: String,
    lowered: Vec<u16>,
}

impl Item {
    fn new(text: String) -> Self {
        let units: Vec<u16> = text.encode_utf16().collect();
        Self {
            blank: is_blank(&text),
            tokens: token_count(&units),
            lowered: text.to_lowercase().encode_utf16().collect(),
            text,
        }
    }

    fn relevance(&self, searcher: &Searcher) -> f64 {
        if self.blank {
            return f64::NEG_INFINITY;
        }
        let o = &searcher.options;
        let prepared;
        let text = if !o.is_case_sensitive && !o.ignore_diacritics {
            &self.lowered
        } else {
            prepared = prepare(&self.text, o);
            &prepared
        };
        let (matched, score) = searcher.search_in(text);
        if !matched {
            return f64::NEG_INFINITY;
        }
        let exponent = if o.ignore_field_norm {
            1.0
        } else {
            field_norm(self.tokens, o.field_norm_weight)
        };
        -score.powf(exponent)
    }
}

/// Port of `relevance` (`src/rust/relevance.ts:23`).
pub fn relevance(text: String, pattern: String, options: Value) -> Result<f64, String> {
    let options = parse_options(&options)?;
    let searcher = Searcher::new(&pattern, &options);
    Ok(Item::new(text).relevance(&searcher))
}

type LastRun = (String, Value, Vec<f64>);

/// The strings of a `RelevanceBatch`, prepared once: lowercased, counted and checked for blanks.
/// The last results are kept, so `rank` then `run` for the same search scores the list once.
pub struct RelevanceIndex {
    items: Vec<Item>,
    last: std::sync::Mutex<Option<LastRun>>,
}

impl RelevanceIndex {
    pub fn new(items: Vec<String>) -> Self {
        Self {
            items: items.into_par_iter().map(Item::new).collect(),
            last: std::sync::Mutex::new(None),
        }
    }

    pub fn run(&self, pattern: String, options: Value) -> Result<Vec<f64>, String> {
        if self.items.is_empty() {
            return Ok(Vec::new());
        }
        if let Ok(last) = self.last.lock()
            && let Some((p, o, scores)) = last.as_ref()
            && *p == pattern
            && *o == options
        {
            return Ok(scores.clone());
        }
        let parsed = parse_options(&options)?;
        let searcher = Searcher::new(&pattern, &parsed);
        let scores: Vec<f64> = self
            .items
            .par_iter()
            .map(|item| item.relevance(&searcher))
            .collect();
        if let Ok(mut last) = self.last.lock() {
            *last = Some((pattern, options, scores.clone()));
        }
        Ok(scores)
    }
}
