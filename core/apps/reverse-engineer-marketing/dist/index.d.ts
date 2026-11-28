import { type ChannelScore } from "./analyze/scorecard.js";
import { type Ctx } from "./context.js";
import { type ContentItem, type Evidence, type SourceRun, type Unknown } from "./evidence.js";
import type { LogoCandidate } from "./sources/html.js";
import { type Founder } from "./sources/people.js";
import { type Target } from "./target.js";
export type Area = "website" | "seo" | "history" | "apps" | "paid" | "social" | "founders" | "community";
export declare const AREAS: Area[];
export interface RunOptions {
    /** Limit to some areas (website always runs: it discovers handles for the rest). */
    only?: Area[];
    maxCredits?: number;
    /** Override discovered handles, e.g. { tiktok: "notionhq" }. */
    handles?: Ctx["found"]["socials"];
    log?: (msg: string) => void;
    /** Structured progress for UIs: website first, then the areas in parallel. */
    onStage?: (stage: "website" | Area, state: "start" | "done" | "error", detail?: string) => void;
}
export interface EvidenceBundle {
    tool: {
        name: "reverse-engineer-marketing";
        version: string;
    };
    harness: {
        version: string;
        sha: string;
    };
    target: Target;
    generatedAt: string;
    brand: string;
    discovered: Ctx["found"];
    scorecard: ChannelScore[];
    evidence: Evidence[];
    unknowns: Unknown[];
    sources: SourceRun[];
    credits: {
        scrapecreators: number | null;
    };
    /** Posts, videos, ads and threads to review (not sent to the LLM). */
    content: ContentItem[];
    /** Brand logo (best first, UI falls through on load errors) and ranked founders. */
    identity: {
        logo?: string;
        logos: LogoCandidate[];
        founders: Founder[];
    };
}
export declare const VERSION = "0.1.0";
export declare function reverseEngineer(input: string, opts?: RunOptions): Promise<EvidenceBundle>;
export { parseTarget } from "./target.js";
export { renderMarkdown } from "./report/markdown.js";
export { synthesize } from "./analyze/synthesize.js";
export { validateReport } from "./report/validate.js";
export type { ChannelScore } from "./analyze/scorecard.js";
export type { Evidence, Unknown } from "./evidence.js";
