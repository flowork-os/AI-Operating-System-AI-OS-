//! The Rust port of `packages/core/src/plugins.ts`.
//!
//! `isPreset` and `createRegistry` stay in TS: plugins are objects of functions.

#![forbid(unsafe_code)]

/// Port of `extensionOf` (`packages/core/src/plugins.ts:61`): lower-cased, without the dot;
/// empty for dotfiles and names without an extension.
pub fn extension_of(path: String) -> String {
    // `/` and `.` are ASCII: byte positions cut where JS's UTF-16 positions do.
    let base = path.rfind('/').map_or(path.as_str(), |i| &path[i + 1..]);
    match base.rfind('.') {
        Some(dot) if dot > 0 => base[dot + 1..].to_lowercase(),
        _ => String::new(),
    }
}

#[cfg(test)]
mod tests {
    use super::extension_of;

    #[test]
    fn reads_extensions() {
        assert_eq!(extension_of("src/locales/en.JSON".into()), "json");
        assert_eq!(extension_of("a/.env".into()), "");
        assert_eq!(extension_of("a.b/c".into()), "");
        assert_eq!(extension_of("x.tar.gz".into()), "gz");
    }
}
