import type { EvidenceBundle } from "../index.js";
export declare const DEFAULT_MODEL = "claude-opus-5";
export interface SynthesisResult {
    markdown: string;
    model: string;
    usage: {
        input: number;
        output: number;
        cacheRead: number;
    };
}
/**
 * Writes the strategy report from the evidence bundle with the harness as the
 * system prompt. The harness is stable across runs, so it is cached.
 */
export declare function synthesize(bundle: EvidenceBundle, opts?: {
    model?: string;
    onText?: (delta: string) => void;
}): Promise<SynthesisResult>;
export declare function userPrompt(bundle: EvidenceBundle): string;
