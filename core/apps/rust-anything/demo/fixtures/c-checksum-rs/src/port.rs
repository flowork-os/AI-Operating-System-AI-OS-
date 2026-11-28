//! The Rust port of `src/checksum.c`: safe Rust; `lib.rs` exports each function under its C name.

#![forbid(unsafe_code)]

use std::ffi::{c_int, c_long};

const MOD_ADLER: u32 = 65521;

/// Port of `uint32_t adler32(const char *data)` (`src/checksum.c:5`).
pub fn adler32(data: Option<&[u8]>) -> u32 {
    let Some(data) = data else { return 0 };
    let (mut a, mut b) = (1u32, 0u32);
    for &byte in data {
        a = (a + u32::from(byte)) % MOD_ADLER;
        b = (b + a) % MOD_ADLER;
    }
    (b << 16) | a
}

/// Port of `uint32_t fnv1a(const char *data)` (`src/checksum.c:15`).
pub fn fnv1a(data: Option<&[u8]>) -> u32 {
    let mut hash: u32 = 2_166_136_261;
    for &byte in data.unwrap_or_default() {
        hash ^= u32::from(byte);
        hash = hash.wrapping_mul(16_777_619);
    }
    hash
}

/// Port of `int clamp(int value, int low, int high)` (`src/checksum.c:24`).
pub fn clamp(value: c_int, low: c_int, high: c_int) -> c_int {
    if value < low {
        low
    } else if value > high {
        high
    } else {
        value
    }
}

/// Port of `long gcd(long a, long b)` (`src/checksum.c:30`). `-LONG_MIN` wraps, as compiled C does.
pub fn gcd(a: c_long, b: c_long) -> c_long {
    let (mut a, mut b) = (
        if a < 0 { a.wrapping_neg() } else { a },
        if b < 0 { b.wrapping_neg() } else { b },
    );
    while b != 0 {
        let t = a.wrapping_rem(b);
        a = b;
        b = t;
    }
    a
}

/// Port of `double mean3(double a, double b, double c)` (`src/checksum.c:41`).
pub fn mean3(a: f64, b: f64, c: f64) -> f64 {
    (a + b + c) / 3.0
}
