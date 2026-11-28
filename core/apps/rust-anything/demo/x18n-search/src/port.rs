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

/// The keys `fuzzy_score` searches, prepared once: lowercased UTF-16 in one buffer, and a mask
/// of the code units each key holds, so most keys that cannot match are rejected without being
/// read. `run` gives exactly `fuzzy_score(query, key)` for every key, on all cores.
pub struct FuzzyScoreIndex {
    units: Vec<u16>,
    /// Each key's range in `units`, and its mask.
    keys: Vec<(u32, u32, u64)>,
    /// The same text as bytes where a key is ASCII (most keys): searched byte by byte.
    /// For ASCII, byte positions are UTF-16 positions, so scores are the same.
    bytes: Vec<u8>,
    ascii: Vec<bool>,
    /// Per character of [`ALPHABET`], each key's first position of it (column by column):
    /// a one-letter query is one column. [`FAR`] marks a position past 253, [`NONE`] absence.
    first: Vec<u8>,
    /// The last ranked query (lowercased) and the keys it matched, in key order. A key that
    /// does not match a query matches no query that extends it, so typing `se` after `s` only
    /// rescores the keys `s` matched.
    last: std::sync::Mutex<Option<LastQuery>>,
}

/// A ranked query, lowercased, and the keys it matched.
type LastQuery = (Vec<u16>, std::sync::Arc<Vec<u32>>);

/// The characters whose first positions are kept: what one-letter queries are made of.
const ALPHABET: &[u8] = b"abcdefghijklmnopqrstuvwxyz0123456789._-/";
const FAR: u8 = 254;
const NONE: u8 = 255;

/// One bit per code unit (modulo 64): a key lacking any bit of the query cannot match it.
fn mask(units: &[u16]) -> u64 {
    units.iter().fold(0, |m, u| m | 1 << (u % 64))
}

impl FuzzyScoreIndex {
    pub fn new(items: Vec<String>) -> Self {
        let mut all = Vec::new();
        let mut keys = Vec::with_capacity(items.len());
        for item in &items {
            let start = all.len();
            all.extend(units(&item.to_lowercase()));
            let at = |n: usize| u32::try_from(n).unwrap_or(u32::MAX);
            keys.push((at(start), at(all.len()), mask(&all[start..])));
        }
        let ascii = keys
            .iter()
            .map(|&(a, b, _)| all[a as usize..b as usize].iter().all(|u| *u < 0x80))
            .collect();
        let bytes = all.iter().map(|&u| u8::try_from(u).unwrap_or(0)).collect();
        let mut first = vec![NONE; ALPHABET.len() * keys.len()];
        for (k, &(a, b, _)) in keys.iter().enumerate() {
            for (pos, &u) in all[a as usize..b as usize].iter().enumerate() {
                if let Some(c) = ALPHABET.iter().position(|&x| u16::from(x) == u) {
                    let slot = &mut first[c * keys.len() + k];
                    if *slot == NONE {
                        *slot = u8::try_from(pos).unwrap_or(FAR).min(FAR);
                    }
                }
            }
        }
        Self {
            units: all,
            keys,
            bytes,
            ascii,
            first,
            last: std::sync::Mutex::new(None),
        }
    }

    /// [`Self::rank`] for a one-letter query: its score is `2000 - first position`, read from
    /// the letter's column, and the order is by position, found in one pass.
    fn rank_letter(&self, q: Vec<u16>, c: usize, min: f64) -> Vec<u32> {
        let n = self.keys.len();
        let column = &self.first[c * n..(c + 1) * n];
        let mut matched = Vec::new();
        let mut by_position: Vec<Vec<u32>> = vec![Vec::new(); usize::from(FAR) + 1];
        for (i, &pos) in (0u32..).zip(column) {
            if pos != NONE {
                matched.push(i);
                by_position[usize::from(pos)].push(i);
            }
        }
        if let Ok(mut last) = self.last.lock() {
            *last = Some((q, std::sync::Arc::new(matched)));
        }
        let mut out = Vec::new();
        for (pos, keys) in by_position.iter().enumerate().take(usize::from(FAR)) {
            if 2000.0 - pos as f64 >= min {
                out.extend_from_slice(keys);
            }
        }
        // Positions past 253: score those keys exactly, then order them.
        let far: Vec<(f64, u32)> = by_position[usize::from(FAR)]
            .iter()
            .map(|&i| {
                let (a, b, _) = self.keys[i as usize];
                let at = self.units[a as usize..b as usize]
                    .iter()
                    .position(|&u| u16::from(ALPHABET[c]) == u);
                (2000.0 - at.unwrap_or(0).min(1000) as f64, i)
            })
            .filter(|(s, _)| *s >= min)
            .collect();
        out.extend(order(far));
        out
    }

