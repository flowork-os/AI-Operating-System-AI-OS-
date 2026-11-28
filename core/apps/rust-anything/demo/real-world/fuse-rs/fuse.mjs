// A drop-in for `Fuse` that searches string lists in Rust (all cores) and hands everything else
// (object lists with keys, extended or token search, includeMatches, custom sortFn or getFn) to
// the original Fuse, so results are always Fuse's.
import { createRequire } from 'node:module'

const { RelevanceBatch } = createRequire(import.meta.url)('./index.cjs')

const PORTED = new Set([
  'isCaseSensitive', 'ignoreDiacritics', 'ignoreLocation', 'findAllMatches', 'ignoreFieldNorm',
  'threshold', 'location', 'distance', 'minMatchCharLength', 'fieldNormWeight'
])
const HANDLED = new Set([...PORTED, 'includeScore', 'shouldSort', 'keys'])

const portable = (docs, options) =>
  Array.isArray(docs) && docs.every((d) => typeof d === 'string') &&
  Object.entries(options).every(([k, v]) => v === undefined || HANDLED.has(k)) &&
  (options.shouldSort === undefined || options.shouldSort === true) &&
  (options.keys === undefined || (Array.isArray(options.keys) && options.keys.length === 0)) &&
  (options.location === undefined || Number.isInteger(options.location)) &&
  [...PORTED].every((k) => {
    const v = options[k]
    return v === undefined || (typeof v === 'boolean' ? !k.match(/threshold|location|distance|Length|Weight/) : Number.isFinite(v) && typeof v === 'number')
  })

export function withRust(Fuse) {
  return class RustFuse {
    constructor(docs, options = {}, index) {
      this._docs = docs
      this._options = options
      if (index === undefined && options && portable(docs, options)) {
        this._batch = new RelevanceBatch(docs)
        this._portOptions = Object.fromEntries(Object.entries(options).filter(([k, v]) => PORTED.has(k) && v !== undefined))
      } else {
        this._fuse = new Fuse(docs, options, index)
      }
    }

    search(query, options) {
      if (this._fuse || typeof query !== 'string') {
        return (this._fuse ??= new Fuse(this._docs, this._options)).search(query, options)
      }
      const { limit = -1 } = options || {}
      if (!query.trim()) {
        const all = this._docs.map((item, refIndex) => ({ item, refIndex }))
        return typeof limit === 'number' && limit > -1 ? all.slice(0, limit) : all
      }
      let order = this._batch.rank(query, this._portOptions, -Number.MAX_VALUE)
      if (typeof limit === 'number' && limit > -1) order = order.subarray(0, limit)
      const scores = this._options.includeScore ? this._batch.run(query, this._portOptions) : null
      const out = new Array(order.length)
      for (let i = 0; i < order.length; i++) {
        const refIndex = order[i]
        out[i] = scores
          ? { item: this._docs[refIndex], refIndex, score: -scores[refIndex] }
          : { item: this._docs[refIndex], refIndex }
      }
      return out
    }
  }
}
