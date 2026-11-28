# Real-world ports

The crates rust-anything produced in the runs described in
[`docs/real-world-languages.md`](../../docs/real-world-languages.md): each holds the Rust port
(`src/port.rs`), the generated bridge, `cases.jsonl` (the recorded behavior of the original) and,
where used, `inputs.jsonl` (extra inputs passed to `rust-anything record --inputs`).

| Crate | Original | Where it came from |
| --- | --- | --- |
| `go-path-rs` | Go's `path` package | `$(go env GOROOT)/src/path` (Go 1.24), as module `example.com/gopath`, with `internal/bytealg` calls replaced by their `strings` equivalents |
| `ruby-shellwords-rs` | Ruby's `shellwords.rb` | `RbConfig::CONFIG["rubylibdir"]/shellwords.rb` (Ruby 3.3), as `lib/shellwords.rb` of a project with a `Gemfile` |
| `python-colorsys-rs` | Python's `colorsys.py` | CPython 3.13's `Lib/colorsys.py`, as `src/colorsys_pkg/colorsys.py` of a project with a `pyproject.toml` |
| `java-jdk-rs` | JDK 21 behind `original/Jdk.java` | `original/Jdk.java` in `src/main/java/com/example/jdk/` of a project with a `pom.xml` |
| `c-libc-rs` | glibc behind `original/facade.c` | `original/facade.c` in `src/` of a project with a `Makefile` |
| `vercel-ms-rs` | [vercel/ms](https://github.com/vercel/ms) (MIT) | a clone at commit `4ff48ce`, with the crate at `rust/index-rs` (where `bench_batch.mjs` finds `src/index.ts`) |
| `fuse-rs` | [Fuse.js](https://github.com/krisk/Fuse) (Apache-2.0) | a clone at commit `edf2fb6` with `adapter/relevance.ts` copied to `src/rust/relevance.ts`, bundled by `esbuild src/rust/relevance.ts --bundle --format=esm --platform=node --outfile=build/relevance.mjs` and recorded with `--module build/relevance.mjs`; `bench.mjs` also needs Fuse bundled to `build/fuse.mjs` |

The originals are not copied here: the standard-library sources keep their own licenses, and the
ports name theirs in `src/port.rs`. To rerun one, put the original in place as described, point
`rust-anything.json`'s `root` at that project, and run:

```sh
rust-anything record <crate> --inputs <crate>/inputs.jsonl   # or keep the recorded cases.jsonl
rust-anything gate <crate>
rust-anything bench <crate>
```
