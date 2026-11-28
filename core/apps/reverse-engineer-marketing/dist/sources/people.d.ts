import { type Ctx, type FounderHint } from "../context.js";
/**
 * "Co-Founder & CEO at Cal AI" / "Cal AI co-founder" → true;
 * "Founder/CEO at Notion Skincare", "ML Engineering at Notion AI, ex-YC Founder" → false.
 */
export declare function founderOf(text: string, brand: string): boolean;
export interface Founder {
    name: string;
    role?: string;
    confidence: "high" | "medium" | "low";
    score: number;
    sources: FounderHint["source"][];
    evidenceUrls: string[];
    linkedin?: string;
    linkedinFollowers?: number | null;
    photo?: string;
    location?: string;
    x?: {
        handle: string;
        followers: number | null;
        bio?: string;
        url: string;
    };
    recentPosts?: {
        date?: string;
        title: string;
        url?: string;
    }[];
    recentXPosts?: {
        id: string;
        text: string;
        views: number;
        likes?: number;
        date?: string;
        url: string;
        thumb?: string;
    }[];
    articles?: {
        headline?: string;
        date?: string;
        url?: string;
    }[];
    postsRecently?: boolean;
}
/** Merge hints by name; more independent sources = more confidence. */
export declare function mergeFounders(hints: FounderHint[]): Founder[];
export declare function collectFounders(ctx: Ctx): Promise<void>;
export declare function collectCommunity(ctx: Ctx): Promise<void>;
