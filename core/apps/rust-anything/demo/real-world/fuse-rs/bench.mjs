// Fuse.js against the Rust drop-in on a 50,000-string list: same results first, then time.
import Fuse from '../../build/fuse.mjs'
import { withRust } from './fuse.mjs'
const RustFuse = withRust(Fuse)
const words = 'the of and a to in is you that it he was for on are as with his they at be this have from or one had by word but not what all were we when your can said there use an each which she do how their if will up other about out many then them these so some her would make like him into time has look two more write go see number no way could people my than first water been call who oil its now find long down day did get come made may part apple banana cherry orange mango grape lemon peach melon berry river mountain forest ocean desert island valley canyon prairie glacier'.split(' ')
let s = 7
const r = () => (s = (s * 48271) % 2147483647) / 2147483647
const list = Array.from({ length: 50_000 }, () => Array.from({ length: 2 + Math.floor(r() * 5) }, () => words[Math.floor(r() * words.length)]).join(' '))
const queries = ['mango', 'riverr', 'forest ocean', 'glacer', 'apple banana cherry', 'the']
const best = (f, runs = 7) => { let t = Infinity; for (let i = 0; i < runs; i++) { const a = performance.now(); f(); t = Math.min(t, performance.now() - a) } return t }
for (const options of [{}, { includeScore: true }]) {
  const fuse = new Fuse(list, options), rust = new RustFuse(list, options)
  for (const q of queries) if (JSON.stringify(fuse.search(q)) !== JSON.stringify(rust.search(q))) throw new Error(`results differ for ${q}`)
  const js = best(() => { for (const q of queries) fuse.search(q) }) / queries.length
  const rs = best(() => { for (const q of queries) rust.search(q) }) / queries.length
  const jsNew = best(() => new Fuse(list, options)), rsNew = best(() => new RustFuse(list, options))
  console.log(`${JSON.stringify(options).padEnd(22)} search: Fuse ${js.toFixed(1)} ms, Rust ${rs.toFixed(1)} ms (${(js / rs).toFixed(1)}x) · new: Fuse ${jsNew.toFixed(1)} ms, Rust ${rsNew.toFixed(1)} ms`)
}
console.log('matches per query:', queries.map(q => new Fuse(list).search(q).length).join(', '))
