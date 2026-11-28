<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="口がコードタグになっている rust-anything のカニのロゴ">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">作者: <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · 日本語 · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>この翻訳はコミュニティによって管理されており、<a href="../README.md">英語版 README</a> より古い場合があります。</sub></p>

<p align="center"><em>アプリ全体を Rust で書き直す。その間ずっと動く状態を保ったまま。</em></p>

<p align="center"><em>CLI、サーバー、ライブラリを一つずつ移植し、あらゆる段階で元の実装と照合して検証します。</em></p>

<p align="center">Node.js / TypeScript · Python · C · Go · Ruby · Java · PHP と C# はプレビュー版</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io バージョン"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm バージョン"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 言語対応">
  <a href="#対応エージェント"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 つのエージェントに対応"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="テスト"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT ライセンス"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub スター"></a>
</p>

<p align="center">最大 20 倍高速化 · 38,251 件の記録ケースをリプレイ · 0 件の不一致 · コマンドひとつで</p>

<p align="center">
  <img src="assets/race.gif" alt="50,000 キーに対する x18n の検索で user.profile を入力した場合: TypeScript は 143 ms、rust-anything のバッチ処理は 6.9 ms で、すべてのキー入力において同一の結果を返します。" width="820">
</p>

**アプリ全体を、一つずつ Rust に書き直しましょう。** rust-anything は、既存の Node.js（TypeScript/JavaScript）、Python、C、Go、Ruby、または Java アプリが現在どう振る舞うかを記録し、Rust で書き直した各パーツを次へ進む前にその記録と照合して、最終的にアプリ全体が純粋な Rust になるまで検証を続けます。CLI、HTTP サーバー、ライブラリに対応しており、Rust コードを書くのはコーディングエージェント（あるいはあなた自身）です。記録がカバーしている範囲しか検出できない点には注意してください（[検出できないもの](#検出できないもの)を参照）。遅い部分だけを高速化したい場合は、ホットパスだけを一つずつ移植することもできます:

| 実ワークロード（元の実装と同一の結果） | 元の実装 | rust-anything 使用時 |
| --- | ---: | ---: |
| x18n のサイドバー検索、50,000 キー（TypeScript、Node） | 1 クエリあたり 10 ms | **0.5 ms: 20 倍高速** |
| 同じ検索をブラウザ上で実行（wasm、シングルスレッド） | 10 ms | **0.95 ms: 11.5 倍** |
| 20,000 文字列に対する `slugify`（Python） | 98 ms | **17 倍高速** |
| Ruby 標準ライブラリの `Shellwords.shellescape`、50,000 値 | 88 ms | **11.8 倍高速** |
| 50,000 文字列に対する `Slugify`（Go） | 49 ms | **4 倍高速** |
| 50,000 文字列に対する `slugify`（Java） | 43 ms | **3 倍高速** |

4 コア環境での計測結果です。すべての数値は [`demo/`](../demo) 内のベンチマークに基づいており、事前に結果が完全に一致することを確認しています。小さな関数ごとに毎回 Rust を呼び出すと、通常は JIT より*遅く*なります。rust-anything は移植する価値のあるループを見つけ出し、そのループごと移行します。

> rust-anything は独立したプロジェクトであり、Rust Project または Rust Foundation と提携・承認関係にあるものではありません。"Rust" は Rust Foundation の商標です。

## クイックスタート

Claude Code、Codex、Cursor、または Gemini CLI に以下を貼り付けて、エージェントにインストールを任せてください:

```text
rust-anything をインストールして: `cargo install rust-anything` を実行し、次に `rust-anything setup` を実行してください。
あなたを再起動すべきタイミングが来たら教えてください。
```

または自分で実行します:

```sh
cargo install rust-anything   # crates.io からインストール
rust-anything setup           # Claude Code、Codex、Cursor、Gemini CLI に登録
```

Rust ツールチェーンをまだ導入していない場合は、各 [GitHub release](https://github.com/erkamyaman/rust-anything/releases) に macOS、Linux、Windows 向けのビルド済みバイナリが添付されています。JavaScript プロジェクトの場合は `npm install -g rust-anything` でも同じバイナリをインストールできます。

Claude Code ではプラグインとしてインストールすることもできます（MCP サーバーとワークフロースキルが含まれます。上記の CLI が `PATH` に通っている必要があります）:

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` は見つかった各エージェントに MCP サーバーを追加し、エージェントがスキルを読み込む場所にワークフロースキルをインストールします。他の設定は保持され、何度実行しても安全で、`--remove` で追加・更新されたエントリを削除できます（`setup` が上書き更新した以前の値は復元されません）。あとはエージェントに次のように依頼するだけです:

- *"rust-anything を使ってこの CLI をエンドツーエンドで Rust に書き直し、元の実装と同じ挙動であることを証明して。"*
- *"この検索が遅く感じる。rust-anything でプロファイルを取って、ホットループを Rust に移して。"*
- *"rust-anything で `src/parser/` の Rust 移行計画を立てて。最初のユニットを移植して検証して。"*
- *"`rust/text-rs` の Rust 移植版と元の実装をベンチマーク比較して、出荷すべきか教えて。"*

### 対応エージェント

| エージェント | `rust-anything setup` が追加する内容 |
| --- | --- |
| Claude Code | `~/.claude.json` の MCP サーバー、`~/.claude/skills/` のスキル |
| Codex | `~/.codex/config.toml` の MCP サーバー、`~/.codex/skills/` のスキル |
| Cursor | `~/.cursor/mcp.json` の MCP サーバー |
| Gemini CLI | `~/.gemini/settings.json` の MCP サーバー |
| その他の MCP クライアント | 手動で `rust-anything mcp` を stdio サーバーとして追加（[インストール](#インストール)を参照） |

既存のファイルを変更する前に、`setup` は同じ場所にバックアップ（`<file>.rust-anything.bak`）を保存します。

自分で各ステップを実行することもできます:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile がループ内の fuzzyScore を検出し、bridge --batch が Rust クレートを生成し、gate が 2000/2000 件の記録ケースに合格し、ベンチマークで TS より 20.7 倍高速であることを示しています。" width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # どこがホットスポットで、誰が呼んでいるか
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# src/port.rs を書く（またはエージェントに書かせる）。その後:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # 記録されたすべてのケースが一致する必要がある
rust-anything bench rust/fuzzy-rs                      # 速くなったか？判定結果が出る
rust-anything gate rust/fuzzy-rs                       # これに通れば完了
```

rust-anything 自体はコードを自動翻訳しません。Rust コードを書くのはあなたのコーディングエージェント（Claude Code、Codex、Cursor など）またはあなた自身です。rust-anything が提供するのは、エージェントが推測では確実に当てられない部分です: どこに時間がかかっているか、何をどの順番で移植すべきか、既存のコードが API を変えずに Rust を呼び出すためのブリッジ、移植版が一致させるべき正確な挙動、安全に出荷する手段、そして移植の完了を判定するゲートです。

## 対応言語

| 言語 | 移植単位 | ブリッジ | 記録とリプレイの実行方法 |
| --- | --- | --- | --- |
| TypeScript/JavaScript | フォルダまたはファイル | napi-rs または wasm-bindgen（自動生成されたバイナリワイヤプロトコル使用、クラスと async にも対応） | Node で `.ts` ソースを直接実行 |
| Python | パッケージまたはモジュール | PyO3（abi3）、直接型変換、型付き例外 | Python で元のモジュールをインポート |
| C | `.c` ファイル | 元の関数名を持つ `extern "C"` 関数とヘッダ | 元のコードを共有ライブラリにコンパイルし、ctypes 経由でケースごとに fork して呼び出し |
| Go | パッケージ | 型付き cgo 呼び出しと自動生成バイナリワイヤ、元の API を持つパッケージとして提供 | 独立したモジュールとしてビルドされる自動生成 Go ドライバ |
| Ruby | モジュール関数を含むファイルまたはフォルダ | 元のモジュール配下に配置される magnus 拡張 | 自動生成 Ruby ドライバ |
| Java | `public static` メソッドのパッケージ | 型付き JNI と自動生成バイナリワイヤ、元のメソッドを持つラッパークラスとして提供 | 自動生成リフレクションドライバ |
| PHP（プレビュー） | 関数および `public static` メソッドのフォルダ | 近日対応予定: C ABI 越しの PHP FFI | 現時点でアプリ全体に対応: CLI およびサーバー（`php -S`）向けの `app record`、`app replay`、フロントドア |
| C#（プレビュー） | `public static` メソッドのフォルダ | 近日対応予定: C ABI 越しの P/Invoke | 現時点でアプリ全体に対応: CLI および ASP.NET サーバー（`dotnet <app>.dll`）向けの `app record`、`app replay`、フロントドア |

C 言語を除くすべての言語でバッチクラス（`--batch`）も生成されます。要素は一度だけ境界を越えて Rust 側に保持され、呼び出しのたびに全コアを使って全要素を一括処理します。

言語はリポジトリから自動検出されます（`go.mod`、`pom.xml`、`.csproj` または `.sln`、`pyproject.toml`、`Gemfile`、`composer.json`、`package.json` の順で判定し、該当しない場合は最も多いソースファイルから判断）。`--lang` で上書きもできます。型情報はソースから取得します: TS の型、Python の型ヒント、C/Go/Java/C# のシグネチャ、Ruby の YARD タグ、PHP の型および phpdoc。型注釈がなく数値として使われている引数は数値型と推論されます。

PHP はプレビュー版です: `analyze` で PHP アプリの移行計画を立てられ（Composer パッケージと PSR-4 オートローディング、緩い比較や整数オーバーフローによる float 化などのリスク、Composer パッケージからクレートへのマッピング）、PHP の CLI やサーバーを記録・リプレイして Rust 製フロントドアの背後に配置できます。PHP の FFI を通じたユニット単位の Rust 移植は次のステップです（[issue #2](https://github.com/erkamyaman/rust-anything/issues/2)）。

C# も同様にプレビュー版です: `analyze` は `.csproj` プロジェクトとその NuGet パッケージ（クレートにマッピング）を読み取り、`using` ディレクティブをフォルダに解決して、C# 特有の挙動の違い（`decimal`、`dynamic`、LINQ の遅延クエリ、`Task`、`lock`、リフレクション）を指摘します。C# の CLI や ASP.NET サーバーは記録・リプレイ・Rust フロントドア化が可能で、P/Invoke を用いたユニット単位の移植が次のステップです。

## 仕組み

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 時間のかかる 何から移植   Rust クレート  元の実装の   あなたや     記録済み   速いか？   本番環境で   これに通れば
 箇所を特定   すべきか     とラッパー     挙動を記録   エージェント ケースと   判定を     並行稼働     移植完了
                                                     が実装       全件照合   下す       して検証
```

元の実装が常に信頼できる唯一の情報源（Source of Truth）であり続けます。`record` はエッジケース（およびあなた自身の入力）で元の実装を実行し、戻り値やスローされた例外を保存します。`diff` はすべてのケースを Rust 側でリプレイします。全ケースが一致し `gate` に合格するまで、何も出荷されません。呼び出し側はずっと元の API を使い続けられます。

アプリ全体もユニット単位で同じループを回しながら、プログラム全体を証明する外枠の中で進めます（[アプリ全体の移植](#アプリ全体の移植)を参照）:

```
analyze --whole-app ──> app record ──> app front-door ──> ユニットごとに上記ループを実行後 app wire ──> app lift
 全体構造、全依存関係、    アプリを外から   Rust がエントリ       gate 通過でユニットが Rust で応答:      純粋な Rust 化、
 決めるべき事項の整理      見た挙動を記録   ポイントを担当、       リプレイ 100% 維持のまま               リプレイで証明
                                            他は元の実装が応答     フォールバック率が低下
```

## 移植ループ

| ステップ | コマンド | 内容 |
| --- | --- | --- |
| 0. プロファイル | `rust-anything profile <repo> -- node bench.mjs` | 言語ごとのプロファイラ（node、cProfile、`go test` pprof、JFR、Ruby tracer）で実ワークロードを実行: インクルーシブ時間に基づくホット関数、その呼び出し元、バッチ化すべきループを特定。すでにコンパイル済みのコード（numba、Cython、JAX）は Rust 化の恩恵が少ないものとしてフラグ付け |
| 1. 計画 | `rust-anything analyze <repo>` | ユニット一覧、移植順序、`file:line` 付きリスク、ユニットごとのブリッジ方式、依存関係のクレート適合度、最初に移植すべき最適候補を提示。`--whole-app` を付けるとエントリポイントとアプリ形状、（インポートまたは宣言された）全依存関係と対応クレート、ピース（相互インポートするユニット群をまとめて移動）、推奨回答付きの番号付き決定事項も出力 |
| 2. ブリッジ | `rust-anything bridge <repo> <unit>` | バインディング（`lib.rs` と元の言語が読み込むラッパー）および移植用スタブ（`port.rs`）を含むクレートを生成。`--batch fn:param` は多数の `param` 値を Rust 内に保持するクラスを追加 |
| 3. 記録 | `rust-anything record <crate>` | 生成したエッジケース（非 ASCII、絵文字、`-0`、`NaN`、float 想定箇所への int など）および各引数のあらゆる意味的罠（文字列長や大文字小文字、符号付き除算、オーバーフロー境界、float 出力形式、Map やソート順）で元の実装を実行し `cases.jsonl` に保存。数値計算コード向けには `--float-tolerance 1e-9` でその割合以内の浮動小数点誤差を許容 |
| 3. ビルド | `rust-anything build <crate>` | Rust 側をビルド: `.node`、wasm パッケージ、Python 拡張、または共有ライブラリ |
| 3. 差分検証 | `rust-anything diff <crate>` | 元の呼び出し元と同じ方法で Rust 側を呼び出し、記録済みケースをリプレイして不一致を一覧表示 |
| 3. ベンチマーク | `rust-anything bench <crate>` | 記録済みケースを元の実装と Rust 側（ブリッジ経由を含む）で計測比較 |
| 4. シャドウ | `rust-anything shadow <crate>` | 既存コードと差し替え可能なラッパーで両方を実行し、元の実装の結果を返しつつ不一致を報告。`RUST_ANYTHING_MODE=old\|shadow\|new` で切り替え |
| 5. ゲート | `rust-anything gate <crate>` | fmt、clippy `-D warnings`、テスト、`unsafe` 監査、未移植の残存なし、元のエラー経路すべてに対する失敗ケースの記録、元の実装がエラーを返す箇所での `unwrap`/`expect`/`panic!` 禁止（`// INFALLIBLE: <理由>` 明記時を除く）、ビルド、API、挙動を検証 |
| エージェント連携 | `rust-anything setup` | コーディングエージェントに MCP サーバー（`rust-anything mcp`: 各ステップをツールとして公開）とワークフロースキル（[`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)）を登録 |

## アプリ全体の移植

ゴールは、元の実装と同じように動作する純粋な Rust アプリです（元の実装はリファレンスとして残します）。エージェントが Rust を書き、rust-anything が作業の順序付け、足場（スキャフォールド）生成、そして各ステップの検証を行います。[whole-app スキル](../skills/rust-anything/whole-app.md)は、まずあなたにしか下せない判断からエージェントを導いていきます:

- **徹底ヒアリング（Grilling）**: 移植を左右するすべての決定事項が固まるまで、エージェントが推奨回答付きで段階的に質問し、各決定を `rust/DECISIONS.md` に ADR として記録するとともに、元の用語と Rust 名の対応表 `rust/GLOSSARY.md` を作成します。
- **調査（Research）**: バックグラウンドエージェントが各依存関係の一次ソースを読み込み、見つかったあらゆる意味的な罠を `rust/research/<topic>.md` にまとめます。
- **セッションをまたいだ継続（Across sessions）**: `rust/MAP.md` に全ユニットの状態が記録されます。セッション開始時に 1 ユニットを割り当て、各チェックポイントで次のセッション向けに `rust/HANDOFF.md` を残します。同じウェーブ内のユニットはサブエージェントで並列に移植できます。
- **切り替え（Cutover）**: エージェントは自動化できる作業を進め、あなたにしかできない手順（デプロイ、DNS、シークレット設定）については各ステップに切り戻し手段を備えた対話式スクリプト `rust/cutover.sh` を生成します。

徹底ヒアリングや調査といったこれらの手法は [Matt Pocock's skills](https://github.com/mattpocock/skills) を参考にしています。

まずは計画を立てます。`rust-anything analyze . --whole-app` を実行すると、アプリの形状（CLI、サーバー、ライブラリ）とエントリポイント、（インポートまたは宣言された）すべての外部依存関係と対応 Rust クレート・適合度、ピース単位の移植順序（相互インポートするユニット群をまとめて移動）、そして推奨回答付きの番号付き決定事項（維持するユニット、ブロックされているユニット、クレートが存在しない・または部分的にしか対応しない依存関係）が出力されます。

次にプログラム全体を外側から証明します。`record` と `diff` が 1 ユニットを証明するのに対し、`app record` と `app replay` は 6 言語すべての CLI とサーバーについてアプリ全体を（ブラックボックスとして）証明します:

```sh
rust-anything app record . -- python3 cli.py          # 元のアプリを起動するコマンド
rust-anything app replay .                            # 元のアプリは 100% パスする必要がある
rust-anything app replay . --build "target/release/mytool"
```

- `app record` は、アプリ自身のドキュメント内の使用例（Markdown やシェルスクリプト内の `$ mytool ...` 行および参照ファイル）、`--inputs` JSONL ファイル（`{"name", "args", "stdin", "env", "files"}`）、そしてそれらのケースから派生させた意味的罠（非 ASCII や絵文字文字列、負数の除算と剰余、オーバーフロー、極大・極小の浮動小数点数、Map の順序、存在しないファイル）で元のアプリを実行します。各ケースは 2 回実行され、実行間で変化した箇所は `[..]` ワイルドカードになります。`--normalize timestamps|uuids|key-order` や `--normalize name=regex` で正規化ルールを追加し、ケースと一緒に保存できます。
- ケースは `rust/app-cases/` に [trycmd](https://docs.rs/trycmd) ファイルとして保存されます: `<case>.toml`（argv、env、終了コード）、`.stdin`、`.stdout`、`.stderr`、`.in/`（入力ファイル）、`.out/`（出力ファイル）。手で読んで編集でき、移植版にバイナリができたら Rust のテストから `trycmd` で実行できます。
- `app replay` は任意のビルド成果物に対してケースを実行し、`passed/total` を表示して、失敗したケースごとの diff を `rust/app-cases/replay-report.md` に書き出し、1 件でも不一致があれば非ゼロで終了します。下のフロントドアのように `RUST_ANYTHING_FALLBACK_LOG` で指定されたファイルに（元の実装へフォールバックするたび 1 行）追記するビルドであれば、フォールバック率もあわせて報告されます。
- `app replay --case <name>` はレポートに出力されたケース名を指定して 1 件だけ再実行します。全体を再実行する前に不一致を素早く修正するための、再現性の高いループです。

次にエントリポイントを Rust へ移し、1 ユニットずつコマンドを引き渡していきます:

```sh
rust-anything app front-door .                            # rust/app: すべてのコマンドで元の実装を実行
rust-anything app wire . textkit --command upper          # textkit-rs が gate を通過した後に実行
# rust/app/src/units/textkit.rs にグルーコードを記述し、次に:
rust-anything app wire . textkit                          # 再び 100% 通過、フォールバック率が低下
```

- `app front-door` はアプリ名を冠した Rust バイナリ `rust/app` のひな形を生成します。記録ケース内のコマンドとフラグを受け取る clap パーサーを備え、すべてのコマンドについて同じ argv・stdin・環境変数で元の実装を実行し、出力と終了コードをそのまま透過させます。フォールバックはすべてカウントされるため、生成直後のフロントドアをリプレイすると「100% 合格・フォールバック率 100%」になります（それを示すためにビルドとリプレイが実行されます）。既存の `rust/app` を上書きすることはないため、生成後のコードは自由に編集できます。
- `app wire <repo> <unit> --command <name>` は対象ユニットのクレートに `gate` を実行し（直前に通過済みなら `--skip-gate`）、`rust/app` にライブラリとして追加し、あなたやエージェントが中身（引数のパース、`<crate>::port` の呼び出し、元の実装と同じ出力の印字）を埋めるための `src/units/<unit>.rs` を初回のみ生成して、対象コマンドをそちらへルーティングし、ビルドとリプレイを実行します。lift が完了するまでは `RUST_ANYTHING_UNIT_<NAME>=original` で接続済みユニットを元の実装へ戻せます。

サブコマンドを指定しない argv（引数なし、未知のコマンド、使い方エラー）に対しては、アプリ自身の名前をコマンドとして接続してください（`--command mytool`）。

フォールバック率 0 でリプレイが全件合格し、すべてのユニットが `gate` を通過したら、純粋な Rust アプリに仕上げます:

```sh
rust-anything app lift .
```

- `app lift` は両方の条件を満たすまで実行を拒否し、何がブロックしているか（まだフォールバックしているケース、スタブのままのグルーコード、gate 未通過のユニット）を表示します。
- まずコピー上で作業し、フォールバック経路とキルスイッチを取り除き、各ユニットクレートを `rust/app` の通常のライブラリ（`cdylib` やバインディング、生成ラッパーなし）に変換し、`cargo test` 時に trycmd で `rust/app-cases` を実行する `rust/app/tests/app_cases.rs` を追加します。これにより CI で必要なものは cargo だけになります。
- 続いてリフトチェックリストを実行します: 全ユニットと `rust/app` に対する fmt、clippy `-D warnings`、テスト、`rust/DECISIONS.md` に記載されたインストール済みターゲットのビルドまたはチェック、実行時に読み込むファイルや未埋め込みのアセットフォルダの確認、そして純粋バイナリでのリプレイです。これらすべてに通った場合のみ変更が書き戻されます。元のコードには一切手を触れません。

### サーバー

HTTP サーバーも同様のコマンドで検証できます。`--http` はコマンドがサーバーを起動することを示し、ポート番号は `PORT` 環境変数またはコマンド内の `{port}` から渡します（常に固定ポートで待ち受けるサーバーには `--port` を使用）:

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: 全ルートをプロキシ
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- リクエストはアプリのドキュメント内の `curl` 行（`curl -X POST -d ... http://localhost:8080/x`）、`--inputs`（`{"name", "method", "path", "headers", "body"}`）、および罠ケースから収集されます。パスセグメントとクエリ値は CLI 引数と同じ罠に置き換えられ、ボディはテキストおよび JSON の罠に置き換えられ、さらに未知のルートも追加されます。各実行ではサーバーを新しく起動して名前順にリクエストを送るため、リクエスト間の状態も維持されます。
- ケースは `rust/app-cases/http/<case>.toml`（リクエスト、ステータス、重要なヘッダ）と `<case>.body`（レスポンスボディ、2 回の実行で異なった箇所は `[..]`）として保存されます。`Date` や `Server` のようなリクエストごとに変わるヘッダは除外され、不要なヘッダ行は削除できます。
- フロントドアは axum サーバーとして動作し、別ポートで元のサーバーを起動して、どのユニットも応答しないルートをすべてプロキシします。`wire --route` には axum 形式のルート（`METHOD /path/{param}`、任意メソッドの `/path`、その他すべての `*`）を指定します。グルーコードにはルート、パラメータ、リクエストが渡されます。`lift` によりプロキシが取り除かれ、以後は CI 上で `app replay` により HTTP ケースを実行できます。

### ライブラリ

ライブラリにはリプレイ対象のプロセスが存在しないため、公開 API 自体がフロントドアとなり、各ユニットの記録済みケースが証明になります。

```sh
rust-anything app front-door .        # rust/app: 公開 API を持つ Rust クレート
# 各ユニットでループを実行: bridge、record、port.rs、build、diff、gate。その後:
rust-anything app wire . textkit-rs   # rust/app から再エクスポート。元の側はそのシャドウをインポート
rust-anything app replay .            # 接続済み全ユニットのケースを実行。フォールバック = まだ元の実装にあるエクスポート
rust-anything app lift .
```

- `app front-door` はリポジトリに `main` もサーバーもない場合（それ以外は `--library` を指定）に公開 API（各ユニットのエクスポート）を検出し、ライブラリクレートとして `rust/app` を生成します。接続された各ユニットはそのモジュールになります: `pub use textkit_rs::port as textkit;`。
- `app wire` は `bridge` で作成したクレートを受け取り、`gate` を実行し、そのユニットのシャドウ差し替えモジュールを書き出します。元のパッケージはユニットの代わりにこれをインポートするため、呼び出し側は元の API のまま Rust 実装に到達します。`RUST_ANYTHING_UNIT_<NAME>=original` でユニットを元に戻せます（C の場合はシャドウ用フラグなしでビルド）。
- `app replay` は接続済みの各ユニットの記録済みケースをバインディング経由で実行します。フォールバック率は、未接続のユニットや `bridge` が元の言語に残したエクスポートなど、まだ Rust が応答していない公開エクスポートの割合を表します。
- `app lift` にはフォールバック 0 と全ユニットの `gate` 通過が必要です。ユニットからバインディング、ラッパー、シャドウを取り除き、`rust/app` を 1 つの純粋な Rust ライブラリとして残します。`port.rs` には一切触れないため、バインディング越しに一致していたケースは引き続きその挙動を表します。チェックリストでは、まだシャドウをインポートしている元コードのファイルについて警告を出します。

これら 5 つのコマンドは MCP ツールとしても用意されています: `app_record`、`app_replay`、`app_front_door`、`app_wire`、`app_lift`。

## ケーススタディ: x18n のコア

API を変更せずに移行できる x18n コアの全 29 関数を rust-anything で移植しました。すべてのゲートを通過し、7,925 件の記録済みケースが完全に一致しました。しかしその後、`rust-anything bench` によって、処理そのものよりブリッジのコストの方が大きいため JS から呼び出すと TS より遅くなることが判明しました。詳細なレポートは [`demo/x18n-core`](../demo/x18n-core/README.md) にあります。この教訓は仕組みに組み込まれています: 移植版を出荷する前に `bench` で必ず計測してください。

## ホットパス: データを Rust 側に保持する

要素ごとに 1 回ずつ呼び出される移植コードは、要素のたびにブリッジコストを払うため JIT に負けます。勝つ方法はループごと移行することです: `profile` がそれを見つけ出し、`--batch` が要素を一度だけ受け取り、呼び出しごとに全コアを使って全要素へ関数を適用し型付き配列で結果を返すクラスを生成します。

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: 実行時間の 4 分の 1 を占め、`matched` からキーごとに呼ばれている: バッチ化する
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // 初回のみ
const order = search.rank(query, 0)               // キー入力ごと: 最適順のインデックス配列
```

`port.rs` の `FuzzyScoreIndex` 構造体は、デフォルトのループを「要素を一度だけ前処理し、自力でランキングできる（`rank`）」実装に置き換えます: 小文字化したキーとそれぞれの文字マスク、各キーにおける一般的な文字の初回出現位置テーブル（1 文字クエリなら 1 列だけ見る）、そして直前のクエリの一致結果（`s` に続いて `se` と入力したら `s` が一致したものだけ再スコアする）を保持します。50,000 キーに対する x18n のサイドバー検索で、1 文字ずつ入力した場合の同一結果での比較は次の通りです:

| | 1 クエリあたり | vs TS |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`、filter、sort | 10 ms | 1x |
| インデックスと同じ絞り込みを行う TS | 4.1-5.4 ms | 2x |
| 同じ移植版をキーごとに個別呼び出し | - | 0.2-0.4x |
| `FuzzyScoreBatch`、デフォルトインデックス（4 コア） | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` + `FuzzyScoreIndex`（napi、4 コア） | 0.45-0.56 ms | **18-22x** |
| 同じ実装を wasm で実行（シングルスレッド） | 0.95 ms | **11.5x** |

同じ絞り込みを行う TS と比較しても、Rust は依然として 7〜12 倍高速です（wasm は 5 倍）。返されたインデックスをキーに戻す際は単純なループを使ってください: `Array.from(order, i => keys[i])` は 20 倍（0.4 ms）も余計に時間がかかります。

すべての言語でバッチクラスを利用でき、個別呼び出しでは負けるケースでも元の実装を上回ります。4 コアでの同一ワークロード、同一の結果とエラーでの比較です（各 demo フォルダにベンチマークあり）:

| 言語 | ワークロード | 元の実装 | 個別呼び出し移植版 vs 元の実装 | バッチ vs 元の実装 |
| --- | --- | ---: | ---: | ---: |
| TS | x18n 検索、50,000 キー | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`、20,000 文字列 | 98 ms | - | **17x** |
| Ruby | `slugify`、20,000 文字列 | 110 ms | - | **12.7x** |
| Ruby | `shellescape`（標準ライブラリ）、50,000 混合値 | 88 ms | - | **11.8x** |
| Go | `Slugify`、50,000 文字列 | 49 ms | 0.93x | **4x** |
| Java | `slugify`、50,000 文字列 | 43 ms | 0.68x | **3x** |

元の言語がコンパイル言語の場合は伸び幅が小さくなります。要素ごとの処理がすでに高速なため、バッチ化による高速化は主にコア数に比例するためです。バッチクレートはアロケータに mimalloc を使用しています: システムアロケータでは Go のバッチ版がシングルスレッドより遅くなりました。デモ: [`demo/x18n-search`](../demo/x18n-search/README.md)。

## 6 言語の実コードでの検証

Go の `path`、Ruby の `shellwords`、Python の `colorsys`、そして薄いファサード越しに扱う JDK と glibc の挙動まで、合計 13,010 件の記録済みケースですべての移植版がゲートを通過しました。これらの実行を通じて rust-anything 自体のバグも見つかり修正されました（`serde_json` 経由で浮動小数点が 1 ULP ずれる問題、記録中の C のクラッシュ、型のないコードにゴミ入力が渡る問題）。関数単位で呼び出した場合、Ruby 移植版は Ruby より 4.4 倍、Python 移植版は CPython より 1.35 倍高速で、Go と Java のリーフ関数は元の言語のままの方が高速でしたが、バッチ化するとすべてが勝利します（上の表を参照）。
レポート: [`docs/real-world-languages.md`](./real-world-languages.md)。

## 例: x18n の実際のモジュール

[x18n](https://github.com/x18n-dev/x18n) の `packages/core/src/fuzzy.ts` を [`demo/`](../demo) 内で両方の方式で移植した例です:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: 移植可能、wasm-bindgen（core はブラウザ上で動作）
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# src/port.rs を記述
rust-anything gate demo/fuzzy-rs
```

Rust の `char` 単位でインデックスを扱った最初の移植版は、単純なテストには通ったものの `diff` で失敗しました:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS の `indexOf` は UTF-16 コード単位で数えるため、絵文字 1 つが 2 位置分になります。`demo/*/src/port.rs` の移植版では生成された `utf16` ヘルパーを使用し、napi-rs（`demo/fuzzy-napi`）と wasm-bindgen（`demo/fuzzy-rs`）の両方で 2000/2000 ケースおよびゲートを通過しています。

rust-anything が x18n 全体に対して生成した計画: [`docs/examples/x18n.md`](./examples/x18n.md)。

## インストール

```sh
cargo install --path .
```

`record`、`diff`、`bench` は元の実装をそれぞれのランタイム上で実行します: TS には Node 22.6+（`.ts` ソースを直接実行可能）、Python と C（ctypes）には Python 3.9+、Go 1.21+、Ruby 3+、JDK 17+（`javac` と `java`）が必要です。C ではさらに C コンパイラも必要です。wasm ブリッジを使う場合は `rustup target add wasm32-unknown-unknown` および `cargo install wasm-bindgen-cli --version <該当クレートの wasm-bindgen バージョン> --locked` も必要です（正確なバージョンは `build` が表示します）。

エージェント向けには `rust-anything setup` がすべてを登録します（クイックスタートを参照）。代わりに 1 つのプロジェクトへ手動で MCP サーバーを追加する場合は、`.mcp.json` に次のように記述します:

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` が判断すること

- ブリッジを越えられないエクスポートは理由とともに元の言語に残され、シャドウモジュールが元の実装を再エクスポートします。TS の場合、関数を受け取る／返す関数、ジェネレータとイテレータ、RegExp、`instanceof` チェック、ジェネリクス、および型（インポート、再エクスポート、`extends` を辿って解決）に関数を含む値が対象です。`--keep "name: reason"` を使うと、例えば `Intl` データに依存するコードなど、さらに多くを元の言語側に残せます。
- TS の型は Rust の型へマッピングされ、型エイリアスはインポート先を辿って解決し、引数の型はデフォルト値から推論されます。構造化データは自動生成されたバイナリワイヤプロトコル経由で渡されます（ワイヤが表現できない形状のみ JSON にフォールバック）。
- JSON は `undefined`、NaN、Infinity、-0、孤立サロゲートを表現できないため、構造化値にはマーカー（`{"$undefined": true}`、`{"$num": "NaN"}`、`{"$utf16": [...]}`）が付与され、生成された `index.cjs` がクレート内の `js.rs` のヘルパーとともに変換を行います。

`record` は TS ソースをそのまま実行します: Node の resolve フックがバンドラ形式のインポート（`./errors` から `./errors.ts` へ）を解決し、リポジトリに npm パッケージが未インストールの場合は `--resolve-from` で供給でき、変換が必要な TS 構文（enum やパラメータプロパティ）は `--experimental-transform-types` で再試行されます。

## `analyze` が見ること

- パッケージ（`package.json`）とソースファイルを解析し、`node_modules`、ビルド出力、フィクスチャ、プレイグラウンド、ツール設定はスキップします。Vue/Svelte/Astro の `<script>` ブロックもインポート抽出のため解析されます。
- **ユニット**: ソースファイルのフォルダ、またはパッケージのソースルートにあるファイル。
- **ウェーブ**: インポートされる側のユニットが先のウェーブに入り、循環インポートはまとめて移植されます。
- **ブリッジ**: ユニットやそのインポート先が Node を必要とする場合は napi-rs、ポータブルなコードには wasm-bindgen、UI やエディタ関連コードは JS 側に維持。
- **準備度（Readiness）**（どれほど安全か）と**優先度（Priority）**（安全かつ移植する価値が高いか: ループや文字列処理、テストの有無、サイズ）。

| リスク | 重要度 | 例 |
| --- | --- | --- |
| 文字列オフセット | high | `slice`、`indexOf`、`matchAll`、`d` フラグ: UTF-16 と UTF-8 の違い |
| 正規表現構文 | high | 先読み／後読み、後方参照、`y` フラグ: `regex` クレートでは非対応 |
| 動的正規表現 | high | `new RegExp(userPattern)`: 実行時の JS 構文 |
| 動的コード | high | `eval`、`new Function`、動的に計算される `import()` |
| 動的型付け | medium | `any`、`'key' in value` |
| 順序付きコレクション | medium | `Map`、`Set`、`Object.keys`: 挿入順の保持 |
| 非同期・ジェネレータ | medium | Promise とジェネレータの境界 |
| クラス継承・リフレクション | medium | `extends`、`Proxy`、`Reflect`、`Symbol` |
| コールバック形式の API | medium | 関数型の引数やメソッド: ブリッジ越しの呼び出しが多発 |
| 例外・数値・JSON | low | `throw`、ビット演算、`JSON.stringify` のキー順 |

## 開発

```sh
cargo test                        # ユニットテスト、フィクスチャリポジトリ、record/diff/shadow ループ（node が必要）、言語ごとの app record/replay
cargo clippy --all-targets -- -D warnings
cargo fmt
```

設計上の選択とその理由は [DECISIONS.md](../DECISIONS.md) に記載しています。

## 更新またはアンインストール

```sh
cargo install rust-anything                                    # 更新（Cargo）
npm install -g rust-anything@latest                            # 更新（npm）
rust-anything setup                                            # エージェント設定を再反映
rust-anything setup --remove && cargo uninstall rust-anything  # 削除（Cargo）
rust-anything setup --remove && npm uninstall -g rust-anything # 削除（npm）
```

`setup --remove` は rust-anything のエントリだけを取り除きます。書き込み前に現在の設定ファイルが `<file>.rust-anything.bak` に再バックアップされるため、初回 `setup` 時のバックアップは上書きされ、そのファイルはあなたが削除するまで残ります。

## 検出できないもの

合格とは「記録されたすべてのケースと Rust の結果が一致した」という意味であり、それ以上ではありません。書き直しでつまずきやすい点は通常、記録の外側に潜んでいるため、限界を把握しておいてください:

- **記録されなかった入力。** 生成されたケース、罠ケース、そしてあなた自身の `--inputs` が検証の上限です。実際の入力（本番環境のサンプル、バグ報告、元のテストフィクスチャ）を追加してください。本番環境を壊すユーザー入力は、ジェネレータが思いつくようなものとは限らないからです。
- **正規表現。** `regex` クレートには先読み／後読みや後方参照がなく、コンパイルできるパターンであっても非 ASCII テキストに対する `\w`、`\b`、`\d` や大文字小文字を区別しないマッチの挙動が JS、Python、Java と異なる場合があります。`fancy-regex` に差し替えたりパターンを書き換えたりして記録済みケースすべてに通ったとしても、トルコ語のドットなし `ı` やゼロ幅接合子（ZWJ）で食い違うことがあります。`record` は正規表現を使うファイル内の全関数に正規表現の罠（前述の文字、ケルビン記号、長い s、アラビア・インド数字、行区切り文字、語末シグマ）を追加しますが、実際のテキストに対して実際のパターンをファズテストすることも重要です。
- **実行ごとに変化するもの。** `record` は元の実装を 2 回実行して差異を分類します: 変化した値（時刻、ID）はワイルドカードになり、順序だけが異なる同じ行（ハッシュマップ、並行処理）は順不同で比較されるため移植版でもまったく同じ行を出力する必要があり、行数が変わる部分は任意の内容にマッチする `...` になります。`record` は種類ごとに一覧を出力するので、すべてに目を通してください。ハッシュ順や並行性の違いは、まさに移植版で実際に挙動が変わり得る箇所です。
- **浮動小数点数。** 数値から文字列へのフォーマットは言語ごとに異なります（`1e21`、`-0`、桁数など）。罠ケースにはそれらの値が含まれており、完全に一致する必要があります。`--float-tolerance` が許容するのは丸め誤差のみであり、フォーマットの違いは許容されません。
- **出力に現れないもの。** 実行時間、メモリ使用量、高負荷時の並行性、および標準出力・標準エラー・終了コード・書き込まれたファイル・HTTP レスポンス以外の副作用（ネットワーク呼び出し、データベース、シグナル）は比較されません。
- **他のプラットフォーム。** 記録が証明するのは、それを実行したマシン上での挙動だけです。型のサイズやエンディアン、コンパイラに結果が依存する C コードは、ターゲット環境で異なる動きをする可能性があります。`analyze` がハードウェア寄りの C コードを C に残すのはそのためです。

## よくある質問

**コードを自動で書き換えてくれますか？** いいえ。どこを移すべきかを見つけ、ブリッジを生成し、元の実装の挙動を記録し、それに対して Rust を検証します。`port.rs` の Rust コードを書くのはあなたやあなたのエージェントで、正しいかどうかを判定するのが `diff` と `gate` です。

**アプリの API は変わりますか？** いいえ。呼び出し側は同じ関数をインポートし続けます（あるいは、信頼性を確かめる間は両方を実行して元の結果を返すシャドウモジュールを使います）。

**Rust は常に速いですか？** いいえ、rust-anything はその事実もそのまま伝えます。要素ごとに 1 回ずつ呼ばれる小さな関数は、毎回ブリッジを越えるコストがかかるため、Rust の方が遅くなりがちです。V8、JVM、Go はそのような関数をナノ秒単位で実行します。`profile` がその外側のループを見つけ、`--batch` がループごと移植し、`bench` が出荷前に判定を下します。numba、Cython、JAX ですでにマシン語にコンパイルされているコードも同様で、`profile` と `analyze` は移植しても速度向上の余地が少ないとしてフラグを立てます。

**数値計算コードなのですが、浮動小数点は完全に一致しますか？** 一致しないことがよくあります: 演算順序、積和演算（FMA）、数学ライブラリはコンパイラごとに異なります。`--float-tolerance 1e-9` を指定して記録（`record` または `app record`）すると、大きい方の値のその割合以内（絶対値が 1 未満なら絶対誤差）で一致とみなします。整数、文字列、構造体は引き続き完全一致が必要です。

**APK、JAR、`.exe` しかないアプリを移植できますか？** いいえ。対象はソースコードの移植です。関数をパースし、それぞれの挙動を記録し、実行中の元の実装と照合して Rust を検証します。コンパイル済みアプリにはその材料がなく、`analyze` もその旨を表示します。バイナリの観測可能な挙動から新しい Rust アプリを一から書くのは別のプロジェクトの領域です。

**実績のある C コードも移植すべきですか？** 多くの場合すべきではなく、`analyze` が該当箇所を指摘します。ハードウェアレジスタに触れる、コンパイラの型サイズやメモリレイアウトに依存する、あるいはインラインアセンブリを使う C コード（`volatile`、ビットフィールド、パック構造体、`__asm__`、アドレスへの整数キャスト）は「C に残す（keep in C）」とマークされます。手元のマシンでの記録はターゲット環境での動作を証明せず、安定したドライバやファームウェアを書き直すメリットは薄いからです。その周辺にあるポータブルなロジック（パース、プロトコル、データ処理）こそが移植に向いています。

**Electron アプリを移植できますか？** ロジックは可能で、ウィンドウはウェブページのまま残ります。`analyze --whole-app` は Electron を認識し、レンダラーをそのままにメインプロセスを段階的に移行する計画を立てます。ロジックが Rust になった後、UI を Tauri（同じ Web UI を Rust バックエンド上で動かす構成）へ移すのは独立した次のステップになります。

**C#、Kotlin、Swift はどうですか？** C# はプレビュー版です（[対応言語](#対応言語)を参照）。Kotlin と Swift はまだ対応していません。言語ごとにパーサー、レコーダー、ブリッジ、リプレイドライバをすべてエンドツーエンドでテストして構築する必要があります。必要な言語があれば Issue を立てるか、既存の Issue に投票してください。

**移植後の Rust コードは元のコードよりかなり大きくなりませんか？** そうはならないはずです。`gate` は移植版の行数を元の実装と比較し、3 倍（に加えてインポートとシグネチャ用の 50 行）を超えると失敗させます。そうなるのは通常、既存のクレートでできる処理を手書きしていたり、ケースを一つずつ個別処理していたりする場合です。使うべきクレートは `analyze` が一覧表示します。

**一つずつ移植すると、Rust 側が古いアプリの設計に縛られませんか？** 両者が並行稼働している間だけです。記録はアプリの境界での挙動（CLI の出力、サーバーのレスポンス、モジュールのエクスポート関数）をチェックしており、内部実装までは縛りません。ユニットがまだブリッジを越えている間だけ旧構造を鏡写しにし、`app lift` で元の実装を取り除いた後は自由に Rust 側を再構築してください。その状態でも `app replay` で挙動は引き続き証明できます。また元の実装への逆呼び出しも発生しません: フロントドアは元の実装を別プロセスとして実行（または HTTP を転送）し、ブリッジされたユニットは元の実装から呼ばれるだけで逆はなく、コールバックは元の言語側にとどまります。

**コードがマシンの外に送信されますか？** いいえ。rust-anything はローカルで動作し、あなたのコードをどこにも送信しません。Cargo は通常通りクレートをダウンロードし、エージェントがモデルプロバイダへ送る内容については各プロバイダ自身のポリシーに従います。

**何のインストールが必要ですか？** Rust に加え、移植対象言語のランタイムが必要です（[インストール](#インストール)を参照）。

**何か壊れています。** 実行したコマンド、その出力、お使いのプラットフォームを添えて Issue を開いてください。

## スポンサー

rust-anything は無料のオープンソースソフトウェアです。お役に立ちましたら、ぜひスポンサーをご検討ください。皆様のご支援が開発を支えます。

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### 企業スポンサー

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### 個人スポンサー

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

## 貢献

Issue や Pull Request を歓迎します。[CONTRIBUTING.md](../CONTRIBUTING.md) にセットアップ手順、テストの配置場所、新しい言語の追加方法が記載されています。設計上の選択とその理由は [DECISIONS.md](../DECISIONS.md) にあります。実際の移植事例（ケーススタディ）も特に歓迎しています。セキュリティ上の問題は非公開でご報告いただき（[SECURITY.md](../SECURITY.md)）、[行動規範](../CODE_OF_CONDUCT.md)をご確認ください。

## ライセンス

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman)。あなたのリポジトリで作成された移植版および生成コードはすべてあなたのものです。
