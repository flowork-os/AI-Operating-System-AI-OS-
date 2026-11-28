//! The Rust port of `packages/core/src/keys.ts`.
//!
//! `globToRegExp`, `keyMatcher` and `pathMatcher` stay in TS: they return a RegExp or a function.

#![forbid(unsafe_code)]

use serde_json::{Value, json};

use crate::js;
use crate::utf16;

/// Port of `joinKey` (`packages/core/src/keys.ts:4`): `ns:a.b.c`, or `a.b.c` without namespace.
pub fn join_key(namespace: Option<String>, path: Vec<String>) -> String {
    let dotted = path.join(".");
    match namespace {
        None => dotted,
        Some(ns) => format!("{ns}:{dotted}"),
    }
}

/// Port of `splitKey` (`packages/core/src/keys.ts:12`). Without `namespaced`, `:` is part of the key.
pub fn split_key(key: String, namespaced: Option<bool>) -> Value {
    // `:` is ASCII: its UTF-8 position splits the string where JS's UTF-16 index does.
    let index = if namespaced.unwrap_or(true) {
        key.find(':')
    } else {
        None
    };
    let (namespace, rest) = match index {
        Some(i) => (Value::String(key[..i].to_string()), &key[i + 1..]),
        None => (js::undefined(), key.as_str()),
    };
    let path: Vec<&str> = if rest.is_empty() {
        Vec::new()
    } else {
        rest.split('.').collect()
    };
    json!({ "namespace": namespace, "path": path })
}

/// Port of `isKeyUnder` (`packages/core/src/keys.ts:31`): `a.b` is under `a`.
pub fn is_key_under(key: String, prefix: String) -> bool {
    if key == prefix {
        return true;
    }
    let sep = if prefix.ends_with(':') { "" } else { "." };
    key.starts_with(&format!("{prefix}{sep}"))
}

/// Port of `replaceKeyPrefix` (`packages/core/src/keys.ts:40`).
///
/// Returns UTF-16 code units: when `from` is not really a prefix, JS `slice` can cut a
/// surrogate pair in half, and that half survives in JS but not in a Rust `String`.
/// `index.cjs` turns the units back into the exact JS string.
pub fn replace_key_prefix(key: String, from: String, to: String) -> Vec<u16> {
    if key == from {
        return utf16::units(&to);
    }
    // `key.slice(from.length)`: both lengths are UTF-16 code units in JS.
    let units = utf16::units(&key);
    let skip = from.encode_utf16().count().min(units.len());
    let mut out = utf16::units(&to);
    out.extend_from_slice(&units[skip..]);
    out
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn keys_round_trip() {
        assert_eq!(
            join_key(Some("ns".into()), vec!["a".into(), "b".into()]),
            "ns:a.b"
        );
        assert_eq!(
            split_key("ns:a.b".into(), None),
            json!({ "namespace": "ns", "path": ["a", "b"] })
        );
        assert_eq!(split_key("a:b".into(), Some(false))["path"], json!(["a:b"]));
        assert!(js::is_undefined(
            &split_key("a.b".into(), None)["namespace"]
        ));
        assert!(is_key_under("a.b".into(), "a".into()));
        assert!(!is_key_under("ab".into(), "a".into()));
        assert!(is_key_under("ns:a".into(), "ns:".into()));
        assert_eq!(
            String::from_utf16(&replace_key_prefix("😀.x".into(), "😀".into(), "y".into())).ok(),
            Some("y.x".to_string())
        );
        // Cutting inside "😀" keeps the lone low surrogate, as JS does.
        assert_eq!(
            replace_key_prefix("😀x".into(), "a".into(), "".into()),
            [0xDE00, u16::from(b'x')]
        );
    }
}
