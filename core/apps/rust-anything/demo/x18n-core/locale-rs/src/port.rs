//! The Rust port of `packages/core/src/locale.ts`.
//!
//! `parseLocaleInfo` stays in TS: it reads CLDR data through `Intl`, which differs between JS
//! engines and versions; a Rust copy of that data would drift from the one users see.

#![forbid(unsafe_code)]

use serde_json::{Map, Value};

use crate::js;

const NOT_OBJECT: &str = "TypeError: Cannot convert undefined or null to object";

/// Port of `resolveFallbacks` (`packages/core/src/locale.ts:37`): the fallback of each locale.
pub fn resolve_fallbacks(
    setting: Value,
    locales: Vec<String>,
    source_locale: String,
) -> Result<Value, String> {
    if setting != Value::String("auto".into()) {
        let mut out = Map::new();
        for (locale, fallback) in object_entries(&setting)? {
            if locale != source_locale {
                out.insert(locale, fallback);
            }
        }
        return Ok(Value::Object(out));
    }
    let mut fallbacks = Map::new();
    for locale in &locales {
        if *locale == source_locale {
            continue;
        }
        // `locale.search(/[-_][^-_]*$/)`: the last separator. Separators are ASCII, so byte
        // positions cut where JS's UTF-16 positions do.
        let mut cut = last_separator(locale);
        while let Some(at) = cut.filter(|&at| at > 0) {
            let parent = &locale[..at];
            if let Some(found) = locales.iter().find(|code| code.as_str() == parent) {
                fallbacks.insert(locale.clone(), Value::String(found.clone()));
                break;
            }
            cut = last_separator(parent);
        }
    }
    Ok(Value::Object(fallbacks))
}

/// Port of `fallbackChain` (`packages/core/src/locale.ts:56`): nearest first, stops at a cycle.
///
/// Returns JSON values: JS returns whatever values the map holds, strings or not.
pub fn fallback_chain(fallbacks: Value, locale: String) -> Result<Vec<Value>, String> {
    let mut chain: Vec<Value> = Vec::new();
    let mut next = get(&fallbacks, &locale)?;
    while let Some(value) = next {
        if value == Value::String(locale.clone()) || chain.contains(&value) {
            break;
        }
        let key = property_key(&value);
        chain.push(value);
        next = get(&fallbacks, &key)?;
    }
    Ok(chain)
}

/// Port of `localeSpellingKey` (`packages/core/src/locale.ts:131`): `zh_CN` and `zh-cn` agree.
pub fn locale_spelling_key(code: String) -> String {
    code.replace('_', "-").to_lowercase()
}

fn last_separator(s: &str) -> Option<usize> {
    s.rfind(['-', '_'])
}

/// `value[key]` for a JSON value; `None` is `undefined`.
fn get(value: &Value, key: &str) -> Result<Option<Value>, String> {
    if value.is_null() || js::is_undefined(value) {
        return Err(format!(
            "TypeError: Cannot read properties of null (reading '{key}')"
        ));
    }
    if let Some(units) = js::string_units(value) {
        return Ok(match key {
            "length" => Some(Value::from(units.len())),
            _ => index(key)
                .and_then(|i| units.get(i))
                .map(|u| js::utf16_string(&[*u])),
        });
    }
    Ok(match value {
        Value::Object(o) => o.get(key).filter(|v| !js::is_undefined(v)).cloned(),
        Value::Array(items) => match key {
            "length" => Some(Value::from(items.len())),
            _ => index(key).and_then(|i| items.get(i)).cloned(),
        },
        _ => None,
    })
}

/// A canonical array index (`"0"`, `"12"`, not `"01"`).
fn index(key: &str) -> Option<usize> {
    let i: usize = key.parse().ok()?;
    (i.to_string() == key).then_some(i)
}

/// `Object.entries(value)`.
fn object_entries(value: &Value) -> Result<Vec<(String, Value)>, String> {
    if value.is_null() || js::is_undefined(value) {
        return Err(NOT_OBJECT.into());
    }
    if let Some(units) = js::string_units(value) {
        return Ok(units
            .iter()
            .enumerate()
            .map(|(i, u)| (i.to_string(), js::utf16_string(&[*u])))
            .collect());
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

/// JS `ToPropertyKey`.
fn property_key(value: &Value) -> String {
    if js::is_undefined(value) {
        return "undefined".into();
    }
    if let Some(units) = js::string_units(value) {
        return String::from_utf16_lossy(&units);
    }
    match value {
        Value::Null => "null".into(),
        Value::Bool(b) => b.to_string(),
        Value::Number(n) => {
            let f = n.as_f64().unwrap_or(f64::NAN);
            if f == f.trunc() && f.abs() < 1e21 {
                format!("{f:.0}").replace("-0", "0")
            } else {
                f.to_string()
            }
        }
        Value::String(s) => s.clone(),
        Value::Array(items) => items
            .iter()
            .map(|v| {
                if v.is_null() || js::is_undefined(v) {
                    String::new()
                } else {
                    property_key(v)
                }
            })
            .collect::<Vec<_>>()
            .join(","),
        Value::Object(_) => "[object Object]".into(),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn resolves_fallbacks() {
        let locales: Vec<String> = ["en", "pt", "pt-BR", "zh-Hant-TW", "zh"]
            .map(String::from)
            .to_vec();
        assert_eq!(
            resolve_fallbacks(json!("auto"), locales, "en".into()),
            Ok(json!({ "pt-BR": "pt", "zh-Hant-TW": "zh" }))
        );
        assert_eq!(
            resolve_fallbacks(json!({ "en": "x", "de": "en" }), vec![], "en".into()),
            Ok(json!({ "de": "en" }))
        );
        assert!(resolve_fallbacks(Value::Null, vec![], "en".into()).is_err());
    }

    #[test]
    fn follows_chains() {
        let map = json!({ "a": "b", "b": "c", "c": "a" });
        assert_eq!(
            fallback_chain(map, "a".into()),
            Ok(vec![json!("b"), json!("c")])
        );
        assert_eq!(locale_spelling_key("zh_CN".into()), "zh-cn");
    }
}
