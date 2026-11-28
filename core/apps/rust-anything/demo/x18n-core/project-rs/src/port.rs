//! The Rust port of the pure helpers in `packages/core/src/project/`.
//!
//! The rest of `project/` is the engine (`createProject`, `createPlanner`, ...): it calls JS
//! plugins and hosts through callbacks and stays in TS. Strings are handled as UTF-16 code
//! units where JS semantics depend on it; invalid input returns an error where JS throws.

#![forbid(unsafe_code)]

use std::cmp::Ordering;

use serde_json::{Map, Value, json};

use crate::js;

// ---- isOutdated, valueText, sourceHash -------------------------------------------------------

/// Port of `isOutdated` (`project/history.ts:8`): the target changed before its source.
pub fn is_outdated(source: Value, target: Value) -> Result<bool, String> {
    if js::is_undefined(&source) || js::is_undefined(&target) {
        return Ok(false);
    }
    let target_at = prop(&target, "updatedAt")?;
    let source_at = prop(&source, "updatedAt")?;
    Ok(less_than(target_at.as_ref(), source_at.as_ref()))
}

/// Port of `valueText` (`project/reviews.ts:8`): `''` for null, else `String(value)`.
pub fn value_text(value: Value) -> Value {
    if value.is_null() {
        return Value::String(String::new());
    }
    js::utf16_string(&to_js_string(&value))
}

/// Port of `sourceHash` (`project/reviews.ts:15`): `hashText(JSON.stringify(value))`.
pub fn source_hash(value: Value) -> Result<String, String> {
    let text = json_stringify(&value)
        .ok_or("TypeError: Cannot read properties of undefined (reading 'length')")?;
    Ok(cyrb53(&text))
}

// ---- findReview, sortReviews -----------------------------------------------------------------

/// Port of `findReview` (`project/reviews.ts:91`): the comment with `id`, with its key and locale.
pub fn find_review(data: Value, id: String) -> Result<Value, String> {
    let threads = prop(&data, "threads")?.unwrap_or_else(js::undefined);
    for (key, by_locale) in object_entries(&threads)? {
        for (locale, comments) in object_entries(&by_locale)? {
            let Value::Array(comments) = comments else {
                return Err("TypeError: comments.find is not a function".into());
            };
            for comment in comments {
                if prop(&comment, "id")?.as_ref() == Some(&Value::String(id.clone())) {
                    return Ok(json!({ "key": key, "locale": locale, "comment": comment }));
                }
            }
        }
    }
    Ok(js::undefined())
}

/// Port of `sortReviews` (`project/reviews.ts:115`): keys and locales in code order, empty keys dropped.
pub fn sort_reviews(data: Value) -> Result<Value, String> {
    let threads = sort_section(&prop(&data, "threads")?.unwrap_or_else(js::undefined))?;
    let sources = sort_section(&prop(&data, "sources")?.unwrap_or_else(js::undefined))?;
    Ok(json!({ "threads": threads, "sources": sources }))
}

fn sort_section(section: &Value) -> Result<Value, String> {
    let mut entries = Vec::new();
    for (key, by_locale) in object_entries(section)? {
        if !object_entries(&by_locale)?.is_empty() {
            entries.push((key, by_locale));
        }
    }
    entries.sort_by(|(a, _), (b, _)| by_code(a, b));
    let mut out = Map::new();
    for (key, by_locale) in entries {
        let mut locales = object_entries(&by_locale)?;
        locales.sort_by(|(a, _), (b, _)| by_code(a, b));
        out.insert(key, Value::Object(locales.into_iter().collect()));
    }
    Ok(Value::Object(out))
}

/// `byCode`: JS `<` on strings, which compares UTF-16 code units (not code points).
fn by_code(a: &str, b: &str) -> Ordering {
    a.encode_utf16().cmp(b.encode_utf16())
}

// ---- prefixMatches, suppressedRanges, categoriesOf -------------------------------------------

