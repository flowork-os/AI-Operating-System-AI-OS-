//! The Rust port of Ruby's `shellwords.rb`.
//! Translated from Ruby 3.3 `lib/shellwords.rb` (BSD-2-Clause or the Ruby license).

#![forbid(unsafe_code)]

use serde_json::Value;

/// Ruby's `\s`: ASCII whitespace.
fn is_space(c: char) -> bool {
    matches!(c, ' ' | '\t' | '\n' | '\r' | '\x0c' | '\x0b')
}

/// Ruby's class name of a JSON-shaped value, as `NoMethodError` messages print it.
fn ruby_class(v: &Value) -> &'static str {
    match v {
        Value::Null => "nil",
        Value::Bool(true) => "true",
        Value::Bool(false) => "false",
        Value::Number(n) if n.is_f64() => "an instance of Float",
        Value::Number(_) => "an instance of Integer",
        Value::String(_) => "an instance of String",
        Value::Array(_) => "an instance of Array",
        Value::Object(_) => "an instance of Hash",
    }
}

fn no_method(name: &str, v: &Value) -> String {
    format!(
        "NoMethodError: undefined method `{name}' for {}",
        ruby_class(v)
    )
}

/// Ruby's `Float#to_s`: shortest round-trip digits, exponent form outside 1e-4..1e15.
fn float_to_s(x: f64) -> String {
    if x.is_nan() {
        return "NaN".into();
    }
    if x.is_infinite() {
        return if x > 0.0 {
            "Infinity".into()
        } else {
            "-Infinity".into()
        };
    }
    let sci = format!("{x:e}"); // like "-1.2345e3"
    let (mantissa, exp) = sci.split_once('e').unwrap_or((&sci, "0"));
    let exp: i32 = exp.parse().unwrap_or(0);
    let negative = mantissa.starts_with('-');
    let digits: String = mantissa.chars().filter(char::is_ascii_digit).collect();
    let sign = if negative { "-" } else { "" };
    let decpt = exp + 1;
    if !(-3..=15).contains(&decpt) {
        let (first, rest) = digits.split_at(1);
        let rest = if rest.is_empty() { "0" } else { rest };
        return format!(
            "{sign}{first}.{rest}e{}{:02}",
            if exp < 0 { '-' } else { '+' },
            exp.abs()
        );
    }
    if decpt <= 0 {
        return format!(
            "{sign}0.{}{digits}",
            "0".repeat(decpt.unsigned_abs() as usize)
        );
    }
    let decpt = decpt as usize;
    if digits.len() <= decpt {
        format!("{sign}{digits}{}.0", "0".repeat(decpt - digits.len()))
    } else {
        format!("{sign}{}.{}", &digits[..decpt], &digits[decpt..])
    }
}

/// Ruby's `String#inspect` for the characters these inputs hold.
fn inspect_str(s: &str) -> String {
    let mut out = String::from("\"");
    for c in s.chars() {
        match c {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\t' => out.push_str("\\t"),
            '\r' => out.push_str("\\r"),
            '\x0c' => out.push_str("\\f"),
            '\x0b' => out.push_str("\\v"),
            '\x07' => out.push_str("\\a"),
            '\x08' => out.push_str("\\b"),
            '\x1b' => out.push_str("\\e"),
            '#' => out.push('#'),
            c if (c as u32) < 0x20 || c as u32 == 0x7f => {
                out.push_str(&format!("\\x{:02X}", c as u32))
            }
            c => out.push(c),
        }
    }
    out.push('"');
    // `#{`, `#$` and `#@` would interpolate: Ruby escapes the `#`.
    out.replace("#{", "\\#{")
        .replace("#$", "\\#$")
        .replace("#@", "\\#@")
}

/// A Ruby Symbol, which crosses as `{"$sym": name}`.
fn symbol(v: &Value) -> Option<&str> {
    match v {
        Value::Object(map) if map.len() == 1 => map.get("$sym")?.as_str(),
        _ => None,
    }
}

fn inspect(v: &Value) -> String {
    if let Some(name) = symbol(v) {
        let mut chars = name.chars();
        let plain = chars.next().is_some_and(|c| c.is_alphabetic() || c == '_')
            && name
                .trim_end_matches(['?', '!', '='])
                .chars()
                .all(|c| c.is_alphanumeric() || c == '_');
        return if plain {
            format!(":{name}")
        } else {
            format!(":{}", inspect_str(name))
        };
    }
    match v {
        Value::String(s) => inspect_str(s),
        Value::Array(items) => format!(
            "[{}]",
            items.iter().map(inspect).collect::<Vec<_>>().join(", ")
        ),
        Value::Object(map) => {
            if map.is_empty() {
                return "{}".into();
            }
            let pairs: Vec<String> = map
                .iter()
                .map(|(k, v)| format!("{}=>{}", inspect_str(k), inspect(v)))
                .collect();
            format!("{{{}}}", pairs.join(", "))
        }
        Value::Null => "nil".into(),
        other => to_s(other),
    }
}

