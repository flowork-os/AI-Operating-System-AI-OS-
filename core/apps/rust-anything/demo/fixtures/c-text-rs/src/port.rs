//! The Rust port of `src/text.c`: safe Rust; `lib.rs` exports each function under its C name.

#![forbid(unsafe_code)]

/// C `isspace` in the "C" locale.
fn is_space(b: u8) -> bool {
    matches!(b, b' ' | b'\t' | b'\n' | b'\x0b' | b'\x0c' | b'\r')
}

/// Port of `size_t count_words(const char *s)` (`src/text.c:6`).
pub fn count_words(s: Option<&[u8]>) -> usize {
    let Some(s) = s else { return 0 };
    s.split(|&b| is_space(b)).filter(|w| !w.is_empty()).count()
}

/// Port of `int vowels(const char *s)` (`src/text.c:21`).
pub fn vowels(s: Option<&[u8]>) -> std::ffi::c_int {
    let Some(s) = s else { return -1 };
    let n = s.iter().filter(|b| b"aeiouAEIOU".contains(b)).count();
    std::ffi::c_int::try_from(n).unwrap_or(std::ffi::c_int::MAX)
}

/// Port of `bool is_palindrome(const char *s)` (`src/text.c:30`).
pub fn is_palindrome(s: Option<&[u8]>) -> bool {
    s.is_some_and(|s| s.iter().eq(s.iter().rev()))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn words() {
        assert_eq!(count_words(Some(b"  a b\tc ")), 3);
        assert_eq!(vowels(None), -1);
        assert!(is_palindrome(Some(b"abba")));
    }
}
