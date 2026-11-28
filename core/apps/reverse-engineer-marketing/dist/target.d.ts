export interface Target {
    input: string;
    kind: "website" | "app_store" | "play_store";
    /** Homepage URL (may be filled in later for app-store inputs). */
    url?: string;
    domain?: string;
    /** Other domains that redirect here (e.g. notion.so → notion.com). */
    aliases?: string[];
    brand?: string;
    appleId?: string;
    playId?: string;
}
/** Accepts "notion.so", "https://www.notion.so/pricing", App Store or Google Play links. */
export declare function parseTarget(input: string): Target;
export declare function brandFromDomain(domain: string): string;
export declare function sameSite(a: string, b: string): boolean;
