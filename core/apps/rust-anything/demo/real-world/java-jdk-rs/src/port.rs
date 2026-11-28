//! The Rust port of the JDK behavior behind `com.example.jdk.Jdk`.

#![forbid(unsafe_code)]

const NFE: &str = "NumberFormatException";

/// Port of `Integer.toString(int, int)`: radix outside 2..=36 means 10.
pub fn to_radix(value: i64, radix: i64) -> Result<String, String> {
    let value = value as i32;
    let radix = if (2..=36).contains(&radix) {
        radix as u32
    } else {
        10
    };
    let mut magnitude = i64::from(value).unsigned_abs();
    if magnitude == 0 {
        return Ok("0".into());
    }
    let mut digits = Vec::new();
    while magnitude > 0 {
        let d = (magnitude % u64::from(radix)) as u32;
        digits.push(char::from_digit(d, radix).unwrap_or('?'));
        magnitude /= u64::from(radix);
    }
    if value < 0 {
        digits.push('-');
    }
    Ok(digits.iter().rev().collect())
}

/// Zero points of the Unicode decimal-digit runs (`Nd`) `Character.digit` reads.
const DIGIT_ZEROS: &[u32] = &[
    0x30, 0x660, 0x6F0, 0x7C0, 0x966, 0x9E6, 0xA66, 0xAE6, 0xB66, 0xBE6, 0xC66, 0xCE6, 0xD66,
    0xDE6, 0xE50, 0xED0, 0xF20, 0x1040, 0x1090, 0x17E0, 0x1810, 0x1946, 0x19D0, 0x1A80, 0x1A90,
    0x1B50, 0x1BB0, 0x1C40, 0x1C50, 0xA620, 0xA8D0, 0xA900, 0xA9D0, 0xA9F0, 0xAA50, 0xABF0, 0xFF10,
];

/// `Character.digit(c, radix)`.
fn java_digit(c: char, radix: u32) -> Option<u32> {
    let cp = c as u32;
    let value = if let Some(zero) = DIGIT_ZEROS.iter().find(|&&z| (z..z + 10).contains(&cp)) {
        cp - zero
    } else {
        match c {
            'a'..='z' => cp - 'a' as u32 + 10,
            'A'..='Z' => cp - 'A' as u32 + 10,
            '\u{FF21}'..='\u{FF3A}' => cp - 0xFF21 + 10,
            '\u{FF41}'..='\u{FF5A}' => cp - 0xFF41 + 10,
            _ => return None,
        }
    };
    (value < radix).then_some(value)
}

/// Port of `Integer.parseInt(String, int)`.
pub fn parse_radix(text: String, radix: i64) -> Result<i64, String> {
    if !(2..=36).contains(&radix) {
        return Err(format!("{NFE}: radix {radix} out of range"));
    }
    let radix = radix as u32;
    let fail = || format!("{NFE}: For input string: \"{text}\"");
    let mut chars = text.chars().peekable();
    let negative = match chars.peek() {
        Some('-') => {
            chars.next();
            true
        }
        Some('+') => {
            chars.next();
            false
        }
        Some(_) => false,
        None => return Err(format!("{NFE}: Cannot parse null string: \"\"")),
    };
    let mut any = false;
    let mut result: i64 = 0;
    for c in chars {
        let d = java_digit(c, radix).ok_or_else(fail)?;
        result = result * i64::from(radix) + i64::from(d);
        if result > i64::from(i32::MAX) + 1 {
            return Err(fail());
        }
        any = true;
    }
    if !any {
        return Err(fail());
    }
    let value = if negative { -result } else { result };
    i32::try_from(value).map(i64::from).map_err(|_| fail())
}

/// Port of `Integer.toBinaryString(int)`.
pub fn to_binary(value: i64) -> Result<String, String> {
    Ok(format!("{:b}", value as i32 as u32))
}

/// Port of `Long.toHexString(long)`.
pub fn to_hex(value: i64) -> Result<String, String> {
    Ok(format!("{:x}", value as u64))
}

/// Port of `Integer.reverse(int)`.
pub fn reverse_bits(value: i64) -> Result<i64, String> {
    Ok(i64::from((value as i32).reverse_bits()))
}

