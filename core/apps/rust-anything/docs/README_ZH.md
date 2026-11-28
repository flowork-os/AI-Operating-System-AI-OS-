<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="rust-anything 螃蟹图标，嘴部为一个代码标签">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">作者：<a href="https://github.com/erkamyaman">erKam Yaman</a></p>
<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · 简体中文 · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>本译文由社区维护，可能落后于<a href="../README.md">英文 README</a>。</sub></p>

<p align="center"><em>用 Rust 重写你的整个应用，并在每一步都保持正常运行。</em></p>

<p align="center"><em>无论是命令行工具（CLI）、服务端还是库，都能逐块迁移，每一步都与原实现严格比对校验。</em></p>

<p align="center">Node.js 与 TypeScript · Python · C · Go · Ruby · Java · PHP 与 C# 处于预览阶段</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io version"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm version"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 languages">
  <a href="#适配工具"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="Works with 4 agents"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Tests"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT license"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub stars"></a>
</p>

<p align="center">最高提速 20 倍 · 回放 38,251 条录制用例 · 0 差异 · 一条命令搞定</p>

<p align="center">
  <img src="assets/race.gif" alt="在 x18n 的 50,000 个键中搜索 user.profile：TypeScript 耗时 143 ms，rust-anything 批处理仅耗时 6.9 ms，且每次击键的结果完全一致。" width="820">
</p>

