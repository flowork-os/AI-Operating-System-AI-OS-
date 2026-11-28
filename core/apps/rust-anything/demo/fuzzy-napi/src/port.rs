//! The Rust port of `packages/core/src/fuzzy.ts`.

#![forbid(unsafe_code)]

use crate::utf16::{index_of, units};

/// Port of `fuzzyScore` (`packages/core/src/fuzzy.ts:2`).
///
/// Subsequence match score of `query` in `text`, case-insensitive; higher is better, -1 when it
/// does not match. Substring hits rank above every subsequence. Positions are UTF-16 code
/// units, as in JS, so scores match for non-ASCII text too.
pub fn fuzzy_score(query: String, text: String) -> f64 {
    let q = query.to_lowercase();
    let s = units(&text.to_lowercase());
    if let Some(exact) = index_of(&s, &units(&q), 0) {
        return 2000.0 - exact.min(1000) as f64;
    }
    let mut score = 0.0;
    // `at` is the UTF-16 index of the last match; JS starts it at -1.
    let mut next_from = 0;
    let mut previous: Option<usize> = None;
    // `for (const char of q)` walks code points, so astral characters stay whole.
    for c in q.chars() {
        let mut buf = [0u16; 2];
        let Some(next) = index_of(&s, c.encode_utf16(&mut buf), next_from) else {
            return -1.0;
        };
        let adjacent = previous.map_or(next == 0, |at| next == at + 1);
        score += if adjacent { 2.0 } else { 1.0 };
        previous = Some(next);
        next_from = next + 1;
    }
    score
}

#[cfg(test)]
mod tests {
    use super::fuzzy_score;

    #[test]
    fn scores_like_js() {
        assert_eq!(fuzzy_score("b".into(), "abc".into()), 1999.0);
        assert_eq!(fuzzy_score("ac".into(), "abc".into()), 3.0);
        assert_eq!(fuzzy_score("x".into(), "abc".into()), -1.0);
        // "😀" is two UTF-16 units: the substring starts at index 3 in JS.
        assert_eq!(fuzzy_score("b😀".into(), "a😀b😀c".into()), 1997.0);
    }
}
