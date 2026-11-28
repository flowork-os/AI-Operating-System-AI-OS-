//! The Rust port of `lib/textkit/`.

#![forbid(unsafe_code)]

use serde_json::{Map, Value, json};

/// Port of `page_count` (`lib/textkit/nums.rb:8`).
pub fn page_count(total: i64, per_page: i64) -> Result<i64, String> {
    if per_page <= 0 {
        return Err("ArgumentError: per_page must be positive".into());
    }
    Ok(-((-total).div_euclid(per_page)))
}

/// Port of `mean` (`lib/textkit/nums.rb:17`).
pub fn mean(values: Vec<f64>) -> Result<Option<f64>, String> {
    if values.is_empty() {
        return Ok(None);
    }
    Ok(Some(ruby_sum(&values) / values.len() as f64))
}

/// Ruby's `Array#sum` over floats: starts from integer 0, Kahan-Babuska compensated.
fn ruby_sum(values: &[f64]) -> f64 {
    let (mut sum, mut c) = (0.0f64, 0.0f64);
    for &x in values {
        if !x.is_finite() || !sum.is_finite() {
            // Ruby falls back to plain addition once a value is not finite.
            return values.iter().fold(0.0, |a, b| a + b);
        }
        let t = sum + x;
        if sum.abs() >= x.abs() {
            c += (sum - t) + x;
        } else {
            c += (x - t) + sum;
        }
        sum = t;
    }
    sum + c
}

/// Port of `clamp` (`lib/textkit/nums.rb:27`).
pub fn clamp(value: i64, low: i64, high: i64) -> Result<i64, String> {
    if low > high {
        return Err(
            "ArgumentError: min argument must be less than or equal to max argument".into(),
        );
    }
    Ok(value.clamp(low, high))
}

/// Port of `slugify` (`lib/textkit/words.rb:9`).
pub fn slugify(text: String, sep: String, max: Option<i64>) -> Result<String, String> {
    // Ruby lowercases each character on its own: no final-sigma rule.
    let lower: String = text.chars().flat_map(char::to_lowercase).collect();
    let words: Vec<&str> = lower
        .split(|c: char| !c.is_alphanumeric())
        .filter(|w| !w.is_empty())
        .collect();
    let slug = words.join(&sep);
    let Some(max) = max else { return Ok(slug) };
    if max < 0 {
        // `slug[0, max]` is nil for a negative length, and nil has no `chomp`.
        return Err("NoMethodError: undefined method `chomp' for nil".into());
    }
    let cut: String = slug
        .chars()
        .take(usize::try_from(max).unwrap_or(0))
        .collect();
    Ok(cut
        .strip_suffix(sep.as_str())
        .map(str::to_string)
        .unwrap_or(cut))
}

/// Port of `word_count` (`lib/textkit/words.rb:17`).
pub fn word_count(text: String) -> Result<Value, String> {
    let mut counts = Map::new();
    for w in text.split_whitespace() {
        let key: String = w.chars().flat_map(char::to_lowercase).collect();
        let n = counts.get(&key).and_then(Value::as_i64).unwrap_or(0);
        counts.insert(key, json!(n + 1));
    }
    Ok(Value::Object(counts))
}

/// Port of `titleize` (`lib/textkit/words.rb:23`).
pub fn titleize(text: String) -> Result<String, String> {
    let mut out = String::new();
    let mut start = true;
    for c in text.chars() {
        if c.is_whitespace() {
            start = true;
            out.push(c);
        } else if start {
            out.extend(c.to_uppercase());
            start = false;
        } else {
            out.extend(c.to_lowercase());
        }
    }
    Ok(out)
}
