//! The Rust port of `packages/core/src/contracts.ts`.
//!
//! `toWireDiagnostic` (takes a callback) and `envelope` (generic data) stay in TS.

#![forbid(unsafe_code)]

use serde_json::{Value, json};

use crate::js;

/// Port of `toWireRange` (`packages/core/src/contracts.ts:42`): 1-based lines and columns of an
/// offset range. Offsets and columns are UTF-16 code units, as in JS.
pub fn to_wire_range(text: Option<String>, start: f64, end: f64) -> Value {
    let units: Vec<u16> = text.unwrap_or_default().encode_utf16().collect();
    // `createLineIndex`: the offset after each `\n`.
    let mut starts = vec![0.0];
    starts.extend(
        units
            .iter()
            .enumerate()
            .filter(|(_, u)| **u == 10)
            .map(|(i, _)| (i + 1) as f64),
    );
    let position = |offset: f64| -> (f64, f64) {
        let (mut low, mut high) = (0usize, starts.len() - 1);
        while low < high {
            let mid = (low + high + 1) >> 1;
            if starts[mid] <= offset {
                low = mid
            } else {
                high = mid - 1
            }
        }
        (low as f64, offset - starts[low])
    };
    let (line, character) = position(start);
    let (end_line, end_character) = position(end);
    json!({
        "line": js::number(line + 1.0),
        "column": js::number(character + 1.0),
        "endLine": js::number(end_line + 1.0),
        "endColumn": js::number(end_character + 1.0),
        "start": js::number(start),
        "end": js::number(end),
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn maps_offsets_to_lines() {
        let range = to_wire_range(Some("ab\ncd".into()), 1.0, 4.0);
        assert_eq!(
            range,
            json!({ "line": 1, "column": 2, "endLine": 2, "endColumn": 2, "start": 1, "end": 4 })
        );
        let nan = to_wire_range(None, f64::NAN, 0.0);
        assert_eq!(nan["column"], js::number(f64::NAN));
    }
}
