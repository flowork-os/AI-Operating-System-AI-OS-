import type { EvidenceBundle } from "./index.js";
export declare const DATA_DIR: string;
export declare const RUNS_DIR: string;
export declare function runId(bundle: EvidenceBundle): string;
export declare function saveRun(bundle: EvidenceBundle): Promise<{
    id: string;
    path: string;
}>;
export declare function saveReport(id: string, markdown: string, meta: {
    engine: string;
    model?: string;
}): Promise<void>;
export declare function loadRun(id: string): Promise<EvidenceBundle>;
export declare function loadReport(id: string): Promise<{
    markdown: string;
    engine?: string;
    model?: string;
} | null>;
export interface RunSummary {
    id: string;
    brand: string;
    domain?: string;
    at: string;
    evidence: number;
    hasReport: boolean;
    logo?: string;
}
export declare function listRuns(limit?: number): Promise<RunSummary[]>;
/** Saved runs for a domain, newest first (for `rem diff <domain>`). */
export declare function runsForDomain(domain: string): Promise<RunSummary[]>;
/** A run id, a path to an evidence bundle JSON, or a domain (latest run). */
export declare function resolveRun(ref: string): Promise<EvidenceBundle>;