/// Port of `prefixMatches` (`project/usages.ts:100`): a `prefix` usage whose key starts `key`.
pub fn prefix_matches(usage: Value, key: String) -> Result<bool, String> {
    if prop(&usage, "dynamic")?.as_ref() != Some(&Value::String("prefix".into())) {
        return Ok(false);
    }
    let Some(prefix) = prop(&usage, "key")? else {
        return Ok(false);
    };
    Ok(key
        .encode_utf16()
        .collect::<Vec<_>>()
        .starts_with(&to_js_string(&prefix)))
}

/// Port of `suppressedRanges` (`project/usages.ts:105`): ranges under `x18n-disable-next-line`,
/// and from `x18n-disable` to `x18n-enable`. Offsets are UTF-16 code units.
///
/// Searches the UTF-8 bytes (the markers and `\n` are ASCII, so byte matches are exactly the
/// JS matches) and converts only the positions it reports to UTF-16 offsets.
pub fn suppressed_ranges(text: String) -> Vec<Value> {
    if !text.contains("x18n-disable") {
        return Vec::new();
    }
    let bytes = text.as_bytes();
    let newline = |from: usize| {
        bytes
            .get(from..)
            .and_then(|rest| rest.iter().position(|&b| b == b'\n'))
            .map(|i| i + from)
    };
    let mut offsets = Utf16Offsets::new(&text);
    let mut ranges = Vec::new();

    // /x18n-disable-next-line/g
    let mut next_line = Vec::new();
    for (index, _) in text.match_indices("x18n-disable-next-line") {
        let Some(line_end) = newline(index) else {
            continue;
        };
        let next_end = newline(line_end + 1).unwrap_or(bytes.len());
        next_line.push((line_end + 1, next_end));
    }
    for (start, end) in next_line {
        let start = offsets.at(start);
        let end = offsets.at(end);
        ranges.push(json!({ "start": start, "end": end }));
    }

    // /x18n-disable(?![-\w])/g: the `regex` crate has no lookahead, so check the next byte.
    let mut offsets = Utf16Offsets::new(&text);
    let mut ends = Utf16Offsets::new(&text);
    for (index, marker) in text.match_indices("x18n-disable") {
        let after = bytes.get(index + marker.len()).copied();
        if after.is_some_and(|b| b == b'-' || b.is_ascii_alphanumeric() || b == b'_') {
            continue;
        }
        let end = text[index..]
            .find("x18n-enable")
            .map_or(bytes.len(), |i| i + index);
        let start = offsets.at(index);
        let end = ends.at(end);
        ranges.push(json!({ "start": start, "end": end }));
    }
    ranges
}

/// UTF-8 byte offsets to UTF-16 offsets, for increasing byte offsets in one pass.
struct Utf16Offsets<'t> {
    text: &'t str,
    byte: usize,
    utf16: usize,
}

impl<'t> Utf16Offsets<'t> {
    fn new(text: &'t str) -> Self {
        Self {
            text,
            byte: 0,
            utf16: 0,
        }
    }

    fn at(&mut self, byte: usize) -> usize {
        if byte < self.byte {
            *self = Self::new(self.text);
        }
        let segment = &self.text.as_bytes()[self.byte..byte];
        // ASCII runs are one unit per byte; only non-ASCII needs decoding.
        self.utf16 += if segment.is_ascii() {
            segment.len()
        } else {
            self.text[self.byte..byte].encode_utf16().count()
        };
        self.byte = byte;
        self.utf16
    }
}

/// Port of `categoriesOf` (`project/usages.ts:136`).
pub fn categories_of(info: Value, kind: Value) -> Result<Value, String> {
    let field = if kind == Value::String("ordinal".into()) {
        "ordinalCategories"
    } else {
        "pluralCategories"
    };
    Ok(prop(&info, field)?.unwrap_or_else(js::undefined))
}

// ---- renderPrompt ----------------------------------------------------------------------------

