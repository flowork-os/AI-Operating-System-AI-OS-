//! The Rust port of `src/main/java/com/example/text/`.

#![forbid(unsafe_code)]

use serde_json::{Map, Value, json};

/// Port of `gcd` (`Nums.java:7`). `Math.abs(Long.MIN_VALUE)` stays negative, as in Java.
pub fn gcd(a: i64, b: i64) -> Result<i64, String> {
    let (mut a, mut b) = (a.wrapping_abs(), b.wrapping_abs());
    while b != 0 {
        let t = a.wrapping_rem(b);
        a = b;
        b = t;
    }
    Ok(a)
}

/// Port of `mean` (`Nums.java:18`).
pub fn mean(values: Vec<f64>) -> Result<f64, String> {
    if values.is_empty() {
        return Ok(f64::NAN);
    }
    let mut sum = 0.0;
    for v in &values {
        sum += v;
    }
    Ok(sum / values.len() as f64)
}

/// Port of `pages` (`Nums.java:29`): 32-bit arithmetic that wraps, division by zero throws.
pub fn pages(total: i64, per_page: i64) -> Result<i64, String> {
    let (total, per_page) = (total as i32, per_page as i32);
    if per_page == 0 {
        return Err("ArithmeticException: / by zero".into());
    }
    Ok(i64::from(
        total
            .wrapping_add(per_page)
            .wrapping_sub(1)
            .wrapping_div(per_page),
    ))
}

/// Port of `slugify` (`Strings.java:14`).
pub fn slugify(text: String, max: i64) -> Result<String, String> {
    let mut out = String::with_capacity(text.len());
    let mut dash = false;
    let mut push = |c: char| {
        let alnum = if c.is_ascii() {
            c.is_ascii_alphanumeric()
        } else {
            c.is_alphanumeric()
        };
        if alnum {
            out.push(c);
            dash = false;
        } else if !dash && !out.is_empty() {
            out.push('-');
            dash = true;
        }
    };
    // `toLowerCase` lowers each character on its own, except a final sigma. That rule looks past
    // neighbours only through cased and case-ignorable characters, which whitespace is not: a
    // piece up to whitespace that holds a `Σ` is lowered whole, the rest per character.
    for piece in text.split_inclusive(char::is_whitespace) {
        if piece.contains('Σ') {
            piece.to_lowercase().chars().for_each(&mut push);
            continue;
        }
        for c in piece.chars() {
            if c.is_ascii() {
                push(c.to_ascii_lowercase());
            } else {
                c.to_lowercase().for_each(&mut push);
            }
        }
    }
    if out.ends_with('-') {
        out.pop();
    }
    // Bytes are at least characters: a short slug needs no count.
    if max > 0 && out.len() as i64 > max && out.chars().count() as i64 > max {
        out = out.chars().take(max as usize).collect();
    }
    Ok(out)
}

/// Java's `\\s`: ASCII whitespace only, unlike `char::is_whitespace`.
fn java_space(c: char) -> bool {
    matches!(c, ' ' | '\t' | '\n' | '\x0b' | '\x0c' | '\r')
}

/// Port of `words` (`Strings.java:37`): `text.trim().split("\\s+")`, empty pieces dropped.
pub fn words(text: String) -> Result<Vec<String>, String> {
    Ok(text
        .trim_matches(|c: char| c <= ' ')
        .split(java_space)
        .filter(|w| !w.is_empty())
        .map(str::to_string)
        .collect())
}

/// Port of `frequencies` (`Strings.java:48`).
pub fn frequencies(text: String) -> Result<Value, String> {
    let mut counts = Map::new();
    for w in words(text)? {
        let key = w.to_lowercase();
        let n = counts.get(&key).and_then(Value::as_i64).unwrap_or(0);
        counts.insert(key, json!(n + 1));
    }
    Ok(Value::Object(counts))
}

/// Port of `parsePort` (`Strings.java:57`).
pub fn parse_port(text: String) -> Result<i64, String> {
    let trimmed = text.trim_matches(|c: char| c <= ' ');
    let port: i32 = trimmed
        .parse()
        .map_err(|_| format!("NumberFormatException: For input string: \"{trimmed}\""))?;
    if !(1..=65535).contains(&port) {
        return Err(format!(
            "IllegalArgumentException: port out of range: {port}"
        ));
    }
    Ok(i64::from(port))
}

/// Port of `hash` (`Strings.java:66`): over UTF-16 code units, wrapping at 32 bits.
pub fn hash(text: String) -> Result<i64, String> {
    let mut h: i32 = 0;
    for unit in text.encode_utf16() {
        h = h.wrapping_mul(31).wrapping_add(i32::from(unit));
    }
    Ok(i64::from(h))
}

#[cfg(test)]
mod tests {
    #[test]
    fn slugify_lowers_like_the_whole_string() {
        // Final sigma depends on the neighbours: lowering per piece must agree with lowering the
        // whole text, then slugifying.
        for text in [
            "ΣΊΣΥΦΟΣ  and ΟΔΟΣ.",
            "AΣ Σ ΣA",
            "ΣΣ'Σ x",
            "İstanbul ΣΑΣ\u{301} Σ",
        ] {
            let lower = text.to_lowercase();
            assert_eq!(
                super::slugify(text.into(), 0),
                super::slugify(lower, 0),
                "{text}"
            );
        }
    }
}
