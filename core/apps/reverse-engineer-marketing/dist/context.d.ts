import type { ContentItem, EvidenceStore } from "./evidence.js";
import type { LogoCandidate } from "./sources/html.js";
import type { ScrapeCreators } from "./sources/scrapecreators.js";
import type { Target } from "./target.js";
/** Social handles and links discovered on the site (and enriched by later sources). */
export interface Discovered {
    socials: Partial<Record<"tiktok" | "instagram" | "youtube" | "x" | "linkedin" | "facebook" | "threads" | "reddit" | "discord" | "github" | "producthunt", string>>;
    /** linkedin.com/in/... links found on the site — usually founders or team. */
    people: string[];
    appStoreIds: string[];
    playIds: string[];
    /** Brand name as the company writes it (og:site_name / JSON-LD / title). */
    brandName?: string;
    logos: LogoCandidate[];
    founderHints: FounderHint[];
}
/** A founder/leader name seen somewhere; merged and ranked in people.ts. */
export interface FounderHint {
    name: string;
    role?: string;
    source: "wikidata" | "jsonld" | "website_text" | "google_snippet" | "linkedin_search" | "site_link" | "appstore_seller";
    url?: string;
    linkedin?: string;
    x?: string;
    photo?: string;
}
export interface Ctx {
    target: Target;
    store: EvidenceStore;
    sc: ScrapeCreators | null;
    found: Discovered;
    content: ContentItem[];
    log: (msg: string) => void;
}
/** Attach items to the evidence that summarizes them, dropping duplicates. */
export declare function addContent(ctx: Ctx, items: ContentItem[], evidenceId?: string): void;
export type Collector = (ctx: Ctx) => Promise<void>;
export declare function runSource(ctx: Ctx, source: string, fn: Collector): Promise<void>;
export declare function skip(ctx: Ctx, source: string, reason: string): void;
