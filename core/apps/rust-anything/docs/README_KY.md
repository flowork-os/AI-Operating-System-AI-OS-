<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="rust-anything краб, оозу код тегинин формасында">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">автору: <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · Кыргызча · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>Бул котормону коомчулук колдойт, ошондуктан ал <a href="../README.md">англисче README</a> нускасынан артта калышы мүмкүн.</sub></p>

<p align="center"><em>Бүт колдонмоңузду Rust тилинде кайра жазыңыз. Бүт жол бою анын иштеп турушун сактаңыз.</em></p>

<p align="center"><em>CLI'лар, серверлер жана китепканалар, бөлүк-бөлүгү менен, ар бир кадамда түп нуска менен салыштырылып текшерилет.</em></p>

<p align="center">Node.js жана TypeScript · Python · C · Go · Ruby · Java · PHP жана C# preview абалында</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io версиясы"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm версиясы"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 тил">
  <a href="#шайкеш-агенттер"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 агент менен иштейт"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Тесттер"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT лицензиясы"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub жылдыздары"></a>
</p>

<p align="center">20x чейин ылдамыраак · 38,251 жазылган кейс кайра ойнотулду · 0 дал келбестик · бир буйрук</p>

<p align="center">
  <img src="assets/race.gif" alt="x18n издөөсүнө 50,000 ачкыч боюнча user.profile терилүүдө: TypeScript 143 ms коротот, rust-anything batch 6.9 ms, ар бир баскычты басканда натыйжалар бирдей." width="820">
</p>