/// Port of `renderPrompt` (`project/prompt.ts:223`): the Markdown prompt for agents.
pub fn render_prompt(data: Value) -> Result<Value, String> {
    let get = |key: &str| prop(&data, key);
    let to = get("to")?;
    let target: Vec<u16> = match get("targetName")? {
        Some(name) if truthy(&name) => cat(&[
            opt_string(to.as_ref()),
            s(" ("),
            to_js_string(&name),
            s(")"),
        ]),
        _ => opt_string(to.as_ref()),
    };
    let from = opt_string(get("from")?.as_ref());
    let kind = get("kind")?;
    let items = get("items")?;
    let item_count = length(items.as_ref())?;
    let mut out: Vec<Vec<u16>> = Vec::new();
    if kind == Some(Value::String("translate".into())) {
        out.push(cat(&[
            s("# Translate "),
            item_count.clone(),
            s(" messages from "),
            from.clone(),
            s(" to "),
            target.clone(),
        ]));
        out.push(Vec::new());
    } else {
        out.push(cat(&[
            s("# Review "),
            item_count.clone(),
            s(" "),
            target.clone(),
            s(" translations against "),
            from.clone(),
        ]));
        out.push(Vec::new());
        out.push(s("Check meaning, placeholders, glossary terms, tone and length. Report and fix wrong translations."));
        out.push(Vec::new());
    }
    if item_count == s("0") {
        let done = if kind == Some(Value::String("translate".into())) {
            "translated"
        } else {
            "reviewed"
        };
        return Ok(js::utf16_string(&cat(&[
            join(&out),
            s(&format!("Nothing to do: every key is {done}.\n")),
        ])));
    }
    out.push(s("## Rules"));
    out.push(Vec::new());
    for rule in array(get("rules")?.as_ref(), "rules")? {
        out.push(cat(&[s("- "), to_js_string(&rule)]));
    }
    for note in array(get("notes")?.as_ref(), "notes")? {
        out.push(cat(&[s("- "), to_js_string(&note)]));
    }
    out.push(Vec::new());
    let glossary = get("glossary")?;
    if greater_than_zero(length_value(glossary.as_ref())?.as_ref()) {
        out.push(s("## Glossary"));
        out.push(Vec::new());
        for entry in iterate(glossary.as_ref())? {
            let term = to_js_string(&prop(&entry, "term")?.unwrap_or_else(js::undefined));
            let detail = if prop(&entry, "doNotTranslate")?.is_some_and(|v| truthy(&v)) {
                s(": do not translate")
            } else {
                match prop(&entry, "translation")? {
                    Some(t) if truthy(&t) => cat(&[s(" → "), to_js_string(&t)]),
                    _ => Vec::new(),
                }
            };
            let note = match prop(&entry, "note")? {
                Some(n) if truthy(&n) => cat(&[s(" ("), to_js_string(&n), s(")")]),
                _ => Vec::new(),
            };
            out.push(cat(&[s("- "), term, detail, note]));
        }
        out.push(Vec::new());
    }
    let to_text = opt_string(to.as_ref());
    let examples = get("examples")?;
    if greater_than_zero(length_value(examples.as_ref())?.as_ref()) {
        out.push(cat(&[
            s("## Existing "),
            to_text.clone(),
            s(" messages (style reference)"),
        ]));
        out.push(Vec::new());
        for example in iterate(examples.as_ref())? {
            let key = to_js_string(&prop(&example, "key")?.unwrap_or_else(js::undefined));
            let source = stringify_or_undefined(prop(&example, "source")?.as_ref());
            let target = stringify_or_undefined(prop(&example, "target")?.as_ref());
            out.push(cat(&[s("- `"), key, s("`: "), source, s(" → "), target]));
        }
        out.push(Vec::new());
    }
    out.push(s("## Messages"));
    out.push(Vec::new());
    for item in array(items.as_ref(), "items")? {
        out.extend(render_item(&item, &to_text)?);
    }
    out.push(s("## How to write results"));
    out.push(Vec::new());
    for line in array(get("instructions")?.as_ref(), "instructions")? {
        out.push(cat(&[s("- "), to_js_string(&line)]));
    }
    out.push(Vec::new());
    if greater_than_zero(get("remaining")?.as_ref()) {
        let total = opt_string(get("total")?.as_ref());
        out.push(cat(&[
            s("This prompt holds "),
            item_count,
            s(" of "),
            total,
            s(" messages."),
        ]));
        out.push(Vec::new());
    }
    Ok(js::utf16_string(&join(&out)))
}

