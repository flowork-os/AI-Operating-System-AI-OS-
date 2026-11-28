import com.example.text.*;
import java.util.*;

public class Rust {
    public static void main(String[] a) {
        String[] texts = Common.texts();
        int[] totals = Common.totals();
        try (SlugifyBatch sb = new SlugifyBatch(texts); HashBatch hb = new HashBatch(Arrays.asList(texts)); PagesBatch pb = new PagesBatch(totals)) {
            String[] slugs = sb.run(30);
            int[] hashes = hb.run();
            int[] pages = pb.run(7);
            List<Integer> rank = new ArrayList<>();
            for (int i : pb.rank(7, 100)) rank.add(i);
            String err;
            try { pb.run(0); err = "none"; } catch (RuntimeException e) { err = e.getClass().getName() + ": " + e.getMessage(); }
            System.out.println("digest " + Arrays.hashCode(slugs) + " " + Arrays.hashCode(hashes) + " " + Arrays.hashCode(pages) + " " + rank.hashCode() + " " + err);
            String[][] perCall = new String[1][texts.length];
            Runnable per = () -> { for (int i = 0; i < texts.length; i++) perCall[0][i] = Strings.slugify(texts[i], 30); };
            System.out.printf("rust batch slugify %.1f ms, hash %.1f ms; per call slugify %.1f ms%n",
                Common.time(() -> sb.run(30)) / 1e6, Common.time(hb::run) / 1e6, Common.time(per) / 1e6);
        }
        SlugifyBatch closed = new SlugifyBatch(new String[] {"x"});
        closed.close();
        closed.close();
        try { closed.run(3); } catch (IllegalStateException e) { System.out.println("closed: " + e.getMessage()); }
    }
}
