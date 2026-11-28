export type SourceName = "website" | "tracking" | "seo" | "wayback" | "appstore" | "meta_ads" | "google_ads" | "linkedin_ads" | "reddit_ads" | "tiktok" | "instagram" | "youtube" | "x" | "linkedin" | "threads" | "founders" | "reddit" | "hackernews" | "producthunt" | "wikidata" | "apple_ads";
export type Channel = "paid_meta" | "paid_google" | "paid_linkedin" | "paid_reddit" | "paid_tiktok" | "paid_apple" | "organic_tiktok" | "organic_instagram" | "organic_youtube" | "organic_x" | "organic_linkedin" | "seo" | "geo" | "founder_led" | "reddit_marketing" | "community" | "launches" | "app_store" | "lifecycle" | "affiliate" | "sales_led";
export declare const CHANNELS: Channel[];
export interface Evidence {
    id: string;
    source: SourceName;
    kind: "observation" | "derivation";
    /** One line a human can scan. */
    title: string;
    url?: string;
    observedAt: string;
    data: unknown;
}
export interface Unknown {
    channel: Channel | string;
    reason: string;
    /** A URL a human can open to check by hand. */
    manualCheck?: string;
}
export interface SourceRun {
    /** Collector label (an area can feed several evidence sources). */
    source: string;
    status: "ok" | "skipped" | "error";
    reason?: string;
    ms: number;
}
export declare class EvidenceStore {
    readonly items: Evidence[];
    readonly unknowns: Unknown[];
    readonly runs: SourceRun[];
    private seq;
    add(e: Omit<Evidence, "id" | "observedAt">): Evidence;
    unknown(u: Unknown): void;
    bySource(source: SourceName): Evidence[];
    find(source: SourceName, titlePrefix: string): Evidence | undefined;
}
/** A concrete post / video / ad / thread for humans to review (web Content tab, MCP get_content). Not sent to the LLM. */
export interface ContentItem {
    id: string;
    platform: "meta_ads" | "google_ads" | "linkedin_ads" | "apple_ads" | "tiktok" | "instagram" | "youtube" | "x" | "linkedin" | "reddit";
    kind: "ad" | "video" | "post" | "thread" | "comment";
    url: string;
    title?: string;
    text?: string;
    thumb?: string;
    video?: string;
    author?: string;
    date?: string;
    status?: "active" | "inactive";
    metrics?: {
        views?: number;
        likes?: number;
        comments?: number;
        shares?: number;
        score?: number;
        runningDays?: number;
        variants?: number;
    };
    tags?: string[];
    evidence?: string;
}
