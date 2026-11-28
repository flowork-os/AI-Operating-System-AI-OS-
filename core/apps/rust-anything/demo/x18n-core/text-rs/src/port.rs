//! The Rust port of `packages/core/src/text.ts`.
//!
//! `createLineIndex` stays in TS: it returns an object of closures. Offsets are UTF-16 code
//! units throughout, as in JS. Invalid input returns an error where JS throws a TypeError.

#![forbid(unsafe_code)]

use serde_json::{Map, Value, json};

use crate::js;
use crate::utf16;

/// Port of `diffText` (`packages/core/src/text.ts:4`): one edit covering only the part that differs.
pub fn diff_text(before: String, after: String) -> Vec<Value> {
    if before == after {
        return Vec::new();
    }
    let b = utf16::units(&before);
    let a = utf16::units(&after);
    let max = b.len().min(a.len());
    let mut start = 0;
    while start < max && b[start] == a[start] {
        start += 1;
    }
    let (mut end_before, mut end_after) = (b.len(), a.len());
    while end_before > start && end_after > start && b[end_before - 1] == a[end_after - 1] {
        end_before -= 1;
        end_after -= 1;
    }
    // The cut can fall inside a surrogate pair ("😀" vs "😁"): keep the units exact.
    vec![json!({
        "range": { "start": start, "end": end_before },
        "text": js::utf16_string(&a[start..end_after]),
    })]
}

/// Port of `applyTextEdits` (`packages/core/src/text.ts:26`): non-overlapping edits against the same text.
pub fn apply_text_edits(text: String, edits: Vec<Value>) -> Result<Value, String> {
    let mut parsed = Vec::with_capacity(edits.len());
    for edit in &edits {
        // `edit.range.start` throws for a null edit or a missing or null range.
        let range = match edit {
            Value::Object(o) => o
                .get("range")
                .filter(|r| !r.is_null() && !js::is_undefined(r)),
            _ => None,
        }
        .ok_or("TypeError: Cannot read properties of undefined (reading 'start')")?;
        let field = |name: &str| match range {
            Value::Object(r) => r.get(name).and_then(to_number),
            _ => None,
        };
        // `'' + edit.text`, kept as UTF-16 units: the text can be half a surrogate pair.
        let text: Vec<u16> = match edit.get("text") {
            None => "undefined".encode_utf16().collect(),
            Some(t) if js::is_undefined(t) => "undefined".encode_utf16().collect(),
            Some(t) => {
                js::string_units(t).unwrap_or_else(|| to_js_string(t).encode_utf16().collect())
            }
        };
        parsed.push((field("start"), field("end"), text));
    }
    // `b.range.start - a.range.start || b.range.end - a.range.end`; NaN compares as equal.
    // `b.range.start - a.range.start || b.range.end - a.range.end`: NaN and 0 fall through to
    // the second difference; a NaN result makes the order V8's, so sort as V8 does.
    js::sort(&mut parsed, |a, b| {
        let first = sub(b.0, a.0);
        if first != 0.0 && !first.is_nan() {
            first
        } else {
            sub(b.1, a.1)
        }
    });
    let mut out = utf16::units(&text);
    for (start, end, insert) in parsed {
        let len = out.len();
        let head = slice_end(start, len);
        let tail = slice_start(end, len);
        let mut next = out[..head].to_vec();
        next.extend_from_slice(&insert);
        next.extend_from_slice(&out[tail.min(len)..]);
        out = next;
    }
    Ok(js::utf16_string(&out))
}

/// Port of `rangeContains` (`packages/core/src/text.ts:95`).
pub fn range_contains(range: Value, offset: f64) -> Result<bool, String> {
    if range.is_null() || js::is_undefined(&range) {
        return Err("TypeError: Cannot read properties of null (reading 'start')".into());
    }
    let field = |name: &str| match &range {
        Value::Object(r) => r.get(name).and_then(to_number).unwrap_or(f64::NAN),
        _ => f64::NAN,
    };
    Ok(offset >= field("start") && offset <= field("end"))
}

/// Port of `hashText` (`packages/core/src/text.ts:100`): cyrb53 over UTF-16 code units, as hex.
pub fn hash_text(text: String) -> String {
    let mut h1: u32 = 0xDEAD_BEEF;
    let mut h2: u32 = 0x41C6_CE57;
    for ch in text.encode_utf16() {
        h1 = (h1 ^ u32::from(ch)).wrapping_mul(2_654_435_761);
        h2 = (h2 ^ u32::from(ch)).wrapping_mul(1_597_334_677);
    }
    h1 = (h1 ^ (h1 >> 16)).wrapping_mul(2_246_822_507)
        ^ (h2 ^ (h2 >> 13)).wrapping_mul(3_266_489_909);
    h2 = (h2 ^ (h2 >> 16)).wrapping_mul(2_246_822_507)
        ^ (h1 ^ (h1 >> 13)).wrapping_mul(3_266_489_909);
    let value = (u64::from(h2 & 2_097_151) << 32) + u64::from(h1);
    format!("{value:x}")
}

