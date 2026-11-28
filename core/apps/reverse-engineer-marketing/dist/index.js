import { scorecard } from "./analyze/scorecard.js";
import { runSource, skip } from "./context.js";
import { EvidenceStore } from "./evidence.js";
import { loadHarness } from "./harness.js";
import { collectAppleAds } from "./sources/apple-ads.js";
import { collectAppStore, collectHackerNews, collectWayback } from "./sources/free.js";
import { collectPaid } from "./sources/paid.js";
import { rankLogos } from "./sources/identity.js";
import { collectCommunity, collectFounders, mergeFounders } from "./sources/people.js";
import { scrapeCreatorsFromEnv } from "./sources/scrapecreators.js";
import { collectSeo } from "./sources/seo.js";
import { collectSocial } from "./sources/social.js";
import { collectWebsite } from "./sources/website.js";
import { parseTarget } from "./target.js";
export const AREAS = ["website", "seo", "history", "apps", "paid", "social", "founders", "community"];
/** runSource labels that belong to each area (for stage error reporting). */
const RUN_LABELS = {
    website: ["website"],
    seo: ["seo"],
    history: ["wayback"],
    apps: ["appstore", "apple_ads", "hackernews"],
    paid: ["paid"],
    social: ["social"],
    founders: ["founders"],
    community: ["community"],
};
export const VERSION = "0.1.0";
export async function reverseEngineer(input, opts = {}) {
    const target = parseTarget(input);
    const store = new EvidenceStore();
    const sc = scrapeCreatorsFromEnv(opts.maxCredits ?? Number(process.env.REM_MAX_CREDITS ?? 50));
    const log = opts.log ?? (() => { });
    const ctx = { target, store, sc, log, content: [], found: { socials: { ...opts.handles }, people: [], appStoreIds: [], playIds: [], logos: [], founderHints: [] } };
    const want = (a) => !opts.only?.length || opts.only.includes(a);
    const stage = opts.onStage ?? (() => { });
    const timed = async (name, labels, fn) => {
        stage(name, "start");
        const before = store.runs.length;
        await fn();
        const failed = store.runs.slice(before).filter(r => r.status === "error" && labels.includes(r.source));
        stage(name, failed.length ? "error" : "done", failed.map(f => f.reason).join("; ") || undefined);
    };
    // App-store links: resolve the developer website first, then scan it like any site.
    if (target.kind !== "website") {
        log("→ app store");
        await timed("apps", ["appstore"], () => runSource(ctx, "appstore", collectAppStore));
    }
    if (target.url) {
        log(`→ website ${target.url}`);
        await timed("website", ["website"], () => runSource(ctx, "website", collectWebsite));
    }
    else
        skip(ctx, "website", "no website found for this app");
    const jobs = [
        ["seo", "seo", () => runSource(ctx, "seo", collectSeo)],
        ["history", "wayback", () => runSource(ctx, "wayback", collectWayback)],
        ["apps", "appstore + apple search ads + hacker news", async () => {
                if (target.kind === "website")
                    await runSource(ctx, "appstore", collectAppStore);
                await Promise.all([runSource(ctx, "apple_ads", collectAppleAds), runSource(ctx, "hackernews", collectHackerNews)]);
            }],
        ["paid", "ad libraries", () => runSource(ctx, "paid", collectPaid)],
        ["social", "social accounts", () => runSource(ctx, "social", collectSocial)],
        ["founders", "founders", () => runSource(ctx, "founders", collectFounders)],
        ["community", "community", () => runSource(ctx, "community", collectCommunity)],
    ];
    await Promise.all(jobs.filter(([a]) => want(a) && target.url).map(([area, label, fn]) => {
        log(`→ ${label}`);
        return timed(area, RUN_LABELS[area], fn);
    }));
    const harness = loadHarness();
    const logos = rankLogos(ctx.found.logos, target.domain);
    return {
        tool: { name: "reverse-engineer-marketing", version: VERSION },
        harness: { version: harness.version, sha: harness.sha },
        target,
        generatedAt: new Date().toISOString(),
        brand: ctx.found.brandName ?? target.brand ?? target.domain ?? input,
        discovered: ctx.found,
        scorecard: scorecard(store),
        evidence: store.items,
        unknowns: store.unknowns,
        sources: store.runs,
        credits: { scrapecreators: sc ? sc.spent : null },
        content: ctx.content,
        identity: {
            logo: logos[0]?.url,
            logos,
            founders: store.bySource("founders")[0]?.data ?? mergeFounders(ctx.found.founderHints),
        },
    };
}
export { parseTarget } from "./target.js";
export { renderMarkdown } from "./report/markdown.js";
export { synthesize } from "./analyze/synthesize.js";
export { validateReport } from "./report/validate.js";
