// Evidence contract (borrowed from REA): every fact REM reports is either an
// observation (seen directly at a URL / API) or a derivation (computed from
// observations). Interpretations ("they scale with UGC") belong to the report
// and must cite evidence ids. Anything we could not check is an Unknown, never
// silently treated as "not doing it".
export const CHANNELS = [
    "paid_meta",
    "paid_google",
    "paid_linkedin",
    "paid_reddit",
    "paid_tiktok",
    "paid_apple",
    "organic_tiktok",
    "organic_instagram",
    "organic_youtube",
    "organic_x",
    "organic_linkedin",
    "seo",
    "geo",
    "founder_led",
    "reddit_marketing",
    "community",
    "launches",
    "app_store",
    "lifecycle",
    "affiliate",
    "sales_led",
];
export class EvidenceStore {
    items = [];
    unknowns = [];
    runs = [];
    seq = 0;
    add(e) {
        const item = { id: `E${++this.seq}`, observedAt: new Date().toISOString(), ...e };
        this.items.push(item);
        return item;
    }
    unknown(u) {
        if (!this.unknowns.some(x => x.channel === u.channel && x.reason === u.reason))
            this.unknowns.push(u);
    }
    bySource(source) {
        return this.items.filter(e => e.source === source);
    }
    find(source, titlePrefix) {
        return this.items.find(e => e.source === source && e.title.startsWith(titlePrefix));
    }
}
