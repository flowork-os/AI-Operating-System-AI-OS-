//! The Rust port of `src/stats.ts`.

#![forbid(unsafe_code)]

use indexmap::IndexMap;
use serde_json::json;

/// JS `WhiteSpace` and `LineTerminator`, what `\s` matches.
fn is_js_space(u: u16) -> bool {
    matches!(u, 0x09..=0x0D | 0x20 | 0xA0 | 0x1680 | 0x2000..=0x200A | 0x2028 | 0x2029 | 0x202F | 0x205F | 0x3000 | 0xFEFF)
}

/// JS `text.split(separator)` on UTF-16 units; an empty separator splits every unit.
fn split(text: &[u16], separator: &[u16]) -> Vec<Vec<u16>> {
    if separator.is_empty() {
        return text.iter().map(|u| vec![*u]).collect();
    }
    let mut parts = Vec::new();
    let mut start = 0;
    let mut i = 0;
    while i + separator.len() <= text.len() {
        if &text[i..i + separator.len()] == separator {
            parts.push(text[start..i].to_vec());
            i += separator.len();
            start = i;
        } else {
            i += 1;
        }
    }
    parts.push(text[start..].to_vec());
    parts
}

/// Port of class `TextStats` (`src/stats.ts:7`): holds the instance state.
pub struct TextStats {
    words: f64,
    lines: f64,
    longest: Vec<u16>,
    separator: Vec<u16>,
}

impl TextStats {
    /// Port of `TextStats` constructor (`src/stats.ts:7`).
    pub fn new(separator: Option<String>) -> Result<Self, String> {
        Ok(Self {
            words: 0.0,
            lines: 0.0,
            longest: Vec::new(),
            separator: separator
                .unwrap_or_else(|| "\n".into())
                .encode_utf16()
                .collect(),
        })
    }

    /// Port of `TextStats.add` (`src/stats.ts:14`).
    pub fn add(&mut self, text: String) -> Result<f64, String> {
        let text: Vec<u16> = text.encode_utf16().collect();
        let parts = split(&text, &self.separator);
        self.lines += parts.len() as f64;
        for part in &parts {
            for word in part.split(|&u| is_js_space(u)).filter(|w| !w.is_empty()) {
                self.words += 1.0;
                // `word.length`: UTF-16 code units.
                if word.len() > self.longest.len() {
                    self.longest = word.to_vec();
                }
            }
        }
        Ok(self.words)
    }

    /// Port of `TextStats.stats` (`src/stats.ts:28`).
    pub fn stats(&mut self) -> Result<serde_json::Value, String> {
        Ok(json!({ "words": self.words, "lines": self.lines }))
    }

    /// Port of `TextStats.longestWord` (`src/stats.ts:32`).
    ///
    /// UTF-16 units: an empty separator splits surrogate pairs, and JS keeps the halves.
    pub fn longest_word(&self) -> Result<Vec<u16>, String> {
        Ok(self.longest.clone())
    }

    /// Port of `TextStats.reset` (`src/stats.ts:36`).
    pub fn reset(&mut self) -> Result<(), String> {
        self.words = 0.0;
        self.lines = 0.0;
        self.longest.clear();
        Ok(())
    }
}

/// Port of class `LruCache` (`src/stats.ts:44`): holds the instance state.
pub struct LruCache {
    /// Insertion order is recency, as in the JS `Map`.
    map: IndexMap<String, String>,
    capacity: f64,
}

impl LruCache {
    /// Port of `LruCache` constructor (`src/stats.ts:44`).
    pub fn new(capacity: f64) -> Result<Self, String> {
        // `!(capacity >= 1)` also rejects NaN.
        if capacity
            .partial_cmp(&1.0)
            .is_none_or(std::cmp::Ordering::is_lt)
        {
            return Err("capacity must be at least 1".into());
        }
        Ok(Self {
            map: IndexMap::new(),
            capacity,
        })
    }

    /// Port of `LruCache.get` (`src/stats.ts:50`).
    pub fn get(&mut self, key: String) -> Result<Option<String>, String> {
        let value = self.map.shift_remove(&key);
        if let Some(v) = &value {
            self.map.insert(key, v.clone());
        }
        Ok(value)
    }

    /// Port of `LruCache.set` (`src/stats.ts:59`).
    pub fn set(&mut self, key: String, value: String) -> Result<Vec<String>, String> {
        self.map.shift_remove(&key);
        self.map.insert(key, value);
        let mut evicted = Vec::new();
        while self.map.len() as f64 > self.capacity {
            if let Some((oldest, _)) = self.map.shift_remove_index(0) {
                evicted.push(oldest);
            }
        }
        Ok(evicted)
    }

    /// Port of `LruCache.keys` (`src/stats.ts:71`).
    pub fn keys(&self) -> Result<Vec<String>, String> {
        Ok(self.map.keys().cloned().collect())
    }
}
