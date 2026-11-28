import type { Ctx } from "../context.js";
export interface RobotsFacts {
    sitemaps: string[];
    aiBots: Record<string, "blocked" | "allowed" | "unspecified">;
    disallowCount: number;
}
export declare function parseRobots(txt: string): RobotsFacts;
export declare function parseSitemap(xml: string): {
    urls: {
        loc: string;
        lastmod?: string;
    }[];
    children: string[];
};
export interface SitemapAnalysis {
    totalUrls: number;
    sections: {
        path: string;
        count: number;
        examples: string[];
        programmatic: boolean;
        freshLast90d: number;
    }[];
    locales: string[];
    patterns: Record<"comparison" | "alternatives" | "integrations" | "templates" | "tools" | "glossary" | "useCases" | "locations" | "howTo" | "listicles", number>;
    blogPostsLast30d: number;
    blogPostsLast90d: number;
}
/** Groups URLs by first path segment and spots programmatic-SEO page families. */
export declare function analyzeSitemap(urls: {
    loc: string;
    lastmod?: string;
}[], now?: number): SitemapAnalysis;
export declare function collectSeo(ctx: Ctx): Promise<void>;
