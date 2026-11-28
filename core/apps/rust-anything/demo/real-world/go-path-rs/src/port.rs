//! The Rust port of Go's `path` package: slash-separated paths, byte by byte as Go does.
//! Translated from Go 1.24 `src/path` (BSD-3-Clause, Copyright The Go Authors).

#![forbid(unsafe_code)]

use serde_json::{Value, json};

const BAD_PATTERN: &str = "syntax error in pattern";

/// Go's `utf8.DecodeRuneInString`: the rune at the start of `s` and its length; an invalid
/// or truncated sequence reads as U+FFFD with length 1.
fn decode_rune(s: &[u8]) -> (u32, usize) {
    if s.is_empty() {
        return (0xFFFD, 0);
    }
    for n in 1..=s.len().min(4) {
        if let Ok(text) = std::str::from_utf8(&s[..n]) {
            return (text.chars().next().map_or(0xFFFD, u32::from), n);
        }
    }
    (0xFFFD, 1)
}

/// Port of `Match` (`path/match.go:37`).
pub fn r#match(pattern: String, name: String) -> Result<bool, String> {
    let mut pattern = pattern.as_bytes();
    let mut name = name.as_bytes();
    'pattern: while !pattern.is_empty() {
        let (star, chunk, rest) = scan_chunk(pattern);
        pattern = rest;
        if star && chunk.is_empty() {
            // A trailing * matches the rest of the name unless it has a /.
            return Ok(!name.contains(&b'/'));
        }
        let (t, ok, err) = match_chunk(chunk, name);
        if ok && (t.is_empty() || !pattern.is_empty()) {
            name = t;
            continue;
        }
        if let Some(e) = err {
            return Err(e.into());
        }
        if star {
            let mut i = 0;
            while i < name.len() && name[i] != b'/' {
                let (t, ok, err) = match_chunk(chunk, &name[i + 1..]);
                if ok {
                    if pattern.is_empty() && !t.is_empty() {
                        i += 1;
                        continue;
                    }
                    name = t;
                    continue 'pattern;
                }
                if let Some(e) = err {
                    return Err(e.into());
                }
                i += 1;
            }
        }
        // Before answering false, the rest of the pattern must still be well formed.
        while !pattern.is_empty() {
            let (_, chunk, rest) = scan_chunk(pattern);
            pattern = rest;
            if let (_, _, Some(e)) = match_chunk(chunk, b"") {
                return Err(e.into());
            }
        }
        return Ok(false);
    }
    Ok(name.is_empty())
}

/// The next segment of the pattern: a non-star string, possibly preceded by stars.
fn scan_chunk(mut pattern: &[u8]) -> (bool, &[u8], &[u8]) {
    let mut star = false;
    while pattern.first() == Some(&b'*') {
        pattern = &pattern[1..];
        star = true;
    }
    let mut in_range = false;
    let mut i = 0;
    while i < pattern.len() {
        match pattern[i] {
            b'\\' => {
                if i + 1 < pattern.len() {
                    i += 1;
                }
            }
            b'[' => in_range = true,
            b']' => in_range = false,
            b'*' if !in_range => break,
            _ => {}
        }
        i += 1;
    }
    (star, &pattern[..i], &pattern[i..])
}

/// Whether `chunk` matches the start of `s`; the rest of `s` if it does.
fn match_chunk<'s>(mut chunk: &[u8], mut s: &'s [u8]) -> (&'s [u8], bool, Option<&'static str>) {
    let mut failed = false;
    while !chunk.is_empty() {
        if !failed && s.is_empty() {
            failed = true;
        }
        match chunk[0] {
            b'[' => {
                let mut r = 0;
                if !failed {
                    let (rune, n) = decode_rune(s);
                    r = rune;
                    s = &s[n..];
                }
                chunk = &chunk[1..];
                let mut negated = false;
                if chunk.first() == Some(&b'^') {
                    negated = true;
                    chunk = &chunk[1..];
                }
                let mut matched = false;
                let mut ranges = 0;
                loop {
                    if chunk.first() == Some(&b']') && ranges > 0 {
                        chunk = &chunk[1..];
                        break;
                    }
                    let (lo, rest) = match get_esc(chunk) {
                        Ok(v) => v,
                        Err(e) => return (b"", false, Some(e)),
                    };
                    chunk = rest;
                    let mut hi = lo;
                    if chunk[0] == b'-' {
                        match get_esc(&chunk[1..]) {
                            Ok((h, rest)) => {
                                hi = h;
                                chunk = rest;
                            }
                            Err(e) => return (b"", false, Some(e)),
                        }
                    }
                    if lo <= r && r <= hi {
                        matched = true;
                    }
                    ranges += 1;
                }
                if matched == negated {
                    failed = true;
                }
            }
            b'?' => {
                if !failed {
                    if s[0] == b'/' {
                        failed = true;
                    }
                    let (_, n) = decode_rune(s);
                    s = &s[n..];
                }
                chunk = &chunk[1..];
            }
            c => {
                let literal = if c == b'\\' {
                    chunk = &chunk[1..];
                    match chunk.first() {
                        Some(&l) => l,
                        None => return (b"", false, Some(BAD_PATTERN)),
                    }
                } else {
                    c
                };
                if !failed {
                    if literal != s[0] {
                        failed = true;
                    }
                    s = &s[1..];
                }
                chunk = &chunk[1..];
            }
        }
    }
    if failed {
        (b"", false, None)
    } else {
        (s, true, None)
    }
}

