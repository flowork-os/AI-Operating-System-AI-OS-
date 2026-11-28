//! The Rust port of the text helpers in `packages/builtins/src/formats/shared/`.
//!
//! `toLeaf` (`instanceof Date`), `createJsonFormat`, `literalText` and `editLiteral` (objects of
//! functions) stay in TS. Offsets are UTF-16 units; results that may split a surrogate pair
//! carry the exact units through `js::utf16_string`.

#![forbid(unsafe_code)]

use serde_json::{Value, json};

use crate::js;

/// V8's longest string (`String.prototype.repeat` throws beyond it).
const MAX_STRING_LENGTH: f64 = 536_870_888.0;

fn units(s: &str) -> Vec<u16> {
    s.encode_utf16().collect()
}

/// JS `WhiteSpace` and `LineTerminator` (what `\s` matches).
fn is_space(u: u16) -> bool {
    matches!(u, 0x09..=0x0D | 0x20 | 0xA0 | 0x1680 | 0x2000..=0x200A | 0x2028 | 0x2029 | 0x202F | 0x205F | 0x3000 | 0xFEFF)
}

fn is_line_terminator(u: u16) -> bool {
    matches!(u, 0x0A | 0x0D | 0x2028 | 0x2029)
}

/// JS `ToNumber` for the values these helpers receive; `None` is `undefined`.
fn to_number(value: &Value) -> f64 {
    if js::is_undefined(value) {
        return f64::NAN;
    }
    if let Some(n) = js::as_number(value) {
        return n;
    }
    if let Some(u) = js::string_units(value) {
        let t = String::from_utf16_lossy(&u);
        let t = t.trim();
        return if t.is_empty() {
            0.0
        } else {
            t.parse().unwrap_or(f64::NAN)
        };
    }
    match value {
        Value::Null => 0.0,
        Value::Bool(b) => f64::from(u8::from(*b)),
        Value::Array(a) if a.is_empty() => 0.0,
        _ => f64::NAN,
    }
}

/// JS `ToString`.
fn to_string(value: &Value) -> Vec<u16> {
    if js::is_undefined(value) {
        return units("undefined");
    }
    if let Some(n) = js::as_number(value) {
        return units(&number_to_string(n));
    }
    if let Some(u) = js::string_units(value) {
        return u;
    }
    match value {
        Value::Null => units("null"),
        Value::Bool(b) => units(&b.to_string()),
        Value::Array(items) => {
            let parts: Vec<Vec<u16>> = items
                .iter()
                .map(|v| {
                    if v.is_null() || js::is_undefined(v) {
                        Vec::new()
                    } else {
                        to_string(v)
                    }
                })
                .collect();
            parts.join(&u16::from(b','))
        }
        _ => units("[object Object]"),
    }
}

fn number_to_string(n: f64) -> String {
    if n.is_nan() {
        return "NaN".into();
    }
    if n.is_infinite() {
        return if n > 0.0 {
            "Infinity".into()
        } else {
            "-Infinity".into()
        };
    }
    if n == 0.0 {
        return "0".into();
    }
    if n < 0.0 {
        return format!("-{}", number_to_string(-n));
    }
    let exp = format!("{n:e}");
    let (mantissa, e) = exp.split_once('e').unwrap_or((&exp, "0"));
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();
    let k = digits.len() as i64;
    let point = e.parse::<i64>().unwrap_or(0) + 1;
    if k <= point && point <= 21 {
        format!("{digits}{}", "0".repeat((point - k) as usize))
    } else if 0 < point && point <= 21 {
        format!(
            "{}.{}",
            &digits[..point as usize],
            &digits[point as usize..]
        )
    } else if -6 < point && point <= 0 {
        format!("0.{}{digits}", "0".repeat((-point) as usize))
    } else {
        let rest = if k == 1 {
            String::new()
        } else {
            format!(".{}", &digits[1..])
        };
        format!(
            "{}{rest}e{}{}",
            &digits[..1],
            if point > 1 { "+" } else { "-" },
            (point - 1).abs()
        )
    }
}

/// `range.start` / `range.end`: reading from null or undefined throws.
fn field(range: &Value, name: &str) -> Result<Value, String> {
    if range.is_null() || js::is_undefined(range) {
        return Err(format!(
            "TypeError: Cannot read properties of null (reading '{name}')"
        ));
    }
    Ok(range
        .as_object()
        .and_then(|o| o.get(name))
        .cloned()
        .unwrap_or_else(js::undefined))
}

/// A `slice` argument: `undefined` means `default`; else truncate, NaN is 0, negative counts from the end.
fn slice_index(value: &Value, len: usize, default: usize) -> usize {
    if js::is_undefined(value) {
        return default;
    }
    let n = to_number(value);
    let n = if n.is_nan() { 0.0 } else { n.trunc() };
    if n < 0.0 {
        (len as f64 + n).max(0.0) as usize
    } else {
        n.min(len as f64) as usize
    }
}

