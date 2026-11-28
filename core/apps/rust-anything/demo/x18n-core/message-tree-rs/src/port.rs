//! The Rust port of `packages/core/src/message-tree.ts`.
//!
//! `walkLeaves` (a generator) and `sortTree` (takes a compare callback) stay in TS. Trees are
//! JSON objects in JS key order; deletes use `shift_remove` so the other keys keep their order,
//! as JS `delete` does. Invalid input returns an error where JS throws a TypeError.

#![forbid(unsafe_code)]

use serde_json::{Map, Value};

use crate::js;

type Tree = Map<String, Value>;

const NOT_OBJECT: &str = "TypeError: Cannot convert undefined or null to object";
const NO_PATH: &str = "TypeError: path.slice is not a function";

/// Port of `isMessageLeaf` (`packages/core/src/message-tree.ts:4`).
pub fn is_message_leaf(value: Value) -> bool {
    is_leaf(&value)
}

/// Port of `isMessageTree` (`packages/core/src/message-tree.ts:9`).
pub fn is_message_tree(value: Value) -> bool {
    is_tree(&value)
}

/// Port of `pathId` (`packages/core/src/message-tree.ts:16`).
pub fn path_id(path: Vec<String>) -> String {
    path.join("\u{0}")
}

/// Port of `applyMessageOps` (`packages/core/src/message-tree.ts:76`): ops on a copy; emptied parents go.
pub fn apply_message_ops(tree: Value, ops: Vec<Value>) -> Result<Value, String> {
    let mut out = clone_tree(&tree)?;
    for op in &ops {
        // `op.type` throws for null and undefined; other non-objects have no `path` and throw later.
        let op = match op {
            Value::Object(o) if !is_marker(op) => o,
            _ => {
                return Err(
                    "TypeError: Cannot read properties of undefined (reading 'path')".into(),
                );
            }
        };
        let path = path_segments(op.get("path"))?;
        if op.get("type") == Some(&Value::String("set".into())) {
            let value = op.get("value").cloned().unwrap_or_else(js::undefined);
            set_in(&mut out, &path, value);
        } else {
            delete_in(&mut out, &path);
        }
    }
    Ok(Value::Object(out))
}

/// Port of `buildTree` (`packages/core/src/message-tree.ts:100`): a tree from `{ path, value }` leaves.
pub fn build_tree(leaves: Value) -> Result<Value, String> {
    let items: Vec<Value> = match &leaves {
        Value::Array(items) => items.clone(),
        // A string iterates its UTF-16 units; each unit has no `path` and throws below.
        _ if js::string_units(&leaves).is_some() => {
            let units = js::string_units(&leaves).unwrap_or_default();
            units.iter().map(|u| js::utf16_string(&[*u])).collect()
        }
        _ => return Err("TypeError: leaves is not iterable".into()),
    };
    let mut out = Tree::new();
    for leaf in &items {
        let leaf = match leaf {
            Value::Object(o) if !is_marker(leaf) => o,
            _ => return Err(NO_PATH.into()),
        };
        let path = path_segments(leaf.get("path"))?;
        let value = leaf.get("value").cloned().unwrap_or_else(js::undefined);
        set_in(&mut out, &path, value);
    }
    Ok(Value::Object(out))
}

/// `{"$undefined": true}` or `{"$utf16": [...]}`: values that are not objects in JS.
fn is_marker(value: &Value) -> bool {
    js::is_undefined(value) || (value.is_object() && js::string_units(value).is_some())
}

fn is_leaf(value: &Value) -> bool {
    match value {
        Value::Null | Value::Bool(_) | Value::Number(_) | Value::String(_) => true,
        // A marked string is a string; `undefined` is not a leaf.
        Value::Object(_) => !js::is_undefined(value) && js::string_units(value).is_some(),
        Value::Array(_) => false,
    }
}

fn is_tree(value: &Value) -> bool {
    match value {
        Value::Object(o) if !is_marker(value) => {
            o.values().all(|child| is_leaf(child) || is_tree(child))
        }
        _ => false,
    }
}

/// `Object.entries(value)`.
fn object_entries(value: &Value) -> Result<Vec<(String, Value)>, String> {
    if js::is_undefined(value) || value.is_null() {
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
        Value::Array(items) => items
            .iter()
            .enumerate()
            .map(|(i, v)| (i.to_string(), v.clone()))
            .collect(),
        Value::Object(o) => o.iter().map(|(k, v)| (k.clone(), v.clone())).collect(),
        _ => Vec::new(),
    })
}

