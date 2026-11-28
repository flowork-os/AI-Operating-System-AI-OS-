import type { EvidenceBundle } from "../index.js";
type Num = number | null;
export interface RunDiff {
    from: {
        generatedAt: string;
        harness: string;
    };
    to: {
        generatedAt: string;
        harness: string;
    };
    brand: string;
    metrics: {
        name: string;
        before: Num;
        after: Num;
        delta: Num;
    }[];
    channels: {
        channel: string;
        before: string;
        after: string;
    }[];
    positioning: {
        before?: string;
        after?: string;
    } | null;
    content: {
        platform: string;
        added: {
            title?: string;
            text?: string;
            url: string;
            date?: string;
        }[];
        removed: number;
    }[];
}
export declare function diffRuns(a: EvidenceBundle, b: EvidenceBundle): RunDiff;
export declare function renderDiff(d: RunDiff): string;
export {};
