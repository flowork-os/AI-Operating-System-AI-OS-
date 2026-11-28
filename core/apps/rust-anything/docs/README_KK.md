<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="rust-anything шаяны, аузы код тегі түрінде">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">авторы: <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · Қазақша · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>Бұл аударманы қауымдастық жүргізеді, сондықтан ол <a href="../README.md">ағылшынша README</a> нұсқасынан артта қалуы мүмкін.</sub></p>

<p align="center"><em>Бүкіл қолданбаңызды Rust тілінде қайта жазыңыз. Бүкіл жол бойы оны жұмыс күйінде сақтаңыз.</em></p>

<p align="center"><em>CLI-лар, серверлер мен кітапханалар, бөлік-бөлігімен, әр қадамда түпнұсқамен салыстырылып тексеріледі.</em></p>

<p align="center">Node.js және TypeScript · Python · C · Go · Ruby · Java · PHP және C# preview күйінде</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io нұсқасы"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm нұсқасы"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 тіл">
  <a href="#үйлесімді-агенттер"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 агентпен жұмыс істейді"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Тесттер"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT лицензиясы"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub жұлдыздары"></a>
</p>

<p align="center">20x дейін жылдамырақ · 38,251 жазылған кейс қайта ойнатылды · 0 сәйкессіздік · бір команда</p>

<p align="center">
  <img src="assets/race.gif" alt="x18n іздеуіне 50,000 кілт бойынша user.profile теріліп жатыр: TypeScript 143 ms жұмсайды, rust-anything batch 6.9 ms, әр пернені басқан сайын нәтижелер бірдей." width="820">
</p>

