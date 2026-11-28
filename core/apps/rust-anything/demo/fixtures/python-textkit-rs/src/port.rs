//! The Rust port of `src/textkit/` (`words.py`, `stack.py`).
//!
//! Python semantics kept on purpose: `\w` is `str.isalnum()` (by Unicode category, not Rust's
//! `is_alphanumeric`), `str.split()` whitespace includes U+001C..U+001F, `//` floors, `sum()` of
//! floats is compensated (CPython 3.12+), slices and `rstrip` work on code points and char sets.
//! Errors name the Python exception they raise (`"OverflowError: ..."`).

#![forbid(unsafe_code)]

use serde_json::{Map, Value};
use unicode_general_category::{GeneralCategory as G, get_general_category};
use unicode_normalization::UnicodeNormalization;
use unicode_normalization::char::canonical_combining_class;

/// Python `str.isalnum()` for one character: letters and numbers by general category.
fn is_alnum(c: char) -> bool {
    matches!(
        get_general_category(c),
        G::UppercaseLetter
            | G::LowercaseLetter
            | G::TitlecaseLetter
            | G::ModifierLetter
            | G::OtherLetter
            | G::DecimalNumber
            | G::LetterNumber
            | G::OtherNumber
    )
}

/// Python `str.isspace()`.
fn is_space(c: char) -> bool {
    c.is_whitespace() || ('\u{1c}'..='\u{1f}').contains(&c)
}

/// Port of `slugify` (`src/textkit/words.py:9`).
///
/// `sep` defaults to `"-"` in the source.
///
/// `max_length` defaults to `None` in the source: `None` means that default.
pub fn slugify(
    text: String,
    sep: Option<String>,
    max_length: Option<i64>,
) -> Result<String, String> {
    let sep = sep.unwrap_or_else(|| "-".into());
    let ascii_only: String = text
        .nfkd()
        .filter(|c| canonical_combining_class(*c) == 0)
        .collect();
    let lowered = ascii_only.to_lowercase();
    // `re.split(r"[^\w]+", ...)`, keeping the non-empty words.
    let words: Vec<&str> = lowered
        .split(|c: char| !(is_alnum(c) || c == '_'))
        .filter(|w| !w.is_empty())
        .collect();
    let mut slug = words.join(&sep);
    if let Some(max) = max_length {
        // `slug[:max]`: code points; a negative end counts from the end.
        let chars: Vec<char> = slug.chars().collect();
        let len = chars.len() as i64;
        let end = if max < 0 {
            (len + max).max(0)
        } else {
            max.min(len)
        };
        slug = chars[..end as usize].iter().collect();
        // `rstrip(sep)`: any trailing character that appears in `sep`.
        let strip: Vec<char> = sep.chars().collect();
        slug = slug.trim_end_matches(|c| strip.contains(&c)).to_string();
    }
    Ok(slug)
}

/// Port of `word_counts` (`src/textkit/words.py:20`).
///
/// `min_length` defaults to `1` in the source.
pub fn word_counts(text: String, min_length: i64) -> Result<serde_json::Value, String> {
    let mut counts = Map::new();
    for word in text.split(is_space).filter(|w| !w.is_empty()) {
        let word = word
            .trim_matches(|c| ".,;:!?\"'()".contains(c))
            .to_lowercase();
        if word.chars().count() as i64 >= min_length {
            let n = counts.get(&word).and_then(Value::as_i64).unwrap_or(0);
            counts.insert(word, Value::from(n + 1));
        }
    }
    Ok(Value::Object(counts))
}

/// Port of `chunk` (`src/textkit/words.py:30`).
pub fn chunk(items: Vec<i64>, size: i64) -> Result<Vec<Vec<i64>>, String> {
    if size <= 0 {
        return Err("ValueError: size must be positive".into());
    }
    Ok(items
        .chunks(usize::try_from(size).unwrap_or(usize::MAX))
        .map(<[i64]>::to_vec)
        .collect())
}

/// Port of `page_count` (`src/textkit/words.py:37`): `-(-total // per_page)`.
pub fn page_count(total: i64, per_page: i64) -> Result<i64, String> {
    if per_page == 0 {
        return Err("ZeroDivisionError: integer division or modulo by zero".into());
    }
    let (a, b) = (-i128::from(total), i128::from(per_page));
    // Python `//` floors; Rust `/` truncates toward zero.
    let mut q = a / b;
    if a % b != 0 && ((a < 0) != (b < 0)) {
        q -= 1;
    }
    i64::try_from(-q).map_err(|_| "OverflowError: result does not fit in 64 bits".into())
}

/// Port of `mean` (`src/textkit/words.py:42`): `sum(values) / len(values)`.
pub fn mean(values: Vec<f64>) -> Result<f64, String> {
    if values.is_empty() {
        return Err("ZeroDivisionError: division by zero".into());
    }
    // CPython 3.12+ `sum()` of floats: Neumaier compensated summation.
    let (mut total, mut c) = (0.0f64, 0.0f64);
    for x in &values {
        let t = total + x;
        c += if total.abs() >= x.abs() {
            (total - t) + x
        } else {
            (x - t) + total
        };
        total = t;
    }
    if c != 0.0 && c.is_finite() {
        total += c;
    }
    Ok(total / values.len() as f64)
}

/// Port of class `Stack` (`src/textkit/stack.py:4`): holds the instance state.
pub struct Stack {
    items: Vec<String>,
    capacity: i64,
}

impl Stack {
    /// Port of `Stack` constructor (`src/textkit/stack.py:4`).
    pub fn new(capacity: i64) -> Result<Self, String> {
        if capacity < 1 {
            return Err("ValueError: capacity must be at least 1".into());
        }
        Ok(Self {
            items: Vec::new(),
            capacity,
        })
    }

    /// Port of `Stack.push` (`src/textkit/stack.py:13`).
    pub fn push(&mut self, item: String) -> Result<i64, String> {
        if self.items.len() as i64 >= self.capacity {
            return Err("OverflowError: stack is full".into());
        }
        self.items.push(item);
        Ok(self.items.len() as i64)
    }

    /// Port of `Stack.pop` (`src/textkit/stack.py:19`).
    pub fn pop(&mut self) -> Result<Option<String>, String> {
        Ok(self.items.pop())
    }

    /// Port of `Stack.peek` (`src/textkit/stack.py:22`).
    pub fn peek(&self) -> Result<Option<String>, String> {
        Ok(self.items.last().cloned())
    }

    /// Port of `Stack.size` (`src/textkit/stack.py:25`).
    pub fn size(&self) -> Result<i64, String> {
        Ok(self.items.len() as i64)
    }
}
