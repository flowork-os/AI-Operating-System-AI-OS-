export interface Harness {
    version: string;
    sha: string;
    dir: string;
    files: Record<string, string>;
}
export declare function harnessDir(): string;
export declare function loadHarness(dir?: string): Harness;
/** System prompt = role + guardrails + template + lessons + all playbooks. Stable across runs (cacheable). */
export declare function systemPrompt(h: Harness): string;
export declare function playbook(h: Harness, name: string): string | null;