fn render_item(item: &Value, to: &[u16]) -> Result<Vec<Vec<u16>>, String> {
    let key = to_js_string(&prop(item, "key")?.unwrap_or_else(js::undefined));
    let source = stringify_or_undefined(prop(item, "source")?.as_ref());
    let mut out = vec![
        cat(&[s("### `"), key, s("`")]),
        Vec::new(),
        cat(&[s("- Source: "), source]),
    ];
    let placeholders = prop(item, "placeholders")?;
    if length_value(placeholders.as_ref())?.is_some_and(|l| truthy(&l)) {
        let list: Vec<Vec<u16>> = array(placeholders.as_ref(), "placeholders")?
            .iter()
            .map(|p| cat(&[s("`"), to_js_string(p), s("`")]))
            .collect();
        out.push(cat(&[s("- Placeholders: "), join_with(&list, ", ")]));
    }
    if let Some(previous) = prop(item, "previousSource")? {
        out.push(cat(&[
            s("- Source when "),
            to.to_vec(),
            s(" last changed: "),
            stringify_or_undefined(Some(&previous)),
        ]));
    }
    if let Some(existing) = prop(item, "existing")? {
        out.push(cat(&[
            s("- Current "),
            to.to_vec(),
            s(": "),
            stringify_or_undefined(Some(&existing)),
        ]));
    }
    for context in iterate(prop(item, "context")?.as_ref())? {
        let path = to_js_string(&prop(&context, "path")?.unwrap_or_else(js::undefined));
        let line = to_js_string(&prop(&context, "line")?.unwrap_or_else(js::undefined));
        let snippet = prop(&context, "snippet")?
            .and_then(|v| js::string_units(&v))
            .ok_or("TypeError: context.snippet.split is not a function")?;
        out.push(cat(&[s("- Used in `"), path, s(":"), line, s("`:")]));
        out.push(Vec::new());
        out.push(s("  ```"));
        for part in snippet.split(|&u| u == 10) {
            out.push(cat(&[s("  "), part.to_vec()]));
        }
        out.push(s("  ```"));
    }
    out.push(Vec::new());
    Ok(out)
}

// ---- JS semantics ----------------------------------------------------------------------------

fn s(text: &str) -> Vec<u16> {
    text.encode_utf16().collect()
}

fn cat(parts: &[Vec<u16>]) -> Vec<u16> {
    parts.concat()
}

fn join(lines: &[Vec<u16>]) -> Vec<u16> {
    join_with(lines, "\n")
}

fn join_with(parts: &[Vec<u16>], sep: &str) -> Vec<u16> {
    let sep = s(sep);
    let mut out = Vec::new();
    for (i, part) in parts.iter().enumerate() {
        if i > 0 {
            out.extend_from_slice(&sep);
        }
        out.extend_from_slice(part);
    }
    out
}

/// `` `${value}` `` for a property that may be missing.
fn opt_string(value: Option<&Value>) -> Vec<u16> {
    value.map_or_else(|| s("undefined"), to_js_string)
}

/// `JSON.stringify(value)` interpolated: `undefined` when it has no JSON form.
fn stringify_or_undefined(value: Option<&Value>) -> Vec<u16> {
    value
        .and_then(json_stringify)
        .unwrap_or_else(|| s("undefined"))
}

/// `value[key]`: `None` is `undefined`; reading from null or undefined throws.
fn prop(value: &Value, key: &str) -> Result<Option<Value>, String> {
    if value.is_null() || js::is_undefined(value) {
        return Err(format!(
            "TypeError: Cannot read properties of {} (reading '{key}')",
            if value.is_null() { "null" } else { "undefined" }
        ));
    }
    if let Some(units) = js::string_units(value) {
        return Ok(match key {
            "length" => Some(js::number(units.len() as f64)),
            _ => index(key)
                .and_then(|i| units.get(i))
                .map(|u| js::utf16_string(&[*u])),
        });
    }
    if js::as_number(value).is_some() {
        return Ok(None);
    }
    Ok(match value {
        Value::Object(o) => o.get(key).filter(|v| !js::is_undefined(v)).cloned(),
        Value::Array(items) => match key {
            "length" => Some(js::number(items.len() as f64)),
            _ => index(key).and_then(|i| items.get(i)).cloned(),
        },
        _ => None,
    })
}