/// Port of `Math.floorMod(int, int)`: the result has the divisor's sign.
pub fn floor_mod(a: i64, b: i64) -> Result<i64, String> {
    let (a, b) = (a as i32, b as i32);
    if b == 0 {
        return Err("ArithmeticException: / by zero".into());
    }
    let r = a.wrapping_rem(b);
    Ok(i64::from(if r != 0 && (r ^ b) < 0 { r + b } else { r }))
}

/// Port of `Math.addExact(int, int)`.
pub fn add_exact(a: i64, b: i64) -> Result<i64, String> {
    (a as i32)
        .checked_add(b as i32)
        .map(i64::from)
        .ok_or_else(|| "ArithmeticException: integer overflow".into())
}

/// Port of `Double.toString(double)` (JDK 19+): the shortest decimal that rounds to the value,
/// but never fewer than two digits; plain notation for 1e-3 <= |v| < 1e7, else `d.dddE±n`.
pub fn format_double(value: f64) -> Result<String, String> {
    if value.is_nan() {
        return Ok("NaN".into());
    }
    if value.is_infinite() {
        return Ok(if value > 0.0 { "Infinity" } else { "-Infinity" }.into());
    }
    if value == 0.0 {
        return Ok(if value.is_sign_negative() {
            "-0.0"
        } else {
            "0.0"
        }
        .into());
    }
    let sign = if value < 0.0 { "-" } else { "" };
    let x = value.abs();
    let split = |s: &str| -> (String, i32) {
        let (m, e) = s.split_once('e').unwrap_or((s, "0"));
        (
            m.chars().filter(char::is_ascii_digit).collect(),
            e.parse().unwrap_or(0),
        )
    };
    let (mut digits, mut exp) = split(&format!("{x:e}"));
    if digits.len() == 1 {
        // A one-digit shortest form: Java prints the closest two-digit decimal instead.
        (digits, exp) = split(&format!("{x:.1e}"));
    }
    let digits = digits.trim_end_matches('0');
    let digits = if digits.is_empty() { "0" } else { digits };
    if (1e-3..1e7).contains(&x) {
        let point = exp + 1;
        let text = if point <= 0 {
            format!("0.{}{digits}", "0".repeat(point.unsigned_abs() as usize))
        } else if (point as usize) >= digits.len() {
            format!("{digits}{}.0", "0".repeat(point as usize - digits.len()))
        } else {
            format!(
                "{}.{}",
                &digits[..point as usize],
                &digits[point as usize..]
            )
        };
        return Ok(format!("{sign}{text}"));
    }
    let (first, rest) = digits.split_at(1);
    let rest = if rest.is_empty() { "0" } else { rest };
    Ok(format!("{sign}{first}.{rest}E{exp}"))
}

/// Port of `URLEncoder.encode(String, UTF_8)`.
pub fn url_encode(text: String) -> Result<String, String> {
    let mut out = String::new();
    for b in text.bytes() {
        match b {
            b'a'..=b'z' | b'A'..=b'Z' | b'0'..=b'9' | b'.' | b'-' | b'*' | b'_' => {
                out.push(b as char)
            }
            b' ' => out.push('+'),
            _ => out.push_str(&format!("%{b:02X}")),
        }
    }
    Ok(out)
}

/// Port of `Base64.getEncoder().encodeToString(text.getBytes(UTF_8))`.
pub fn base64(text: String) -> Result<String, String> {
    const TABLE: &[u8; 64] = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    let bytes = text.as_bytes();
    let mut out = String::with_capacity(bytes.len().div_ceil(3) * 4);
    for chunk in bytes.chunks(3) {
        let n = (u32::from(chunk[0]) << 16)
            | (u32::from(*chunk.get(1).unwrap_or(&0)) << 8)
            | u32::from(*chunk.get(2).unwrap_or(&0));
        for i in 0..4 {
            if i <= chunk.len() {
                out.push(TABLE[((n >> (18 - 6 * i)) & 63) as usize] as char);
            } else {
                out.push('=');
            }
        }
    }
    Ok(out)
}

/// Port of `String.toUpperCase(Locale.ROOT)`.
pub fn upper(text: String) -> Result<String, String> {
    Ok(text.to_uppercase())
}