/// JS `ToNumber` for JSON values; `None` stands for `undefined`.
fn to_number(value: &Value) -> Option<f64> {
    if js::is_undefined(value) {
        return None;
    }
    // NaN, Infinity and -0 arrive as `{"$num": ...}` markers.
    if let Some(n) = js::as_number(value) {
        return Some(n);
    }
    Some(match value {
        Value::Null => 0.0,
        Value::Bool(b) => f64::from(u8::from(*b)),
        Value::Number(n) => n.as_f64().unwrap_or(f64::NAN),
        Value::String(s) => {
            let t = s.trim();
            if t.is_empty() {
                0.0
            } else {
                t.parse().unwrap_or(f64::NAN)
            }
        }
        Value::Array(items) => match items.as_slice() {
            [] => 0.0,
            [one] => to_number(&Value::String(to_js_string(one))).unwrap_or(f64::NAN),
            _ => f64::NAN,
        },
        Value::Object(_) => f64::NAN,
    })
}

fn sub(a: Option<f64>, b: Option<f64>) -> f64 {
    a.unwrap_or(f64::NAN) - b.unwrap_or(f64::NAN)
}

/// Index from a `slice` end argument: `undefined` means the length.
fn slice_end(n: Option<f64>, len: usize) -> usize {
    n.map_or(len, |n| relative_index(n, len))
}

/// Index from a `slice` start argument: `undefined` means 0.
fn slice_start(n: Option<f64>, len: usize) -> usize {
    n.map_or(0, |n| relative_index(n, len))
}

/// JS `slice` index rules: truncate, NaN is 0, negative counts from the end, clamp.
fn relative_index(n: f64, len: usize) -> usize {
    let n = if n.is_nan() { 0.0 } else { n.trunc() };
    let len_f = len as f64;
    if n < 0.0 {
        (len_f + n).max(0.0) as usize
    } else {
        n.min(len_f) as usize
    }
}

/// JS string conversion, as `'' + value` does.
fn to_js_string(value: &Value) -> String {
    match value {
        Value::Null => "null".into(),
        Value::Bool(b) => b.to_string(),
        Value::Number(n) => number_to_string(n.as_f64().unwrap_or(f64::NAN)),
        Value::String(s) => s.clone(),
        Value::Array(items) => items
            .iter()
            .map(|v| {
                if v.is_null() || js::is_undefined(v) {
                    String::new()
                } else {
                    to_js_string(v)
                }
            })
            .collect::<Vec<_>>()
            .join(","),
        Value::Object(o) => js::string_units(&Value::Object(Map::clone(o))).map_or_else(
            || "[object Object]".into(),
            |u| String::from_utf16_lossy(&u),
        ),
    }
}

/// JS `Number.prototype.toString()` for the values this module sees.
fn number_to_string(n: f64) -> String {
    if n.is_nan() {
        "NaN".into()
    } else if n.is_infinite() {
        if n > 0.0 {
            "Infinity".into()
        } else {
            "-Infinity".into()
        }
    } else if n == n.trunc() && n.abs() < 1e21 {
        format!("{n:.0}").replace("-0", "0")
    } else {
        n.to_string()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn diff_and_apply_round_trip() {
        let edits = diff_text("hello world".into(), "hello there".into());
        assert_eq!(edits[0]["range"], json!({ "start": 6, "end": 11 }));
        assert_eq!(
            apply_text_edits("hello world".into(), edits),
            Ok(json!("hello there"))
        );
        // Emoji that share their high surrogate: the edit holds a lone low surrogate.
        let split = diff_text("😀".into(), "😁".into());
        assert_eq!(split[0]["text"], json!({ "$utf16": [0xDE01] }));
        assert_eq!(apply_text_edits("😀".into(), split), Ok(json!("😁")));
    }

    #[test]
    fn hashes_like_cyrb53() {
        // Values computed with the TS implementation.
        assert_eq!(hash_text(String::new()), "bdcb81aee8d83");
        assert_eq!(hash_text("a😀".into()), "1a27973010b422");
        assert!(range_contains(json!({ "start": 1, "end": 3 }), 3.0).unwrap());
        assert!(range_contains(Value::Null, 1.0).is_err());
    }
}