**Бүт колдонмоңузду Rust тилинде бөлүк-бөлүгү менен кайра жазыңыз.** rust-anything сиздин Node.js
(TypeScript/JavaScript), Python, C, Go, Ruby же Java колдонмоңуз бүгүн эмне кылып жатканын жазып
алат, андан кийин Rust нускасынын ар бир бөлүгүн кийинкисине өтүүдөн мурун ошол жазуу менен салыштырып
текшерет, колдонмо толугу менен таза Rust болгонго чейин. CLI'лар, HTTP серверлер жана китепканалар;
Rust кодун сиздин коддоо агентиңиз (же өзүңүз) жазат. Ал жазуу камтыган нерсени гана кармай алат:
[Ал эмнени кармай албайт](#ал-эмнени-кармай-албайт) бөлүмүн караңыз. Жай бөлүгүн гана ылдамдатуу керекпи?
Ошону гана порттоңуз, бир убакта бир hot path:

| Чыныгы жүктөм, натыйжалары түп нуска менен бирдей | Түп нуска | rust-anything менен |
| --- | ---: | ---: |
| x18n каптал панелиндеги издөө, 50,000 ачкыч (TypeScript, Node) | бир суроого 10 ms | **0.5 ms: 20x ылдамыраак** |
| Ошол эле издөө браузерде (wasm, бир агым) | 10 ms | **0.95 ms: 11.5x** |
| `slugify`, 20,000 сап (Python) | 98 ms | **17x ылдамыраак** |
| Ruby стандарттык китепканасындагы `Shellwords.shellescape`, 50,000 маани | 88 ms | **11.8x ылдамыраак** |
| `Slugify`, 50,000 сап (Go) | 49 ms | **4x ылдамыраак** |
| `slugify`, 50,000 сап (Java) | 43 ms | **3x ылдамыраак** |

4 ядродо өлчөндү; ар бир сан үчүн [`demo/`](../demo) ичинде адегенде натыйжалардын бирдей экенин
текшерген бенчмарк бар. Ар бир кичинекей функция үчүн Rust'ту өзүнчө чакыруу адатта JIT'тен *жайыраак*;
rust-anything көчүрүүгө арзый турган циклди таап, ошону көчүрөт.

> rust-anything көз карандысыз долбоор, ал Rust Project же Rust Foundation уюмдары менен байланышкан
> эмес жана алар тарабынан колдоого алынган эмес. "Rust" Rust Foundation уюмунун соода белгиси.

## Тез баштоо

Муну Claude Code, Codex, Cursor же Gemini CLI ичине чаптап, орнотууну агентиңизге тапшырыңыз:

```text
Install rust-anything: run `cargo install rust-anything`, then `rust-anything setup`.
Tell me when to restart you.
```

Же өзүңүз:

```sh
cargo install rust-anything   # from crates.io
rust-anything setup           # registers it with Claude Code, Codex, Cursor and Gemini CLI
```

Rust toolchain азырынча жокпу? macOS, Linux жана Windows үчүн даяр бинардык файлдар ар бир
[GitHub release](https://github.com/erkamyaman/rust-anything/releases) барагына тиркелген, ал эми
JavaScript долбоорлору үчүн `npm install -g rust-anything` ошол эле бинардык файлды орнотот.

Claude Code ичинде аны плагин катары да орнотсоңуз болот (MCP сервер жана skill; жогорудагы CLI сиздин
`PATH` ичинде болушу керек):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` тапкан ар бир агентке MCP серверди кошот жана workflow skill'ин агент skill'дерди окуган жерге
орнотот. Ал башка жөндөөлөрүңүздү сактайт, аны кайра иштетүү коопсуз, ал эми `--remove` баарын артка
кайтарат. Андан кийин агентиңизден, мисалы, мындай сураңыз:

- *"Бул CLI'ды rust-anything менен башынан аягына чейин Rust тилинде кайра жаз жана анын так ошондой иштээрин далилде."*
- *"Бул издөө жай иштеп жаткандай. Аны rust-anything менен профилде жана hot loop'ту Rust'ка көчүр."*
- *"rust-anything менен `src/parser/` папкасын Rust'ка көчүрүү планын түз; биринчи бирдикти порттоп, далилде."*
- *"`rust/text-rs` ичиндеги Rust портун түп нуска менен бенчмарк аркылуу салыштыр да, аны чыгаруу керекпи, айт."*

### Шайкеш агенттер

| Агент | `rust-anything setup` кошкону |
| --- | --- |
| Claude Code | `~/.claude.json` ичинде MCP сервер, `~/.claude/skills/` ичинде skill |
| Codex | `~/.codex/config.toml` ичинде MCP сервер, `~/.codex/skills/` ичинде skill |
| Cursor | `~/.cursor/mcp.json` ичинде MCP сервер |
| Gemini CLI | `~/.gemini/settings.json` ичинде MCP сервер |
| Башка каалаган MCP кардар | `rust-anything mcp` буйругун stdio сервер катары кол менен кошуңуз ([Орнотуу](#орнотуу) бөлүмүн караңыз) |

Бар файлды өзгөртүүдөн мурун `setup` анын көчүрмөсүн жанына сактайт (`<file>.rust-anything.bak`).

Же кадамдарды өзүңүз аткарыңыз:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile циклдеги fuzzyScore функциясын табат, bridge --batch Rust crate'ин генерациялайт, gate 2000/2000 жазылган кейс менен өтөт, ал эми бенчмарк TS'тен 20.7x ылдамыраак экенин көрсөтөт." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # what is hot, and who calls it
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# write src/port.rs (or let your agent), then:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # every recorded case must match
rust-anything bench rust/fuzzy-rs                      # faster? the verdict says
rust-anything gate rust/fuzzy-rs                       # done means this passes
```

rust-anything кодду которбойт: Rust кодун сиздин коддоо агентиңиз (Claude Code, Codex, Cursor, ...)
же өзүңүз жазасыз. rust-anything агент ишенимдүү түрдө болжолдой албаган нерселерди берет: убакыт
кайда кетет, адегенде эмнени жана кандай тартипте порттоо керек, калган код Rust'ту API'син өзгөртпөй
чакырышы үчүн bridge, порт дал келиши керек болгон так жүрүм-турум, аны чыгаруунун коопсуз жолу жана
порт качан даяр болгонун айткан gate.

## Тилдер

| Тил | Бирдик | Bridge | Ким жазып алат жана кайра ойнотот |
| --- | --- | --- | --- |
| TypeScript/JavaScript | папка же файл | генерацияланган бинардык wire менен napi-rs же wasm-bindgen; класстар жана async да бар | Node, `.ts` баштапкы файлдарын түз иштетет |
| Python | пакет же модуль | PyO3 (abi3), түз айландыруу, типтелген exception'дор | Python, түп нусканы импорттойт |
| C | `.c` файлы | түп нуска аталыштары жана header менен `extern "C"` функциялары | shared library катары компиляцияланган түп нуска, ctypes аркылуу чакырылат, ар бир кейске бир fork |
| Go | пакет | типтелген cgo чакыруулары жана генерацияланган бинардык wire, түп нуска API'си бар пакетте | генерацияланган Go драйвери, өзүнчө модуль катары курулат |
| Ruby | модуль функцияларынан турган файл же папка | түп нуска модулдардын астындагы magnus кеңейтүүсү | генерацияланган Ruby драйвери |
| Java | `public static` методдорунан турган пакет | типтелген JNI жана генерацияланган бинардык wire, түп нуска методдору бар wrapper класстарында | генерацияланган reflection драйвери |
| PHP (preview) | функциялар жана `public static` методдорунан турган папка | кийинки кезекте: C ABI аркылуу PHP FFI | бүгүн бүт колдонмолор: `app record`, `app replay` жана front door, CLI'лар жана серверлер үчүн (`php -S`) |
| C# (preview) | `public static` методдорунан турган папка | кийинки кезекте: C ABI аркылуу P/Invoke | бүгүн бүт колдонмолор: `app record`, `app replay` жана front door, CLI'лар жана ASP.NET серверлери үчүн (`dotnet <app>.dll`) |

C'дан башка ар бир тил batch класстарын да алат (`--batch`): элементтер чектен бир жолу өтүп, Rust
ичинде калат, ал эми ар бир чакыруу алардын баарын бардык ядролордо иштетет.

Тил репозиторийден аныкталат (`go.mod`, `pom.xml`, `.csproj` же `.sln`, `pyproject.toml`, `Gemfile`,
`composer.json`, `package.json`, болбосо эң көп кездешкен баштапкы файлдар боюнча); `--lang` аны кол
менен көрсөтөт. Типтер баштапкы коддон алынат: TS типтери, Python hint'тери, C, Go, Java жана C#
сигнатуралары, Ruby YARD тегдери, PHP типтери жана phpdoc; сан катары колдонулган типсиз параметрлер
сан деп эсептелет.

PHP preview абалында: `analyze` PHP колдонмосун пландайт (Composer пакеттери жана PSR-4 autoloading,
loose comparison жана integer'дин float'ка толуп кетиши сыяктуу тобокелдиктер, crate'терге шайкештелген
Composer пакеттери), ал эми PHP CLI же серверин жазып алууга, кайра ойнотууга жана Rust front door'дун
артына коюуга болот. Анын бирдиктерин PHP FFI аркылуу Rust'ка порттоо кийинки кадам
([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# да ушундай эле preview абалында: `analyze` `.csproj` долбоорлорун жана алардын NuGet пакеттерин
окуйт (crate'терге шайкештелет), `using` директиваларын папкаларга чечет жана C# башкача кылган
нерселерди белгилейт (`decimal`, `dynamic`, LINQ'тун кийинкиге калтырылган суроо-талаптары, `Task`,
`lock`, reflection). C# CLI же ASP.NET серверин жазып алууга, кайра ойнотууга жана Rust front door'дун
артына коюуга болот; бирдиктерди P/Invoke аркылуу порттоо кийинки кезекте.

## Кантип иштейт

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 where the    what to     the Rust   what the    you or      every     faster?    both side   done means
 time goes    port first  crate and  original    your agent  recorded  the        by side in  this passes
                          wrapper    does        write it    case      verdict    production
```

Түп нуска чындыктын булагы бойдон калат: `record` аны чектик учурларда (жана сиздин өз киргизүүлөрүңүздө)
иштетип, эмне кайтарарын же кандай ката ыргытарын сактайт; `diff` ар бир кейсти Rust'ка каршы кайра
ойнотот; баары дал келип, `gate` өтмөйүнчө эч нерсе чыгарылбайт. Чакыруучулар бүт процесс бою түп
нусканын API'син колдоно беришет.

Бүт колдонмо да ошол эле циклден бирдик-бирдиги менен өтөт, бүт программаны далилдеген алкактын ичинде
([Бүт колдонмону порттоо](#бүт-колдонмону-порттоо)):

```
analyze --whole-app ──> app record ──> app front-door ──> per unit: the loop above, then app wire ──> app lift
 shape, every           what the app    Rust owns the       gate passes, so the unit answers in         pure Rust,
 dependency, the        does from the   entry point; the     Rust: replay 100%, fallback rate down      proved by
 decisions to make      outside         original answers                                                replay
```

## Цикл

| Кадам | Буйрук | Эмне кылат |
| --- | --- | --- |
| 0. Профиль | `rust-anything profile <repo> -- node bench.mjs` | Чыныгы жүктөмдү тилдин профайлеринин астында иштетет (node, cProfile, `go test` pprof, JFR, Ruby tracer): инклюзивдүү убакыт боюнча ысык функциялар, аларды чакыргандар жана кайсы циклдерди batch'ке айландыруу керек; мурунтан компиляцияланган кодду белгилейт (numba, Cython, JAX), анда Rust аз пайда берет |
| 1. План | `rust-anything analyze <repo>` | Бирдиктер, порттоо тартиби, `file:line` көрсөтүлгөн тобокелдиктер, ар бир бирдик үчүн bridge, көз карандылыктардын crate'терге шайкештиги, эң жакшы алгачкы порттор; `--whole-app` кирүү чекиттерин жана колдонмонун формасын, ар бир көз карандылыкты (импорттолгон же жарыяланган) анын crate'и менен, бөлүктөрдү (бири-бирин импорттогон бирдиктер чогуу көчөт) жана сунушталган жообу бар номурланган чечимдерди кошот |
| 2. Bridge | `rust-anything bridge <repo> <unit>` | Байланыштары бар crate (`lib.rs`, ошондой эле баштапкы тил жүктөгөн wrapper) жана порттоого арналган stub'тар (`port.rs`); `--batch fn:param` көп `param` маанилерин Rust ичинде кармаган класс кошот |
| 3. Жазуу | `rust-anything record <crate>` | Түп нусканы генерацияланган чектик учурларда (ASCII эмес, эмодзи, `-0`, `NaN`, float күтүлгөн жерде int, ...) жана ар бир параметрдеги ар бир семантикалык тузакта (саптын узундугу жана регистри, белгилүү бөлүү, толуп кетүү чектери, float'торду басып чыгаруу, map жана сорттоо тартиби) иштетип, `cases.jsonl` сактайт; `--float-tolerance 1e-9` сандык код үчүн float'торго ушул үлүштүн чегинде дал келүүгө уруксат берет |
| 3. Куруу | `rust-anything build <crate>` | Rust тарабын курат: `.node`, wasm пакети, Python кеңейтүүсү же shared library |
| 3. Салыштыруу | `rust-anything diff <crate>` | Жазылган кейстерди Rust'ка каршы, түп нусканы чакыргандар кандай чакырса, ошондой кайра ойнотот; дал келбестиктерди тизмелейт |
| 3. Бенчмарк | `rust-anything bench <crate>` | Жазылган кейстердин түп нускада жана Rust'та аткарылуу убактысын өлчөйт, bridge'ди кошо алганда |
| 4. Shadow | `rust-anything shadow <crate>` | Экөөнү тең иштеткен, түп нусканын натыйжасын кайтарган жана дал келбестиктер жөнүндө кабарлаган drop-in алмаштыргыч; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, тесттер, `unsafe` аудити, портталбаган эч нерсе калбашы, түп нусканын ар бир ката жолу үчүн жазылган ийгиликсиз кейс, түп нуска ката кайтарган жерде `unwrap`/`expect`/`panic!` болбошу (`// INFALLIBLE: <why>` деп белгиленбесе), build, API, жүрүм-турум |
| Агенттер | `rust-anything setup` | MCP серверди (`rust-anything mcp`, ар бир кадам tool катары) жана workflow skill'ин ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) сиздин коддоо агенттериңизге каттайт |

## Бүт колдонмону порттоо

Максат: түп нуска сыяктуу иштеген таза Rust колдонмосу, ал эми түп нуска эталон катары сакталат. Rust
кодун агентиңиз жазат; rust-anything ишти тартипке келтирет, каркасын түзөт жана ар бир кадамды
далилдейт. [Whole-app skill](../skills/rust-anything/whole-app.md) агентти ушул жол менен жетелейт,
сиз гана кабыл ала турган чечимдерден баштап:

- **Grilling**: агент суроолорду раунддар менен берет, ар бир суроодо сунушталган жооп болот, порт көз
  каранды болгон ар бир чечим аныкталганга чейин, жана ар бирин `rust/DECISIONS.md` ичине ADR катары
  жазат, ал эми `rust/GLOSSARY.md` түп нусканын терминдерин Rust аталыштарына шайкештейт.
- **Изилдөө**: фондук агенттер ар бир көз карандылыктын баштапкы булактарын окуп, тапкан ар бир
  семантикалык тузагы менен `rust/research/<topic>.md` жазышат.
- **Сессиялар аралык**: `rust/MAP.md` ар бир бирдикти абалы менен тизмелейт; сессия иш баштаардан мурун
  бир бирдикти өзүнө алат, ал эми ар бир checkpoint кийинки сессия үчүн `rust/HANDOFF.md` калтырат. Бир
  толкундагы бирдиктерди subagent'тер параллелдүү порттой алышат.
- **Cutover**: агент колунан келгенин жасап, `rust/cutover.sh` жазат, бул сиз гана аткара ала турган
  кадамдар (deploy, DNS, купуя ачкычтар) үчүн интерактивдүү скрипт, ар бир кадамда артка кайтуу жолу бар.

Grilling, изилдөө жана бул практикалар
[Matt Pocock'тун skill'деринен](https://github.com/mattpocock/skills) алынып, ыңгайлаштырылган.

Адегенде план: `rust-anything analyze . --whole-app` колдонмонун формасын (CLI, сервер же китепкана)
жана кирүү чекиттерин, ар бир тышкы көз карандылыкты (импорттолгон же жарыяланган) анын Rust crate'и
жана шайкештиги менен, порттоо тартибин бөлүктөр түрүндө (бири-бирин импорттогон бирдиктер чогуу көчөт)
жана сунушталган жообу бар номурланган чечимдерди кошот: сакталуучу бирдиктер, бөгөттөлгөн бирдиктер,
crate'и жок же жарым-жартылай гана бар көз карандылыктар.

Андан кийин бүт программаны сырттан далилдеңиз. `record` жана `diff` бир бирдикти далилдейт;
`app record` жана `app replay` колдонмону далилдейт, алты тилдин каалаганындагы CLI'лар жана серверлер
үчүн (колдонмо кара куту катары каралат):

```sh
rust-anything app record . -- python3 cli.py          # the command that runs the original
rust-anything app replay .                            # the original must pass 100%
rust-anything app replay . --build "target/release/mytool"
```

- `app record` түп нусканы колдонмонун өз документациясындагы мисалдарда (анын Markdown жана shell
  файлдарындагы `$ mytool ...` саптары, алар аталган файлдар менен), `--inputs` JSONL файлында
  (`{"name", "args", "stdin", "env", "files"}`) жана ошол кейстерден чыгарылган семантикалык тузактарда
  (ASCII эмес жана эмодзи саптары, терс бөлүү жана modulo, толуп кетүү, абдан чоң жана абдан кичине
  float'тор, map тартиби, жок файлдар) иштетет. Ар бир кейс эки жолу аткарылат; эки аткаруунун
  ортосунда айырмаланган нерсе `[..]` wildcard'ка айланат. `--normalize timestamps|uuids|key-order` же
  `--normalize name=regex` нормализаторлорду кошот, алар кейстер менен бирге сакталат.
- Кейстер `rust/app-cases/` ичиндеги [trycmd](https://docs.rs/trycmd) файлдары: `<case>.toml` (argv,
  env, exit code), `.stdin`, `.stdout`, `.stderr`, `.in/` (кирүүчү файлдар) жана `.out/` (жазылган
  файлдар). Аларды кол менен окуп, оңдой аласыз; порттун бинардык файлы пайда болгондо, Rust тести
  аларды `trycmd` менен иштете алат.
- `app replay` каалаган build'ди кейстерге каршы иштетет, `passed/total` басып чыгарат, ар бир
  ийгиликсиз кейс үчүн diff менен `rust/app-cases/replay-report.md` жазат жана каалаган дал келбестикте
  нөлдөн башка код менен аяктайт. `RUST_ANYTHING_FALLBACK_LOG` аталган файлга сап кошкон build (түп
  нускага ар бир fallback үчүн бир сап), төмөндөгү front door сыяктуу, өзүнүн fallback rate көрсөткүчүн
  да алат.
- `app replay --case <name>` отчеттогу аталышы боюнча бир кейсти кайра иштетет: баарын кайра
  иштетүүдөн мурун дал келбестикти оңдоо үчүн ылдам, кайталануучу цикл.

Андан кийин кирүү чекитин Rust'ка көчүрүп, буйруктарды ага бирден бирдик менен бериңиз:

```sh
rust-anything app front-door .                            # rust/app: every command runs the original
rust-anything app wire . textkit --command upper          # after textkit-rs passes gate
# write the glue in rust/app/src/units/textkit.rs, then:
rust-anything app wire . textkit                          # 100% again, lower fallback rate
```

- `app front-door` `rust/app` каркасын түзөт, бул колдонмонун атынан аталган Rust бинардык файлы:
  жазылган кейстердеги буйруктар жана флагдар үчүн clap парсери, мында ар бир буйрук түп нусканы ошол
  эле argv, stdin жана environment менен иштетип, анын чыгышын жана exit code'ун өзгөртпөй өткөрөт. Ар
  бир fallback саналат, ошондуктан жаңы front door'ду кайра ойнотуу 100% fallback менен 100% passed
  берет (муну көрсөтүү үчүн ал build жасап, replay иштетет). Ал `rust/app` папкасын эч качан кайра
  жазбайт: ушул учурдан тартып код сиздики.
- `app wire <repo> <unit> --command <name>` бирдиктин crate'ине `gate` иштетет (жаңы эле өткөн болсо,
  `--skip-gate`), аны `rust/app` ичине китепкана катары кошот, сиз же агентиңиз толтурушу үчүн
  `src/units/<unit>.rs` файлын бир жолу жазат (аргументтерди талдоо, `<crate>::port` чакыруу, түп нуска
  басып чыгарганды басып чыгаруу), буйруктарды ага багыттайт, андан кийин build жасап, replay иштетет.
  `RUST_ANYTHING_UNIT_<NAME>=original` кошулган бирдикти lift'ке чейин түп нускага кайтарат.

Эч бир буйрукту атабаган argv үчүн (аргументсиз чакыруу, белгисиз буйруктар, usage каталары)
колдонмонун өз атын буйрук катары кошуңуз (`--command mytool`).

Replay 0 fallback rate менен өтүп, ар бир бирдик gate'тен өткөндө, аны таза Rust колдонмосуна айландырыңыз:

```sh
rust-anything app lift .
```

- `app lift` эки шарт тең аткарылмайынча баш тартат жана эмне тоскоол болуп жатканын айтат: дагы эле
  fallback'ке түшкөн кейстер, дагы эле stub абалындагы glue код, gate'тен өтпөгөн бирдиктер.
- Адегенде көчүрмөдө fallback жолун жана kill switch'терди алып салат, ар бир бирдик crate'ин
  `rust/app` долбоорунун жөнөкөй китепканасына айландырат (`cdylib`, байланыштар же генерацияланган
  wrapper'лер жок) жана `cargo test` учурунда `rust/app-cases` кейстерин trycmd менен иштеткен
  `rust/app/tests/app_cases.rs` кошот, ошондуктан CI үчүн cargo'дон башка эч нерсе керек эмес.
- Андан кийин lift чек-листин аткарат: ар бир бирдикте жана `rust/app` ичинде fmt, clippy
  `-D warnings` жана тесттер, `rust/DECISIONS.md` ичинде аталган ар бир target орнотулган жерде курулат
  же текшерилет, иштөө учурунда окулган файлдар жана кыстарылбаган asset папкалары, жана таза бинардык
  файлда replay. Баары өткөндө гана өзгөртүүлөр кайра жазылат. Түп нускага эч качан тийбейт.

### Серверлер

Ошол эле буйруктар HTTP серверлерди да далилдейт. `--http` буйрук серверди иштетерин билдирет; ал
портун `PORT` өзгөрмөсүнөн же буйруктагы `{port}` ичинен алат (дайыма бир эле портту угуучу сервер
үчүн `--port`):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: every route proxied
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Суроо-талаптар колдонмонун документациясындагы `curl` саптарынан
  (`curl -X POST -d ... http://localhost:8080/x`), `--inputs` ичинен
  (`{"name", "method", "path", "headers", "body"}`) жана тузактардан алынат: жол сегменттери жана query
  маанилери CLI аргументтериндеги тузактар менен алмаштырылат, body'лер текст жана JSON тузактары менен,
  кошумча бир белгисиз route. Ар бир аткаруу серверди жаңыдан иштетип, суроо-талаптарды аталыш тартиби
  менен жөнөтөт, ошондуктан суроо-талаптардын ортосундагы абал сакталат.
- Кейстер `rust/app-cases/http/<case>.toml` (суроо-талап, статус жана маанилүү header'лер) жана
  `<case>.body` (жооптун body'си, эки аткаруу айырмаланган жерлерде `[..]`). Date, server жана ар бир
  жоопто өзгөрүүчү башка header'лер алынып салынат; өзүңүзгө кереги жок каалаган header сабын өчүрүңүз.
- Front door бул axum сервери: ал түп нусканы өзүнүн жеке портунда иштетип, эч бир бирдик жооп бербеген
  ар бир route'ту проксилейт. `wire --route` axum route'торун кабыл алат: `METHOD /path/{param}`,
  каалаган метод үчүн `/path`, калганы үчүн `*`; glue код route'ту, анын параметрлерин жана суроо-талапты
  алат. `lift` проксини алып салат; андан кийин HTTP кейстери CI ичинде `app replay` менен аткарылат.

### Китепканалар

Китепкананын кайра ойното турган процесси жок: анын public API'си front door болуп саналат, ал эми ар
бир бирдиктин жазылган кейстери далил болот.

```sh
rust-anything app front-door .        # rust/app: a Rust crate with the public API
# each unit through the loop: bridge, record, port.rs, build, diff, gate; then:
rust-anything app wire . textkit-rs   # re-exported from rust/app; the original imports its shadow
rust-anything app replay .            # every wired unit's cases; fallback = exports still in the original
rust-anything app lift .
```

- `app front-door` репозиторийде `main` да, сервер да жок болсо (болбосо `--library`), public API'ни
  (ар бир бирдиктин экспорттарын) табат жана `rust/app` папкасын китепкана crate'и катары түзөт. Ар бир
  кошулган бирдик анын модулуна айланат: `pub use textkit_rs::port as textkit;`.
- `app wire` `bridge` түзгөн crate'ти алат, `gate` иштетет жана бирдиктин shadow drop-in модулун жазат:
  түп нуска пакет аны бирдиктин ордуна импорттойт, ошондуктан анын чакыруучулары түп нусканын API'син
  сактап, Rust'ка жетишет. `RUST_ANYTHING_UNIT_<NAME>=original` бирдикти артка кайтарат (C: shadow'дун
  флагдарысыз куруңуз).
- `app replay` ар бир кошулган бирдиктин жазылган кейстерин анын байланыштары аркылуу иштетет. Fallback
  rate деп Rust азырынча жооп бербеген public экспорттордун үлүшүн айтабыз: кошулбаган бирдиктер жана
  `bridge` баштапкы тилде калтырган экспорттор.
- `app lift` 0 fallback жана ар бир бирдиктин `gate`'тен өтүшүн талап кылат; ал бирдиктерден
  байланыштарды, wrapper'лерди жана shadow'дорду алып салып, `rust/app` папкасын бир таза Rust
  китепканасы катары калтырат. Ал эч бир `port.rs` файлына тийбейт, ошондуктан байланыштар аркылуу дал
  келген кейстер аны дагы эле сүрөттөйт; чек-лист shadow'дорду дагы эле импорттогон түп нуска файлдары
  жөнүндө эскертет.

Бешөө тең MCP tool катары да бар: `app_record`, `app_replay`, `app_front_door`, `app_wire` жана
`app_lift`.

## Практикалык мисал: x18n ядросу

x18n ядросунун API'син өзгөртпөй көчүрүүгө мүмкүн болгон бардык 29 функциясы rust-anything менен
портталды: ар бир gate өтөт жана 7,925 жазылган кейс так дал келет. Андан кийин `rust-anything bench`
JS'тен чакырылганда порттор TS'тен жайыраак экенин көрсөттү, анткени bridge иштин өзүнөн кымбатка
турат. Толук отчет: [`demo/x18n-core`](../demo/x18n-core/README.md). Бул сабак куралдын өзүнө
киргизилген: портту чыгаруудан мурун `bench` менен өлчөңүз.

## Hot paths: маалыматты Rust ичинде кармоо

Ар бир элемент үчүн бир жолу чакырылган порт bridge баасын да ар бир элемент үчүн төлөйт жана JIT'ке
утулат. Циклди көчүрүү утат: `profile` аны табат, ал эми `--batch` элементтерди бир жолу кабыл алып,
функцияны ар бир чакырууда алардын баарына бардык ядролордо аткарган жана натыйжаларды typed array
түрүндө кайтарган класс генерациялайт.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: a quarter of the run, called per key by `matched`: batch it
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // once
const order = search.rank(query, 0)               // per keystroke: indexes, best first
```

`port.rs` ичиндеги `FuzzyScoreIndex` struct'у демейки циклди элементтерди бир жолу даярдаган жана өзү
рейтинг түзө алган (`rank`) цикл менен алмаштырат: ал ачкычтарды кичине тамга менен, ар бирин белги
маскасы менен сактайт, ар бир ачкычтагы ар бир көп кездешүүчү белгинин биринчи позициясынын таблицасын
кармайт (бир тамгалуу суроо бир мамыча болот) жана акыркы суроонун дал келүүлөрүн сактайт (`s` кийин `se`
терилсе, `s` дал келгендер гана кайра бааланат). x18n каптал панелиндеги 50,000 ачкыч боюнча издөөдө,
тамга-тамгасы менен терилгенде, натыйжалар бирдей болгондо:

| | Бир суроого | TS менен салыштырганда |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| Индекстегидей тарытуусу бар TS | 4.1-5.4 ms | 2x |
| Ошол эле порт, ар бир ачкыч үчүн чакырылат | - | 0.2-0.4x |
| `FuzzyScoreBatch`, демейки индекс (4 ядро) | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` жана `FuzzyScoreIndex` (napi, 4 ядро) | 0.45-0.56 ms | **18-22x** |
| Ошол эле нерсе wasm менен (бир агым) | 0.95 ms | **11.5x** |

Так ошондой тарытуу жасаган TS менен салыштырганда да Rust дагы эле 7-12x ылдамыраак (wasm 5x).
Кайтарылган индекстерди ачкычтарга жөнөкөй цикл менен айландырыңыз: `Array.from(order, i => keys[i])`
20x кымбатка, 0.4 ms'ке турду.

Ар бир тил batch алат жана алар ар бир чакырууга арналган порттор утулган жерлерде да түп нускадан
ашып түшөт. Ошол эле иш 4 ядродо, натыйжалар жана каталар бирдей (бенчмарктар ар бир demo папкасында):

| Тил | Жүктөм | Түп нуска | Ар бир чакырууга порт / түп нуска | Batch / түп нуска |
| --- | --- | ---: | ---: | ---: |
| TS | x18n издөөсү, 50,000 ачкыч | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 сап | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 сап | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 аралаш маани | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 сап | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 сап | 43 ms | 0.68x | **3x** |

Компиляцияланган түп нускалар азыраак утат: ар бир элементке кеткен иш ансыз да ылдам, ошондуктан batch
ядролордун санына жараша утат. Batch crate'тери mimalloc менен эс тутум бөлөт: системалык allocator
менен Go batch бир агымдан жайыраак болгон. Demo: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Алты тилдеги чыныгы код

Go'нун `path`, Ruby'нин `shellwords`, Python'дун `colorsys`, кичинекей facade'дардын артындагы JDK жана
glibc жүрүм-туруму: ар бир порт өз gate'инен өтөт, бардыгы 13,010 жазылган кейс. Бул сыноолор
rust-anything ичиндеги каталарды таап, оңдоду (`serde_json` аркылуу бир ULP'ка четтеген float'тор, жазуу
учурундагы C кулоолору, типсиз кодго маанисиз киргизүүлөрдүн берилиши). Ар бир функция үчүн
чакырганда Ruby порту Ruby'ден 4.4x, ал эми Python порту CPython'дон 1.35x ылдам иштейт, ал эми Go жана
Java'нын leaf функциялары өз тилинде ылдамыраак бойдон калат; batch катары алардын баары утат
(жогорудагы таблицаны караңыз). Отчет: [`docs/real-world-languages.md`](./real-world-languages.md).

## Мисал: x18n'ден чыныгы модуль

[x18n](https://github.com/x18n-dev/x18n) долбоорундагы `packages/core/src/fuzzy.ts`, эки жол менен тең
[`demo/`](../demo) ичинде портталган:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: ready, wasm-bindgen (core runs in browsers)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# write src/port.rs
rust-anything gate demo/fuzzy-rs
```

Rust `char` боюнча индекстеген алгачкы порт жөнөкөй тесттерден өттү, бирок `diff`'тен өтпөй калды:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS `indexOf` UTF-16 code unit'терин санайт, ошондуктан эмодзи эки позицияны ээлейт. `demo/*/src/port.rs`
ичиндеги порт генерацияланган `utf16` жардамчы функцияларын колдонот жана 2000/2000 кейстен жана
gate'тен өтөт, napi-rs (`demo/fuzzy-napi`) катары да, wasm-bindgen (`demo/fuzzy-rs`) катары да.

rust-anything бүт x18n үчүн жазган план: [`docs/examples/x18n.md`](./examples/x18n.md).

## Орнотуу

```sh
cargo install --path .
```

`record`, `diff` жана `bench` түп нусканы өз runtime'ында иштетет: TS үчүн Node 22.6+ (ал `.ts` баштапкы
файлдарын түз иштетет), Python жана C үчүн Python 3.9+ (ctypes), Go 1.21+, Ruby 3+, JDK 17+ (`javac`
жана `java`). C үчүн C компилятору да керек. wasm bridge'дери үчүн кошумча
`rustup target add wasm32-unknown-unknown` жана
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked` керек; `build`
так версияны атайт.

Агенттер үчүн `rust-anything setup` баарын каттайт (Тез баштоо бөлүмүн караңыз). Анын ордуна MCP
серверди бир долбоорго кол менен кошуу үчүн (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` эмнени чечет

- Bridge аркылуу өтө албаган экспорттор себеби көрсөтүлүп, баштапкы тилде калат, ал эми shadow модуль
  түп нусканы кайра экспорттойт. TS үчүн:
  функцияларды кабыл алган же кайтарган функциялар, генераторлор жана итераторлор, RegExp, `instanceof`
  текшерүүлөрү, generic'тер жана типтеринде (импорттор, кайра экспорттор жана `extends` аркылуу
  аныкталат) функциялар бар маанилер. `--keep "name: reason"` дагы көп нерсени калтырат, мисалы, `Intl`
  маалыматтарына көз каранды кодду.
- TS типтери Rust типтерине шайкештелет, type alias'тар импорттор аркылуу чечилет, ал эми параметр
  типтери демейки маанилерден чыгарылат; түзүмдүү маанилер генерацияланган бинардык wire аркылуу өтөт
  (JSON wire моделдебеген формалар үчүн гана fallback катары).
- JSON `undefined`, NaN, Infinity, -0 же жалгыз surrogate'терди бере албайт: түзүмдүү маанилер
  генерацияланган `index.cjs` которгон маркерлерди (`{"$undefined": true}`, `{"$num": "NaN"}`,
  `{"$utf16": [...]}`) алып жүрөт, ал эми жардамчы функциялар crate'тин `js.rs` файлында.

`record` TS баштапкы файлдарын болгон абалында иштетет: Node resolve hook bundler стилиндеги
импорттордун артынан барат (`./errors` -> `./errors.ts`), репозиторийде npm пакеттери орнотулбаган
болсо, `--resolve-from` аларды камсыз кылат, ал эми өзгөртүүнү талап кылган TS (enum'дор, parameter
properties) `--experimental-transform-types` менен кайра аракет кылынат.

## `analyze` эмнени карайт

- Пакеттер (`package.json`) жана баштапкы файлдар; `node_modules`, build чыгышын, fixture'лерди,
  playground'дорду, курал конфигурацияларын өткөрүп жиберет. Vue/Svelte/Astro `<script>` блоктору
  импорттор үчүн талданат.
- **Бирдиктер**: баштапкы файлдардын папкасы же пакеттин баштапкы тамырындагы файл.
- **Толкундар**: бирдиктин импорттору мурунку толкундарда болот; импорт циклдери чогуу портталат.
- **Bridge**: бирдикке же ал импорттогон бир нерсеге Node керек болсо, napi-rs; портативдүү код үчүн
  wasm-bindgen; UI жана редактор коду үчүн JS'те калтыруу.
- **Readiness** (канчалык коопсуз) жана **priority** (коопсуз жана арзыйт: циклдер жана саптар менен
  иштөө, тесттер, көлөм).

| Тобокелдик | Олуттуулугу | Мисал |
| --- | --- | --- |
| Сап офсеттери | жогору | `slice`, `indexOf`, `matchAll`, `d` флагы: UTF-16 жана UTF-8 |
| Regex синтаксиси | жогору | lookaround, backreference, `y`: `regex` crate'инде жок |
| Динамикалык regex | жогору | `new RegExp(userPattern)`: иштөө учурундагы JS синтаксиси |
| Динамикалык код | жогору | `eval`, `new Function`, эсептелүүчү `import()` |
| Динамикалык типтөө | орто | `any`, `'key' in value` |
| Иреттелген коллекциялар | орто | `Map`, `Set`, `Object.keys`: кошулуу тартиби |
| Async, генераторлор | орто | promise жана генератор чектери |
| Класстардын мурастоосу, reflection | орто | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback түрүндөгү API'лер | орто | функция типиндеги параметрлер жана методдор: көп сүйлөшкөн bridge'дер |
| Exception'дор, сандар, JSON | төмөн | `throw`, биттик операциялар, `JSON.stringify` тартиби |

## Иштеп чыгуу

```sh
cargo test                        # unit tests, fixture repo, record/diff/shadow loop (needs node), app record/replay per language
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Дизайн чечимдери жана алардын себептери: [DECISIONS.md](../DECISIONS.md).

## Жаңыртуу же өчүрүү

```sh
cargo install rust-anything                                    # update (Cargo)
npm install -g rust-anything@latest                            # update (npm)
rust-anything setup                                            # refresh agent settings
rust-anything setup --remove && cargo uninstall rust-anything  # remove (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # remove (npm)
```

`setup --remove` rust-anything жазууларын гана алып салат; ал сактаган көчүрмөлөр
(`<file>.rust-anything.bak`) өзүңүз өчүрмөйүнчө кала берет.

## Ал эмнени кармай албайт

Өтүү Rust жазылган ар бир кейске дал келет дегенди билдирет, андан ашык эмес. Кайра жазууну бузган
нерселер адатта жазуудан тышкары жатат, ошондуктан чектер кайда экенин билиңиз:

- **Эч ким жазып албаган киргизүүлөр.** Генерацияланган кейстер, тузактар жана сиздин өз `--inputs`
  маалыматтарыңыз чекти аныктайт. Чыныгы киргизүүлөрдү кошуңуз (production үлгүлөрү, bug report'тор, түп
  нусканын тест fixture'лери); prod'ду бузган колдонуучу киргизүүсүн генератор сейрек ойлоп табат.
- **Regex'тер.** `regex` crate'инде lookaround же backreference жок, ал тургай компиляцияланган үлгү да
  ASCII эмес текстте `\w`, `\b`, `\d` жана регистрге көз карандысыз дал келтирүүнү JS, Python же Java'дан
  башкача иштетиши мүмкүн. `fancy-regex`'ке өтүү же үлгүнү кайра жазуу ар бир жазылган кейстен өтүп,
  бирок түркчө чекитсиз `ı` же zero-width joiner'де баары бир айырмаланышы мүмкүн. `record` regex
  колдонгон файлдагы ар бир функцияга regex тузактарын (жогорудагылар, Кельвин белгиси, узун s,
  араб-инди цифралары, сап бөлгүчтөр, акыркы сигма) кошот, бирок чыныгы үлгүлөрүңүздү чыныгы текст
  менен fuzz кылыңыз.
- **Аткаруулардын ортосунда өзгөргөн нерселер.** `record` түп нусканы эки жолу иштетип, эмне
  айырмаланганын иреттейт: өзгөргөн маанилер (убакыт, id) wildcard'ка айланат; башка тартипте келген
  бирдей саптар (hash map'тар, concurrency) каалаган тартипте салыштырылат, ошондуктан порт так ошол
  саптарды чыгарышы керек; саптардын саны айырмаланса, каалаган нерсеге дал келген `...` болот. `record`
  ар бир түрүн тизмелейт: ар бирин карап чыгыңыз, анткени hash тартиби же concurrency айырмасы так портто
  чындап өзгөрүшү мүмкүн болгон нерсе.
- **Float'тор.** Санды текстке форматтоо тилдердин ортосунда айырмаланат (`1e21`, `-0`, цифралардын
  саны). Тузактар ошол маанилерди камтыйт жана алар так дал келиши керек; `--float-tolerance` тегеректөөнү
  гана кечирет, форматтоону эч качан кечирбейт.
- **Чыгышта жок нерселер.** Убакыт, эс тутум, жүктөм астындагы concurrency жана stdout, stderr, exit
  code, жазылган файлдар жана HTTP жооптордон башка кошумча таасирлер (тармак чакыруулары, маалымат
  базалары, сигналдар) салыштырылбайт.
- **Башка платформалар.** Жазуу аны аткарган машинадагы жүрүм-турумду гана далилдейт. Натыйжалары тип
  өлчөмдөрүнө, endianness'ке же компиляторго көз каранды C коду target системада башкача иштеши мүмкүн;
  ошондуктан `analyze` hardware'га жакын C кодун C'де калтырат.

## Көп берилүүчү суроолор

**Ал менин кодумду автоматтык түрдө кайра жазабы?** Жок. Ал эмнени көчүрүү керектигин табат, bridge
генерациялайт, түп нуска эмне кыларын жазып алат жана Rust'ту ага каршы текшерет. Rust кодун `port.rs`
ичинде сиз же агентиңиз жазасыз; анын туура экенин `diff` жана `gate` чечет.

**Колдонмомдун API'си өзгөрөбү?** Жок. Чакыруучулар ошол эле функцияларды импорттошот (же shadow
модулду, ал сиз ишеним топтоп жатканда экөөнү тең иштетип, түп нусканын натыйжасын кайтарат).

**Rust дайыма ылдамыраакпы?** Жок, жана rust-anything муну ачык айтат. Ар бир элемент үчүн бир жолу
чакырылган кичинекей функция Rust'та көбүнчө жайыраак, анткени ар бир чакыруу bridge аркылуу өтөт; V8,
JVM жана Go мындай функцияларды наносекунддарда аткарат. `profile` анын айланасындагы циклди табат,
`--batch` бүт циклди көчүрөт, ал эми `bench` чыгаруудан мурун корутунду берет. numba, Cython же JAX
аркылуу мурунтан компиляцияланган код да машиналык код катары иштейт: `profile` жана `analyze` аны
белгилейт, анткени аны порттоо ылдамдыкка аз пайда берет.

**Менин кодум сандык; float'тор так дал келеби?** Көбүнчө жок: операциялардын тартиби, fused
multiply-add жана математикалык китепкана компиляторлордун ортосунда айырмаланат.
`--float-tolerance 1e-9` менен жазыңыз (`record` же `app record`), ошондо float'тор чоңураак маанинин
ушул үлүшүнүн чегинде дал келет (1'ден төмөн болсо, абсолюттук түрдө). Бүтүн сандар, текст жана
түзүлүш баары бир так дал келиши керек.

**Ал APK, JAR же .exe түрүндө гана бар колдонмону порттой алабы?** Жок. Ал баштапкы кодду порттойт:
функцияларды талдайт, ар бири эмне кыларын жазып алат жана Rust'ту иштеп жаткан түп нускага каршы
текшерет. Компиляцияланган колдонмодо мунун эч бири жок, жана `analyze` муну айтат. Бинардык файлдын
көрүнгөн жүрүм-турумуна карап жаңы Rust колдонмосун жазуу башка долбоор.

**Сыноодон өткөн C кодун порттоо керекпи?** Көбүнчө жок, жана `analyze` кайсы жерде экенин айтат.
Hardware регистрлери менен иштеген, компилятордун тип өлчөмдөрүнө же эс тутумдун жайгашуусуна таянган
же inline assembly колдонгон C коду (`volatile`, bitfield'дер, packed struct'тар, `__asm__`, дарекке
айландырылган бүтүн сандар) "keep in C" деп белгиленет: сиздин машинаңыздагы жазуу target жөнүндө эч
нерсени далилдебейт, ал эми туруктуу драйвер же firmware коду кайра жазуудан аз утат. Анын айланасындагы
портативдүү логика (парсинг, протоколдор, маалыматтарды иштетүү) жакшы көчөт.

**Ал менин Electron колдонмомду порттой алабы?** Логикасын, ооба; терезелер веб-барактар бойдон калат.
`analyze --whole-app` Electron'ду аныктап, main процессти бөлүк-бөлүгү менен пландайт, ал эми renderer
ошол бойдон калат. UI'ды Tauri'ге көчүрүү (Rust backend'деги ошол эле веб UI) логика Rust'ка өткөндөн
кийинки өзүнчө кадам.

**C#, Kotlin же Swift чечи?** C# preview абалында ([Тилдер](#тилдер) бөлүмүн караңыз); Kotlin жана Swift
азырынча колдоого алынбайт. Ар бир тилге парсер, recorder, bridge жана replay драйвери керек, баары
башынан аягына чейин тестирленген. Өзүңүзгө керектүү тил үчүн issue ачыңыз (же барына добуш бериңиз).

**Rust коду түп нускадан алда канча чоң болуп кетпейби?** Болбошу керек. `gate` порттун саптарынын
санын түп нусканыкы менен салыштырат жана 3x'тен ашса (плюс импорттор жана сигнатуралар үчүн 50 сап)
ийгиликсиз аяктайт: бул адатта crate мурунтан эле жасаган нерсени кол менен жазууну же учурларды бирден
иштетүүнү билдирет. `analyze` колдонуу керек болгон crate'терди тизмелейт.

**Бөлүк-бөлүгү менен порттоо Rust'ту эски колдонмонун дизайнына байлап койбойбу?** Экөө катар иштеп
турганда гана. Жазуулар жүрүм-турумду колдонмонун ички түзүлүшүнөн эмес, анын чектеринен текшерет (CLI
чыгышы, сервердин жооптору, модулдун экспорттолгон функциялары). Бирдиктер дагы эле bridge аркылуу
өтүп жатканда эски түзүлүштү кайталаңыз; `app lift` түп нусканы алып салгандан кийин Rust'ту эркин
кайра түзүңүз, ал эми `app replay` жүрүм-турумду баары бир далилдейт. Эч нерсе түп нускага кайра
чакыруу да жасабайт: front door аны өзүнчө процесс катары иштетет (же ага HTTP жөнөтөт), bridge менен
кошулган бирдиктерди түп нуска чакырат, тескерисинче эч качан эмес, ал эми callback'тер баштапкы тилде
калат.

**Менин кодум машинамдан чыгып кетеби?** Жок: rust-anything локалдык иштейт жана кодуңуздун эч бир
бөлүгүн эч жакка жөнөтпөйт. Cargo crate'терди адаттагыдай жүктөйт, ал эми агентиңиздин модель
провайдери агентиңиз ага жөнөткөндү өз саясатына ылайык көрөт.

**Эмне орнотулушу керек?** Rust жана сиз порттогон тилдин runtime'ы ([Орнотуу](#орнотуу) бөлүмүн
караңыз).

**Бир нерсе бузулду.** Буйрук, анын чыгышы жана платформаңыз көрсөтүлгөн issue ачыңыз.

## Демөөрчүлөр

rust-anything акысыз жана ачык булак коддуу долбоор. Эгер ал ишиңизге жардам берсе, ага демөөрчү
болууну карап көрүңүз. Сиздин колдооңуз иштеп чыгууну улантууга жардам берет.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="GitHub'да rust-anything долбооруна демөөрчү болуу" /></a>
</p>

### Компания демөөрчүлөрү

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Жеке демөөрчүлөр

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

## Салым кошуу

Issue'лар жана pull request'тер кубаттуу кабыл алынат; [CONTRIBUTING.md](../CONTRIBUTING.md) чөйрөнү
жөндөөнү, тесттер кайда жайгашарын жана жаңы тилди кантип кошууну түшүндүрөт. Дизайн чечимдери жана
алардын себептери [DECISIONS.md](../DECISIONS.md) ичинде. Чыныгы порттордун практикалык мисалдары
өзгөчө кубаттуу кабыл алынат. Коопсуздук көйгөйлөрү жөнүндө жеке кабарлаңыз
([SECURITY.md](../SECURITY.md)), ошондой эле [жүрүм-турум кодексин](../CODE_OF_CONDUCT.md) караңыз.

## Лицензия

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Репозиторийиңиздеги порттор жана генерацияланган код сиздики.
