/**
 * Thin Scrape Creators client with a hard credit budget. Every call costs ~1
 * credit, so collectors ask `can()` before optional calls and the run reports
 * how many were spent.
 */
export declare class ScrapeCreators {
    private readonly apiKey;
    readonly budget: number;
    spent: number;
    constructor(apiKey: string, budget: number);
    can(n?: number): boolean;
    get<T = any>(path: string, params: Record<string, string | number | undefined>): Promise<T | null>;
}
export declare function scrapeCreatorsFromEnv(budget: number): ScrapeCreators | null;