fn index(key: &str) -> Option<usize> {
    let i: usize = key.parse().ok()?;
    (i.to_string() == key).then_some(i)
}

/// `value.length` (throws on null or undefined).
fn length_value(value: Option<&Value>) -> Result<Option<Value>, String> {
    match value {
        None => Err("TypeError: Cannot read properties of undefined (reading 'length')".into()),
        Some(v) => prop(v, "length"),
    }
}

/// `${value.length}`.
fn length(value: Option<&Value>) -> Result<Vec<u16>, String> {
    Ok(opt_string(length_value(value)?.as_ref()))
}

/// Elements for `.map` / `.flatMap`: only arrays have them.
fn array(value: Option<&Value>, name: &str) -> Result<Vec<Value>, String> {
    match value {
        Some(Value::Array(items)) => Ok(items.clone()),
        Some(v) if !v.is_null() && !js::is_undefined(v) => {
            Err(format!("TypeError: {name}.map is not a function"))
        }
        _ => Err(format!(
            "TypeError: Cannot read properties of undefined (reading 'map') of {name}"
        )),
    }
}

/// Elements for `for...of`: arrays, and strings by code point.
fn iterate(value: Option<&Value>) -> Result<Vec<Value>, String> {
    match value {
        Some(Value::Array(items)) => Ok(items.clone()),
        Some(v) => match js::string_units(v) {
            Some(units) => Ok(char::decode_utf16(units.iter().copied())
                .map(|r| match r {
                    Ok(c) => Value::String(c.to_string()),
                    Err(e) => js::utf16_string(&[e.unpaired_surrogate()]),
                })
                .collect()),
            None => Err("TypeError: value is not iterable".into()),
        },
        None => Err("TypeError: undefined is not iterable".into()),
    }
}

/// `value > 0` for a property that may be missing (`undefined > 0` is false).
fn greater_than_zero(value: Option<&Value>) -> bool {
    value.is_some_and(|v| to_number(v) > 0.0)
}

fn truthy(value: &Value) -> bool {
    if js::is_undefined(value) {
        return false;
    }
    if let Some(n) = js::as_number(value) {
        return n != 0.0 && !n.is_nan();
    }
    if let Some(units) = js::string_units(value) {
        return !units.is_empty();
    }
    match value {
        Value::Null => false,
        Value::Bool(b) => *b,
        _ => true,
    }
}

/// JS `a < b` (abstract relational comparison); `None` is `undefined`.
fn less_than(a: Option<&Value>, b: Option<&Value>) -> bool {
    if let (Some(a), Some(b)) = (a, b)
        && let (Some(x), Some(y)) = (string_prim(a), string_prim(b))
    {
        return x < y;
    }
    let x = a.map_or(f64::NAN, to_number);
    let y = b.map_or(f64::NAN, to_number);
    x < y
}

/// The UTF-16 units of `ToPrimitive(value)` when that is a string.
fn string_prim(value: &Value) -> Option<Vec<u16>> {
    if js::as_number(value).is_some() || js::is_undefined(value) {
        return None;
    }
    match value {
        Value::Array(_) | Value::Object(_) => {
            js::string_units(value).or_else(|| Some(to_js_string(value)))
        }
        _ => js::string_units(value),
    }
}

/// JS `ToNumber`.
fn to_number(value: &Value) -> f64 {
    if js::is_undefined(value) {
        return f64::NAN;
    }
    if let Some(n) = js::as_number(value) {
        return n;
    }
    if let Some(units) = js::string_units(value) {
        return string_to_number(&String::from_utf16_lossy(&units));
    }
    match value {
        Value::Null => 0.0,
        Value::Bool(b) => f64::from(u8::from(*b)),
        Value::Array(_) => string_to_number(&String::from_utf16_lossy(&to_js_string(value))),
        _ => f64::NAN,
    }
}

