package com.example.jdk;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;
import java.util.Base64;
import java.util.Locale;

/** JDK behavior an application depends on, one method per JDK call. */
public final class Jdk {
    private Jdk() {}

    public static String toRadix(int value, int radix) {
        return Integer.toString(value, radix);
    }

    public static int parseRadix(String text, int radix) {
        return Integer.parseInt(text, radix);
    }

    public static String toBinary(int value) {
        return Integer.toBinaryString(value);
    }

    public static String toHex(long value) {
        return Long.toHexString(value);
    }

    public static int reverseBits(int value) {
        return Integer.reverse(value);
    }

    public static int floorMod(int a, int b) {
        return Math.floorMod(a, b);
    }

    public static int addExact(int a, int b) {
        return Math.addExact(a, b);
    }

    public static String formatDouble(double value) {
        return Double.toString(value);
    }

    public static String urlEncode(String text) {
        return URLEncoder.encode(text, StandardCharsets.UTF_8);
    }

    public static String base64(String text) {
        return Base64.getEncoder().encodeToString(text.getBytes(StandardCharsets.UTF_8));
    }

    public static String upper(String text) {
        return text.toUpperCase(Locale.ROOT);
    }
}
