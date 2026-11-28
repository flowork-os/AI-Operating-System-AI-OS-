//! The Rust port of `packages/core/src/schema.ts`.
//!
//! `validate` and the valibot schemas stay in TS: a schema is a JS object of functions, and
//! issue messages come from valibot.

#![forbid(unsafe_code)]

use serde_json::Value;

use crate::js;

/// Port of `isJsonObject` (`packages/core/src/schema.ts:25`): a plain object of JSON values.
pub fn is_json_object(value: Value) -> bool {
    is_object(&value)
}

fn is_object(value: &Value) -> bool {
    match value {
        // Markers stand for `undefined`, strings and numbers, which are not objects.
        Value::Object(o) if !is_marker(value) => o.values().all(is_json_value),
        _ => false,
    }
}

/// `isJsonValue`: null, string, number, boolean, or arrays and objects of those.
fn is_json_value(value: &Value) -> bool {
    match value {
        Value::Null | Value::String(_) | Value::Number(_) | Value::Bool(_) => true,
        Value::Array(items) => items.iter().all(is_json_value),
        Value::Object(_) => {
            js::string_units(value).is_some() || js::as_number(value).is_some() || is_object(value)
        }
    }
}

fn is_marker(value: &Value) -> bool {
    js::is_undefined(value) || js::string_units(value).is_some() || js::as_number(value).is_some()
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn checks_json_objects() {
        assert!(is_json_object(
            json!({ "a": [1, "x", null, { "b": true }] })
        ));
        assert!(!is_json_object(json!([])));
        assert!(!is_json_object(json!({ "a": js::undefined() })));
        assert!(!is_json_object(Value::Null));
    }
}