fn string_to_number(text: &str) -> f64 {
    let t = text.trim();
    match t {
        "" => 0.0,
        "Infinity" | "+Infinity" => f64::INFINITY,
        "-Infinity" => f64::NEG_INFINITY,
        _ if t.len() > 2 && (t.starts_with("0x") || t.starts_with("0X")) => {
            u64::from_str_radix(&t[2..], 16).map_or(f64::NAN, |n| n as f64)
        }
        _ if t
            .chars()
            .all(|c| c.is_ascii_digit() || matches!(c, '+' | '-' | '.' | 'e' | 'E')) =>
        {
            t.parse().unwrap_or(f64::NAN)
        }
        _ => f64::NAN,
    }
}

/// JS `ToString`, as UTF-16 code units.
fn to_js_string(value: &Value) -> Vec<u16> {
    if js::is_undefined(value) {
        return s("undefined");
    }
    if let Some(n) = js::as_number(value) {
        return s(&number_to_string(n));
    }
    if let Some(units) = js::string_units(value) {
        return units;
    }
    match value {
        Value::Null => s("null"),
        Value::Bool(b) => s(&b.to_string()),
        Value::Number(n) => s(&number_to_string(n.as_f64().unwrap_or(f64::NAN))),
        Value::Array(items) => {
            let parts: Vec<Vec<u16>> = items
                .iter()
                .map(|v| {
                    if v.is_null() || js::is_undefined(v) {
                        Vec::new()
                    } else {
                        to_js_string(v)
                    }
                })
                .collect();
            join_with(&parts, ",")
        }
        Value::String(_) | Value::Object(_) => s("[object Object]"),
    }
}

/// ECMAScript `Number::toString(10)`: shortest round-trip digits, exponent past 1e21 and below 1e-6.
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
    // Rust's `{:e}` prints the shortest digits that round-trip, like JS.
    let exp_form = format!("{n:e}");
    let (mantissa, exponent) = exp_form.split_once('e').unwrap_or((&exp_form, "0"));
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();
    let k = digits.len() as i64;
    let e: i64 = exponent.parse().unwrap_or(0);
    let point = e + 1;
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
        let sign = if point - 1 < 0 { "-" } else { "+" };
        let rest = if k == 1 {
            String::new()
        } else {
            format!(".{}", &digits[1..])
        };
        format!("{}{rest}e{sign}{}", &digits[..1], (point - 1).abs())
    }
}

/// `JSON.stringify(value)` as UTF-16 code units; `None` when JS returns `undefined`.
fn json_stringify(value: &Value) -> Option<Vec<u16>> {
    if js::is_undefined(value) {
        return None;
    }
    if let Some(n) = js::as_number(value) {
        return Some(s(&if n.is_finite() {
            number_to_string(n)
        } else {
            "null".into()
        }));
    }
    if let Some(units) = js::string_units(value) {
        return Some(quote(&units));
    }
    Some(match value {
        Value::Null => s("null"),
        Value::Bool(b) => s(&b.to_string()),
        Value::Number(n) => s(&number_to_string(n.as_f64().unwrap_or(f64::NAN))),
        Value::String(_) => unreachable_string(),
        Value::Array(items) => {
            let parts: Vec<Vec<u16>> = items
                .iter()
                .map(|v| json_stringify(v).unwrap_or_else(|| s("null")))
                .collect();
            cat(&[s("["), join_with(&parts, ","), s("]")])
        }
        Value::Object(o) => {
            let parts: Vec<Vec<u16>> = o
                .iter()
                .filter_map(|(k, v)| json_stringify(v).map(|v| cat(&[quote(&s(k)), s(":"), v])))
                .collect();
            cat(&[s("{"), join_with(&parts, ","), s("}")])
        }
    })
}

/// Strings are handled by `string_units` above; this keeps the match exhaustive.
fn unreachable_string() -> Vec<u16> {
    Vec::new()
}

