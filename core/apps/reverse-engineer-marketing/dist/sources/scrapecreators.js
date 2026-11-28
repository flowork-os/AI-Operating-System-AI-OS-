import { cached } from "../http.js";
const BASE = "https://api.scrapecreators.com";
/**
 * Thin Scrape Creators client with a hard credit budget. Every call costs ~1
 * credit, so collectors ask `can()` before optional calls and the run reports
 * how many were spent.
 */
export class ScrapeCreators {
    apiKey;
    budget;
    spent = 0;
    constructor(apiKey, budget) {
        this.apiKey = apiKey;
        this.budget = budget;
    }
    can(n = 1) {
        return this.spent + n <= this.budget;
    }
    async get(path, params) {
        const qs = new URLSearchParams();
        for (const [k, v] of Object.entries(params))
            if (v !== undefined && v !== "")
                qs.set(k, String(v));
        const url = `${BASE}${path}?${qs}`;
        return cached(`sc:${url}`, async () => {
            if (!this.can())
                throw new Error(`Scrape Creators credit budget (${this.budget}) reached`);
            this.spent++;
            const res = await fetch(url, { headers: { "x-api-key": this.apiKey }, signal: AbortSignal.timeout(45_000) });
            const json = (await res.json().catch(() => null));
            if (!res.ok || json?.success === false) {
                const msg = json?.message || json?.error || `HTTP ${res.status}`;
                throw new Error(`scrapecreators ${path}: ${msg}`);
            }
            return json;
        });
    }
}
export function scrapeCreatorsFromEnv(budget) {
    const key = process.env.SCRAPECREATORS_API_KEY || process.env.SCRAPE_CREATORS_API_KEY;
    return key ? new ScrapeCreators(key, budget) : null;
}
