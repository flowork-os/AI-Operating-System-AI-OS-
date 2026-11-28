<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="rust-anything 螃蟹標誌，嘴巴為一個程式碼標籤">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">作者：<a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · 繁體中文 · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>本譯文由社群維護，可能落後於<a href="../README.md">英文 README</a>。</sub></p>

<p align="center"><em>用 Rust 重寫你的整個應用程式，並在每一步都保持正常運作。</em></p>

<p align="center"><em>無論是命令列工具（CLI）、伺服器還是函式庫，都能逐塊重寫，每一步都與原版實作進行比對驗證。</em></p>

<p align="center">Node.js 與 TypeScript · Python · C · Go · Ruby · Java · PHP 與 C# 搶先預覽中</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io 版本"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm 版本"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="支援 6 種語言">
  <a href="#支援的代理程式"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="支援 4 種代理程式"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="測試狀態"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT 授權條款"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub Stars"></a>
</p>

<p align="center">最高提速 20 倍 · 重播 38,251 筆錄製案例 · 0 筆差異 · 一條指令搞定</p>

<p align="center">
  <img src="assets/race.gif" alt="在 x18n 的 50,000 個鍵中搜尋 user.profile：TypeScript 耗時 143 ms，rust-anything 批次處理僅耗時 6.9 ms，且每次按鍵的結果完全相同。" width="820">
</p>