**逐块将你的整个应用重写为 Rust。** rust-anything 会先录制你现有的 Node.js（TypeScript/JavaScript）、Python、C、Go、Ruby 或 Java 应用的行为，然后每重写一块 Rust 代码就对照录制结果进行校验，合格后再继续推进，直到整个应用变成纯 Rust。无论是 CLI、HTTP 服务端还是程序库都能适用，由你的编程智能体（或你本人）来编写 Rust 代码。它只能捕获录制用例覆盖到的行为，详见[它捕获不到什么](#它捕获不到什么)。如果只想加速慢的部分，也可以只针对热点路径逐个迁移：

| 真实工作负载（结果与原实现完全一致） | 原实现 | 使用 rust-anything |
| --- | ---: | ---: |
| x18n 侧边栏搜索，50,000 个键（TypeScript，Node） | 每次查询 10 ms | **0.5 ms：提速 20 倍** |
| 浏览器端同一搜索（wasm，单线程） | 10 ms | **0.95 ms：提速 11.5 倍** |
| 20,000 个字符串的 `slugify`（Python） | 98 ms | **提速 17 倍** |
| Ruby 标准库 `Shellwords.shellescape`，50,000 个值 | 88 ms | **提速 11.8 倍** |
| 50,000 个字符串的 `Slugify`（Go） | 49 ms | **提速 4 倍** |
| 50,000 个字符串的 `slugify`（Java） | 43 ms | **提速 3 倍** |

以上数据均在 4 核环境下测得；每一项数字在 [`demo/`](../demo) 中都有对应的基准测试，并且都会先校验结果完全一致。逐个小函数调用 Rust 通常比 JIT 更*慢*；rust-anything 会找出真正值得迁移的循环，再把整个循环搬过去。

> rust-anything 是一个独立项目，与 Rust Project 或 Rust Foundation 没有任何关联或背书关系。“Rust” 是 Rust Foundation 的商标。

## 快速开始

将下面这段话粘贴给 Claude Code、Codex、Cursor 或 Gemini CLI，让你的智能体自动完成安装：

```text
安装 rust-anything：先运行 `cargo install rust-anything`，再运行 `rust-anything setup`。
完成后告诉我什么时候需要重启你。
```

或者自行执行安装：

```sh
cargo install rust-anything   # 从 crates.io 安装
rust-anything setup           # 自动注册到 Claude Code、Codex、Cursor 和 Gemini CLI
```

还没有安装 Rust 工具链？每个 [GitHub release](https://github.com/erkamyaman/rust-anything/releases) 都附带了 macOS、Linux 和 Windows 的预编译二进制文件；对于 JavaScript 项目，也可以直接运行 `npm install -g rust-anything` 安装相同的二进制文件。

在 Claude Code 中还可以将其作为插件安装（包含 MCP 服务器和工作流技能，需确保上述 CLI 已加入 `PATH`）：

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` 会把 MCP 服务器添加到它检测到的每一个智能体中，并把工作流技能安装到对应智能体读取技能的目录。它会保留你的其他配置，支持重复安全运行，且可以用 `--remove` 移除这些配置（不会恢复 `setup` 曾覆盖更新过的同名旧条目）。之后你就可以直接向智能体提需求，例如：

- *"使用 rust-anything 将这个 CLI 端到端重写为 Rust，并证明其行为完全一致。"*
- *"这个搜索感觉很慢。用 rust-anything 做性能分析，把热点循环迁移到 Rust。"*
- *"用 rust-anything 规划 `src/parser/` 向 Rust 的迁移；先迁移第一个单元并验证。"*
- *"将 `rust/text-rs` 中的 Rust 移植版与原实现做基准对比，告诉我是否值得上线。"*

### 适配工具

| 智能体 | `rust-anything setup` 会写入的配置 |
| --- | --- |
| Claude Code | `~/.claude.json` 中的 MCP 服务器、`~/.claude/skills/` 中的技能 |
| Codex | `~/.codex/config.toml` 中的 MCP 服务器、`~/.codex/skills/` 中的技能 |
| Cursor | `~/.cursor/mcp.json` 中的 MCP 服务器 |
| Gemini CLI | `~/.gemini/settings.json` 中的 MCP 服务器 |
| 其他任意 MCP 客户端 | 手动将 `rust-anything mcp` 添加为 stdio 服务器（见[安装](#安装)） |

修改任何已有配置文件前，`setup` 都会在同目录下保存一份备份（`<file>.rust-anything.bak`）。

你也可以手动执行每一步：

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile 定位到循环中的 fuzzyScore，bridge --batch 生成 Rust crate，gate 通过全部 2000/2000 条录制用例，基准测试显示比 TS 快 20.7 倍。" width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # 找出热点函数及其调用方
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# 编写 src/port.rs（或交给智能体编写），然后运行：
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # 每条录制用例都必须一致
rust-anything bench rust/fuzzy-rs                      # 是否更快？由基准测试结论说了算
rust-anything gate rust/fuzzy-rs                       # 通过该门禁才算完成
```

rust-anything 并不负责自动翻译代码：具体 Rust 代码由你的编程智能体（Claude Code、Codex、Cursor 等）或你本人编写。rust-anything 提供的是智能体难以靠猜测稳妥获得的东西：时间花在哪里、先迁移什么以及按什么顺序迁移、让其余代码无需改动 API 就能调用 Rust 的桥接层、移植代码必须匹配的精确行为、安全的上线方式，以及判断迁移是否达标的门禁。

## 支持语言

| 语言 | 迁移单元 | 桥接层 | 录制与回放方式 |
| --- | --- | --- | --- |
| TypeScript/JavaScript | 文件夹或单文件 | napi-rs 或 wasm-bindgen，配合生成的二进制传输协议；支持类和异步 | Node 直接运行 `.ts` 源码 |
| Python | 包或模块 | PyO3（abi3），直接类型转换，保留类型化异常 | Python 直接导入原模块 |
| C | `.c` 文件 | 与原函数同名的 `extern "C"` 函数及头文件 | 将原代码编译为共享库，通过 ctypes 调用，每条用例独立 fork |
| Go | 包（package） | 类型化 cgo 调用与生成的二进制传输协议，封装为保持原 API 的包 | 生成独立的 Go 驱动模块进行构建运行 |
| Ruby | 包含模块函数的文件或文件夹 | 挂载在原模块名下的 magnus 扩展 | 生成的 Ruby 驱动 |
| Java | 包含 `public static` 方法的包 | 类型化 JNI 与生成的二进制传输协议，封装为保持原方法的包装类 | 生成的反射驱动 |
| PHP（预览） | 包含函数和 `public static` 方法的文件夹 | 下一步规划：基于 C ABI 的 PHP FFI | 现已支持整应用级工作流：`app record`、`app replay` 和前门代理，适用于 CLI 与服务端（`php -S`） |
| C#（预览） | 包含 `public static` 方法的文件夹 | 下一步规划：基于 C ABI 的 P/Invoke | 现已支持整应用级工作流：`app record`、`app replay` 和前门代理，适用于 CLI 与 ASP.NET 服务端（`dotnet <app>.dll`） |

除 C 语言外，每种语言都支持生成批处理类（`--batch`）：数据只需跨边界传入一次并常驻 Rust 侧，每次调用即可在全部 CPU 核心上并行处理所有条目。

语言会根据代码库自动检测（依次检查 `go.mod`、`pom.xml`、`.csproj` 或 `.sln`、`pyproject.toml`、`Gemfile`、`composer.json`、`package.json`，否则统计最常见的源码文件）；也可以通过 `--lang` 手动指定。类型信息直接从源码提取：TS 类型、Python 类型注解、C/Go/Java/C# 函数签名、Ruby YARD 标签、PHP 类型与 phpdoc；对于未标注类型但按数值使用的参数，会自动推断为数值类型。

PHP 目前处于预览阶段：`analyze` 可为 PHP 应用生成迁移规划（支持 Composer 包与 PSR-4 自动加载、识别松散比较和整数溢出转浮点等风险、将 Composer 包映射为 Rust crate），并且支持对 PHP CLI 或服务端进行录制、回放与 Rust 前门接管。通过 PHP FFI 将单元逐个迁入 Rust 是下一步计划（[issue #2](https://github.com/erkamyaman/rust-anything/issues/2)）。

C# 同样处于预览阶段：`analyze` 会读取 `.csproj` 工程及其 NuGet 包（映射为 crate），将 `using` 指令解析到对应目录，并标记 C# 特有的语义差异（`decimal`、`dynamic`、LINQ 延迟查询、`Task`、`lock`、反射）。现已支持对 C# CLI 或 ASP.NET 服务端进行录制、回放与 Rust 前门接管；通过 P/Invoke 迁移单个单元将在后续支持。

## 工作原理

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 耗时所在    先迁哪里    生成 Rust    录制原实现   你或智能体    逐条比对   是否更快？   生产环境     通过才算
                       crate 与包装  的真实行为   编写实现     录制用例   给出结论     双跑校验     正式完成
```

原实现始终是唯一事实来源（Source of Truth）：`record` 会在边界用例（以及你提供的输入）上运行原实现并记录其返回值或抛出的异常；`diff` 将每条用例在 Rust 实现上重放；在所有用例全部一致且 `gate` 检查通过之前，不会对外交付。整个过程中，调用方始终沿用原有的 API。

整应用迁移也会沿用这套单元级闭环，只是外层多了一套从外部证明整套程序行为一致的框架（见[迁移整个应用](#迁移整个应用)）：

```
analyze --whole-app ──> app record ──> app front-door ──> 逐单元走完上述闭环，再执行 app wire ──> app lift
 应用形态、全部依赖、      从外部录制       Rust 接管入口；       单元通过门禁后切由 Rust 响应：          纯 Rust 应用，
 需要敲定的决策            应用行为         其余暂由原实现兜底     回放仍 100% 通过，回退率下降            由回放验证
```

## 核心闭环命令

| 步骤 | 命令 | 作用 |
| --- | --- | --- |
| 0. 性能分析 | `rust-anything profile <repo> -- node bench.mjs` | 在对应语言的性能分析器下运行真实负载（node、cProfile、`go test` pprof、JFR、Ruby tracer）：按总耗时（inclusive time）列出热点函数、调用方及适合批处理的循环；标记已经过编译加速的代码（numba、Cython、JAX），提示迁移收益有限 |
| 1. 规划 | `rust-anything analyze <repo>` | 划分迁移单元、迁移顺序、带 `file:line` 的风险提示、各单元桥接方式、依赖到 crate 的适配度、最佳首批迁移对象；加上 `--whole-app` 还会输出入口点与应用形态、全部（导入或声明的）依赖及其对应 crate、强耦合单元组（相互导入的单元同步迁移）以及带推荐答案的编号决策清单 |
| 2. 桥接 | `rust-anything bridge <repo> <unit>` | 生成包含绑定代码（`lib.rs` 以及供原语言加载的包装层）和待迁移桩代码（`port.rs`）的 crate；`--batch fn:param` 会额外生成一个类，将大量 `param` 数据常驻保存在 Rust 侧 |
| 3. 录制 | `rust-anything record <crate>` | 在自动生成的边界用例（非 ASCII 字符、emoji、`-0`、`NaN`、期望浮点却传入整数等）以及覆盖所有参数语义陷阱的输入（字符串长度与大小写、有符号除法、溢出边界、浮点格式化、Map 与排序顺序）上运行原实现，保存为 `cases.jsonl`；对于数值代码可用 `--float-tolerance 1e-9` 允许在该相对误差范围内匹配 |
| 3. 构建 | `rust-anything build <crate>` | 构建 Rust 侧产物：`.node`、wasm 包、Python 扩展或共享库 |
| 3. 比对 | `rust-anything diff <crate>` | 按原调用方实际调用的方式在 Rust 上重放所有录制用例，列出所有不一致项 |
| 3. 基准测试 | `rust-anything bench <crate>` | 分别测量原实现与包含桥接开销在内的 Rust 实现运行录制用例的耗时 |
| 4. 影子模式 | `rust-anything shadow <crate>` | 无侵入替换模块：同时运行新旧两套实现，对外返回原实现结果并上报差异；可通过 `RUST_ANYTHING_MODE=old\|shadow\|new` 切换模式 |
| 5. 门禁 | `rust-anything gate <crate>` | 检查 fmt、clippy `-D warnings`、测试、`unsafe` 审计、无未迁移桩函数、原实现每条报错路径均有对应的失败录制用例、原实现返回错误的位置不能出现 `unwrap`/`expect`/`panic!`（除非显式标注 `// INFALLIBLE: <原因>`）、构建、API 与行为一致性 |
| 智能体接入 | `rust-anything setup` | 向你的编程智能体注册 MCP 服务器（`rust-anything mcp`，将每个步骤暴露为工具）和工作流技能（[`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)） |

## 迁移整个应用

最终目标是交付一个行为与原实现一致的纯 Rust 应用，同时保留原实现作为参照基准。具体 Rust 代码由你的智能体编写；rust-anything 负责排定工作顺序、搭建脚手架并验证每一步。[整应用迁移技能（whole-app skill）](../skills/rust-anything/whole-app.md) 会引导智能体完成全过程，首先从只有你能拍板的决策开始：

- **深度访谈（Grilling）**：智能体分轮提问（每个问题均附推荐答案），直到敲定迁移所依赖的全部决策，随后将每项决策以 ADR（架构决策记录）形式写入 `rust/DECISIONS.md`，并在 `rust/GLOSSARY.md` 中建立原项目术语到 Rust 命名的映射表。
- **调研（Research）**：后台智能体查阅每个外部依赖的一手源码，编写 `rust/research/<topic>.md`，列出发现的所有语义陷阱。
- **跨会话接力（Across sessions）**：`rust/MAP.md` 记录每个单元的状态；每次会话开始前先认领一个单元，每个检查点都会生成 `rust/HANDOFF.md` 交接给下一次会话。同一波次内的单元可由子智能体并行迁移。
- **切换上线（Cutover）**：智能体完成它能做的部分，并生成交互式脚本 `rust/cutover.sh`，引导你完成只有人工才能执行的步骤（部署、DNS、密钥配置），每一步都附带回滚方案。

深度访谈、源码调研等实践借鉴自 [Matt Pocock's skills](https://github.com/mattpocock/skills)。

首先做规划：`rust-anything analyze . --whole-app` 会给出应用形态（CLI、服务端或库）与入口点、全部（导入或声明的）外部依赖及其 Rust crate 适配度、按耦合关系编排的迁移波次（相互导入的单元同步迁移），以及带推荐答案的编号决策项（保留原样的单元、受阻单元、没有或只有部分替代 crate 的依赖）。

接着从外部验证整个程序。`record` 和 `diff` 用于验证单个单元；`app record` 和 `app replay` 则面向黑盒应用，适用于全部六种语言的 CLI 与服务端：

```sh
rust-anything app record . -- python3 cli.py          # 运行原应用的命令
rust-anything app replay .                            # 原应用必须 100% 通过
rust-anything app replay . --build "target/release/mytool"
```

- `app record` 会用以下输入运行原应用：项目自带文档中的示例（Markdown 和 shell 文件中的 `$ mytool ...` 命令行及其引用的文件）、通过 `--inputs` 传入的 JSONL 文件（`{"name", "args", "stdin", "env", "files"}`），以及基于这些用例衍生出的语义陷阱（非 ASCII 与 emoji 字符串、负数除法与取模、整数溢出、极大/极小浮点数、Map 键顺序、缺失文件）。每条用例会运行两次；两次输出不同的部分会自动变为 `[..]` 通配符。可通过 `--normalize timestamps|uuids|key-order` 或 `--normalize name=regex` 添加归一化规则，并随用例一并保存。
- 用例以 [trycmd](https://docs.rs/trycmd) 文件格式存放在 `rust/app-cases/` 中：`<case>.toml`（argv、env、退出码）、`.stdin`、`.stdout`、`.stderr`、`.in/`（输入文件）和 `.out/`（输出文件）。你可以直接阅读和手工修改这些文件；一旦有了 Rust 二进制产物，就可以在 Rust 测试中用 `trycmd` 直接运行它们。
- `app replay` 会针对这些用例运行任意构建产物，输出 `passed/total`，在 `rust/app-cases/replay-report.md` 中为每条失败用例生成 diff，并在存在任何不一致时以非零状态码退出。如果构建产物会向 `RUST_ANYTHING_FALLBACK_LOG` 指定的文件追加日志（每次回退到原实现记一行），例如下文的前门程序，回放报告还会统计回退率。
- `app replay --case <name>` 可按报告中的用例名单独重跑某条用例，方便在全量回归前快速定位并修复单个不一致问题。

随后将入口点迁入 Rust，并逐个单元把命令切给 Rust：

```sh
rust-anything app front-door .                            # 生成 rust/app：所有命令暂时都调原实现
rust-anything app wire . textkit --command upper          # 待 textkit-rs 通过 gate 后接入
# 在 rust/app/src/units/textkit.rs 中编写胶水代码，然后：
rust-anything app wire . textkit                          # 再次 100% 通过，同时回退率降低
```

- `app front-door` 会脚手架生成以应用命名的 Rust 二进制项目 `rust/app`：基于 clap 为录制用例中的命令和参数生成解析器，每条命令都会带着相同的 argv、stdin 和环境变量调用原实现，并透传其输出与退出码。每次回退都会被计数，因此刚生成的前门程序回放结果是 100% 通过且 100% 回退（生成后会自动构建并回放一遍以作演示）。该命令绝不会覆盖已存在的 `rust/app`：一旦生成，代码就完全归你掌控。
- `app wire <repo> <unit> --command <name>` 会对该单元的 crate 运行 `gate`（若刚通过可加 `--skip-gate`），将其作为库依赖加入 `rust/app`，首次生成 `src/units/<unit>.rs` 供你或智能体填写胶水逻辑（解析参数、调用 `<crate>::port`、打印与原实现一致的输出），将对应命令路由过去，然后重新构建并回放。在最终收口（lift）前，设置 `RUST_ANYTHING_UNIT_<NAME>=original` 可随时将某个已接入单元切回原实现。

对于未指定子命令的命令行调用（无参数、未知命令、用法错误），可以将应用自身名称作为命令名来挂载（`--command mytool`）。

当回放 100% 通过、回退率降为 0，且所有单元均已通过 `gate` 时，就可以将其收口为纯 Rust 应用：

```sh
rust-anything app lift .
```

- 在上述两个条件同时满足前，`app lift` 会拒绝执行并明确指出卡点：哪些用例仍在回退、哪些胶水代码还是桩函数、哪些单元未通过 gate。
- 它会先在副本上操作：移除回退路径与应急开关，将各个单元 crate 转为 `rust/app` 的普通库依赖（去掉 `cdylib`、绑定代码和生成的包装层），并添加 `rust/app/tests/app_cases.rs` 以便 `cargo test` 通过 trycmd 运行 `rust/app-cases`，从此 CI 只需要 cargo 即可运行。
- 接着运行收口检查清单：对每个单元和 `rust/app` 执行 fmt、clippy `-D warnings` 与测试，针对 `rust/DECISIONS.md` 中列出的已安装目标平台逐一构建或检查，检查运行时读取的文件和未嵌入的资源目录，并对纯 Rust 二进制运行全量回放。只有全部通过后，变更才会写回工作区。原项目文件全程不会被修改。

### 服务端应用

这套命令同样适用于验证 HTTP 服务端。`--http` 表明该命令会启动一个服务端，端口从环境变量 `PORT` 或命令中的 `{port}` 占位符获取（如果服务端总是监听固定端口，可使用 `--port`）：

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum：所有路由默认反向代理到原服务
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- 请求来源包括项目文档中的 `curl` 命令（`curl -X POST -d ... http://localhost:8080/x`）、`--inputs`（`{"name", "method", "path", "headers", "body"}`）以及语义陷阱：路径段和查询参数会按与 CLI 参数相同的规则替换陷阱值，请求体按文本与 JSON 陷阱替换，并额外包含一个未知路由请求。每次运行都会全新启动服务端并按名称顺序发送请求，从而保留请求之间的状态。
- 用例保存为 `rust/app-cases/http/<case>.toml`（请求信息、状态码和需要校验的响应头）与 `<case>.body`（响应体，两次运行不一致的部分替换为 `[..]`）。`Date`、`Server` 等每次响应都会变的头会自动剔除；不需要关心的响应头行也可以直接删掉。
- 前门是一个 axum 服务端，它会在独立端口拉起原服务，并将尚无单元接管的路由全部代理过去。`wire --route` 接受 axum 路由写法：`METHOD /path/{param}`、不写方法名的 `/path`（匹配任意方法）、以及兜底用的 `*`；胶水函数会收到路由、路径参数和完整请求。`lift` 会移除代理逻辑；此后 HTTP 用例即可在 CI 中通过 `app replay` 运行。

### 程序库

程序库没有独立进程可供回放：它的公共 API 本身就是前门，而各个单元的录制用例就是行为证明。

```sh
rust-anything app front-door .        # rust/app：包含公共 API 的 Rust crate
# 每个单元依次走完核心闭环：bridge、record、port.rs、build、diff、gate；然后：
rust-anything app wire . textkit-rs   # 从 rust/app 重新导出；原项目导入其影子模块
rust-anything app replay .            # 运行所有已接入单元的用例；回退率 = 仍在原实现中的导出项占比
rust-anything app lift .
```

- 当仓库既没有 `main` 也没有服务端时（否则可加 `--library`），`app front-door` 会扫描全部公共 API（所有单元的导出项），并脚手架生成作为库 crate 的 `rust/app`。每个接入的单元都会成为它的一个模块：`pub use textkit_rs::port as textkit;`。
- `app wire` 接收由 `bridge` 生成的 crate，运行 `gate`，并写出该单元的影子替换模块：原包会导入它来替代原单元，从而让调用方在保持原 API 不变的前提下调用到 Rust 实现。`RUST_ANYTHING_UNIT_<NAME>=original` 可将该单元切回原实现（C 语言只需在编译时不加影子模块的编译参数即可）。
- `app replay` 会通过绑定层运行所有已接入单元的录制用例。回退率表示尚未由 Rust 接管的公共导出占比：包括未接入的单元，以及 `bridge` 保留在原语言中的导出项。
- `app lift` 要求回退率为 0 且所有单元通过 `gate`；它会剥离各单元的绑定、包装与影子层，让 `rust/app` 成为一个纯粹的 Rust 库。它不会修改任何 `port.rs`，因此此前通过绑定验证过的用例依然有效；收口检查清单也会提示原项目中是否还有文件在导入影子模块。

上述五个命令同样已封装为 MCP 工具：`app_record`、`app_replay`、`app_front_door`、`app_wire` 和 `app_lift`。

## 案例研究：x18n 核心库

x18n 核心库中所有无需更改 API 即可迁移的 29 个函数已全部通过 rust-anything 完成移植：每项门禁均已通过，7,925 条录制用例完全一致。随后 `rust-anything bench` 显示，从 JS 调用这些单函数移植版反而比原 TS 代码更慢，因为跨桥接层调用的开销超过了函数本身的计算开销。完整报告见 [`demo/x18n-core`](../demo/x18n-core/README.md)。这条经验已经内化在工具流程中：在发布移植版本前，务必先用 `bench` 实测。

## 热点路径：把数据留在 Rust 侧

每处理一个条目就跨桥接调用一次 Rust，会为每个条目支付一次桥接开销，往往跑不过 JIT。真正能赢的做法是把整个循环搬进 Rust：`profile` 会找出这个循环，而 `--batch` 会生成一个类，一次性把数据传入 Rust，每次调用即可利用全部核心并行遍历处理，并返回类型化数组结果。

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore：占整个运行时间的四分之一，由 `matched` 按键逐个调用：将其批处理化
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // 初始化一次
const order = search.rank(query, 0)               // 每次击键调用：返回按最佳匹配排序的索引
```

`port.rs` 中的 `FuzzyScoreIndex` 结构体用“预先准备数据一次、再直接排序（`rank`）”的策略替代了默认循环：它保存转小写后的键及各自的字符掩码、一张记录每个键中常用字符首次出现位置的索引表（单字符查询只需看一列），以及上一次查询的匹配结果（输入 `s` 后再输入 `se` 时，只对 `s` 命中的子集重新打分）。在 x18n 侧边栏对 50,000 个键逐字输入的搜索测试中，结果完全一致：

| 方案 | 每次查询耗时 | 对比 TS |
| --- | ---: | ---: |
| TS：`map(fuzzyScore)`、过滤、排序 | 10 ms | 1x |
| TS 采用与索引相同的缩窄剪枝策略 | 4.1-5.4 ms | 2x |
| 同一 Rust 移植版，按单个键逐次调用 | - | 0.2-0.4x |
| `FuzzyScoreBatch`，默认索引（4 核） | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` + `FuzzyScoreIndex`（napi，4 核） | 0.45-0.56 ms | **18-22x** |
| 同上，使用 wasm（单线程） | 0.95 ms | **11.5x** |

即便与采用同样缩窄优化的 TS 相比，Rust 仍然快 7–12 倍（wasm 快 5 倍）。把返回的索引还原成键名时建议用普通循环：`Array.from(order, i => keys[i])` 会多花 20 倍时间（0.4 ms）。

所有支持语言都具备批处理能力，甚至在单次调用跑输原实现的地方，批处理依然能胜出。在 4 核上运行相同工作负载，结果与错误完全一致（各语言 demo 目录中均附有基准测试）：

| 语言 | 工作负载 | 原实现 | 逐次调用移植版 vs 原实现 | 批处理 vs 原实现 |
| --- | --- | ---: | ---: | ---: |
| TS | x18n 搜索，50,000 个键 | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`，20,000 个字符串 | 98 ms | - | **17x** |
| Ruby | `slugify`，20,000 个字符串 | 110 ms | - | **12.7x** |
| Ruby | `shellescape`（标准库），50,000 个混合值 | 88 ms | - | **11.8x** |
| Go | `Slugify`，50,000 个字符串 | 49 ms | 0.93x | **4x** |
| Java | `slugify`，50,000 个字符串 | 43 ms | 0.68x | **3x** |

原语言本就是编译型语言时，单个条目的计算已经很快，因此提升相对有限，批处理主要靠多核并行取胜。批处理 crate 默认使用 mimalloc 分配器：使用系统分配器时，Go 批处理甚至比单线程还慢。演示项目见 [`demo/x18n-search`](../demo/x18n-search/README.md)。

## 六种语言的真实代码实测

Go 的 `path`、Ruby 的 `shellwords`、Python 的 `colorsys`，以及轻量封装后的 JDK 与 glibc 行为：所有移植均通过门禁，累计验证 13,010 条录制用例。这轮实战还顺带发现并修复了 rust-anything 自身的多个 bug（经过 `serde_json` 时浮点数偏差 1 个 ULP、C 语言录制期间崩溃、无类型代码收到垃圾输入）。按单函数调用时，Ruby 移植版比原 Ruby 快 4.4 倍，Python 移植版比 CPython 快 1.35 倍，而 Go 和 Java 的叶子函数在原语言下依然更快；一旦转为批处理，所有语言全面胜出（见上表）。详细报告见 [`docs/real-world-languages.md`](./real-world-languages.md)。

## 示例：来自 x18n 的真实模块

[`demo/`](../demo) 目录中用两种方式移植了来自 [x18n](https://github.com/x18n-dev/x18n) 的 `packages/core/src/fuzzy.ts`：

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts：就绪，推荐 wasm-bindgen（core 需在浏览器运行）
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# 编写 src/port.rs
rust-anything gate demo/fuzzy-rs
```

第一版移植直接按 Rust 的 `char` 做索引，能跑通简单测试，但在 `diff` 环节失败了：

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS 的 `indexOf` 按 UTF-16 代码单元计数，因此一个 emoji 占两个位置。`demo/*/src/port.rs` 中的实现使用了自动生成的 `utf16` 辅助函数，从而以 napi-rs（`demo/fuzzy-napi`）和 wasm-bindgen（`demo/fuzzy-rs`）两种形式都通过了全部 2000/2000 条用例以及门禁检查。

rust-anything 为整个 x18n 生成的迁移规划见 [`docs/examples/x18n.md`](./examples/x18n.md)。

## 安装

```sh
cargo install --path .
```

`record`、`diff` 和 `bench` 会在原语言自身的运行时中执行原实现：TypeScript 需要 Node 22.6+（可直接运行 `.ts` 源码），Python 与 C（ctypes）需要 Python 3.9+，其余对应 Go 1.21+、Ruby 3+、JDK 17+（`javac` 与 `java`）。C 语言还需要系统装有 C 编译器。构建 wasm 桥接层还需要 `rustup target add wasm32-unknown-unknown` 和 `cargo install wasm-bindgen-cli --version <该 crate 的 wasm-bindgen 版本> --locked`；执行 `build` 时会提示所需精确版本号。

面向智能体场景时，直接执行 `rust-anything setup` 即可完成全部注册（见快速开始）。若只想为单个项目手动添加 MCP 服务器，可在 `.mcp.json` 中写入：

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` 如何做决策

- 无法跨桥接层传递的导出项会保留在原语言中，并附带原因说明，影子模块会继续重新导出原实现。以 TS 为例：接受或返回函数的函数、生成器和迭代器、RegExp、`instanceof` 检查、泛型，以及顺着导入、重导出和 `extends` 追踪后发现类型中包含函数的值。使用 `--keep "name: reason"` 可以主动保留更多项，例如依赖 `Intl` 本地化数据的代码。
- TS 类型会自动映射到 Rust 类型，类型别名会顺着导入解析，参数类型可从默认值推断；结构化数据通过生成的二进制协议传输（仅在该协议无法表达的形态下退回 JSON）。
- JSON 无法表示 `undefined`、NaN、Infinity、-0 或孤立代理项（lone surrogates）：结构化值会携带标记对象（`{"$undefined": true}`、`{"$num": "NaN"}`、`{"$utf16": [...]}`），由生成的 `index.cjs` 负责转换，并由 crate 中的 `js.rs` 提供辅助函数。

`record` 会直接按原样运行 TS 源码：内置的 Node 解析钩子会处理打包器风格的导入（如将 `./errors` 解析为 `./errors.ts`），当仓库尚未安装依赖时可通过 `--resolve-from` 指定 npm 包路径，对于需要转译的 TS 语法（如枚举、参数属性）会自动改用 `--experimental-transform-types` 重试。

## `analyze` 检查哪些内容

- 扫描包（`package.json`）与源码文件；自动跳过 `node_modules`、构建产物、测试夹具（fixtures）、演练场（playgrounds）和工具配置。会解析 Vue/Svelte/Astro 的 `<script>` 块以提取导入关系。
- **单元（Units）**：一个源码文件夹，或位于包源码根目录下的单文件。
- **波次（Waves）**：被导入的单元排在更早的波次；存在循环导入的单元会合并在同一波次一起迁移。
- **桥接方式（Bridge）**：若单元或其导入链路依赖 Node 环境，选用 napi-rs；纯可移植代码选用 wasm-bindgen；UI 与编辑器相关代码保留在 JS 侧。
- **就绪度（Readiness）**（代表安全程度）与**优先级（Priority）**（既安全又值得迁：包含循环和字符串处理、有测试覆盖、体量适中）。

| 风险项 | 严重程度 | 示例 |
| --- | --- | --- |
| 字符串偏移量 | high | `slice`、`indexOf`、`matchAll`、`d` 修饰符：UTF-16 与 UTF-8 差异 |
| 正则语法 | high | 环视（lookaround）、反向引用、`y` 修饰符：`regex` crate 不支持 |
| 动态正则 | high | `new RegExp(userPattern)`：运行时动态解析 JS 正则语法 |
| 动态代码 | high | `eval`、`new Function`、动态计算参数的 `import()` |
| 动态类型 | medium | `any`、`'key' in value` |
| 有序集合 | medium | `Map`、`Set`、`Object.keys`：依赖插入顺序 |
| 异步与生成器 | medium | Promise 与生成器跨边界交互 |
| 类继承与反射 | medium | `extends`、`Proxy`、`Reflect`、`Symbol` |
| 回调风格 API | medium | 函数类型参数与方法：高频跨桥接调用开销大 |
| 异常、数值与 JSON | low | `throw`、位运算、`JSON.stringify` 键顺序 |

## 开发

```sh
cargo test                        # 单元测试、夹具仓库测试、record/diff/shadow 闭环（需要 node）、各语言的 app record/replay 测试
cargo clippy --all-targets -- -D warnings
cargo fmt
```

设计取舍及其原因见 [DECISIONS.md](../DECISIONS.md)。

## 更新或卸载

```sh
cargo install rust-anything                                    # 更新（Cargo）
npm install -g rust-anything@latest                            # 更新（npm）
rust-anything setup                                            # 刷新智能体配置
rust-anything setup --remove && cargo uninstall rust-anything  # 卸载（Cargo）
rust-anything setup --remove && npm uninstall -g rust-anything # 卸载（npm）
```

`setup --remove` 只会移除 rust-anything 写入的条目；修改前会把当前配置文件重新备份为 `<file>.rust-anything.bak`（因此会覆盖此前 `setup` 留下的同名备份），该备份文件会一直保留，直到你手动删除。

## 它捕获不到什么

通过验证只代表 Rust 实现与已录制的每条用例一致，仅此而已。重写过程中真正会踩坑的地方往往在录制范围之外，因此务必清楚边界所在：

- **没人录制过的输入。** 自动生成的用例、语义陷阱以及你自己传入的 `--inputs` 就是覆盖上限。请务必补充真实输入（线上样本、bug 工单数据、原项目的测试夹具）；线上真正会把程序搞崩的用户输入，很少是生成器能想到的。
- **正则表达式。** `regex` crate 不支持环视和反向引用，而且即便能编译通过的正则，在处理非 ASCII 文本时的 `\w`、` \b`、`\d` 以及忽略大小写匹配行为也可能与 JS、Python 或 Java 不同。换成 `fancy-regex` 或改写正则后，可能跑通所有录制用例，却在遇到土耳其语无点 `ı` 或零宽连字（ZWJ）时出现差异。`record` 会为使用正则的文件里的每个函数都注入正则陷阱（包括上述字符、开尔文符号、长 s、阿拉伯-印地数字、行分隔符、词尾西格玛），但你仍需拿真实文本对实际正则做模糊测试。
- **两次运行之间会变化的内容。** `record` 会把原实现跑两遍并归类出每次不同的部分：变化的值（时间戳、ID）会被设为通配符；行相同但顺序不同的输出（哈希表、并发任务）会按无序集合比对，也就是说移植版仍必须产出完全相同的这些行；行数本身都不一致的则会变成 `...`，匹配任意内容。`record` 会逐一列出这些类别：每一项都值得你人工过一遍，因为哈希顺序或并发时序差异，往往就是移植版在真实场景下行为漂移的根源。
- **浮点数。** 不同语言的数值转文本格式存在差异（如 `1e21`、`-0`、有效数字位数）。语义陷阱中已包含这些边界值，且必须精确匹配；`--float-tolerance` 只宽容舍入误差，绝不宽容格式化差异。
- **输出之外的一切。** 耗时、内存占用、高并发负载下的表现，以及除 stdout、stderr、退出码、写入文件和 HTTP 响应之外的副作用（网络请求、数据库写入、系统信号），均不在比对范围内。
- **其他平台。** 录制结果只能证明在运行录制的那台机器上的行为。如果 C 代码的结果依赖于类型字节大小、字节序或特定编译器实现，在目标平台上可能会表现不同；正因如此，`analyze` 会把贴近硬件的 C 代码保留在 C 中。

## 常见问题

**它会自动帮我重写代码吗？** 不会。它负责找出该迁哪里、生成桥接层、录制原实现行为并校验 Rust 实现是否正确。`port.rs` 中的 Rust 代码需要由你或你的智能体编写；最终是否达标由 `diff` 和 `gate` 决定。

**我的应用 API 会变吗？** 不会。调用方导入的函数签名保持不变（或者使用影子模块——在建立信心的过渡期内同时跑两套实现并返回原实现结果）。

**Rust 一定更快吗？** 不一定，rust-anything 也会如实告诉你。每条数据调用一次的小函数在 Rust 里往往更慢，因为每次调用都要跨过桥接层；而 V8、JVM 和 Go 运行这类函数只需要纳秒级时间。`profile` 会定位包在外层的循环，`--batch` 负责把整个循环迁走，`bench` 则在上线前给你一个明确结论。至于已经由 numba、Cython 或 JAX 编译为机器码的代码：`profile` 和 `analyze` 会直接标出，因为迁移它们几乎换不来额外提速。

**我的代码偏数值计算，浮点数能精确一致吗？** 通常不能：不同编译器之间的运算顺序、乘加融合指令（FMA）以及数学库实现都有差异。在执行 `record` 或 `app record` 时加上 `--float-tolerance 1e-9`，即可允许浮点数在较大值该比例（绝对值小于 1 时按绝对误差）内通过校验。整数、文本和数据结构仍需精确一致。

**如果我只有 APK、JAR 或 `.exe`，能用它迁移吗？** 不能。它面向的是源码迁移：解析函数、录制每个函数的行为，并拿 Rust 对照运行中的原程序做检验。已编译的二进制产物不具备这些条件，`analyze` 也会直接提示。仅根据二进制可观测行为重写一个全新 Rust 应用属于另一类项目。

**经过实战检验的 C 代码应该迁吗？** 通常不建议，`analyze` 会标出具体位置。操作硬件寄存器、依赖编译器类型大小或内存布局、或使用内联汇编的 C 代码（如 `volatile`、位域、紧凑结构体、`__asm__`、整型强转指针地址）都会被标记为“保留在 C 中（keep in C）”：在本机录制的行为并不能代表目标硬件，而且稳定的驱动或固件代码重写收益极低。适合迁走的是它周围的可移植逻辑（解析器、协议处理、数据处理）。

**能用来迁移我的 Electron 应用吗？** 业务逻辑可以，窗口本身仍保持网页形态。`analyze --whole-app` 会识别出 Electron 架构，规划将主进程逐块迁往 Rust，而渲染进程保持不变。等核心逻辑全部变成 Rust 后，再将界面迁往 Tauri（同一套 Web UI 跑在 Rust 后端上）则是另一个独立步骤。

**支持 C#、Kotlin 或 Swift 吗？** C# 目前处于预览阶段（见[支持语言](#支持语言)）；Kotlin 和 Swift 暂未支持。每增加一种语言都需要开发一套解析器、录制器、桥接生成器和回放驱动，且都要经过端到端测试。如果你需要某种语言，欢迎提 issue（或为已有 issue 点赞投票）。

**移植出来的 Rust 代码会不会比原版臃肿很多？** 正常情况下不会。`gate` 会比较移植版与原实现的代码行数，超过 3 倍（另加 50 行用于导入和函数签名）就会不通过：出现这种情况通常意味着你在手写现有 crate 已经提供的功能，或者在逐个分支硬编码枚举各种情况。`analyze` 会列出推荐使用的 crate。

**逐块迁移会不会把 Rust 锁死在旧应用的设计架构里？** 只有在新旧代码并存过渡期间才会。录制验证的是应用边界处的行为（CLI 的输出、服务端的响应、模块导出的函数），而不是内部实现细节。在单元还需要跨桥接调用时保持与旧结构镜像对应即可；一旦 `app lift` 移除了原实现，你就可以自由重构 Rust 架构，同时继续用 `app replay` 验证对外行为不变。此外也不存在反向回调原实现的问题：前门仅把原实现当作独立进程运行（或转发 HTTP 请求），桥接单元只会被原实现调用而绝不会反过来调回原语言，回调函数也始终留在原语言侧。

**我的代码会离开本机吗？** 不会：rust-anything 完全在本地运行，不会向外部发送任何代码。Cargo 会按常规流程下载 crate；至于你的编程智能体发送给模型服务商的内容，则遵循你所选模型服务商各自的隐私策略。

**需要提前安装什么环境？** Rust 工具链，以及待迁移语言对应的运行时（见[安装](#安装)）。

**遇到报错怎么办？** 请提交 issue，附上执行的命令、完整输出以及你的操作系统平台信息。

## 赞助商

rust-anything 是一款免费开源项目。如果它对你的工作有所帮助，欢迎考虑赞助支持，你的支持将助力项目持续开发。

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### 企业赞助商

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### 个人赞助商

<!-- sponsors -->
<!-- prettier-ignore-start -->
<table>
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/aliyilmazco"><img src="https://github.com/aliyilmazco.png?size=100" width="80px;" alt="Ali Yilmaz"/><br /><sub><b>Ali Yilmaz</b></sub></a></td>
    </tr>
  </tbody>
</table>
<!-- prettier-ignore-end -->
<!-- /sponsors -->

## 参与贡献

欢迎提交 Issue 和 Pull Request；[CONTRIBUTING.md](../CONTRIBUTING.md) 说明了开发环境搭建、测试存放位置以及如何新增语言支持。设计决策与原因见 [DECISIONS.md](../DECISIONS.md)。特别欢迎提交真实项目的迁移案例研究。安全漏洞请私下报告（[SECURITY.md](../SECURITY.md)），并请遵守[行为准则](../CODE_OF_CONDUCT.md)。

## 许可证

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman)。你在自己仓库中生成的移植代码与产物均归你所有。
