import java.util.*;

/** The inputs, and a digest of results, shared by both runs. */
final class Common {
    static String[] texts() {
        String[] t = new String[50000];
        for (int i = 0; i < t.length; i++) {
            t[i] = "Hello, Wörld " + i + " -- Ünïcode Title_" + (i % 7) + "! ΣΊΣΥΦΟΣ  and   more words here";
        }
        return t;
    }

    static int[] totals() {
        int[] t = new int[50000];
        for (int i = 0; i < t.length; i++) t[i] = i * 37 - 1000;
        return t;
    }

    static long time(Runnable r) {
        long best = Long.MAX_VALUE;
        for (int i = 0; i < 15; i++) {
            long s = System.nanoTime();
            r.run();
            best = Math.min(best, System.nanoTime() - s);
        }
        return best;
    }
}
