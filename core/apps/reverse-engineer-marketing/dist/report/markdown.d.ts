import { type ChannelScore } from "../analyze/scorecard.js";
import type { EvidenceBundle } from "../index.js";
export declare function channelLabel(c: string): string;
export declare function scorecardTable(card: ChannelScore[]): string;
export declare function evidenceAppendix(bundle: EvidenceBundle): string;
export declare function unknownsSection(bundle: EvidenceBundle): string;
export declare function renderMarkdown(bundle: EvidenceBundle, opts?: {
    narrative?: string;
}): string;
