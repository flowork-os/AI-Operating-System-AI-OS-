import type { Ctx, FounderHint } from "../context.js";
import type { LogoCandidate } from "./html.js";
/** Finds the Wikidata item whose official website is this domain (product → developer org for founders). */
export declare function collectWikidata(ctx: Ctx): Promise<void>;
/** Best-first logo list; the UI falls through on load errors. Square marks beat banners. */
export declare function rankLogos(logos: LogoCandidate[], domain?: string): LogoCandidate[];
export declare function addHint(found: Ctx["found"], hint: FounderHint): void;