**Бүкіл қолданбаңызды Rust тілінде бөлік-бөлігімен қайта жазыңыз.** rust-anything сіздің Node.js
(TypeScript/JavaScript), Python, C, Go, Ruby немесе Java қолданбаңыздың бүгін не істейтінін жазып
алады, содан кейін Rust нұсқасының әр бөлігін келесіге өтпес бұрын сол жазбамен салыстырып тексереді,
қолданба толығымен таза Rust болғанша. CLI-лар, HTTP серверлер және кітапханалар; Rust кодын сіздің
кодинг-агентіңіз (немесе өзіңіз) жазады. Ол тек жазба қамтитын нәрсені ғана ұстай алады:
[Ол нені ұстай алмайды](#ол-нені-ұстай-алмайды) бөлімін қараңыз. Тек баяу бөлікті жылдамдату керек пе?
Тек соны порттаңыз, бір уақытта бір hot path:

| Нақты жүктеме, нәтижелері түпнұсқамен бірдей | Түпнұсқа | rust-anything-пен |
| --- | ---: | ---: |
| x18n бүйірлік панеліндегі іздеу, 50,000 кілт (TypeScript, Node) | бір сұранысқа 10 ms | **0.5 ms: 20x жылдамырақ** |
| Сол іздеу браузерде (wasm, бір ағын) | 10 ms | **0.95 ms: 11.5x** |
| `slugify`, 20,000 жол (Python) | 98 ms | **17x жылдамырақ** |
| Ruby стандартты кітапханасындағы `Shellwords.shellescape`, 50,000 мән | 88 ms | **11.8x жылдамырақ** |
| `Slugify`, 50,000 жол (Go) | 49 ms | **4x жылдамырақ** |
| `slugify`, 50,000 жол (Java) | 43 ms | **3x жылдамырақ** |

4 ядрода өлшенді; әр сан үшін [`demo/`](../demo) ішінде алдымен нәтижелердің бірдей екенін тексеретін
бенчмарк бар. Әр кішкентай функция үшін Rust-ты жеке-жеке шақыру әдетте JIT-тен *баяуырақ*;
rust-anything көшіруге тұрарлық циклды тауып, соны көшіреді.

> rust-anything тәуелсіз жоба, ол Rust Project немесе Rust Foundation ұйымдарымен байланысты емес
> және олар тарапынан мақұлданбаған. «Rust» Rust Foundation ұйымының сауда белгісі.

## Жылдам бастау

Мынаны Claude Code, Codex, Cursor немесе Gemini CLI ішіне қойып, орнатуды агентіңізге тапсырыңыз:

```text
Install rust-anything: run `cargo install rust-anything`, then `rust-anything setup`.
Tell me when to restart you.
```

Немесе өзіңіз:

```sh
cargo install rust-anything   # from crates.io
rust-anything setup           # registers it with Claude Code, Codex, Cursor and Gemini CLI
```

Rust toolchain әлі жоқ па? macOS, Linux және Windows үшін дайын бинарлық файлдар әр
[GitHub release](https://github.com/erkamyaman/rust-anything/releases) бетіне тіркелген, ал JavaScript
жобалары үшін `npm install -g rust-anything` сол бинарлық файлды орнатады.

Claude Code ішінде оны плагин ретінде де орнатуға болады (MCP сервер және skill; жоғарыдағы CLI сіздің
`PATH` ішінде болуы керек):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` тапқан әр агентке MCP серверді қосады және workflow skill-ін агент skill-дерді оқитын жерге
орнатады. Ол басқа баптауларыңызды сақтайды, оны қайта іске қосу қауіпсіз, ал `--remove` барлығын кері
қайтарады. Содан кейін агентіңізден, мысалы, былай сұраңыз:

- *"Осы CLI-ды rust-anything көмегімен басынан аяғына дейін Rust тілінде қайта жаз және оның дәл солай жұмыс істейтінін дәлелде."*
- *"Бұл іздеу баяу сияқты. Оны rust-anything көмегімен профайлда және hot loop-ты Rust-қа көшір."*
- *"rust-anything көмегімен `src/parser/` бумасын Rust-қа көшіру жоспарын жаса; бірінші бірлікті порттап, дәлелде."*
- *"`rust/text-rs` ішіндегі Rust портын түпнұсқамен бенчмарк арқылы салыстыр да, оны шығару керек пе, айт."*

### Үйлесімді агенттер

| Агент | `rust-anything setup` қосатыны |
| --- | --- |
| Claude Code | `~/.claude.json` ішінде MCP сервер, `~/.claude/skills/` ішінде skill |
| Codex | `~/.codex/config.toml` ішінде MCP сервер, `~/.codex/skills/` ішінде skill |
| Cursor | `~/.cursor/mcp.json` ішінде MCP сервер |
| Gemini CLI | `~/.gemini/settings.json` ішінде MCP сервер |
| Кез келген басқа MCP клиент | `rust-anything mcp` командасын stdio сервер ретінде қолмен қосыңыз ([Орнату](#орнату) бөлімін қараңыз) |

Бар файлды өзгертпес бұрын `setup` оның көшірмесін қасына сақтайды (`<file>.rust-anything.bak`).

Немесе қадамдарды өзіңіз орындаңыз:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile циклдағы fuzzyScore функциясын табады, bridge --batch Rust crate-ін генерациялайды, gate 2000/2000 жазылған кейспен өтеді, ал бенчмарк TS-тен 20.7x жылдамырақ екенін көрсетеді." width="820">
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

rust-anything кодты аудармайды: Rust кодын сіздің кодинг-агентіңіз (Claude Code, Codex, Cursor, ...)
немесе өзіңіз жазасыз. rust-anything агент сенімді түрде болжай алмайтын нәрселерді береді: уақыт қайда
кетеді, алдымен нені және қандай ретпен порттау керек, қалған код Rust-ты API-ін өзгертпей шақыруы үшін
bridge, порт сәйкес келуге тиіс нақты мінез-құлық, оны шығарудың қауіпсіз жолы және порттың қашан дайын
болғанын айтатын gate.

## Тілдер

| Тіл | Бірлік | Bridge | Жазып алатын және қайта ойнататын |
| --- | --- | --- | --- |
| TypeScript/JavaScript | бума немесе файл | генерацияланған бинарлық wire бар napi-rs немесе wasm-bindgen; кластар мен async те бар | Node, `.ts` бастапқы файлдарын тікелей іске қосады |
| Python | пакет немесе модуль | PyO3 (abi3), тікелей түрлендіру, типтелген exception-дар | Python, түпнұсқаны импорттайды |
| C | `.c` файлы | түпнұсқа атаулары мен header бар `extern "C"` функциялары | shared library ретінде компиляцияланған түпнұсқа, ctypes арқылы шақырылады, әр кейске бір fork |
| Go | пакет | типтелген cgo шақырулары және генерацияланған бинарлық wire, түпнұсқа API бар пакетте | генерацияланған Go драйвері, жеке модуль ретінде құрастырылады |
| Ruby | модуль функцияларынан тұратын файл немесе бума | түпнұсқа модульдер астындағы magnus кеңейтімі | генерацияланған Ruby драйвері |
| Java | `public static` әдістерінен тұратын пакет | типтелген JNI және генерацияланған бинарлық wire, түпнұсқа әдістері бар wrapper кластарында | генерацияланған reflection драйвері |
| PHP (preview) | функциялар мен `public static` әдістерінен тұратын бума | келесі кезекте: C ABI арқылы PHP FFI | бүгін бүкіл қолданбалар: `app record`, `app replay` және front door, CLI-лар мен серверлер үшін (`php -S`) |
| C# (preview) | `public static` әдістерінен тұратын бума | келесі кезекте: C ABI арқылы P/Invoke | бүгін бүкіл қолданбалар: `app record`, `app replay` және front door, CLI-лар мен ASP.NET серверлері үшін (`dotnet <app>.dll`) |

C-дан басқа әр тіл batch кластарын да алады (`--batch`): элементтер шекарадан бір рет өтіп, Rust ішінде
қалады, ал әр шақыру олардың барлығын барлық ядроларда өңдейді.

Тіл репозиторийден анықталады (`go.mod`, `pom.xml`, `.csproj` немесе `.sln`, `pyproject.toml`,
`Gemfile`, `composer.json`, `package.json`, әйтпесе ең көп кездесетін бастапқы файлдар бойынша);
`--lang` оны қолмен көрсетеді. Типтер бастапқы кодтан алынады: TS типтері, Python hint-тері, C, Go, Java
және C# сигнатуралары, Ruby YARD тегтері, PHP типтері және phpdoc; сан ретінде қолданылатын типсіз
параметрлер сан деп есептеледі.

PHP preview күйінде: `analyze` PHP қолданбасын жоспарлайды (Composer пакеттері және PSR-4 autoloading,
loose comparison және integer-дің float-қа толып кетуі сияқты тәуекелдер, crate-терге сәйкестендірілген
Composer пакеттері), ал PHP CLI немесе серверін жазып алуға, қайта ойнатуға және Rust front door-ының
артына қоюға болады. Оның бірліктерін PHP FFI арқылы Rust-қа порттау келесі қадам
([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# та дәл солай preview күйінде: `analyze` `.csproj` жобалары мен олардың NuGet пакеттерін оқиды
(crate-терге сәйкестендіріледі), `using` директиваларын бумаларға шешеді және C# басқаша істейтін
нәрселерді белгілейді (`decimal`, `dynamic`, LINQ-тің кейінге қалдырылған сұраныстары, `Task`, `lock`,
reflection). C# CLI немесе ASP.NET серверін жазып алуға, қайта ойнатуға және Rust front door-ының
артына қоюға болады; бірліктерді P/Invoke арқылы порттау келесі кезекте.

## Қалай жұмыс істейді

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 where the    what to     the Rust   what the    you or      every     faster?    both side   done means
 time goes    port first  crate and  original    your agent  recorded  the        by side in  this passes
                          wrapper    does        write it    case      verdict    production
```

Түпнұсқа ақиқат көзі болып қала береді: `record` оны шеткі жағдайларда (және сіздің өз кіріс
деректеріңізде) іске қосып, оның не қайтаратынын немесе қандай қате лақтыратынын сақтайды; `diff` әр
кейсті Rust-қа қарсы қайта ойнатады; бәрі сәйкес келіп, `gate` өтпейінше ештеңе шығарылмайды.
Шақырушылар бүкіл процесс бойы түпнұсқа API-ді пайдалана береді.

Бүкіл қолданба да сол циклдан бірлік-бірлігімен өтеді, бүкіл бағдарламаны дәлелдейтін шеңбер ішінде
([Бүкіл қолданбаны порттау](#бүкіл-қолданбаны-порттау)):

```
analyze --whole-app ──> app record ──> app front-door ──> per unit: the loop above, then app wire ──> app lift
 shape, every           what the app    Rust owns the       gate passes, so the unit answers in         pure Rust,
 dependency, the        does from the   entry point; the     Rust: replay 100%, fallback rate down      proved by
 decisions to make      outside         original answers                                                replay
```

## Цикл

| Қадам | Команда | Не істейді |
| --- | --- | --- |
| 0. Профайл | `rust-anything profile <repo> -- node bench.mjs` | Нақты жүктемені тілдің профайлері астында іске қосады (node, cProfile, `go test` pprof, JFR, Ruby tracer): инклюзивті уақыт бойынша ыстық функциялар, оларды шақыратындар және қай циклдарды batch-ке айналдыру керек; бұрыннан компиляцияланған кодты белгілейді (numba, Cython, JAX), онда Rust аз пайда береді |
| 1. Жоспар | `rust-anything analyze <repo>` | Бірліктер, порттау реті, `file:line` көрсетілген тәуекелдер, әр бірлікке арналған bridge, тәуелділіктердің crate-терге сәйкестігі, ең жақсы алғашқы порттар; `--whole-app` кіру нүктелері мен қолданба пішінін, әр тәуелділікті (импортталған немесе жарияланған) оның crate-імен, бөліктерді (бір-бірін импорттайтын бірліктер бірге көшеді) және ұсынылған жауабы бар нөмірленген шешімдерді қосады |
| 2. Bridge | `rust-anything bridge <repo> <unit>` | Байланыстары бар crate (`lib.rs`, сондай-ақ бастапқы тіл жүктейтін wrapper) және порттауға арналған stub-тар (`port.rs`); `--batch fn:param` көптеген `param` мәндерін Rust ішінде ұстайтын класс қосады |
| 3. Жазу | `rust-anything record <crate>` | Түпнұсқаны генерацияланған шеткі жағдайларда (ASCII емес, эмодзи, `-0`, `NaN`, float күтілетін жерде int, ...) және әр параметрдегі әр семантикалық тұзақта (жолдың ұзындығы мен регистрі, таңбалы бөлу, толып кету шектері, float-тарды басып шығару, map және сұрыптау реті) іске қосып, `cases.jsonl` сақтайды; `--float-tolerance 1e-9` сандық код үшін float-тардың осы үлес шегінде сәйкес келуіне рұқсат береді |
| 3. Құрастыру | `rust-anything build <crate>` | Rust жағын құрастырады: `.node`, wasm пакеті, Python кеңейтімі немесе shared library |
| 3. Салыстыру | `rust-anything diff <crate>` | Жазылған кейстерді Rust-қа қарсы, түпнұсқаны шақыратындар қалай шақырса, солай қайта ойнатады; сәйкессіздіктерді тізеді |
| 3. Бенчмарк | `rust-anything bench <crate>` | Жазылған кейстердің түпнұсқада және Rust-та орындалу уақытын өлшейді, bridge-ді қоса алғанда |
| 4. Shadow | `rust-anything shadow <crate>` | Екеуін де іске қосатын, түпнұсқаның нәтижесін қайтаратын және сәйкессіздіктер туралы хабарлайтын drop-in алмастырғыш; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, тесттер, `unsafe` аудиті, портталмаған ештеңе қалмауы, түпнұсқаның әр қате жолы үшін жазылған сәтсіз кейс, түпнұсқа қате қайтаратын жерде `unwrap`/`expect`/`panic!` болмауы (`// INFALLIBLE: <why>` деп белгіленбесе), build, API, мінез-құлық |
| Агенттер | `rust-anything setup` | MCP серверді (`rust-anything mcp`, әр қадам tool ретінде) және workflow skill-ін ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) сіздің кодинг-агенттеріңізге тіркейді |

## Бүкіл қолданбаны порттау

Мақсат: түпнұсқа сияқты жұмыс істейтін таза Rust қолданбасы, ал түпнұсқа эталон ретінде сақталады.
Rust кодын агентіңіз жазады; rust-anything жұмысты ретке келтіреді, қаңқасын жасайды және әр қадамды
дәлелдейді. [Whole-app skill](../skills/rust-anything/whole-app.md) агентті осы жол арқылы бастайды,
тек сіз ғана қабылдай алатын шешімдерден бастап:

- **Grilling**: агент сұрақтарды раундтармен қояды, әр сұрақта ұсынылған жауап болады, порт тәуелді
  әр шешім анықталғанша, және әрқайсысын `rust/DECISIONS.md` ішіне ADR ретінде жазады, ал
  `rust/GLOSSARY.md` түпнұсқаның терминдерін Rust атауларына сәйкестендіреді.
- **Зерттеу**: фондық агенттер әр тәуелділіктің бастапқы дереккөздерін оқиды және тапқан әр
  семантикалық тұзағымен бірге `rust/research/<topic>.md` жазады.
- **Сессиялар арасында**: `rust/MAP.md` әр бірлікті күйімен бірге тізеді; сессия жұмысты бастамас
  бұрын бір бірлікті өзіне алады, ал әр checkpoint келесі сессия үшін `rust/HANDOFF.md` қалдырады. Бір
  толқындағы бірліктерді subagent-тер параллель порттай алады.
- **Cutover**: агент қолынан келгенін істейді және `rust/cutover.sh` жазады, бұл тек сіз ғана
  орындай алатын қадамдарға (deploy, DNS, құпия кілттер) арналған интерактивті скрипт, әр қадамда кері
  қайту жолы бар.

Grilling, зерттеу және осы тәжірибелер
[Matt Pocock skill-дерінен](https://github.com/mattpocock/skills) алынып, бейімделген.

Алдымен жоспар: `rust-anything analyze . --whole-app` қолданбаның пішінін (CLI, сервер немесе
кітапхана) және кіру нүктелерін, әр сыртқы тәуелділікті (импортталған немесе жарияланған) оның Rust
crate-імен және сәйкестігімен, порттау ретін бөліктер түрінде (бір-бірін импорттайтын бірліктер бірге
көшеді) және ұсынылған жауабы бар нөмірленген шешімдерді қосады: сақталатын бірліктер, бұғатталған
бірліктер, crate-і жоқ немесе ішінара ғана бар тәуелділіктер.

Содан кейін бүкіл бағдарламаны сырттан дәлелдеңіз. `record` және `diff` бір бірлікті дәлелдейді;
`app record` және `app replay` қолданбаны дәлелдейді, алты тілдің кез келгеніндегі CLI-лар мен серверлер
үшін (қолданба қара жәшік ретінде қарастырылады):

```sh
rust-anything app record . -- python3 cli.py          # the command that runs the original
rust-anything app replay .                            # the original must pass 100%
rust-anything app replay . --build "target/release/mytool"
```

- `app record` түпнұсқаны қолданбаның өз құжаттамасындағы мысалдарда (оның Markdown және shell
  файлдарындағы `$ mytool ...` жолдары, олар атайтын файлдармен бірге), `--inputs` JSONL файлында
  (`{"name", "args", "stdin", "env", "files"}`) және осы кейстерден шығарылған семантикалық тұзақтарда
  (ASCII емес және эмодзи жолдары, теріс бөлу және modulo, толып кету, өте үлкен және өте кіші
  float-тар, map реті, жоқ файлдар) іске қосады. Әр кейс екі рет орындалады; екі орындау арасында
  өзгерген нәрсе `[..]` wildcard-қа айналады. `--normalize timestamps|uuids|key-order` немесе
  `--normalize name=regex` нормализаторлар қосады, олар кейстермен бірге сақталады.
- Кейстер `rust/app-cases/` ішіндегі [trycmd](https://docs.rs/trycmd) файлдары: `<case>.toml` (argv,
  env, exit code), `.stdin`, `.stdout`, `.stderr`, `.in/` (кіріс файлдары) және `.out/` (жазылған
  файлдар). Оларды қолмен оқып, өңдей аласыз; порттың бинарлық файлы пайда болғанда, Rust тесті оларды
  `trycmd` арқылы іске қоса алады.
- `app replay` кез келген build-ті кейстерге қарсы іске қосады, `passed/total` басып шығарады,
  әр сәтсіз кейс үшін diff бар `rust/app-cases/replay-report.md` жазады және кез келген сәйкессіздікте
  нөлден өзге кодпен аяқталады. `RUST_ANYTHING_FALLBACK_LOG` атаған файлға жол қосатын build (түпнұсқаға
  әр fallback үшін бір жол), төмендегі front door сияқты, өзінің fallback rate көрсеткішін де алады.
- `app replay --case <name>` есептегі атауы бойынша бір кейсті қайта іске қосады: бәрін қайта
  іске қоспас бұрын сәйкессіздікті түзетуге арналған жылдам, қайталанатын цикл.

Содан кейін кіру нүктесін Rust-қа көшіріп, командаларды оған бір-бір бірліктен беріңіз:

```sh
rust-anything app front-door .                            # rust/app: every command runs the original
rust-anything app wire . textkit --command upper          # after textkit-rs passes gate
# write the glue in rust/app/src/units/textkit.rs, then:
rust-anything app wire . textkit                          # 100% again, lower fallback rate
```

- `app front-door` `rust/app` қаңқасын жасайды, бұл қолданбаның атымен аталған Rust бинарлық файлы:
  жазылған кейстердегі командалар мен флагтарға арналған clap парсері, мұнда әр команда түпнұсқаны сол
  argv, stdin және environment арқылы іске қосып, оның шығысы мен exit code-ын өзгертпей өткізеді. Әр
  fallback саналады, сондықтан жаңа front door-ды қайта ойнату 100% fallback кезінде 100% passed береді
  (мұны көрсету үшін ол build жасап, replay іске қосады). Ол `rust/app` бумасын ешқашан қайта жазбайды:
  осы сәттен бастап код сіздікі.
- `app wire <repo> <unit> --command <name>` бірліктің crate-іне `gate` іске қосады (жаңа ғана өткен
  болса, `--skip-gate`), оны `rust/app` ішіне кітапхана ретінде қосады, сіз немесе агентіңіз толтыруы
  үшін `src/units/<unit>.rs` файлын бір рет жазады (аргументтерді талдау, `<crate>::port` шақыру,
  түпнұсқа басып шығаратынды басып шығару), командаларды соған бағыттайды, содан кейін build жасап,
  replay іске қосады. `RUST_ANYTHING_UNIT_<NAME>=original` қосылған бірлікті lift-ке дейін түпнұсқаға
  қайтарады.

Ешбір команданы атамайтын argv үшін (аргументсіз шақыру, белгісіз командалар, usage қателері)
қолданбаның өз атын команда ретінде қосыңыз (`--command mytool`).

Replay 0 fallback rate кезінде өтіп, әр бірлік gate-тен өткенде, оны таза Rust қолданбасына айналдырыңыз:

```sh
rust-anything app lift .
```

- `app lift` екі шарт та орындалмайынша бас тартады және не кедергі екенін айтады: әлі fallback-ке
  түсіп жатқан кейстер, әлі stub күйіндегі glue код, gate-тен өтпейтін бірліктер.
- Алдымен көшірмеде fallback жолы мен kill switch-терді алып тастайды, әр бірлік crate-ін `rust/app`
  жобасының қарапайым кітапханасына айналдырады (`cdylib`, байланыстар немесе генерацияланған
  wrapper-лер жоқ) және `cargo test` кезінде `rust/app-cases` кейстерін trycmd арқылы іске қосатын
  `rust/app/tests/app_cases.rs` қосады, сондықтан CI үшін cargo-дан басқа ештеңе қажет емес.
- Содан кейін lift чек-листін орындайды: әр бірлікте және `rust/app` ішінде fmt, clippy `-D warnings`
  және тесттер, `rust/DECISIONS.md` ішінде аталған әр target орнатылған жерде құрастырылады немесе
  тексеріледі, орындалу кезінде оқылатын файлдар мен ендірілмеген asset бумалары, және таза бинарлық
  файлда replay. Барлығы өткенде ғана өзгерістер кері жазылады. Түпнұсқаға ешқашан қол тигізілмейді.

### Серверлер

Дәл сол командалар HTTP серверлерді де дәлелдейді. `--http` команда серверді іске қосатынын
білдіреді; ол портын `PORT` айнымалысынан немесе командадағы `{port}` ішінен алады (әрқашан бір портты
тыңдайтын сервер үшін `--port`):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: every route proxied
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Сұраныстар қолданба құжаттамасындағы `curl` жолдарынан (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs` ішінен (`{"name", "method", "path", "headers", "body"}`) және тұзақтардан алынады: жол
  сегменттері мен query мәндері CLI аргументтеріндегі тұзақтармен алмастырылады, body-лер мәтін және
  JSON тұзақтарымен, плюс бір белгісіз route. Әр орындау серверді жаңадан іске қосып, сұраныстарды
  атау ретімен жібереді, сондықтан сұраныстар арасындағы күй сақталады.
- Кейстер `rust/app-cases/http/<case>.toml` (сұраныс, статус және маңызды header-лер) және
  `<case>.body` (жауап body-сі, екі орындау өзгеше болған жерлерде `[..]`). Date, server және әр
  жауапта өзгеретін басқа header-лер алынып тасталады; өзіңізге қажет емес кез келген header жолын
  жойыңыз.
- Front door бұл axum сервері: ол түпнұсқаны өзінің жеке портында іске қосып, ешбір бірлік жауап
  бермейтін әр route-ты проксилейді. `wire --route` axum route-тарын қабылдайды: `METHOD /path/{param}`,
  кез келген әдіс үшін `/path`, қалғаны үшін `*`; glue код route-ты, оның параметрлерін және
  сұранысты алады. `lift` проксиді алып тастайды; содан кейін HTTP кейстері CI ішінде `app replay`
  арқылы орындалады.

### Кітапханалар

Кітапхананың қайта ойнататын процесі жоқ: оның public API-і front door болып табылады, ал әр бірліктің
жазылған кейстері дәлел болады.

```sh
rust-anything app front-door .        # rust/app: a Rust crate with the public API
# each unit through the loop: bridge, record, port.rs, build, diff, gate; then:
rust-anything app wire . textkit-rs   # re-exported from rust/app; the original imports its shadow
rust-anything app replay .            # every wired unit's cases; fallback = exports still in the original
rust-anything app lift .
```

- `app front-door` репозиторийде `main` те, сервер де болмаса (әйтпесе `--library`), public API-ді
  (әр бірліктің экспорттарын) табады және `rust/app` бумасын кітапхана crate-і ретінде жасайды. Әр
  қосылған бірлік оның модуліне айналады: `pub use textkit_rs::port as textkit;`.
- `app wire` `bridge` жасаған crate-ті алады, `gate` іске қосады және бірліктің shadow drop-in
  модулін жазады: түпнұсқа пакет оны бірліктің орнына импорттайды, сондықтан оның шақырушылары түпнұсқа
  API-ді сақтап, Rust-қа жетеді. `RUST_ANYTHING_UNIT_<NAME>=original` бірлікті кері қайтарады (C: shadow
  флагтарынсыз құрастырыңыз).
- `app replay` әр қосылған бірліктің жазылған кейстерін оның байланыстары арқылы іске қосады. Fallback
  rate деп Rust әлі жауап бермейтін public экспорттардың үлесін айтамыз: қосылмаған бірліктер және
  `bridge` бастапқы тілде қалдыратын экспорттар.
- `app lift` 0 fallback және әр бірліктің `gate`-тен өтуін талап етеді; ол бірліктерден байланыстарды,
  wrapper-лер мен shadow-ларды алып тастап, `rust/app` бумасын бір таза Rust кітапханасы ретінде
  қалдырады. Ол ешбір `port.rs` файлына тимейді, сондықтан байланыстар арқылы сәйкес келген кейстер
  оны әлі де сипаттайды; чек-лист shadow-ларды әлі импорттайтын түпнұсқа файлдары туралы ескертеді.

Бесеуі де MCP tool ретінде қолжетімді: `app_record`, `app_replay`, `app_front_door`, `app_wire` және
`app_lift`.

## Тәжірибе: x18n ядросы

x18n ядросының API-ін өзгертпей көшіруге болатын барлық 29 функциясы rust-anything көмегімен
портталды: әр gate өтеді және 7,925 жазылған кейс дәл сәйкес келеді. Содан кейін `rust-anything bench`
JS-тен шақырылғанда порттардың TS-тен баяуырақ екенін көрсетті, себебі bridge жұмыстың өзінен қымбатқа
түседі. Толық есеп: [`demo/x18n-core`](../demo/x18n-core/README.md). Бұл сабақ құралдың өзіне енгізілген:
портты шығармас бұрын `bench` арқылы өлшеңіз.

## Hot paths: деректерді Rust ішінде ұстау

Әр элемент үшін бір рет шақырылатын порт bridge құнын да әр элемент үшін төлейді және JIT-ке
жеңіледі. Циклды көшіру жеңеді: `profile` оны табады, ал `--batch` элементтерді бір рет қабылдап,
функцияны әр шақыруда олардың барлығына барлық ядроларда орындайтын және нәтижелерді typed array
түрінде қайтаратын класс генерациялайды.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: a quarter of the run, called per key by `matched`: batch it
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // once
const order = search.rank(query, 0)               // per keystroke: indexes, best first
```

`port.rs` ішіндегі `FuzzyScoreIndex` struct-ы әдепкі циклды элементтерді бір рет дайындайтын және
өздігінен рейтинг жасай алатын (`rank`) циклмен алмастырады: ол кілттерді кіші әріппен, әрқайсысын
таңба маскасымен сақтайды, әр кілттегі әр жиі кездесетін таңбаның бірінші позициясының кестесін
ұстайды (бір әріптік сұраныс бір баған болады) және соңғы сұраныстың сәйкестіктерін сақтайды (`s`
кейін `se` терілсе, тек `s` сәйкес келгендер қайта бағаланады). x18n бүйірлік панеліндегі 50,000 кілт
бойынша іздеуде, әріп-әріппен терілгенде, нәтижелер бірдей болғанда:

| | Бір сұранысқа | TS-пен салыстырғанда |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| Индекстегідей тарылтуы бар TS | 4.1-5.4 ms | 2x |
| Сол порт, әр кілт үшін шақырылады | - | 0.2-0.4x |
| `FuzzyScoreBatch`, әдепкі индекс (4 ядро) | 5.1 ms | 1.7x |
| `FuzzyScoreBatch` және `FuzzyScoreIndex` (napi, 4 ядро) | 0.45-0.56 ms | **18-22x** |
| Сол нәрсе wasm-да (бір ағын) | 0.95 ms | **11.5x** |

Дәл сондай тарылту жасайтын TS-пен салыстырғанда да Rust әлі 7-12x жылдамырақ (wasm 5x). Қайтарылған
индекстерді кілттерге қарапайым циклмен айналдырыңыз: `Array.from(order, i => keys[i])` 20x қымбатқа,
0.4 ms-қа түсті.

Әр тіл batch алады және олар әр шақыруға арналған порттар жеңілетін жерлерде де түпнұсқадан озады.
Сол жұмыс 4 ядрода, нәтижелер мен қателер бірдей (бенчмарктар әр demo бумасында):

| Тіл | Жүктеме | Түпнұсқа | Әр шақыруға порт / түпнұсқа | Batch / түпнұсқа |
| --- | --- | ---: | ---: | ---: |
| TS | x18n іздеуі, 50,000 кілт | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 жол | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 жол | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 аралас мән | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 жол | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 жол | 43 ms | 0.68x | **3x** |

Компиляцияланған түпнұсқалар азырақ ұтады: әр элементке кететін жұмыс онсыз да жылдам, сондықтан batch
ядролар санына қарай ұтады. Batch crate-тері mimalloc арқылы жад бөледі: жүйелік allocator-мен Go batch
бір ағыннан баяу болды. Demo: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Алты тілдегі нақты код

Go-ның `path`, Ruby-дің `shellwords`, Python-ның `colorsys`, шағын facade-тар артындағы JDK және glibc
мінез-құлқы: әр порт өз gate-інен өтеді, барлығы 13,010 жазылған кейс. Бұл сынақтар rust-anything
ішіндегі қателерді тауып, түзетті (`serde_json` арқылы бір ULP-қа ауытқыған float-тар, жазу кезіндегі C
құлаулары, типсіз кодқа мағынасыз кіріс деректердің берілуі). Әр функция үшін шақырғанда Ruby порты
Ruby-ден 4.4x, ал Python порты CPython-нан 1.35x жылдам жұмыс істейді, ал Go мен Java-ның leaf
функциялары өз тілінде жылдамырақ болып қалады; batch ретінде олардың бәрі ұтады (жоғарыдағы кестені
қараңыз). Есеп: [`docs/real-world-languages.md`](./real-world-languages.md).

## Мысал: x18n-нен нақты модуль

[x18n](https://github.com/x18n-dev/x18n) жобасындағы `packages/core/src/fuzzy.ts`, екі тәсілмен де
[`demo/`](../demo) ішінде портталған:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: ready, wasm-bindgen (core runs in browsers)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# write src/port.rs
rust-anything gate demo/fuzzy-rs
```

Rust `char` бойынша индекстеген алғашқы порт қарапайым тесттерден өтті, бірақ `diff`-тен өтпеді:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS `indexOf` UTF-16 code unit-терін санайды, сондықтан эмодзи екі позиция алады. `demo/*/src/port.rs`
ішіндегі порт генерацияланған `utf16` көмекші функцияларын пайдаланады және 2000/2000 кейстен және
gate-тен өтеді, napi-rs (`demo/fuzzy-napi`) ретінде де, wasm-bindgen (`demo/fuzzy-rs`) ретінде де.

rust-anything бүкіл x18n үшін жазатын жоспар: [`docs/examples/x18n.md`](./examples/x18n.md).

## Орнату

```sh
cargo install --path .
```

`record`, `diff` және `bench` түпнұсқаны өз runtime-ында іске қосады: TS үшін Node 22.6+ (ол `.ts`
бастапқы файлдарын тікелей іске қосады), Python мен C үшін Python 3.9+ (ctypes), Go 1.21+, Ruby 3+,
JDK 17+ (`javac` және `java`). C үшін сондай-ақ C компиляторы керек. wasm bridge-тері үшін қосымша
`rustup target add wasm32-unknown-unknown` және
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked` керек; `build`
нақты нұсқаны атайды.

Агенттер үшін `rust-anything setup` бәрін тіркейді (Жылдам бастау бөлімін қараңыз). Оның орнына MCP
серверді бір жобаға қолмен қосу үшін (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` не шешеді

- Bridge арқылы өте алмайтын экспорттар себебі көрсетіліп, бастапқы тілде қалады, ал shadow модуль
  түпнұсқаны қайта экспорттайды. TS үшін:
  функцияларды қабылдайтын немесе қайтаратын функциялар, генераторлар мен итераторлар, RegExp,
  `instanceof` тексерулері, generic-тер және типтерінде (импорттар, қайта экспорттар және `extends`
  арқылы қадағаланады) функциялар бар мәндер. `--keep "name: reason"` көбірек нәрсені қалдырады,
  мысалы, `Intl` деректеріне тәуелді кодты.
- TS типтері Rust типтеріне сәйкестендіріледі, type alias-тар импорттар арқылы шешіледі, ал параметр
  типтері әдепкі мәндерден шығарылады; құрылымды мәндер генерацияланған бинарлық wire арқылы өтеді (JSON
  тек wire модельдемейтін пішіндер үшін fallback ретінде).
- JSON `undefined`, NaN, Infinity, -0 немесе жалғыз surrogate-тарды бере алмайды: құрылымды мәндер
  генерацияланған `index.cjs` аударатын маркерлерді (`{"$undefined": true}`, `{"$num": "NaN"}`,
  `{"$utf16": [...]}`) алып жүреді, ал көмекші функциялар crate-тің `js.rs` файлында.

`record` TS бастапқы файлдарын сол күйінде іске қосады: Node resolve hook bundler стиліндегі
импорттарды қадағалайды (`./errors` -> `./errors.ts`), репозиторийде npm пакеттері орнатылмаған болса,
`--resolve-from` оларды ұсынады, ал түрлендіруді қажет ететін TS (enum-дар, parameter properties)
`--experimental-transform-types` арқылы қайта іске қосылады.

## `analyze` нені қарайды

- Пакеттер (`package.json`) және бастапқы файлдар; `node_modules`, build шығысы, fixture-лер,
  playground-тар, құрал конфигурацияларын өткізіп жібереді. Vue/Svelte/Astro `<script>` блоктары
  импорттар үшін талданады.
- **Бірліктер**: бастапқы файлдар бумасы немесе пакеттің бастапқы түбіріндегі файл.
- **Толқындар**: бірліктің импорттары ертерек толқындарда болады; импорт циклдары бірге портталады.
- **Bridge**: бірлікке немесе ол импорттайтын бір нәрсеге Node керек болса, napi-rs; портативті код
  үшін wasm-bindgen; UI және редактор коды үшін JS-те қалдыру.
- **Readiness** (қаншалықты қауіпсіз) және **priority** (қауіпсіз әрі тұрарлық: циклдар мен жолдармен
  жұмыс, тесттер, көлем).

| Тәуекел | Маңыздылығы | Мысал |
| --- | --- | --- |
| Жол офсеттері | жоғары | `slice`, `indexOf`, `matchAll`, `d` флагы: UTF-16 және UTF-8 |
| Regex синтаксисі | жоғары | lookaround, backreference, `y`: `regex` crate-інде жоқ |
| Динамикалық regex | жоғары | `new RegExp(userPattern)`: орындалу кезіндегі JS синтаксисі |
| Динамикалық код | жоғары | `eval`, `new Function`, есептелетін `import()` |
| Динамикалық типтеу | орташа | `any`, `'key' in value` |
| Реттелген коллекциялар | орташа | `Map`, `Set`, `Object.keys`: қосылу реті |
| Async, генераторлар | орташа | promise және генератор шекаралары |
| Кластардың мұрагерлігі, reflection | орташа | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback түріндегі API-лер | орташа | функция типіндегі параметрлер мен әдістер: көп сөйлесетін bridge-тер |
| Exception-дар, сандар, JSON | төмен | `throw`, биттік операциялар, `JSON.stringify` реті |

## Әзірлеу

```sh
cargo test                        # unit tests, fixture repo, record/diff/shadow loop (needs node), app record/replay per language
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Дизайн шешімдері және олардың себептері: [DECISIONS.md](../DECISIONS.md).

## Жаңарту немесе жою

```sh
cargo install rust-anything                                    # update (Cargo)
npm install -g rust-anything@latest                            # update (npm)
rust-anything setup                                            # refresh agent settings
rust-anything setup --remove && cargo uninstall rust-anything  # remove (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # remove (npm)
```

`setup --remove` тек rust-anything жазбаларын алып тастайды; ол сақтаған көшірмелер
(`<file>.rust-anything.bak`) өзіңіз жоймайынша қала береді.

## Ол нені ұстай алмайды

Өту дегеніміз Rust жазылған әр кейске сәйкес келеді деген сөз, одан артық емес. Қайта жазуды
бұзатын нәрселер әдетте жазбадан тыс жатады, сондықтан шекаралардың қай жерде екенін біліңіз:

- **Ешкім жазып алмаған кіріс деректер.** Генерацияланған кейстер, тұзақтар және сіздің өз `--inputs`
  деректеріңіз шекті белгілейді. Нақты кіріс деректерді қосыңыз (production үлгілері, bug report-тар,
  түпнұсқаның тест fixture-лері); prod-ты бұзатын пайдаланушы енгізуін генератор сирек ойлап табады.
- **Regex-тер.** `regex` crate-інде lookaround немесе backreference жоқ, тіпті компиляцияланатын
  үлгінің өзі ASCII емес мәтінде `\w`, `\b`, `\d` және регистрге тәуелсіз сәйкестендіруді JS, Python
  немесе Java-дан басқаша өңдеуі мүмкін. `fancy-regex`-ке ауысу немесе үлгіні қайта жазу әр жазылған
  кейстен өтіп, бірақ түрікше нүктесіз `ı` немесе zero-width joiner-де бәрібір өзгеше болуы мүмкін.
  `record` regex қолданатын файлдағы әр функцияға regex тұзақтарын (жоғарыдағылар, Кельвин белгісі,
  ұзын s, араб-үнді цифрлары, жол бөлгіштер, соңғы сигма) қосады, бірақ нақты үлгілеріңізді нақты
  мәтінмен fuzz етіңіз.
- **Орындаулар арасында өзгеретін нәрселер.** `record` түпнұсқаны екі рет іске қосып, нені өзгеше
  болғанын сұрыптайды: өзгерген мәндер (уақыт, id) wildcard-қа айналады; басқа ретпен келген бірдей
  жолдар (hash map-тар, concurrency) кез келген ретпен салыстырылады, сондықтан порт дәл сол жолдарды
  шығаруы керек; жолдар саны өзгеше болса, кез келгенге сәйкес келетін `...` болады. `record` әр түрін
  тізеді: әрқайсысын қарап шығыңыз, өйткені hash реті немесе concurrency айырмашылығы дәл портта шын
  өзгеруі мүмкін нәрсе.
- **Float-тар.** Санды мәтінге пішімдеу тілдер арасында өзгеше болады (`1e21`, `-0`, цифрлар саны).
  Тұзақтар осы мәндерді қамтиды және олар дәл сәйкес келуі керек; `--float-tolerance` тек дөңгелектеуді
  кешіреді, пішімдеуді ешқашан кешірмейді.
- **Шығыста жоқ нәрселер.** Уақыт, жад, жүктеме кезіндегі concurrency және stdout, stderr, exit code,
  жазылған файлдар мен HTTP жауаптарынан басқа жанама әсерлер (желі шақырулары, дерекқорлар,
  сигналдар) салыстырылмайды.
- **Басқа платформалар.** Жазба оны орындаған машинадағы мінез-құлықты ғана дәлелдейді. Нәтижелері
  тип өлшемдеріне, endianness немесе компиляторға тәуелді C коды target жүйеде басқаша жұмыс істеуі
  мүмкін; сондықтан `analyze` hardware-ға жақын C кодын C-де қалдырады.

## Жиі қойылатын сұрақтар

**Ол менің кодымды автоматты түрде қайта жаза ма?** Жоқ. Ол нені көшіру керегін табады, bridge
генерациялайды, түпнұсқаның не істейтінін жазып алады және Rust-ты соған қарсы тексереді. Rust кодын
`port.rs` ішінде сіз немесе агентіңіз жазады; оның дұрыс екенін `diff` және `gate` шешеді.

**Қолданбамның API-і өзгере ме?** Жоқ. Шақырушылар сол функцияларды импорттайды (немесе shadow
модульді, ол сенімділік жинап жатқан кезде екеуін де іске қосып, түпнұсқаның нәтижесін қайтарады).

**Rust әрқашан жылдамырақ па?** Жоқ, және rust-anything мұны ашық айтады. Әр элемент үшін бір рет
шақырылатын шағын функция Rust-та жиі баяуырақ, өйткені әр шақыру bridge арқылы өтеді; V8, JVM және Go
мұндай функцияларды наносекундтарда орындайды. `profile` оның айналасындағы циклды табады, `--batch`
бүкіл циклды көшіреді, ал `bench` шығармас бұрын қорытынды береді. numba, Cython немесе JAX арқылы
бұрыннан компиляцияланған код та машиналық код ретінде орындалады: `profile` және `analyze` оны
белгілейді, өйткені оны порттау жылдамдыққа аз пайда береді.

**Менің кодым сандық; float-тар дәл сәйкес келе ме?** Көбіне жоқ: операциялар реті, fused
multiply-add және математикалық кітапхана компиляторлар арасында өзгеше. `--float-tolerance 1e-9`
арқылы жазыңыз (`record` немесе `app record`), сонда float-тар үлкенірек мәннің осы үлесі шегінде
сәйкес келеді (1-ден төмен болса, абсолютті түрде). Бүтін сандар, мәтін және құрылым бәрібір дәл сәйкес
келуі керек.

**Тек APK, JAR немесе .exe түрінде ғана бар қолданбаны порттай ала ма?** Жоқ. Ол бастапқы кодты
порттайды: функцияларды талдайды, әрқайсысының не істейтінін жазып алады және Rust-ты іске қосылған
түпнұсқаға қарсы тексереді. Компиляцияланған қолданбада бұлардың ешқайсысы жоқ, және `analyze` мұны
айтады. Бинарлық файлдың көрінетін мінез-құлқына қарап жаңа Rust қолданбасын жазу басқа жоба.

**Сыннан өткен C кодын порттау керек пе?** Көбіне жоқ, және `analyze` қай жерде екенін айтады.
Hardware регистрлерімен жұмыс істейтін, компилятордың тип өлшемдеріне немесе жад орналасуына сүйенетін
немесе inline assembly қолданатын C коды (`volatile`, bitfield-тер, packed struct-тар, `__asm__`,
адреске түрлендірілген бүтін сандар) "keep in C" деп белгіленеді: сіздің машинаңыздағы жазба target
туралы ештеңе дәлелдемейді, ал тұрақты драйвер немесе firmware коды қайта жазудан аз ұтады. Оның
айналасындағы портативті логика (парсинг, протоколдар, деректерді өңдеу) жақсы көшеді.

**Ол менің Electron қолданбамды порттай ала ма?** Логикасын, иә; терезелер веб-беттер болып қалады.
`analyze --whole-app` Electron-ды анықтап, main процесті бөлік-бөлігімен жоспарлайды, ал renderer сол
күйінде қалады. UI-ды Tauri-ге көшіру (Rust backend үстіндегі сол веб UI) логика Rust-қа көшкеннен
кейінгі бөлек қадам.

**C#, Kotlin немесе Swift ше?** C# preview күйінде ([Тілдер](#тілдер) бөлімін қараңыз); Kotlin мен
Swift әлі қолдау көрсетілмейді. Әр тілге парсер, recorder, bridge және replay драйвері керек, бәрі
басынан аяғына дейін тестіленген. Өзіңізге қажет тіл үшін issue ашыңыз (немесе барына дауыс беріңіз).

**Rust коды түпнұсқадан әлдеқайда үлкен болып кетпей ме?** Болмауы керек. `gate` порттың жол санын
түпнұсқанікімен салыстырады және 3x-тен асса (плюс импорттар мен сигнатуралар үшін 50 жол) сәтсіз
аяқталады: бұл әдетте crate бұрыннан істейтін нәрсені қолмен жазуды немесе жағдайларды бір-бірлеп
өңдеуді білдіреді. `analyze` пайдалану керек crate-терді тізеді.

**Бөлік-бөлігімен порттау Rust-ты ескі қолданбаның дизайнына байлап қоймай ма?** Екеуі қатар жұмыс
істеп тұрғанда ғана. Жазбалар мінез-құлықты қолданбаның ішкі құрылымынан емес, шекараларынан тексереді
(CLI шығысы, сервер жауаптары, модульдің экспортталған функциялары). Бірліктер әлі bridge арқылы өтіп
жатқанда ескі құрылымды қайталаңыз; `app lift` түпнұсқаны алып тастағаннан кейін Rust-ты еркін қайта
құрылымдаңыз, ал `app replay` мінез-құлықты бәрібір дәлелдейді. Ештеңе түпнұсқаға кері шақыру да
жасамайды: front door оны жеке процесс ретінде іске қосады (немесе оған HTTP жібереді), bridge арқылы
қосылған бірліктерді түпнұсқа шақырады, керісінше ешқашан емес, ал callback-тер бастапқы тілде қалады.

**Менің кодым машинамнан шығып кете ме?** Жоқ: rust-anything локалды жұмыс істейді және кодыңыздың
ешбір бөлігін ешқайда жібермейді. Cargo crate-терді әдеттегідей жүктейді, ал агентіңіздің модель
провайдері агентіңіз оған жіберетінді өз саясатына сәйкес көреді.

**Не орнатылуы керек?** Rust және сіз порттайтын тілдің runtime-ы ([Орнату](#орнату) бөлімін қараңыз).

**Бірдеңе бұзылды.** Команда, оның шығысы және платформаңыз көрсетілген issue ашыңыз.

## Демеушілер

rust-anything тегін және ашық бастапқы кодты жоба. Егер ол жұмысыңызға көмектессе, оған демеуші
болуды қарастырыңыз. Сіздің қолдауыңыз әзірлеуді жалғастыруға мүмкіндік береді.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="GitHub-та rust-anything жобасына демеуші болу" /></a>
</p>

### Компания демеушілері

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Жеке демеушілер

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

## Үлес қосу

Issue-лер мен pull request-тер құпталады; [CONTRIBUTING.md](../CONTRIBUTING.md) ортаны баптауды,
тесттердің қайда орналасатынын және жаңа тілді қалай қосуды түсіндіреді. Дизайн шешімдері және олардың
себептері [DECISIONS.md](../DECISIONS.md) ішінде. Нақты порттардың тәжірибелік мысалдары әсіресе
құпталады. Қауіпсіздік мәселелері туралы жеке хабарлаңыз ([SECURITY.md](../SECURITY.md)), сондай-ақ
[мінез-құлық кодексін](../CODE_OF_CONDUCT.md) қараңыз.

## Лицензия

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Репозиторийіңіздегі порттар мен генерацияланған код сіздікі.