/// JSON string quoting as `JSON.stringify` does it, lone surrogates escaped.
fn quote(units: &[u16]) -> Vec<u16> {
    let mut out = s("\"");
    let mut i = 0;
    while i < units.len() {
        let u = units[i];
        let pair = (0xD800..0xDC00).contains(&u)
            && units
                .get(i + 1)
                .is_some_and(|n| (0xDC00..0xE000).contains(n));
        match u {
            0x22 => out.extend(s("\\\"")),
            0x5C => out.extend(s("\\\\")),
            0x08 => out.extend(s("\\b")),
            0x0C => out.extend(s("\\f")),
            0x0A => out.extend(s("\\n")),
            0x0D => out.extend(s("\\r")),
            0x09 => out.extend(s("\\t")),
            _ if u < 0x20 => out.extend(s(&format!("\\u{u:04x}"))),
            _ if pair => {
                out.push(u);
                out.push(units[i + 1]);
                i += 1;
            }
            0xD800..=0xDFFF => out.extend(s(&format!("\\u{u:04x}"))),
            _ => out.push(u),
        }
        i += 1;
    }
    out.push(u16::from(b'"'));
    out
}

/// `Object.entries(value)`.
fn object_entries(value: &Value) -> Result<Vec<(String, Value)>, String> {
    if value.is_null() || js::is_undefined(value) {
        return Err("TypeError: Cannot convert undefined or null to object".into());
    }
    if let Some(units) = js::string_units(value) {
        return Ok(units
            .iter()
            .enumerate()
            .map(|(i, u)| (i.to_string(), js::utf16_string(&[*u])))
            .collect());
    }
    if js::as_number(value).is_some() {
        return Ok(Vec::new());
    }
    Ok(match value {
        Value::Object(o) => o.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        Value::Array(items) => items
            .iter()
            .enumerate()
            .map(|(i, v)| (i.to_string(), v.clone()))
            .collect(),
        _ => Vec::new(),
    })
}

/// `hashText`: cyrb53 over UTF-16 code units, as hex.
fn cyrb53(units: &[u16]) -> String {
    let mut h1: u32 = 0xDEAD_BEEF;
    let mut h2: u32 = 0x41C6_CE57;
    for &ch in units {
        h1 = (h1 ^ u32::from(ch)).wrapping_mul(2_654_435_761);
        h2 = (h2 ^ u32::from(ch)).wrapping_mul(1_597_334_677);
    }
    h1 = (h1 ^ (h1 >> 16)).wrapping_mul(2_246_822_507)
        ^ (h2 ^ (h2 >> 13)).wrapping_mul(3_266_489_909);
    h2 = (h2 ^ (h2 >> 16)).wrapping_mul(2_246_822_507)
        ^ (h1 ^ (h1 >> 13)).wrapping_mul(3_266_489_909);
    format!("{:x}", (u64::from(h2 & 2_097_151) << 32) + u64::from(h1))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn formats_numbers_like_js() {
        let cases = [
            (1.0, "1"),
            (0.1, "0.1"),
            (1e21, "1e+21"),
            (123_456_789_012_345_680_000.0, "123456789012345680000"),
            (1e-7, "1e-7"),
            (0.000_001, "0.000001"),
            (1.5e-10, "1.5e-10"),
            (-2.5, "-2.5"),
            (-0.0, "0"),
        ];
        for (n, want) in cases {
            assert_eq!(number_to_string(n), want, "{n}");
        }
    }

    #[test]
    fn stringifies_like_js() {
        let text = json_stringify(
            &json!({ "a": "q\"\n\u{1}", "b": [1, null, js::undefined()], "c": js::undefined() }),
        );
        assert_eq!(
            String::from_utf16(&text.unwrap()).unwrap(),
            r#"{"a":"q\"\n\u0001","b":[1,null,null]}"#
        );
        assert_eq!(quote(&[0xD83D]), s("\"\\ud83d\""));
    }

    #[test]
    fn finds_suppressed_ranges() {
        let text = "a\n// x18n-disable-next-line\nt('x')\nb\n/* x18n-disable */ c /* x18n-enable */ x18n-disabled\n";
        let ranges = suppressed_ranges(text.into());
        assert_eq!(ranges.len(), 2);
        assert_eq!(ranges[0], json!({ "start": 28, "end": 34 }));
    }

    #[test]
    fn sorts_by_utf16_code_units() {
        // U+FFFD sorts after an emoji's high surrogate in JS, before it by code point.
        assert_eq!(by_code("\u{FFFD}", "😀"), Ordering::Greater);
    }
}