fn clone_tree(tree: &Value) -> Result<Tree, String> {
    let mut out = Tree::new();
    for (segment, child) in object_entries(tree)? {
        let value = if is_leaf(&child) {
            child
        } else {
            Value::Object(clone_tree(&child)?)
        };
        out.insert(segment, value);
    }
    Ok(out)
}

/// The segments of a `path` argument: an array, or a string (JS indexes its characters).
fn path_segments(path: Option<&Value>) -> Result<Vec<String>, String> {
    let path = path.filter(|p| !js::is_undefined(p)).ok_or(NO_PATH)?;
    if let Some(units) = js::string_units(path) {
        return Ok(units
            .iter()
            .map(|u| String::from_utf16_lossy(&[*u]))
            .collect());
    }
    match path {
        Value::Array(items) => Ok(items.iter().map(property_key).collect()),
        _ => Err(NO_PATH.into()),
    }
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

/// `setIn`: walks `path`, replacing missing children and leaves with objects.
fn set_in(tree: &mut Tree, path: &[String], value: Value) {
    let (parents, last) = match path.split_last() {
        Some((last, parents)) => (parents, last.clone()),
        // `path.at(-1)` of an empty path is `undefined`, a property named "undefined".
        None => (path, "undefined".to_string()),
    };
    let mut node = tree;
    for segment in parents {
        let replace = match node.get(segment) {
            None => true,
            Some(child) => js::is_undefined(child) || is_leaf(child) || !child.is_object(),
        };
        if replace {
            node.insert(segment.clone(), Value::Object(Tree::new()));
        }
        node = match node.get_mut(segment) {
            Some(Value::Object(child)) => child,
            _ => return,
        };
    }
    node.insert(last, value);
}

/// `deleteIn`: removes the leaf, then every parent the removal left empty.
fn delete_in(tree: &mut Tree, path: &[String]) {
    let Some((last, parents)) = path.split_last() else {
        tree.shift_remove("undefined");
        return;
    };
    {
        let mut node: &Tree = tree;
        for segment in parents {
            match node.get(segment) {
                Some(child @ Value::Object(o)) if !is_marker(child) => node = o,
                _ => return,
            }
        }
    }
    if let Some(node) = object_at(tree, parents) {
        node.shift_remove(last);
    }
    for depth in (1..=parents.len()).rev() {
        if object_at(tree, &parents[..depth]).is_none_or(|p| !p.is_empty()) {
            break;
        }
        if let Some(parent) = object_at(tree, &parents[..depth - 1]) {
            parent.shift_remove(&parents[depth - 1]);
        }
    }
}

fn object_at<'t>(tree: &'t mut Tree, path: &[String]) -> Option<&'t mut Tree> {
    let mut node = tree;
    for segment in path {
        node = node.get_mut(segment)?.as_object_mut()?;
    }
    Some(node)
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn applies_ops_like_js() {
        let tree = json!({ "a": { "b": "1", "c": "2" }, "d": "3" });
        let ops = vec![
            json!({ "type": "delete", "path": ["a", "b"] }),
            json!({ "type": "delete", "path": ["a", "c"] }),
            json!({ "type": "set", "path": ["x", "y"], "value": null }),
        ];
        // `a` is left empty and removed; `d` keeps its place.
        assert_eq!(
            apply_message_ops(tree, ops),
            Ok(json!({ "d": "3", "x": { "y": null } }))
        );
        assert!(apply_message_ops(Value::Null, vec![]).is_err());
        assert!(is_message_tree(json!({ "a": { "b": 1 } })));
        assert!(!is_message_tree(json!({ "a": [1] })));
        assert!(!is_message_leaf(js::undefined()));
    }

    #[test]
    fn builds_trees() {
        let leaves =
            json!([{ "path": ["a", "b"], "value": "x" }, { "path": ["a", "c"], "value": 1 }]);
        assert_eq!(build_tree(leaves), Ok(json!({ "a": { "b": "x", "c": 1 } })));
        assert_eq!(build_tree(json!("")), Ok(json!({})));
        assert!(build_tree(json!({})).is_err());
    }
}
