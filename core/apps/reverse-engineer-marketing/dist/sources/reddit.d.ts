import { type Ctx } from "../context.js";
/**
 * Brand/founder-affiliated = username contains the brand or a founder's surname,
 * or the text ties the author to *this* brand ("I built Cal AI", "founder of Linear",
 * "Notion team here", "disclosure: … Cal AI"). Generic "I made…" is not enough.
 */
export declare function affiliated(text: string, author: string, brand: string, founderKeys?: string[]): boolean;
export interface RedditPost {
    id: string;
    subreddit: string;
    title: string;
    author: string;
    score: number;
    comments: number;
    date?: string;
    url: string;
    selfPromo: boolean;
    affiliated: boolean;
    comparison: boolean;
}
/** Word-boundary brand match so "Cal AI" doesn't match "local airport". */
export declare function mentions(text: string, brand: string, domain?: string): boolean;
export declare function classifyPost(p: any, brand: string, domain?: string, founderKeys?: string[]): RedditPost | null;
export declare function collectReddit(ctx: Ctx): Promise<void>;
