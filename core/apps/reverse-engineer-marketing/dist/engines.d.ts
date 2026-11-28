import type { EvidenceBundle } from "./index.js";
export type EngineId = "claude-code" | "codex" | "anthropic-api" | "none";
export interface EngineInfo {
    id: EngineId;
    label: string;
    available: boolean;
    detail: string;
}
export declare function detectEngines(): Promise<EngineInfo[]>;
export interface WriteOptions {
    model?: string;
    onText?: (delta: string) => void;
    onStatus?: (msg: string) => void;
    signal?: AbortSignal;
}
export declare function writeReport(engine: EngineId, bundle: EvidenceBundle, opts?: WriteOptions): Promise<{
    markdown: string;
    model?: string;
}>;