**用 Rust 逐塊重寫你的整個應用程式。** rust-anything 會先錄製你現有的
Node.js（TypeScript/JavaScript）、Python、C、Go、Ruby 或 Java 應用程式的行為，然後針對每一塊
Rust 重寫程式碼對照該錄製紀錄進行驗證，確認無誤後再繼續下一步，直到整個應用程式成為純 Rust。CLI、HTTP
伺服器與函式庫皆適用；由你的程式開發代理程式（或你本人）來撰寫 Rust 程式碼。它只能偵測到錄製內容所涵蓋的行為：請參閱[它偵測不到什麼](#它偵測不到什麼)。如果只需要加速慢的部分，
也可以只針對該熱點路徑逐一移植：

| 真實工作負載（結果與原版完全一致） | 原版 | 使用 rust-anything |
| --- | ---: | ---: |
| x18n 的側邊欄搜尋，50,000 個鍵（TypeScript，Node） | 每次查詢 10 ms | **0.5 ms：提速 20 倍** |
| 瀏覽器端執行相同搜尋（wasm，單執行緒） | 10 ms | **0.95 ms：提速 11.5 倍** |
| 對 20,000 個字串執行 `slugify`（Python） | 98 ms | **提速 17 倍** |
| Ruby 標準函式庫 `Shellwords.shellescape`，50,000 個值 | 88 ms | **提速 11.8 倍** |
| 對 50,000 個字串執行 `Slugify`（Go） | 49 ms | **提速 4 倍** |
| 對 50,000 個字串執行 `slugify`（Java） | 43 ms | **提速 3 倍** |

以上數據均在 4 核心環境下測得；每組數字在 [`demo/`](../demo) 中都有對應的基準測試，且都會先驗證結果完全一致。每個小函式呼叫一次 Rust 通常比 JIT 更*慢*；
rust-anything 會找出真正值得搬移的迴圈，並將整個迴圈移過去。

> rust-anything 是一個獨立專案，與 Rust Project 或 Rust Foundation 無關，亦未獲其背書。「Rust」為 Rust Foundation 之商標。

## 快速開始

將這段話貼給 Claude Code、Codex、Cursor 或 Gemini CLI，讓你的代理程式自動安裝：

```text
安裝 rust-anything：執行 `cargo install rust-anything`，接著執行 `rust-anything setup`。
告訴我什麼時候需要重新啟動你。
```

或是自行安裝：

```sh
cargo install rust-anything   # 從 crates.io 安裝
rust-anything setup           # 向 Claude Code、Codex、Cursor 與 Gemini CLI 註冊
```

還沒有安裝 Rust 工具鏈？每個 [GitHub release](https://github.com/erkamyaman/rust-anything/releases) 都附帶了 macOS、Linux 與 Windows 的預先編譯執行檔；針對 JavaScript
專案，執行 `npm install -g rust-anything` 也能安裝相同的執行檔。

在 Claude Code 中你也可以將它安裝為外掛（包含 MCP 伺服器與工作流程技能；上述 CLI
必須位於你的 `PATH` 中）：

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` 會將 MCP 伺服器加入它所偵測到的每個代理程式中，並將工作流程技能安裝至各代理程式讀取技能的目錄。它會保留你的其他設定、可安全重複執行，且可用 `--remove` 移除這些設定項目（不會還原先前被 `setup` 更新過的同名既有項目）。
接著你就可以直接請你的代理程式協助，例如：

- *「用 rust-anything 將這個 CLI 端到端重寫為 Rust，並證明其行為完全相同。」*
- *「這個搜尋感覺很慢。用 rust-anything 做效能分析，並將熱點迴圈搬移到 Rust。」*
- *「用 rust-anything 規劃將 `src/parser/` 遷移至 Rust；先移植第一個單元並進行驗證。」*
- *「將 `rust/text-rs` 中的 Rust 移植版與原版進行基準測試比對，告訴我是否適合上線。」*

### 支援的代理程式

| 代理程式 | `rust-anything setup` 會加入的設定 |
| --- | --- |
| Claude Code | `~/.claude.json` 中的 MCP 伺服器、`~/.claude/skills/` 中的技能 |
| Codex | `~/.codex/config.toml` 中的 MCP 伺服器、`~/.codex/skills/` 中的技能 |
| Cursor | `~/.cursor/mcp.json` 中的 MCP 伺服器 |
| Gemini CLI | `~/.gemini/settings.json` 中的 MCP 伺服器 |
| 其他任意 MCP 用戶端 | 手動將 `rust-anything mcp` 新增為 stdio 伺服器（見[安裝](#安裝)） |

修改任何已存在的設定檔前，`setup` 都會在同目錄旁留存一份備份（`<file>.rust-anything.bak`）。

你也可以自行執行這些步驟：

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile 找到迴圈中的 fuzzyScore，bridge --batch 產生 Rust crate，gate 通過 2000/2000 筆錄製案例，且基準測試顯示比 TS 快 20.7 倍。" width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # 找出耗時熱點以及誰呼叫了它
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# 撰寫 src/port.rs（或交由代理程式撰寫），接著執行：
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # 每筆錄製案例都必須吻合
rust-anything bench rust/fuzzy-rs                      # 真的更快嗎？讓評估結論說話
rust-anything gate rust/fuzzy-rs                       # 通過此門禁才算完成
```

rust-anything 並不直接翻譯程式碼：Rust 程式碼是由你的程式開發代理程式（Claude Code、Codex、Cursor 等）或你本人所撰寫。rust-anything 提供的是代理程式無法可靠猜測的資訊：時間花在哪裡、該先移植什麼
以及依何種順序移植、讓其餘程式碼無需改變 API 即可呼叫 Rust 的橋接層、
移植版必須完全吻合的精確行為、安全上線的方式，以及判定移植是否達標的門禁。

## 支援語言

| 語言 | 遷移單元 | 橋接層 | 錄製與重播方式 |
| --- | --- | --- | --- |
| TypeScript/JavaScript | 資料夾或單檔 | napi-rs 或 wasm-bindgen 搭配自動產生的二進位傳輸協定；支援類別與非同步 | Node，直接執行 `.ts` 原始碼 |
| Python | 套件或模組 | PyO3（abi3），直接型別轉換，支援型別化例外 | Python，匯入原版模組 |
| C | `.c` 檔案 | 與原函式同名的 `extern "C"` 函式與標頭檔 | 將原版編譯為共享函式庫，透過 ctypes 呼叫，每筆案例獨立 fork |
| Go | 套件（package） | 型別化 cgo 呼叫與自動產生的二進位傳輸協定，封裝於維持原 API 的套件內 | 自動產生的 Go 驅動程式，作為獨立模組建置執行 |
| Ruby | 包含模組函式的檔案或資料夾 | 掛載於原模組名稱下的 magnus 擴充套件 | 自動產生的 Ruby 驅動程式 |
| Java | 包含 `public static` 方法的套件 | 型別化 JNI 與自動產生的二進位傳輸協定，置於維持原方法的包裝類別中 | 自動產生的反射（reflection）驅動程式 |
| PHP（預覽） | 包含函式與 `public static` 方法的資料夾 | 下一步推出：透過 C ABI 運作的 PHP FFI | 目前支援整套應用程式：`app record`、`app replay` 與前門代理，適用於 CLI 與伺服器（`php -S`） |
| C#（預覽） | 包含 `public static` 方法的資料夾 | 下一步推出：透過 C ABI 運作的 P/Invoke | 目前支援整套應用程式：`app record`、`app replay` 與前門代理，適用於 CLI 與 ASP.NET 伺服器（`dotnet <app>.dll`） |

除了 C 語言外，每種語言皆可產生批次處理類別（`--batch`）：所有資料只需跨邊界傳入一次並留在
Rust 中，每次呼叫便會在所有 CPU 核心上平行運算全部項目。

系統會根據儲存庫內容自動偵測語言（依序檢查 `go.mod`、`pom.xml`、`.csproj` 或 `.sln`、
`pyproject.toml`、`Gemfile`、`composer.json`、`package.json`，否則依最常見的原始碼檔案判斷）；
也可以透過 `--lang` 手動覆寫。型別資訊直接來自原始碼：TS 型別、Python 型別提示、C、Go、Java 與 C#
函式簽章、Ruby YARD 標籤、PHP 型別與 phpdoc；未標註型別但當作數值使用的參數，會被自動推斷
為數值型別。

PHP 目前為搶先預覽階段：`analyze` 可為 PHP 應用程式規劃遷移（支援 Composer 套件與 PSR-4 自動載入，偵測
寬鬆比較與整數溢位轉浮點數等風險，並將 Composer 套件對應至 crate），
且支援對 PHP CLI 或伺服器進行錄製、重播與套用 Rust 前門代理。透過 PHP FFI 將各個
單元移植到 Rust 是下一步規劃（[issue #2](https://github.com/erkamyaman/rust-anything/issues/2)）。

C# 同樣處於搶先預覽階段：`analyze` 會讀取 `.csproj` 專案與其 NuGet 套件
（對應至 crate）、將 `using` 指示詞解析至對應資料夾，並標記 C# 的特殊差異
（`decimal`、`dynamic`、LINQ 的延遲查詢、`Task`、`lock`、反射）。目前可對 C# CLI 或 ASP.NET
伺服器進行錄製、重播與套用 Rust 前門代理；透過 P/Invoke 移植個別單元則為下一步支援項目。

## 運作原理

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 時間花      該先移植    Rust       原版程式    由你或      每筆     更快嗎？    在正式環境   通過此門禁
 在哪裡      哪個部分    crate 與   的真實      代理程式    錄製     評估結論    雙軌並跑     才算完成
                         包裝層     行為        撰寫        案例
```

原版實作始終作為唯一事實來源（Source of Truth）：`record` 會在邊界案例（以及你提供的輸入）上執行原版程式，並
儲存其回傳值或拋出的例外；`diff` 會對 Rust 實作重播每筆案例；在所有案例完全吻合且
`gate` 通過之前，絕不會上線。整個過程中，呼叫端始終維持原有的 API。

整個應用程式會以單元為單位走完相同的循環，外層則由一個證明整體程式行為的框架包覆（見[遷移整個應用程式](#遷移整個應用程式)）：

```
analyze --whole-app ──> app record ──> app front-door ──> 逐單元執行上述循環，再接 app wire ──> app lift
 專案架構、所有相依       從外部觀察       Rust 接管程式       單元通過門禁後改由 Rust 回應：         純 Rust，
 套件、需要敲定的決策     應用的行為       進入點；原版負責    重播 100% 通過、回退率下降             由重播驗證
                                           實際回應
```

## 核心流程

| 步驟 | 指令 | 說明 |
| --- | --- | --- |
| 0. 效能分析 | `rust-anything profile <repo> -- node bench.mjs` | 在該語言的效能分析器下執行真實工作負載（node、cProfile、`go test` pprof、JFR、Ruby 追蹤器）：依總耗時（inclusive time）列出熱點函式、其呼叫端，以及適合批次處理的迴圈；標記已經編譯加速的程式碼（numba、Cython、JAX），提示遷移至 Rust 收益有限 |
| 1. 規劃 | `rust-anything analyze <repo>` | 盤點單元、移植順序、附帶 `file:line` 的風險評估、各單元的橋接方式、相依套件與 crate 的適配度、最佳首批移植對象；加上 `--whole-app` 還會列出進入點與架構形態、所有（匯入或宣告的）相依套件及其對應 crate、區塊分群（互相匯入的單元會一起搬移），以及附帶推薦答案的編號決策清單 |
| 2. 橋接 | `rust-anything bridge <repo> <unit>` | 建立包含繫結程式碼（`lib.rs` 以及供原語言載入的包裝層）與待移植佔位實作（`port.rs`）的 crate；`--batch fn:param` 會額外產生一個將大量 `param` 值常駐保留在 Rust 中的類別 |
| 3. 錄製 | `rust-anything record <crate>` | 在自動產生的邊界案例（非 ASCII 字元、emoji、`-0`、`NaN`、預期浮點數卻傳入整數等）與覆蓋每個參數語意陷阱的測試值（字串長度與大小寫、有號除法、溢位邊界、浮點數格式化、Map 與排序順序）上執行原版程式，並儲存為 `cases.jsonl`；數值程式碼可使用 `--float-tolerance 1e-9` 允許浮點數在該誤差比例內比對通過 |
| 3. 建置 | `rust-anything build <crate>` | 建置 Rust 端產物：`.node`、wasm 套件、Python 擴充模組或共享函式庫 |
| 3. 比對 | `rust-anything diff <crate>` | 以原版呼叫端實際呼叫的方式，對 Rust 重播所有已錄製案例，並列出不一致處 |
| 3. 基準測試 | `rust-anything bench <crate>` | 分別測量原版與 Rust（含橋接層開銷）執行已錄製案例的耗時 |
| 4. 影子模式 | `rust-anything shadow <crate>` | 無痛替換模組，同時執行兩邊實作、回傳原版結果並回報差異；透過 `RUST_ANYTHING_MODE=old\|shadow\|new` 切換 |
| 5. 門禁 | `rust-anything gate <crate>` | 檢查 fmt、clippy `-D warnings`、測試、`unsafe` 稽核、無未完成移植的函式、原版每條錯誤路徑皆有對應的錄製失敗案例、在原版回傳錯誤之處不得使用 `unwrap`/`expect`/`panic!`（除非標記 `// INFALLIBLE: <原因>`）、建置、API 與行為一致性 |
| 代理程式 | `rust-anything setup` | 向你的程式開發代理程式註冊 MCP 伺服器（`rust-anything mcp`，將每個步驟包裝為工具）與工作流程技能（[`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)） |

## 遷移整個應用程式

目標是打造出一個行為與原版完全一致的純 Rust 應用程式，同時保留原版作為參考基準。
Rust 程式碼由你的代理程式撰寫；rust-anything 負責排定作業順序、搭建骨架並驗證每一個步驟。
[整套應用程式遷移技能（whole-app skill）](../skills/rust-anything/whole-app.md) 會引導代理程式完成全流程，從只有你能拍板的決策開始：

- **深度詰問（Grilling）**：代理程式會分輪提問，每題皆附有推薦答案，直到移植所依賴的每項決策都確定為止，並將每項決策以 ADR 格式寫入 `rust/DECISIONS.md`，同時建立 `rust/GLOSSARY.md` 將原版術語對應至 Rust 命名。
- **深入調研（Research）**：背景代理程式會閱讀每個相依套件的第一手原始碼，並撰寫 `rust/research/<topic>.md`，記錄所發現的每一個語意陷阱。
- **跨工作階段接力（Across sessions）**：`rust/MAP.md` 列出每個單元的狀態；每個工作階段在開始前會先認領一個單元，並在每個檢查點留下 `rust/HANDOFF.md` 交接給下一個工作階段。同一波次中的單元可由子代理程式平行移植。
- **切換上線（Cutover）**：代理程式會完成它能執行的部分，並撰寫互動式腳本 `rust/cutover.sh` 來處理只有你能執行的步驟（部署、DNS、機密金鑰），且每一步都備有復原方案。

深度詰問、原始碼調研等實務做法改編自 [Matt Pocock's skills](https://github.com/mattpocock/skills)。

先做規劃：`rust-anything analyze . --whole-app` 會補充應用程式的架構形態（CLI、伺服器或函式庫）
與進入點、每個外部相依套件（匯入或宣告）及其對應的 Rust crate 與適配度、
依區塊（互相匯入的單元會一併搬移）編排的移植順序，以及附帶推薦答案的編號決策清單：包含保留原樣的單元、受阻單元、缺乏替代或僅有部分替代 crate 的相依套件。

接著從外部驗證整個程式。`record` 與 `diff` 用於驗證單一單元；`app record`
與 `app replay` 則針對六種語言的 CLI 與伺服器驗證整個應用程式（把應用程式視為一個黑盒子）：

```sh
rust-anything app record . -- python3 cli.py          # 執行原版應用程式的指令
rust-anything app replay .                            # 原版必須 100% 通過
rust-anything app replay . --build "target/release/mytool"
```

- `app record` 會在以下輸入上執行原版應用程式：專案文件內自帶的範例（Markdown 與 shell 檔案中的 `$ mytool ...` 指令列及其指名的檔案）、透過 `--inputs` 傳入的 JSONL 檔案（`{"name", "args", "stdin", "env", "files"}`），以及從這些案例衍生出的語意陷阱（非 ASCII 與 emoji 字串、負數除法與取餘數、溢位、極大與極小浮點數、Map 順序、遺失檔案）。每筆案例皆會執行兩次；兩次輸出不同的部分會自動轉為 `[..]` 萬用字元。`--normalize timestamps|uuids|key-order` 或 `--normalize name=regex` 可加入正規化規則，並與案例一併儲存。
- 案例以 [trycmd](https://docs.rs/trycmd) 檔案格式存放於 `rust/app-cases/`：`<case>.toml`（argv、env、結束代碼）、`.stdin`、`.stdout`、`.stderr`、`.in/`（輸入檔案）與 `.out/`（寫出的檔案）。你可以直接閱讀並手動編輯這些檔案；一旦有了 Rust 執行檔，就能在 Rust 測試中直接透過 `trycmd` 執行它們。
- `app replay` 會針對這些案例執行任意建置產物、印出 `passed/total`、在 `rust/app-cases/replay-report.md` 為每筆失敗案例寫出差異比對，並在出現任何不一致時以非零狀態碼結束。如果建置產物像下方的「前門」程式一樣，會將回退至原版的事件附加寫入 `RUST_ANYTHING_FALLBACK_LOG` 指定的檔案（每次回退一行），系統也會一併回報回退率。
- `app replay --case <name>` 可依報告中的案例名稱單獨重跑某一筆案例：這是在全量重跑前，快速且可重現的除錯與修正迴圈。

接著將程式進入點移至 Rust，並一次一個單元把指令交給 Rust 處理：

```sh
rust-anything app front-door .                            # rust/app：每個指令都會執行原版程式
rust-anything app wire . textkit --command upper          # 在 textkit-rs 通過 gate 之後
# 在 rust/app/src/units/textkit.rs 撰寫銜接程式碼，接著執行：
rust-anything app wire . textkit                          # 再次 100% 通過，且回退率下降
```

- `app front-door` 會建立以應用程式命名的 Rust 二進位專案骨架 `rust/app`：內含根據錄製案例的指令與旗標產生的 clap 解析器，每條指令都會以相同的 argv、stdin 與環境變數執行原版程式，並將其輸出與結束代碼原封不動傳回。每次回退都會被計數，因此剛建立的前門程式重播時會得到 100% 通過、100% 回退（它會實際建置並重播以證明這點）。它絕不會覆蓋已存在的 `rust/app`：從那刻起程式碼完全歸你所有。
- `app wire <repo> <unit> --command <name>` 會對該單元的 crate 執行 `gate`（若剛通過可加 `--skip-gate`），將其作為函式庫加入 `rust/app`，初次建立 `src/units/<unit>.rs` 供你或你的代理程式填入邏輯（解析參數、呼叫 `<crate>::port`、印出與原版相同的輸出），將對應指令導向至該處，接著重新建置並重播。在最後收尾（lift）前，設定 `RUST_ANYTHING_UNIT_<NAME>=original` 即可將已接線的單元切換回原版實作。

對於未指定指令名稱的 argv（無參數、未知指令、用法錯誤），請將應用程式自身的名稱作為指令接線（`--command mytool`）。

當重播通過且回退率為 0、所有單元也都通過 `gate` 時，就可以將它轉為純 Rust 應用程式：

```sh
rust-anything app lift .
```

- 在這兩項條件都達成前，`app lift` 會拒絕執行，並明確指出受阻原因：哪些案例仍在回退、哪些銜接程式碼仍是佔位實作、哪些單元未通過 gate。
- 它會先在複本上執行操作：移除回退路徑與緊急切換開關、將每個單元 crate 轉為 `rust/app` 的一般函式庫（不再需要 `cdylib`、繫結或自動產生的包裝層），並新增 `rust/app/tests/app_cases.rs`，讓 `cargo test` 透過 trycmd 執行 `rust/app-cases`，從此 CI 只需要 cargo 即可運作。
- 接著它會執行收尾檢查清單：對每個單元與 `rust/app` 執行 fmt、clippy `-D warnings` 與測試，建置或檢查 `rust/DECISIONS.md` 中列出的所有已安裝目標平台，檢查執行期讀取的檔案與未嵌入的資源資料夾，並對純 Rust 執行檔執行重播。只有當這一切全部通過後，變更才會寫回工作區。原版檔案自始至終絕不會被修改。

### 伺服器

相同的指令也能用來驗證 HTTP 伺服器。`--http` 表示該指令會啟動一個伺服器；它會從環境變數 `PORT` 或指令中的 `{port}` 取得連接埠號（若伺服器總是監聽固定連接埠，可使用 `--port`）：

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum：將所有路由反向代理給原版伺服器
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- 請求來源包含專案文件中的 `curl` 指令（`curl -X POST -d ... http://localhost:8080/x`）、`--inputs`（`{"name", "method", "path", "headers", "body"}`）與語意陷阱：路徑區段與查詢參數會套用與 CLI 參數相同的陷阱替換，請求主體則套用文字與 JSON 陷阱，並額外包含一個未知路由。每次執行都會全新啟動伺服器，並依名稱順序送出請求，因此請求之間的狀態得以保留。
- 案例儲存為 `rust/app-cases/http/<case>.toml`（請求內容、狀態碼與重要標頭）與 `<case>.body`（回應主體，兩次執行不同處標記為 `[..]`）。`Date`、`Server` 等每次回應都會變動的標頭會自動略過；你也可以刪除任何不在乎的標頭行。
- 前門是一個 axum 伺服器，它會在獨立連接埠啟動原版伺服器，並將所有尚未由 Rust 單元回應的路由代理過去。`wire --route` 接受 axum 路由語法：`METHOD /path/{param}`、不指定方法的 `/path`（匹配任意方法）、以及代表其餘全部的 `*`；銜接程式碼會取得該路由、其參數與請求物件。`lift` 會移除代理；之後 HTTP 案例便可在 CI 中透過 `app replay` 執行。

### 函式庫

函式庫沒有獨立行程可供重播：它的公開 API 就是前門，而每個單元的錄製案例就是驗證依據。

```sh
rust-anything app front-door .        # rust/app：包含公開 API 的 Rust crate
# 每個單元走完循環：bridge、record、port.rs、build、diff、gate；接著：
rust-anything app wire . textkit-rs   # 從 rust/app 重新匯出；原版改為匯入其影子模組
rust-anything app replay .            # 執行每個已接線單元的案例；回退率 = 仍由原版處理的匯出項目比例
rust-anything app lift .
```

- 當儲存庫沒有 `main` 也沒有伺服器時（否則可加上 `--library`），`app front-door` 會找出公開 API（每個單元的匯出項目），並將 `rust/app` 建立為函式庫 crate 骨架。每個已接線的單元都會成為它的一個模組：`pub use textkit_rs::port as textkit;`。
- `app wire` 會接收由 `bridge` 建立的 crate、執行 `gate`，並寫出該單元的影子替換模組：原版套件會改為匯入該影子模組以取代原單元，讓呼叫端保持原有 API 卻實際執行 Rust。設定 `RUST_ANYTHING_UNIT_<NAME>=original` 可將該單元切回原版（C 語言則在建置時不帶入影子模組的旗標即可）。
- `app replay` 會透過繫結執行每個已接線單元的錄製案例。回退率代表尚未由 Rust 回應的公開匯出項目佔比：包含未接線的單元，以及被 `bridge` 保留在原語言中的匯出項目。
- `app lift` 要求回退率為 0 且每個單元都通過 `gate`；它會從各單元剝除繫結、包裝層與影子模組，只留下 `rust/app` 作為一個純 Rust 函式庫。它不會更動任何 `port.rs`，因此先前透過繫結驗證吻合的案例依然適用；檢查清單也會提醒原版程式中是否還有檔案仍在匯入影子模組。

這五個指令同樣提供對應的 MCP 工具：`app_record`、`app_replay`、`app_front_door`、`app_wire` 與 `app_lift`。

## 案例研究：x18n 核心

x18n 核心中所有無需改變 API 即可搬移的 29 個函式，已全部透過 rust-anything 完成移植：
每項門禁皆通過，且 7,925 筆錄製案例完全吻合。但接著 `rust-anything bench` 顯示，從 JS 呼叫這些移植版
反而比原版 TS 更慢，因為跨橋接層的成本高於運算本身的工作量。完整報告請見
[`demo/x18n-core`](../demo/x18n-core/README.md)。這個教訓已內建於流程之中：上線移植版之前，務必先用 `bench` 實測。

## 熱點路徑：把資料留在 Rust 中

每處理一個項目就跨橋接呼叫一次 Rust，等於每個項目都要付一次橋接成本，往往會輸給 JIT。真正能勝出的方法是
搬移整個迴圈：`profile` 會找出熱點迴圈，而 `--batch` 會產生一個類別，只需傳入項目一次，
每次呼叫便可在所有核心上對全部項目進行運算，並回傳型別陣列（TypedArray）結果。

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore：佔整體執行時間四分之一，被 `matched` 按每個鍵逐一呼叫：將它批次化
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // 初始化一次
const order = search.rank(query, 0)               // 每次按鍵呼叫：依最佳匹配排序的索引
```

`port.rs` 中的 `FuzzyScoreIndex` 結構體會取代預設迴圈，改為先預處理項目一次，
並能自行完成排序（`rank`）：它保存轉為小寫的鍵值與各自的字元遮罩、
一張記錄每個鍵中常見字元首次出現位置的對照表（單字元查詢只需讀取一欄），
以及上一次查詢的命中結果（輸入 `s` 後再輸入 `se` 時，僅針對 `s` 命中的項目重新評分）。在
x18n 側邊欄針對 50,000 個鍵逐字輸入的搜尋測試中，結果完全一致：

| 實作方式 | 每次查詢耗時 | 對比 TS |
| --- | ---: | ---: |
| TS：`map(fuzzyScore)`、過濾、排序 | 10 ms | 1x |
| 採用相同索引縮小範圍策略的 TS | 4.1-5.4 ms | 2x |
| 同一份移植版，按鍵逐次呼叫 | - | 0.2-0.4x |
| `FuzzyScoreBatch`，預設索引（4 核心） | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` 搭配 `FuzzyScoreIndex`（napi，4 核心） | 0.45-0.56 ms | **18-22x** |
| 同上，改用 wasm（單執行緒） | 0.95 ms | **11.5x** |

即使與採用相同縮小範圍策略的 TS 相比，Rust 依然快上 7-12 倍（wasm 快 5 倍）。將回傳的
索引轉回鍵值字串時請使用一般迴圈：`Array.from(order, i => keys[i])` 會多花 20 倍的時間（0.4 ms）。

每種語言皆支援批次處理，甚至在單次呼叫輸給原版的場景下也能反敗為勝。在 4 核心上執行
相同的工作負載，結果與錯誤完全一致（各示範資料夾內皆附有基準測試）：

| 語言 | 工作負載 | 原版 | 單次呼叫移植版 vs 原版 | 批次處理 vs 原版 |
| --- | --- | ---: | ---: | ---: |
| TS | x18n 搜尋，50,000 個鍵 | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`，20,000 個字串 | 98 ms | - | **17x** |
| Ruby | `slugify`，20,000 個字串 | 110 ms | - | **12.7x** |
| Ruby | `shellescape`（標準函式庫），50,000 個混合值 | 88 ms | - | **11.8x** |
| Go | `Slugify`，50,000 個字串 | 49 ms | 0.93x | **4x** |
| Java | `slugify`，50,000 個字串 | 43 ms | 0.68x | **3x** |

原版若是編譯型語言，提速幅度會較小：單項處理本來就已經很快，因此批次處理主要靠多核心數量取勝。
批次 crate 預設採用 mimalloc 進行記憶體配置：若改用系統配置器，Go 批次處理甚至比單執行緒還要慢。示範專案：[`demo/x18n-search`](../demo/x18n-search/README.md)。

## 六種語言的真實程式碼實測

Go 的 `path`、Ruby 的 `shellwords`、Python 的 `colorsys`，以及輕量外觀模式背後的 JDK 與 glibc 行為：
每個移植專案皆通過門禁，總計驗證 13,010 筆錄製案例。這些實測也發現並修復了
rust-anything 自身的問題（浮點數經過 `serde_json` 時產生 1 個 ULP 誤差、C 語言在錄製期間當機、
無型別程式碼收到垃圾輸入）。按函式單次呼叫時，Ruby 移植版比 Ruby 快 4.4 倍，
Python 移植版比 CPython 快 1.35 倍，而 Go 與 Java 的葉節點函式在各自原語言中依然較快；
一旦轉為批次處理，所有語言全面勝出（見上方表格）。
實測報告：[`docs/real-world-languages.md`](./real-world-languages.md)。

## 範例：來自 x18n 的真實模組

來自 [x18n](https://github.com/x18n-dev/x18n) 的 `packages/core/src/fuzzy.ts`，已透過兩種方式移植於
[`demo/`](../demo)：

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts：已就緒，wasm-bindgen（核心會在瀏覽器中執行）
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# 撰寫 src/port.rs
rust-anything gate demo/fuzzy-rs
```

第一版移植採用 Rust 的 `char` 作為索引，雖然通過了簡單測試，卻在 `diff` 失敗了：

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS 的 `indexOf` 是以 UTF-16 編碼單元（code unit）計數，因此一個 emoji 會佔用兩個位置。位於
`demo/*/src/port.rs` 中的移植版使用了自動產生的 `utf16` 輔助函式，並分別以 napi-rs（`demo/fuzzy-napi`）與 wasm-bindgen（`demo/fuzzy-rs`）兩種形式
通過了 2000/2000 筆案例與門禁檢查。

rust-anything 為整個 x18n 產生的遷移計畫：[`docs/examples/x18n.md`](./examples/x18n.md)。

## 安裝

```sh
cargo install --path .
```

`record`、`diff` 與 `bench` 會在原語言各自的執行時期環境中執行原版程式碼：TS 需要 Node 22.6+（可直接執行 `.ts`
原始碼），Python 與 C（ctypes）需要 Python 3.9+，其餘為 Go 1.21+、Ruby 3+、JDK 17+
（`javac` 與 `java`）。C 語言另需 C 編譯器。wasm 橋接層則需安裝 `rustup target add wasm32-unknown-unknown` 與
`cargo install wasm-bindgen-cli --version <該 crate 的 wasm-bindgen 版本> --locked`；執行 `build` 時會列出
所需的確切版本號。

針對代理程式環境，`rust-anything setup` 會一次註冊所有項目（見快速開始）。若要手動將 MCP 伺服器
加入單一專案中（`.mcp.json`）：

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` 如何決策

- 無法跨過橋接層的匯出項目會保留在原語言中並附註原因，影子模組則會重新匯出原版實作。以 TS 為例：
  接收或回傳函式的函式、產生器與疊代器、RegExp、`instanceof` 檢查、
  泛型，以及沿著匯入、重新匯出與 `extends` 追蹤後型別內含函式的值。
  `--keep "name: reason"` 可保留更多項目，例如相依於 `Intl` 資料的程式碼。
- TS 型別會對應至 Rust 型別，型別別名會跨匯入解析，參數型別則從預設值推斷；
  結構化值會透過自動產生的二進位傳輸協定傳遞（僅在該協定無法表達的型別結構時退回 JSON）。
- JSON 無法表達 `undefined`、NaN、Infinity、-0 或孤立代理字元（lone surrogates）：結構化值會攜帶
  特殊標記（`{"$undefined": true}`、`{"$num": "NaN"}`、`{"$utf16": [...]}`），由自動產生的
  `index.cjs` 負責轉換，並搭配 crate 中的 `js.rs` 輔助函式處理。

`record` 會直接執行原樣 TS 原始碼：內建的 Node 解析掛鉤（resolve hook）會處理打包工具風格的匯入
（例如將 `./errors` 解析至 `./errors.ts`）；當儲存庫尚未安裝套件時，`--resolve-from` 可指定 npm 套件來源；
而需要轉譯的 TS 語法（如 enum、參數屬性）則會自動改以 `--experimental-transform-types` 重試。

## `analyze` 檢查哪些內容

- 掃描套件（`package.json`）與原始碼檔案；自動略過 `node_modules`、建置產物、測試治具（fixtures）、
  演練場（playgrounds）與工具設定檔。支援從 Vue/Svelte/Astro 的 `<script>` 區塊解析匯入關係。
- **單元（Units）**：一個原始碼資料夾，或位於套件原始碼根目錄的單一檔案。
- **波次（Waves）**：被相依匯入的單元會安排在較早的波次；互相循環匯入的單元會一併移植。
- **橋接（Bridge）**：當該單元或其匯入相依的項目需要 Node 環境時採用 napi-rs；純可攜程式碼採用 wasm-bindgen；UI 與編輯器相關程式碼則保留於 JS 中。
- **就緒度（Readiness）**（代表安全程度）與**優先順序（Priority）**（既安全又值得移植：包含迴圈與字串處理、測試覆蓋度、程式碼規模）。

| 風險項目 | 嚴重程度 | 範例 |
| --- | --- | --- |
| 字串偏移量 | 高 | `slice`、`indexOf`、`matchAll`、`d` 旗標：UTF-16 與 UTF-8 差異 |
| 正規表示式語法 | 高 | 環視（lookaround）、反向參照、`y` 旗標：`regex` crate 不支援 |
| 動態正規表示式 | 高 | `new RegExp(userPattern)`：執行期動態解析 JS 語法 |
| 動態程式碼 | 高 | `eval`、`new Function`、動態計算路徑的 `import()` |
| 動態型別 | 中 | `any`、`'key' in value` |
| 有序集合 | 中 | `Map`、`Set`、`Object.keys`：依賴插入順序 |
| 非同步與產生器 | 中 | Promise 與產生器跨邊界互動 |
| 類別繼承與反射 | 中 | `extends`、`Proxy`、`Reflect`、`Symbol` |
| 回呼風格 API | 中 | 函式型別的參數與方法：跨橋接往返頻繁 |
| 例外處理、數值與 JSON | 低 | `throw`、位元運算、`JSON.stringify` 鍵順序 |

## 開發

```sh
cargo test                        # 單元測試、測試治具儲存庫、record/diff/shadow 循環（需 node）、各語言的 app record/replay 測試
cargo clippy --all-targets -- -D warnings
cargo fmt
```

設計決策與其背後原因：[DECISIONS.md](../DECISIONS.md)。

## 更新或移除

```sh
cargo install rust-anything                                    # 更新（Cargo）
npm install -g rust-anything@latest                            # 更新（npm）
rust-anything setup                                            # 重新整理代理程式設定
rust-anything setup --remove && cargo uninstall rust-anything  # 移除（Cargo）
rust-anything setup --remove && npm uninstall -g rust-anything # 移除（npm）
```

`setup --remove` 只會移除 rust-anything 寫入的設定項目；修改前會將目前的設定檔重新備份至
`<file>.rust-anything.bak`（這會覆蓋先前 `setup` 留下的備份），該備份檔案會保留至你手動刪除為止。

## 它偵測不到什麼

通過測試代表 Rust 實作吻合所有已錄製的案例，僅此而已。重寫過程中最容易出問題的陷阱
通常存在於錄製範圍之外，因此務必清楚邊界所在：

- **沒人錄製過的輸入。** 自動產生的案例、語意陷阱與你自行提供的 `--inputs` 就是涵蓋上限。請務必加入真實輸入（正式環境樣本、錯誤回報紀錄、原版測試治具）；真正會讓線上環境出錯的使用者輸入，很少是產生器能預料到的。
- **正規表示式。** `regex` crate 不支援環視（lookaround）或反向參照，而且即使是能夠編譯的樣式，在處理非 ASCII 文字時的 `\w`、`\b`、`\d` 與不分大小寫比對行為，也可能與 JS、Python 或 Java 不同。改用 `fancy-regex` 或重寫樣式雖然能通過每筆錄製案例，卻仍可能在遇到土耳其語無點 `ı` 或零寬連字元（zero-width joiner）時出現差異。`record` 會對使用正規表示式的檔案內每個函式注入正規表示式陷阱（包含前述字元、克耳文符號、長 s、阿拉伯-印地數字、行分隔符號、詞尾希臘字母 sigma），但你仍需使用真實文字對實際樣式進行模糊測試。
- **兩次執行之間會變動的內容。** `record` 會執行原版兩次並分類出每次不同的部分：變動的值（時間戳記、ID）會成為萬用字元；內容相同但順序不同的輸出行（雜湊表、並行處理）會以不計順序的方式比對，因此移植版仍必須輸出完全相同的這些行；若連行數都不同則會轉為 `...`，匹配任何內容。`record` 會列出每一種情況：請務必逐一檢視，因為雜湊順序或並行差異，正是移植版在真實情境下最可能產生行為變化的地方。
- **浮點數。** 數值轉為文字的格式在不同語言之間有所差異（`1e21`、`-0`、有效位數）。語意陷阱已涵蓋這些數值且必須完全一致；`--float-tolerance` 僅寬容四捨五入的數值誤差，絕不寬容格式差異。
- **輸出之外的一切。** 執行時間、記憶體用量、高負載下的並行表現，以及除 stdout、stderr、結束代碼、寫入檔案與 HTTP 回應之外的副作用（網路呼叫、資料庫、系統訊號），皆不在比對範圍之內。
- **其他平台。** 錄製結果只能證明執行錄製當下那台機器上的行為。如果 C 語言程式碼的結果取決於型別大小、位元組序或特定編譯器，在目標平台上可能會表現不同；這正是 `analyze` 會將貼近硬體的 C 程式碼保留在 C 中的原因。

## 常見問題

**它會自動幫我重寫程式碼嗎？** 不會。它負責找出該搬移什麼、產生橋接層、錄製原版行為，並用該紀錄檢查 Rust 實作。`port.rs` 中的 Rust 程式碼由你或你的代理程式撰寫；何時算完成則由 `diff` 與 `gate` 決定。

**我的應用程式 API 會改變嗎？** 不會。呼叫端匯入的函式維持原樣（或使用影子模組，在建立信心的過渡期間同時執行兩邊並回傳原版結果）。

**Rust 永遠比較快嗎？** 不一定，rust-anything 也會老實告訴你。每個項目只呼叫一次的小函式在 Rust 中往往更慢，因為每次呼叫都要跨過橋接層；V8、JVM 與 Go 執行這類函式只需要奈秒級的時間。`profile` 會找出外層的迴圈，`--batch` 會搬移整個迴圈，而 `bench` 則會在你上線前給出明確結論。已被 numba、Cython 或 JAX 編譯為機器碼的程式碼也是如此：`profile` 與 `analyze` 會將其標記出來，因為移植這類程式碼帶來的提速相當有限。

**我的程式碼偏向數值運算；浮點數會完全吻合嗎？** 通常不會：不同編譯器之間的運算順序、乘加融合指令（FMA）與數學函式庫都有差異。在執行 `record` 或 `app record` 時加上 `--float-tolerance 1e-9`，浮點數便會在較大值該比例的誤差範圍內（絕對值小於 1 時改採絕對誤差）視為吻合。整數、文字與資料結構仍須完全一致。

**如果我只有 APK、JAR 或 `.exe`，能用它移植嗎？** 不行。它針對的是原始碼移植：解析函式、錄製每個函式的行為，並將 Rust 對照正在執行的原版程式進行驗證。已編譯的應用程式不具備這些資訊，`analyze` 也會直接說明這點。僅憑執行檔的可觀察行為去重寫一個全新 Rust 應用程式屬於另一個不同領域的專案。

**我應該移植久經考驗的 C 程式碼嗎？** 通常不需要，`analyze` 會標示出應保留的位置。存取硬體暫存器、依賴編譯器型別大小或記憶體配置，或使用內嵌組譯的 C 程式碼（`volatile`、位元欄位、緊湊結構體、`__asm__`、將整數轉型為記憶體位址）會被標記為「keep in C（保留在 C 中）」：在你的機器上錄製無法代表目標硬體，且穩定的驅動程式或韌體程式碼重寫幾乎沒有好處。其周圍的可攜邏輯（解析器、通訊協定、資料處理）才是適合搬移的部分。

**它可以移植我的 Electron 應用程式嗎？** 業務邏輯可以，視窗介面則維持網頁形式。`analyze --whole-app` 會偵測 Electron 並規劃將主行程（main process）逐塊移植，同時保持渲染行程（renderer）不變。當邏輯皆轉為 Rust 後，若要將 UI 搬移至 Tauri（同一套網頁介面搭配 Rust 後端），則是後續另一項獨立步驟。

**支援 C#、Kotlin 或 Swift 嗎？** C# 目前處於搶先預覽階段（見[支援語言](#支援語言)）；Kotlin 與 Swift 尚未支援。每新增一種語言都需要建置解析器、錄製器、橋接產生器與重播驅動程式，且必須通過端到端測試。歡迎為你需要的語言開啟 issue（或為既有 issue 投票）。

**移植後的 Rust 程式碼會不會比原版大上許多？** 正常來說不會。`gate` 會比較移植版與原版的行數，若超過 3 倍（另加 50 行用於匯入與簽章）便會不通過：這通常意味著你在手動重寫現有 crate 已經實作好的功能，或是在逐一列舉特例。`analyze` 會列出建議使用的 crate。

**逐塊移植會不會把 Rust 鎖死在舊應用程式的設計架構中？** 只會在兩者並行運作的過渡時期。錄製檢查的是應用程式邊界的行為（CLI 的輸出、伺服器的回應、模組匯出的函式），而非內部實作細節。在單元仍需跨橋接呼叫的階段可先鏡像舊架構；一旦 `app lift` 移除了原版實作，你就可以自由重構 Rust 程式碼，且 `app replay` 仍能證明對外行為一致。此外也不會發生反向回呼原版的情況：前門是將原版作為獨立行程執行（或將 HTTP 轉發給它），橋接單元只會被原版呼叫而絕不會反向呼叫，回呼函式也會留在原語言中。

**我的程式碼會離開本機嗎？** 不會：rust-anything 完全在本機執行，不會將你的任何程式碼傳送至外部。Cargo 會依常規下載 crate，而你的代理程式模型供應商則會依其各自的隱私政策讀取你透過代理程式傳送的內容。

**需要預先安裝什麼？** Rust 工具鏈，以及你要移植的語言對應之執行時期環境（見[安裝](#安裝)）。

**遇到異常或錯誤怎麼辦？** 請開啟 issue，並附上執行的指令、輸出結果以及你的作業系統平台資訊。

## 贊助商

rust-anything 是一款免費且開源的專案。如果它對你的工作有所幫助，歡迎考慮贊助支持。你的支持能讓開發持續推進。

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### 企業贊助商

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### 個人贊助商

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

## 參與貢獻

歡迎提交 Issue 與 Pull Request；[CONTRIBUTING.md](../CONTRIBUTING.md) 說明了開發環境設定、測試存放位置以及如何新增語言支援。設計決策與理由載於
[DECISIONS.md](../DECISIONS.md)。尤其歡迎真實移植專案的案例研究。若發現安全性問題請私下通報（[SECURITY.md](../SECURITY.md)），並請參閱
[行為準則](../CODE_OF_CONDUCT.md)。

## 授權條款

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman)。你在自己儲存庫中產生的移植程式碼與產物均歸你所有。