/// Ruby's `to_s`.
fn to_s(v: &Value) -> String {
    if let Some(name) = symbol(v) {
        return name.to_string();
    }
    match v {
        Value::Null => String::new(),
        Value::Bool(b) => b.to_string(),
        Value::Number(n) => match n.as_i64() {
            Some(i) => i.to_string(),
            None => n.as_u64().map_or_else(
                || float_to_s(n.as_f64().unwrap_or(f64::NAN)),
                |u| u.to_string(),
            ),
        },
        Value::String(s) => s.clone(),
        other => inspect(other),
    }
}

/// Port of `shellsplit` (`shellwords.rb:91`): the scan regex, by hand.
pub fn shellsplit(line: Value) -> Result<Value, String> {
    let Value::String(line) = &line else {
        return Err(no_method("scan", &line));
    };
    let chars: Vec<char> = line.chars().collect();
    let mut words: Vec<Value> = Vec::new();
    let mut field = String::new();
    let mut i = 0;
    loop {
        while i < chars.len() && is_space(chars[i]) {
            i += 1;
        }
        if i >= chars.len() {
            break;
        }
        let c = chars[i];
        if !is_space(c) && c != '\\' && c != '\'' && c != '"' {
            while i < chars.len() && !matches!(chars[i], '\\' | '\'' | '"') && !is_space(chars[i]) {
                field.push(chars[i]);
                i += 1;
            }
        } else if c == '\'' && chars[i + 1..].contains(&'\'') {
            let end = i + 1 + chars[i + 1..].iter().position(|&x| x == '\'').unwrap_or(0);
            field.extend(&chars[i + 1..end]);
            i = end + 1;
        } else if c == '"'
            && let Some(end) = closing_quote(&chars, i + 1)
        {
            let mut j = i + 1;
            while j < end {
                if chars[j] == '\\'
                    && j + 1 < end
                    && matches!(chars[j + 1], '$' | '`' | '"' | '\\' | '\n')
                {
                    field.push(chars[j + 1]);
                    j += 2;
                } else {
                    field.push(chars[j]);
                    j += 1;
                }
            }
            i = end + 1;
        } else if c == '\\' {
            // `\\.?` with /m, then `gsub(/\\(.)/, '\1')`, whose `.` skips newlines.
            match chars.get(i + 1) {
                Some('\n') => {
                    field.push_str("\\\n");
                    i += 2;
                }
                Some(&next) => {
                    field.push(next);
                    i += 2;
                }
                None => {
                    field.push('\\');
                    i += 1;
                }
            }
        } else {
            return Err(format!(
                "ArgumentError: Unmatched quote: {}",
                inspect_str(line)
            ));
        }
        // `(\s|\z)?`: one separator, or the end, closes the field.
        if i >= chars.len() || is_space(chars[i]) {
            if i < chars.len() {
                i += 1;
            }
            words.push(Value::String(std::mem::take(&mut field)));
        }
    }
    Ok(Value::Array(words))
}

/// The index of the `"` closing a double-quoted string that starts at `from`.
fn closing_quote(chars: &[char], from: usize) -> Option<usize> {
    let mut j = from;
    while j < chars.len() {
        match chars[j] {
            '"' => return Some(j),
            '\\' if j + 1 < chars.len() => j += 2,
            '\\' => return None,
            _ => j += 1,
        }
    }
    None
}

/// Port of `shellescape` (`shellwords.rb:135`).
pub fn shellescape(str: Value) -> Result<Value, String> {
    let text = to_s(&str);
    if text.is_empty() {
        return Ok(Value::String("''".into()));
    }
    let mut out = String::new();
    for c in text.chars() {
        if c == '\n' {
            out.push_str("'\n'");
        } else if c.is_ascii_alphanumeric() || "_-.,:+/@".contains(c) {
            out.push(c);
        } else {
            out.push('\\');
            out.push(c);
        }
    }
    Ok(Value::String(out))
}

/// Port of `shelljoin` (`shellwords.rb:167`).
pub fn shelljoin(array: Value) -> Result<Value, String> {
    let items: Vec<Value> = match &array {
        Value::Array(items) => items.clone(),
        // `Hash#map` yields `[key, value]` pairs.
        Value::Object(map) => map
            .iter()
            .map(|(k, v)| Value::Array(vec![Value::String(k.clone()), v.clone()]))
            .collect(),
        other => return Err(no_method("map", other)),
    };
    let escaped: Result<Vec<String>, String> = items
        .into_iter()
        .map(|v| shellescape(v).map(|e| e.as_str().unwrap_or_default().to_string()))
        .collect();
    Ok(Value::String(escaped?.join(" ")))
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn symbols_are_their_names() {
        // `Shellwords.shellescape(:sym)` is "sym"; `[:a].to_s` is "[:a]".
        assert_eq!(shellescape(json!({ "$sym": "sym" })).unwrap(), json!("sym"));
        assert_eq!(
            inspect(&json!([{ "$sym": "a" }, { "$sym": "b c" }])),
            "[:a, :\"b c\"]"
        );
    }
}