/// Port of `indentUnit` (`packages/builtins/src/formats/shared/index.ts:4`).
pub fn indent_unit(text: String, indent: Value, fallback: String) -> Result<String, String> {
    if !js::is_undefined(&indent) {
        if indent == Value::String("tab".into()) {
            return Ok("\t".into());
        }
        // `' '.repeat(indent)`
        let count = to_number(&indent);
        let count = if count.is_nan() { 0.0 } else { count.trunc() };
        if count < 0.0 || count.is_infinite() {
            return Err(format!(
                "RangeError: Invalid count value: {}",
                number_to_string(count)
            ));
        }
        if count > MAX_STRING_LENGTH {
            return Err("RangeError: Invalid string length".into());
        }
        return Ok(" ".repeat(count as usize));
    }
    // `/^([ \t]+)\S/m`: at a line start (after any line terminator), spaces or tabs, then a non-space.
    let text = units(&text);
    for start in 0..text.len() {
        if start > 0 && !is_line_terminator(text[start - 1]) {
            continue;
        }
        let run = text[start..]
            .iter()
            .take_while(|&&u| u == 0x20 || u == 0x09)
            .count();
        if run > 0 && text.get(start + run).is_some_and(|&u| !is_space(u)) {
            return Ok(String::from_utf16_lossy(&text[start..start + run]));
        }
    }
    Ok(fallback)
}

/// Port of `detectEol` (`packages/builtins/src/formats/shared/index.ts:13`).
pub fn detect_eol(text: String) -> Result<String, String> {
    Ok(if text.contains("\r\n") { "\r\n" } else { "\n" }.into())
}

/// Port of `leafText` (`packages/builtins/src/formats/shared/index.ts:27`).
pub fn leaf_text(value: Value) -> Result<Value, String> {
    Ok(if value.is_null() {
        Value::String(String::new())
    } else {
        js::utf16_string(&to_string(&value))
    })
}

/// Port of `splice` (`packages/builtins/src/formats/shared/index.ts:33`).
pub fn splice(text: String, range: Value, insert: String) -> Result<Value, String> {
    let start = field(&range, "start")?;
    let end = field(&range, "end")?;
    let text = units(&text);
    let head = slice_index(&start, text.len(), text.len());
    let tail = slice_index(&end, text.len(), 0);
    let out = [&text[..head], &units(&insert)[..], &text[tail..]].concat();
    Ok(js::utf16_string(&out))
}

/// Port of `appendLines` (`packages/builtins/src/formats/shared/index.ts:38`).
pub fn append_lines(text: String, chunk: String) -> Result<String, String> {
    let eol = if text.contains("\r\n") { "\r\n" } else { "\n" };
    let base = if text.is_empty() || text.ends_with('\n') {
        text
    } else {
        format!("{text}{eol}")
    };
    Ok(format!("{base}{}", chunk.replace('\n', eol)))
}

/// Port of `splitLines` (`packages/builtins/src/formats/shared/index.ts:54`).
pub fn split_lines(text: String) -> Result<Vec<Value>, String> {
    let text = units(&text);
    let mut out = Vec::new();
    let mut start = 0;
    while start < text.len() {
        let lf = text[start..]
            .iter()
            .position(|&u| u == 0x0A)
            .map(|i| i + start);
        let next = lf.map_or(text.len(), |lf| lf + 1);
        let end = match lf {
            None => text.len(),
            Some(lf) if lf > start && text[lf - 1] == 0x0D => lf - 1,
            Some(lf) => lf,
        };
        out.push(json!({ "start": start, "end": end, "next": next }));
        start = next;
    }
    Ok(out)
}

/// Port of `withBlankLines` (`packages/builtins/src/formats/shared/index.ts:74`).
pub fn with_blank_lines(text: String, range: Value) -> Result<Value, String> {
    let range_start = field(&range, "start")?;
    let range_end = field(&range, "end")?;
    let text = units(&text);
    let len = text.len();
    // `/^(?:[ \t]*\r?\n)*(?:[ \t]*$)?/` on `text.slice(range.end)`: blank lines, then trailing blanks.
    let rest = &text[slice_index(&range_end, len, 0)..];
    let blank = |u: &u16| *u == 0x20 || *u == 0x09;
    let mut after = 0;
    loop {
        let mut j = after + rest[after..].iter().take_while(|u| blank(u)).count();
        if rest.get(j) == Some(&0x0D) && rest.get(j + 1) == Some(&0x0A) {
            j += 2;
        } else if rest.get(j) == Some(&0x0A) {
            j += 1;
        } else {
            break;
        }
        after = j;
    }
    if after + rest[after..].iter().take_while(|u| blank(u)).count() == rest.len() {
        after = rest.len();
    }
    let end = to_number(&range_end) + after as f64;
    if end < len as f64 {
        return Ok(json!({ "start": range_start, "end": js::number(end) }));
    }
    // `/(?<=\n)(?:[ \t]*\r?\n)+$/` on `text.slice(0, range.start)`: the blank lines that end it,
    // from the leftmost one that follows a `\n`.
    let head = &text[..slice_index(&range_start, len, len)];
    let mut best = None;
    let mut pos = head.len();
    while pos > 0 && head[pos - 1] == 0x0A {
        let line_start = head[..pos - 1]
            .iter()
            .rposition(|&u| u == 0x0A)
            .map_or(0, |i| i + 1);
        let mut content = &head[line_start..pos - 1];
        if content.last() == Some(&0x0D) {
            content = &content[..content.len() - 1];
        }
        if !content.iter().all(blank) || line_start == 0 {
            break;
        }
        best = Some(line_start);
        pos = line_start;
    }
    let before = best.map_or(0, |b| head.len() - b);
    Ok(json!({ "start": js::number(to_number(&range_start) - before as f64), "end": len }))
}
