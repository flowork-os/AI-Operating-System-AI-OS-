import BitapSearch from '../search/bitap'
import normGenerator from '../tools/fieldNorm'
import { computeScoreSingle } from '../core/computeScore'
import { isBlank } from '../helpers/typeGuards'

export interface RelevanceOptions {
  isCaseSensitive?: boolean
  ignoreDiacritics?: boolean
  threshold?: number
  location?: number
  distance?: number
  ignoreLocation?: boolean
  findAllMatches?: boolean
  minMatchCharLength?: number
  ignoreFieldNorm?: boolean
  fieldNormWeight?: number
}

/**
 * Fuse's rank of one string of a string list for `pattern`: minus the score `search` gives it
 * (higher is better), or -Infinity when `search` would leave it out.
 */
export function relevance(
  text: string,
  pattern: string,
  options: RelevanceOptions
): number {
  checkOptions(options)
  if (isBlank(text)) {
    return -Infinity
  }
  const result = new BitapSearch(pattern, options).searchIn(text)
  if (!result.isMatch) {
    return -Infinity
  }
  const norm = normGenerator(options.fieldNormWeight ?? 1, 3).get(text)
  const score = computeScoreSingle(
    [{ score: result.score, norm, key: null } as any],
    { ignoreFieldNorm: options.ignoreFieldNorm ?? false }
  )
  return -score
}

const FLAGS = ['isCaseSensitive', 'ignoreDiacritics', 'ignoreLocation', 'findAllMatches', 'ignoreFieldNorm']
const NUMBERS = ['threshold', 'location', 'distance', 'minMatchCharLength', 'fieldNormWeight']

/** Options of other types go to the original Fuse: the port takes only these. */
function checkOptions(options: RelevanceOptions): void {
  if (options === null || typeof options !== 'object' || Array.isArray(options)) {
    throw new TypeError('options must be an object')
  }
  for (const [key, value] of Object.entries(options)) {
    if (value === undefined) continue
    if (FLAGS.includes(key)) {
      if (typeof value !== 'boolean') throw new TypeError(`${key} must be a boolean`)
    } else if (NUMBERS.includes(key)) {
      if (typeof value !== 'number' || !Number.isFinite(value)) throw new TypeError(`${key} must be a finite number`)
      if (key === 'location' && !Number.isInteger(value)) throw new TypeError('location must be an integer')
    } else {
      throw new TypeError(`unsupported option ${key}`)
    }
  }
}
