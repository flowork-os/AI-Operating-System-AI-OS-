import type { EvidenceBundle } from "../index.js";
export interface ValidationResult {
    ok: boolean;
    score: number;
    checks: {
        name: string;
        ok: boolean;
        detail: string;
    }[];
}
export declare function validateReport(markdown: string, bundle: Pick<EvidenceBundle, "evidence" | "unknowns">): ValidationResult;