    /// The indexes of the keys scoring at least `min`, highest first, ties in key order: the
    /// order of `keys.map(fuzzyScore).filter(...).sort(...)` in JS.
    pub fn rank(&self, query: String, min: f64) -> Result<Vec<u32>, String> {
        use rayon::prelude::*;
        let lower = query.to_lowercase();
        let q = units(&lower);
        let chars: Vec<Vec<u16>> = lower
            .chars()
            .map(|c| c.encode_utf16(&mut [0; 2]).to_vec())
            .collect();
        if let [unit] = q[..]
            && let Some(c) = ALPHABET.iter().position(|&x| u16::from(x) == unit)
        {
            return Ok(self.rank_letter(q, c, min));
        }
        let need = mask(&q);
        let ascii_query = lower.is_ascii().then_some(lower.as_bytes());
        // The query's first character, when the table has it: its first position in a key is
        // where both searches start.
        let first_column = q
            .first()
            .and_then(|&u| ALPHABET.iter().position(|&x| u16::from(x) == u));
        let narrowed = self.last.lock().ok().and_then(|last| {
            last.as_ref()
                .filter(|(prev, _)| q.starts_with(prev))
                .map(|(_, hits)| hits.clone())
        });
        let score_of = |i: u32| {
            let (a, b, m) = self.keys[i as usize];
            if m & need != need {
                return -1.0;
            }
            match &ascii_query {
                Some(query) if self.ascii[i as usize] => {
                    let start = match first_column {
                        Some(c) => match self.first[c * self.keys.len() + i as usize] {
                            NONE => return -1.0,
                            FAR => 0,
                            pos => usize::from(pos),
                        },
                        None => 0,
                    };
                    score_ascii(query, &self.bytes[a as usize..b as usize], start)
                }
                _ => score(&q, &chars, &self.units[a as usize..b as usize]),
            }
        };
        let n = u32::try_from(self.keys.len()).unwrap_or(u32::MAX);
        let matched: Vec<(f64, u32)> = match &narrowed {
            Some(hits) => hits
                .par_iter()
                .with_min_len(1024)
                .map(|&i| (score_of(i), i))
                .filter(|(s, _)| *s >= 0.0)
                .collect(),
            None => (0..n)
                .into_par_iter()
                .with_min_len(1024)
                .map(|i| (score_of(i), i))
                .filter(|(s, _)| *s >= 0.0)
                .collect(),
        };
        if let Ok(mut last) = self.last.lock() {
            *last = Some((
                q,
                std::sync::Arc::new(matched.iter().map(|&(_, i)| i).collect()),
            ));
        }
        let hits: Vec<(f64, u32)> = matched.into_iter().filter(|(s, _)| *s >= min).collect();
        Ok(order(hits))
    }

    pub fn run(&self, query: String) -> Result<Vec<f64>, String> {
        use rayon::prelude::*;
        let lower = query.to_lowercase();
        let q = units(&lower);
        // `for (const char of q)` walks code points: each is one or two code units.
        let chars: Vec<Vec<u16>> = lower
            .chars()
            .map(|c| c.encode_utf16(&mut [0; 2]).to_vec())
            .collect();
        let need = mask(&q);
        Ok(self
            .keys
            .par_iter()
            .with_min_len(1024)
            .map(|&(a, b, m)| {
                if m & need == need {
                    score(&q, &chars, &self.units[a as usize..b as usize])
                } else {
                    -1.0
                }
            })
            .collect())
    }
}

/// Hits (in key order) by score, highest first, ties in key order. Scores are whole numbers up to
/// 2000 (substring hits 1000-2000, subsequences two per character), so a counting sort orders
/// them in one pass; any other score falls back to a comparison sort.
fn order(hits: Vec<(f64, u32)>) -> Vec<u32> {
    const TOP: usize = 2000;
    let bucket =
        |s: f64| (s.fract() == 0.0 && (0.0..=TOP as f64).contains(&s)).then(|| TOP - s as usize);
    if hits.iter().all(|(s, _)| bucket(*s).is_some()) {
        let mut starts = vec![0usize; TOP + 2];
        for (s, _) in &hits {
            starts[bucket(*s).unwrap_or(0) + 1] += 1;
        }
        for b in 1..starts.len() {
            starts[b] += starts[b - 1];
        }
        let mut out = vec![0u32; hits.len()];
        for (s, i) in hits {
            let at = &mut starts[bucket(s).unwrap_or(0)];
            out[*at] = i;
            *at += 1;
        }
        return out;
    }
    use rayon::prelude::*;
    let mut hits = hits;
    // Ties keep key order, as JS's stable sort does: compare indexes after scores.
    hits.par_sort_unstable_by(|a, b| b.0.total_cmp(&a.0).then(a.1.cmp(&b.1)));
    hits.into_iter().map(|(_, i)| i).collect()
}