/// A possibly escaped character of a class, and the rest of the chunk.
fn get_esc(mut chunk: &[u8]) -> Result<(u32, &[u8]), &'static str> {
    if chunk.is_empty() || chunk[0] == b'-' || chunk[0] == b']' {
        return Err(BAD_PATTERN);
    }
    if chunk[0] == b'\\' {
        chunk = &chunk[1..];
        if chunk.is_empty() {
            return Err(BAD_PATTERN);
        }
    }
    let (r, n) = decode_rune(chunk);
    let bad = r == 0xFFFD && n == 1 && !chunk.starts_with("\u{FFFD}".as_bytes());
    let rest = &chunk[n..];
    if bad || rest.is_empty() {
        return Err(BAD_PATTERN);
    }
    Ok((r, rest))
}

/// Port of `Clean` (`path/path.go:69`).
pub fn clean(path: String) -> Result<String, String> {
    Ok(clean_bytes(path.as_bytes()))
}

fn clean_bytes(path: &[u8]) -> String {
    if path.is_empty() {
        return ".".into();
    }
    let rooted = path[0] == b'/';
    let n = path.len();
    // Go's lazybuf: a buffer and a write index `w`; bytes past `w` stay and are read back.
    let mut buf: Vec<u8> = Vec::with_capacity(n);
    let mut w = 0;
    let append = |buf: &mut Vec<u8>, w: &mut usize, c: u8| {
        if *w < buf.len() {
            buf[*w] = c;
        } else {
            buf.push(c);
        }
        *w += 1;
    };
    let (mut r, mut dotdot) = (0, 0);
    if rooted {
        append(&mut buf, &mut w, b'/');
        r = 1;
        dotdot = 1;
    }
    while r < n {
        // An empty element, or `.`.
        if path[r] == b'/' || (path[r] == b'.' && (r + 1 == n || path[r + 1] == b'/')) {
            r += 1;
        } else if path[r] == b'.' && path[r + 1] == b'.' && (r + 2 == n || path[r + 2] == b'/') {
            r += 2;
            if w > dotdot {
                w -= 1;
                while w > dotdot && buf[w] != b'/' {
                    w -= 1;
                }
            } else if !rooted {
                if w > 0 {
                    append(&mut buf, &mut w, b'/');
                }
                append(&mut buf, &mut w, b'.');
                append(&mut buf, &mut w, b'.');
                dotdot = w;
            }
        } else {
            if (rooted && w != 1) || (!rooted && w != 0) {
                append(&mut buf, &mut w, b'/');
            }
            while r < n && path[r] != b'/' {
                append(&mut buf, &mut w, path[r]);
                r += 1;
            }
        }
    }
    if w == 0 {
        return ".".into();
    }
    String::from_utf8_lossy(&buf[..w]).into_owned()
}

/// Port of `Split` (`path/path.go:145`).
pub fn split(path: String) -> Result<Value, String> {
    let i = path.rfind('/').map_or(0, |i| i + 1);
    Ok(json!([&path[..i], &path[i..]]))
}

/// Port of `Ext` (`path/path.go:154`).
pub fn ext(path: String) -> Result<String, String> {
    let bytes = path.as_bytes();
    for i in (0..bytes.len()).rev() {
        match bytes[i] {
            b'/' => break,
            b'.' => return Ok(path[i..].to_string()),
            _ => {}
        }
    }
    Ok(String::new())
}

/// Port of `Base` (`path/path.go:168`).
pub fn base(path: String) -> Result<String, String> {
    if path.is_empty() {
        return Ok(".".into());
    }
    let trimmed = path.trim_end_matches('/');
    let last = trimmed.rfind('/').map_or(trimmed, |i| &trimmed[i + 1..]);
    Ok(if last.is_empty() {
        "/".into()
    } else {
        last.into()
    })
}

/// Port of `IsAbs` (`path/path.go:188`).
pub fn is_abs(path: String) -> Result<bool, String> {
    Ok(path.starts_with('/'))
}

/// Port of `Dir` (`path/path.go:199`).
pub fn dir(path: String) -> Result<String, String> {
    let i = path.rfind('/').map_or(0, |i| i + 1);
    Ok(clean_bytes(&path.as_bytes()[..i]))
}
