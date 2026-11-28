import com.example.text.*;
import java.util.*;

public class Orig {
    public static void main(String[] a) {
        String[] texts = Common.texts();
        int[] totals = Common.totals();
        String[] slugs = new String[texts.length];
        int[] hashes = new int[texts.length];
        int[] pages = new int[totals.length];
        Runnable slug = () -> { for (int i = 0; i < texts.length; i++) slugs[i] = Strings.slugify(texts[i], 30); };
        Runnable hash = () -> { for (int i = 0; i < texts.length; i++) hashes[i] = Strings.hash(texts[i]); };
        slug.run(); hash.run();
        for (int i = 0; i < totals.length; i++) pages[i] = Nums.pages(totals[i], 7);
        Integer[] idx = new Integer[totals.length];
        for (int i = 0; i < idx.length; i++) idx[i] = i;
        List<Integer> rank = new ArrayList<>();
        for (int i : idx) if (pages[i] >= 100) rank.add(i);
        rank.sort((x, y) -> Integer.compare(pages[y], pages[x]));
        String err;
        try { Nums.pages(1, 0); err = "none"; } catch (RuntimeException e) { err = e.getClass().getName() + ": " + e.getMessage(); }
        System.out.println("digest " + Arrays.hashCode(slugs) + " " + Arrays.hashCode(hashes) + " " + Arrays.hashCode(pages) + " " + rank.hashCode() + " " + err);
        System.out.printf("java slugify %.1f ms, hash %.1f ms%n", Common.time(slug) / 1e6, Common.time(hash) / 1e6);
    }
}
