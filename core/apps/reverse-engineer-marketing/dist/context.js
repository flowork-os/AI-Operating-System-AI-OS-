/** Attach items to the evidence that summarizes them, dropping duplicates. */
export function addContent(ctx, items, evidenceId) {
    for (const it of items) {
        if (!it.url || ctx.content.some(c => c.id === it.id))
            continue;
        ctx.content.push({ ...it, evidence: evidenceId });
    }
}
export async function runSource(ctx, source, fn) {
    const t0 = Date.now();
    try {
        await fn(ctx);
        ctx.store.runs.push({ source, status: "ok", ms: Date.now() - t0 });
    }
    catch (err) {
        const reason = err instanceof Error ? err.message : String(err);
        ctx.store.runs.push({ source, status: "error", reason, ms: Date.now() - t0 });
        ctx.log(`  ! ${source}: ${reason}`);
    }
}
export function skip(ctx, source, reason) {
    ctx.store.runs.push({ source, status: "skipped", reason, ms: 0 });
}
