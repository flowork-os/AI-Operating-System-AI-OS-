// Saved runs (evidence bundle + optional report), shared by the MCP server and the web app.
import { mkdir, readdir, readFile, stat, writeFile } from "node:fs/promises";
import { homedir } from "node:os";
import { join } from "node:path";
export const DATA_DIR = process.env.REM_CACHE_DIR || join(homedir(), ".cache", "reverse-engineer-marketing");
export const RUNS_DIR = join(DATA_DIR, "runs");
const safe = (id) => id.replace(/[^a-z0-9._-]/gi, "");
export function runId(bundle) {
    return `${(bundle.target.domain ?? bundle.brand).replace(/[^a-z0-9.-]/gi, "_")}-${bundle.generatedAt.replace(/[-:T]/g, "").slice(0, 12)}`;
}
export async function saveRun(bundle) {
    const id = runId(bundle);
    await mkdir(RUNS_DIR, { recursive: true });
    const path = join(RUNS_DIR, `${id}.json`);
    await writeFile(path, JSON.stringify(bundle, null, 2));
    return { id, path };
}
export async function saveReport(id, markdown, meta) {
    await mkdir(RUNS_DIR, { recursive: true });
    await writeFile(join(RUNS_DIR, `${safe(id)}.md`), markdown);
    await writeFile(join(RUNS_DIR, `${safe(id)}.meta.json`), JSON.stringify({ ...meta, at: new Date().toISOString() }));
}
export async function loadRun(id) {
    try {
        return JSON.parse(await readFile(join(RUNS_DIR, `${safe(id)}.json`), "utf8"));
    }
    catch {
        throw new Error(`Unknown run "${id}"`);
    }
}
export async function loadReport(id) {
    try {
        const markdown = await readFile(join(RUNS_DIR, `${safe(id)}.md`), "utf8");
        const meta = JSON.parse(await readFile(join(RUNS_DIR, `${safe(id)}.meta.json`), "utf8").catch(() => "{}"));
        return { markdown, ...meta };
    }
    catch {
        return null;
    }
}
export async function listRuns(limit = 50) {
    let files;
    try {
        files = (await readdir(RUNS_DIR)).filter(f => f.endsWith(".json") && !f.endsWith(".meta.json"));
    }
    catch {
        return [];
    }
    const withTime = await Promise.all(files.map(async (f) => ({ f, t: (await stat(join(RUNS_DIR, f))).mtimeMs })));
    const recent = withTime.sort((a, b) => b.t - a.t).slice(0, limit);
    const out = [];
    for (const { f } of recent) {
        const id = f.slice(0, -5);
        try {
            const b = JSON.parse(await readFile(join(RUNS_DIR, f), "utf8"));
            const hasReport = await stat(join(RUNS_DIR, `${id}.md`)).then(() => true, () => false);
            out.push({ id, brand: b.brand, domain: b.target.domain, at: b.generatedAt, evidence: b.evidence.length, hasReport, logo: b.identity?.logo });
        }
        catch {
            // skip unreadable
        }
    }
    return out;
}
/** Saved runs for a domain, newest first (for `rem diff <domain>`). */
export async function runsForDomain(domain) {
    const d = domain.replace(/^https?:\/\//, "").replace(/^www\./, "").replace(/\/.*$/, "").toLowerCase();
    return (await listRuns(500)).filter(r => (r.domain ?? "").toLowerCase() === d).sort((a, b) => b.at.localeCompare(a.at));
}
/** A run id, a path to an evidence bundle JSON, or a domain (latest run). */
export async function resolveRun(ref) {
    if (/\.json$/i.test(ref))
        return JSON.parse(await readFile(ref, "utf8"));
    try {
        return await loadRun(ref);
    }
    catch {
        const latest = (await runsForDomain(ref))[0];
        if (!latest)
            throw new Error(`No saved run for "${ref}". Run \`rem ${ref}\` first.`);
        return loadRun(latest.id);
    }
}
