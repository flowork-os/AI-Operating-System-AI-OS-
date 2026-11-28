// Calls every ported x18n core function through its shadow module: callers get the TS
// result, the Rust (wasm) result is compared on every call.
import * as keys from '../keys-rs/shadow/keys.shadow.ts'
import * as text from '../text-rs/shadow/text.shadow.ts'
import * as tree from '../message-tree-rs/shadow/message-tree.shadow.ts'
import * as locale from '../locale-rs/shadow/locale.shadow.ts'
import * as schema from '../schema-rs/shadow/schema.shadow.ts'
import * as plugins from '../plugins-rs/shadow/plugins.shadow.ts'
import * as contracts from '../contracts-rs/shadow/contracts.shadow.ts'
import * as project from '../project-rs/shadow/project.shadow.ts'

const modules = { keys, text, tree, locale, schema, plugins, contracts, project }
const mismatches: string[] = []
for (const m of Object.values(modules)) m.onMismatch(x => mismatches.push(`${x.fn}(${JSON.stringify(x.args)})`))

const source = 'export default {\n  nav: { home: "Home 😀", about: "Über uns" },\n}\n'
const edited = source.replace('Home 😀', 'Start 😁')
for (let i = 0; i < 200; i++) {
  const key = keys.joinKey(i % 2 ? 'common' : undefined, ['nav', `item${i}`, 'title'])
  keys.splitKey(key)
  keys.isKeyUnder(key, 'common:nav')
  keys.replaceKeyPrefix(key, 'common:nav', 'common:menu')
  const edits = text.diffText(source, edited)
  text.applyTextEdits(source, edits)
  text.rangeContains(edits[0]!.range, i)
  text.hashText(`${source}${i}`)
  const t = tree.applyMessageOps({ nav: { home: 'Home', about: 'About' }, [String(i)]: 'n' }, [
    { type: 'set', path: ['nav', `x${i}`], value: `v${i}` },
    { type: 'delete', path: ['nav', 'home'] },
  ])
  tree.isMessageTree(t)
  tree.buildTree([{ path: ['a', String(i)], value: i }])
  tree.pathId(['a', 'b', String(i)])
  const fallbacks = locale.resolveFallbacks('auto', ['en', 'de', 'de-AT', 'pt', 'pt-BR'], 'en')
  locale.fallbackChain(fallbacks, 'de-AT')
  locale.localeSpellingKey(i % 2 ? 'zh_CN' : 'pt-BR')
  schema.isJsonObject({ a: [i, 'x', null], b: { c: true } })
  plugins.extensionOf(`src/locales/de.${i % 2 ? 'JSON' : 'yaml'}`)
  contracts.toWireRange(source, i % source.length, (i * 7) % source.length)
  project.suppressedRanges(`// x18n-disable-next-line\nt("a${i}")\n/* x18n-disable */ t("b") /* x18n-enable */`)
  project.sourceHash(i % 3 ? `value ${i}` : i / 7)
  project.valueText(i % 2 ? i / 3 : null)
  project.isOutdated({ updatedAt: i }, { updatedAt: 100 })
  project.prefixMatches({ dynamic: 'prefix', key: 'nav' } as any, `nav.item${i}`)
}
// Exports that stay in TS are re-exported from the original unchanged.
const kept = [keys.keyMatcher(['nav.**'])('nav.a.b'), typeof text.createLineIndex, typeof locale.parseLocaleInfo]
const calls = Object.values(modules).reduce((n, m) => n + m.shadowStats.calls, 0)
console.log(JSON.stringify({ calls, mismatches: mismatches.length, first: mismatches.slice(0, 3), kept }))