/// The first index at or after `from` where `needle` starts in `hay`.
fn find(hay: &[u16], needle: &[u16], from: usize) -> Option<usize> {
    let (&first, rest) = needle.split_first()?;
    let last = hay.len().checked_sub(needle.len())?;
    (from..=last).find(|&i| hay[i] == first && hay[i + 1..i + needle.len()] == *rest)
}

/// The first position of `q` in `s`, from `from`. Keys are short: plain loops beat library
/// calls (`memchr`, `memcmp`) set up for long text.
fn find_ascii(s: &[u8], q: &[u8], from: usize) -> Option<usize> {
    let Some((&head, rest)) = q.split_first() else {
        return Some(0);
    };
    let last = s.len().checked_sub(q.len())?;
    (from..=last).find(|&i| s[i] == head && rest.iter().zip(&s[i + 1..]).all(|(a, b)| a == b))
}

/// `fuzzy_score` on a lowercased ASCII query and an ASCII key, the search starting at `start`:
/// the key's first position of the query's first character, which nothing can precede.
fn score_ascii(q: &[u8], s: &[u8], start: usize) -> f64 {
    if let Some(exact) = find_ascii(s, q, start) {
        return 2000.0 - exact.min(1000) as f64;
    }
    let mut score = 0.0;
    let mut next_from = start;
    let mut previous: Option<usize> = None;
    for &c in q {
        let Some(next) = s
            .get(next_from..)
            .and_then(|rest| rest.iter().position(|&b| b == c))
            .map(|i| i + next_from)
        else {
            return -1.0;
        };
        let adjacent = previous.map_or(next == 0, |at| next == at + 1);
        score += if adjacent { 2.0 } else { 1.0 };
        previous = Some(next);
        next_from = next + 1;
    }
    score
}

/// `fuzzy_score` on a lowercased query and key.
fn score(q: &[u16], chars: &[Vec<u16>], s: &[u16]) -> f64 {
    let exact = if q.is_empty() { Some(0) } else { find(s, q, 0) };
    if let Some(exact) = exact {
        return 2000.0 - exact.min(1000) as f64;
    }
    let mut score = 0.0;
    let mut next_from = 0;
    let mut previous: Option<usize> = None;
    for c in chars {
        let Some(next) = find(s, c, next_from) else {
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

    #[test]
    fn index_scores_like_the_port() {
        let keys = ["abc", "a😀b😀c", "Settings.Title", "", "ΣΊΣΥΦΟΣ", "x.y.z"];
        let index = super::FuzzyScoreIndex::new(keys.iter().map(|k| k.to_string()).collect());
        for q in ["", "b", "ac", "x", "b😀", "SET", "st", "σ", "zz", "😀c"] {
            let want: Vec<f64> = keys
                .iter()
                .map(|k| fuzzy_score(q.into(), k.to_string()))
                .collect();
            assert_eq!(index.run(q.into()).unwrap(), want, "{q}");
        }
        // Rankings, narrowed or by letter, equal ranking `fuzzy_score` over every key in JS order.
        let long = format!("{}s{}", "x".repeat(300), "t".repeat(5));
        let keys: Vec<String> = [
            "abc",
            "a😀b😀c",
            "Settings.Title",
            "",
            "ΣΊΣΥΦΟΣ",
            "x.y.z",
            &long,
            "set-up/st",
        ]
        .iter()
        .map(|k| k.to_string())
        .collect();
        let index = super::FuzzyScoreIndex::new(keys.clone());
        let reference = |q: &str, min: f64| {
            let mut hits: Vec<(f64, u32)> = (0u32..)
                .zip(&keys)
                .map(|(i, k)| (fuzzy_score(q.into(), k.clone()), i))
                .filter(|(s, _)| *s >= 0.0 && *s >= min)
                .collect();
            hits.sort_by(|a, b| b.0.total_cmp(&a.0));
            hits.into_iter().map(|(_, i)| i).collect::<Vec<u32>>()
        };
        for q in [
            "s", "se", "set", "x", "x.", "x.y", "", "a", "a😀", "a😀b", "t", "S", "😀", "c", "st",
            "/",
        ] {
            assert_eq!(index.rank(q.into(), 0.0).unwrap(), reference(q, 0.0), "{q}");
        }
        assert_eq!(
            index.rank("s".into(), 1999.0).unwrap(),
            reference("s", 1999.0)
        );
        // Both sorts give JS's order: score down, then key order.
        let hits = vec![(3.0, 0), (1999.0, 1), (3.0, 2), (1999.0, 3), (5.0, 4)];
        assert_eq!(super::order(hits.clone()), [1, 3, 4, 0, 2]);
        let odd: Vec<(f64, u32)> = hits.iter().map(|&(s, i)| (s + 0.5, i)).collect();
        assert_eq!(super::order(odd), [1, 3, 4, 0, 2]);
    }
}
