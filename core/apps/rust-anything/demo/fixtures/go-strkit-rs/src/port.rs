//! The Rust port of `strkit/`.

#![forbid(unsafe_code)]

use serde_json::{Map, Value, json};

/// Go's `unicode.ToLower`: one rune to one rune (`İ` to `i`, no final sigma).
fn go_lower(c: char) -> char {
    c.to_lowercase().next().unwrap_or(c)
}

fn go_lower_str(s: &str) -> String {
    s.chars().map(go_lower).collect()
}

/// Port of `Slugify` (`strkit/strkit.go:18`).
pub fn slugify(s: String, max: i64) -> Result<String, String> {
    let mut out = String::with_capacity(s.len());
    let mut dash = false;
    // Go lowers each rune on its own; ASCII needs no table lookups.
    for c in s.chars() {
        let (c, alnum) = if c.is_ascii() {
            let c = c.to_ascii_lowercase();
            (c, c.is_ascii_alphanumeric())
        } else {
            let c = go_lower(c);
            (c, c.is_alphanumeric())
        };
        if alnum {
            out.push(c);
            dash = false;
        } else if !dash && !out.is_empty() {
            out.push('-');
            dash = true;
        }
    }
    let mut out = out.strip_suffix('-').map(str::to_string).unwrap_or(out);
    if max > 0 && out.len() as i64 > max {
        // Go cuts bytes; a cut rune's bytes each read as U+FFFD once encoded.
        let bytes = &out.as_bytes()[..max as usize];
        let valid = match std::str::from_utf8(bytes) {
            Ok(v) => v.len(),
            Err(e) => e.valid_up_to(),
        };
        let mut cut = String::from_utf8_lossy(&bytes[..valid]).into_owned();
        cut.extend(std::iter::repeat_n('\u{FFFD}', bytes.len() - valid));
        out = cut;
        if out.ends_with('-') {
            out.pop();
        }
    }
    Ok(out)
}

/// Port of `WordFreq` (`strkit/strkit.go:38`).
pub fn word_freq(text: String) -> Result<Value, String> {
    let mut counts = Map::new();
    for w in text.split_whitespace() {
        let entry = counts.entry(go_lower_str(w)).or_insert(json!(0));
        *entry = json!(entry.as_i64().unwrap_or(0) + 1);
    }
    Ok(Value::Object(counts))
}

/// Port of `ParsePort` (`strkit/strkit.go:47`).
pub fn parse_port(s: String) -> Result<i64, String> {
    let n: i64 = s.trim().parse().map_err(|_| "not a number".to_string())?;
    if !(1..=65535).contains(&n) {
        return Err("out of range".into());
    }
    Ok(n)
}

/// Port of `Mean` (`strkit/strkit.go:59`).
pub fn mean(xs: Vec<f64>) -> Result<f64, String> {
    if xs.is_empty() {
        return Ok(0.0);
    }
    Ok(xs.iter().sum::<f64>() / xs.len() as f64)
}

/// Port of `Midpoint` (`strkit/strkit.go:71`).
pub fn midpoint(a: Value, b: Value) -> Result<Value, String> {
    let get = |p: &Value, k: &str| p[k].as_f64().unwrap_or(0.0);
    Ok(
        json!({ "x": (get(&a, "x") + get(&b, "x")) / 2.0, "y": (get(&a, "y") + get(&b, "y")) / 2.0 }),
    )
}

/// Port of `Initials` (`strkit/strkit.go:76`).
pub fn initials(name: String) -> Result<String, String> {
    Ok(name
        .split_whitespace()
        .filter_map(|w| w.chars().next())
        .flat_map(char::to_uppercase)
        .collect())
}

/// Port of `SplitPair` (`strkit/strkit.go:85`).
pub fn split_pair(s: String, sep: String) -> Result<Value, String> {
    Ok(match s.split_once(sep.as_str()) {
        Some((a, b)) => json!([a, b, true]),
        None => json!([s, "", false]),
    })
}
