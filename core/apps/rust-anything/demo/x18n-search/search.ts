// The workload to profile: x18n's sidebar search over 50,000 keys, typed letter by letter, in TS.
// It runs in the x18n checkout given as the first argument (`.` when profiling from there).
import { resolve } from 'node:path'

const x18n = resolve(process.argv[2] ?? '.')
const { fuzzyScore } = await import(`${x18n}/packages/core/src/fuzzy.ts`)

const words = ['app', 'settings', 'title', 'button', 'save', 'cancel', 'error', 'message', 'user', 'profile', 'nav', 'home', 'dashboard', 'form', 'label', 'placeholder', 'tooltip', 'dialog', 'confirm', 'delete']
let seed = 7
const r = (k: number) => (seed = (seed * 1103515245 + 12345) % 2147483648) % k
const keys = Array.from({ length: 50000 }, (_, i) => Array.from({ length: 3 + r(3) }, () => words[r(words.length)]).join('.') + i)

export function matched(query: string, all: string[]): string[] {
  return all.map(key => ({ key, score: fuzzyScore(query, key) }))
    .filter(m => m.score >= 0)
    .sort((a, b) => b.score - a.score)
    .map(m => m.key)
}

let total = 0
for (const typed of ['s', 'se', 'set', 'sett', 'setti', 'settin', 'setting', 'n', 'na', 'nav', 'navh', 'navho', 'navhom', 'navhome']) {
  for (let i = 0; i < 3; i++) total += matched(typed, keys).length
}
console.log('matches', total)
