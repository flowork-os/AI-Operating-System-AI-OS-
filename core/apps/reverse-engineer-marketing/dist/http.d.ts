export interface FetchedPage {
    url: string;
    finalUrl: string;
    status: number;
    contentType: string;
    body: string;
}
/**
 * REM only reads public websites. Block loopback / private / link-local targets so a
 * hostile robots.txt, sitemap or redirect can't point it at the user's machine or LAN
 * (including REM's own local web server). Hostnames that *resolve* to private IPs are
 * not checked here (no DNS pinning); this blocks literal addresses and localhost names.
 */
export declare function assertPublicUrl(raw: string): URL;
export declare function fetchText(url: string, opts?: {
    timeoutMs?: number;
    headers?: Record<string, string>;
    maxBytes?: number;
}): Promise<FetchedPage>;
export declare function fetchJson<T = unknown>(url: string, opts?: {
    timeoutMs?: number;
    headers?: Record<string, string>;
}): Promise<{
    status: number;
    json: T | null;
}>;
export declare function cached<T>(key: string, fn: () => Promise<T>): Promise<T>;
export declare function clip(s: unknown, n?: number): string;
export declare function median(xs: number[]): number | null;
/** Posts per week across a set of unix-second timestamps. */
export declare function perWeek(unixSeconds: number[]): number | null;
export declare function daysAgo(unixSeconds: number): number;
