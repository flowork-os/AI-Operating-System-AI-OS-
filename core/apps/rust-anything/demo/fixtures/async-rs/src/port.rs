//! The Rust port of `src/pipeline.ts`.

#![forbid(unsafe_code)]

use serde_json::{Value, json};

use crate::js;

/// JS `WhiteSpace` and `LineTerminator`: what `trim()` and `\s` match. Rust's
/// `char::is_whitespace` differs: it includes U+0085 and excludes U+FEFF.
fn is_js_space(u: u16) -> bool {
    matches!(u, 0x09..=0x0D | 0x20 | 0xA0 | 0x1680 | 0x2000..=0x200A | 0x2028 | 0x2029 | 0x202F | 0x205F | 0x3000 | 0xFEFF)
}

fn trim(units: &[u16]) -> &[u16] {
    let start = units
        .iter()
        .position(|&u| !is_js_space(u))
        .unwrap_or(units.len());
    let end = units
        .iter()
        .rposition(|&u| !is_js_space(u))
        .map_or(start, |i| i + 1);
    &units[start..end]
}

/// `value.trim()`: only strings have it.
fn trimmed(value: Option<&Value>, name: &str) -> Result<Vec<u16>, String> {
    let units = value
        .and_then(js::string_units)
        .ok_or_else(|| format!("TypeError: {name}.trim is not a function"))?;
    Ok(trim(&units).to_vec())
}

/// Port of `normalize` (`src/pipeline.ts:7`).
pub async fn normalize(entries: Vec<Value>, prefix: Option<String>) -> Result<Vec<Value>, String> {
    // `filter` reads `entry.value` of every entry first: null and undefined entries throw.
    for entry in &entries {
        if entry.is_null() || js::is_undefined(entry) {
            return Err("TypeError: Cannot read properties of null (reading 'value')".into());
        }
    }
    let kept = entries.iter().filter(|e| match e {
        Value::Object(o) => !o.get("value").is_some_and(Value::is_null),
        _ => true,
    });
    let prefix: Vec<u16> = prefix.unwrap_or_default().encode_utf16().collect();
    let mut out = Vec::new();
    for entry in kept {
        let key = trimmed(
            entry.get("key").filter(|v| !js::is_undefined(v)),
            "entry.key",
        )?;
        let value = trimmed(
            entry.get("value").filter(|v| !js::is_undefined(v)),
            "entry.value",
        )?;
        let key = [prefix.as_slice(), key.as_slice()].concat();
        out.push(json!({ "key": js::utf16_string(&key), "value": js::utf16_string(&value) }));
    }
    Ok(out)
}

/// Port of `countWords` (`src/pipeline.ts:15`): `text.split(/\s+/).filter(Boolean).length`.
pub async fn count_words(text: String) -> Result<f64, String> {
    let units: Vec<u16> = text.encode_utf16().collect();
    let words = units
        .split(|&u| is_js_space(u))
        .filter(|w| !w.is_empty())
        .count();
    Ok(words as f64)
}

/// Port of `upper` (`src/pipeline.ts:20`).
pub fn upper(text: String) -> Result<String, String> {
    Ok(text.to_uppercase())
}
