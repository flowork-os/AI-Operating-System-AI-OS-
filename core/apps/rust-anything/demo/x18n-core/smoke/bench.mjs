// TS original vs Rust (wasm, through index.cjs). Times are medians of 7 runs.
import { createRequire } from 'node:module'
const require = createRequire(import.meta.url)
const tsText = await import('/home/user/x18n/packages/core/src/text.ts')
const tsKeys = await import('/home/user/x18n/packages/core/src/keys.ts')
const tsUsages = await import('/home/user/x18n/packages/core/src/project/usages.ts')
const rsText = require('../text-rs/index.cjs')
const rsKeys = require('../keys-rs/index.cjs')
const rsProject = require('../project-rs/index.cjs')

const median = (fn) => {
  const times = []
  for (let i = 0; i < 7; i++) {
    const start = performance.now()
    fn()
    times.push(performance.now() - start)
  }
  return times.sort((a, b) => a - b)[3]
}
const big = 'const t = useI18n()\n// some code with ünïcödé and 😀\nt("nav.home")\n'.repeat(20000)
const bigEdited = `${big.slice(0, 500000)}X${big.slice(500001)}`
const marked = big.replaceAll('// some', '// x18n-disable-next-line\n// some')
const rows = [
  ['hashText, 1.4 MB', () => tsText.hashText(big), () => rsText.hashText(big)],
  ['diffText, 1.4 MB', () => tsText.diffText(big, bigEdited), () => rsText.diffText(big, bigEdited)],
  ['suppressedRanges, 1.9 MB, 20k markers', () => tsUsages.suppressedRanges(marked), () => rsProject.suppressedRanges(marked)],
  ['joinKey x 100k calls', () => { for (let i = 0; i < 1e5; i++) tsKeys.joinKey('ns', ['a', 'b']) }, () => { for (let i = 0; i < 1e5; i++) rsKeys.joinKey('ns', ['a', 'b']) }],
  ['isKeyUnder x 100k calls', () => { for (let i = 0; i < 1e5; i++) tsKeys.isKeyUnder('a.b.c', 'a.b') }, () => { for (let i = 0; i < 1e5; i++) rsKeys.isKeyUnder('a.b.c', 'a.b') }],
]
for (const [name, ts, rs] of rows) {
  ts(); rs()
  const t = median(ts), r = median(rs)
  console.log(`${name.padEnd(40)} TS ${t.toFixed(2).padStart(8)} ms   Rust ${r.toFixed(2).padStart(8)} ms   ${(t / r).toFixed(2)}x`)
}
