<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="Ağzı kod teqi olan rust-anything xərçəngi">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">Müəllif: <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · Azərbaycanca · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>
<p align="center"><sub>Bu tərcümə icma tərəfindən dəstəklənir və <a href="../README.md">ingiliscə README</a>-dən geri qala bilər.</sub></p>

<p align="center"><em>Bütün tətbiqinizi Rust-da yenidən yazın. Bütün yol boyu işlək qalsın.</em></p>

<p align="center"><em>CLI-lar, serverlər və kitabxanalar, hissə-hissə, hər addımda orijinalla yoxlanılaraq.</em></p>

<p align="center">Node.js və TypeScript · Python · C · Go · Ruby · Java · PHP və C# önizləmədə</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io versiyası"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm versiyası"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 dil">
  <a href="#dəstəklənən-agentlər"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 agentlə işləyir"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Testlər"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT lisenziyası"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub ulduzları"></a>
</p>

<p align="center">20x-ə qədər daha sürətli · 38,251 qeydə alınmış hal təkrar oynadılıb · 0 uyğunsuzluq · bir əmr</p>

<p align="center">
  <img src="assets/race.gif" alt="x18n-in 50,000 açar üzrə axtarışına user.profile yazılır: TypeScript 143 ms sərf edir, rust-anything batch-i 6.9 ms, hər düymə basışında eyni nəticələrlə." width="820">
</p>

**Bütün tətbiqinizi Rust-da, hissə-hissə yenidən yazın.** rust-anything Node.js
(TypeScript/JavaScript), Python, C, Go, Ruby və ya Java tətbiqinizin bu gün nə etdiyini qeydə alır,
sonra Rust-da yenidən yazılmış hər hissəni növbətiyə keçməzdən əvvəl bu qeydlə yoxlayır, tətbiq
tamamilə Rust olana qədər. CLI-lar, HTTP serverləri və kitabxanalar; Rust kodunu kodlaşdırma
agentiniz (və ya siz) yazır. O, yalnız qeydin əhatə etdiyini tuta bilər: bax
[Nəyi tuta bilmir](#nəyi-tuta-bilmir). Yalnız yavaş hissənin sürətlənməsi lazımdır? Yalnız onu,
hər dəfə bir hot path olmaqla port edin:

| Real iş yükü, orijinalla eyni nəticələr | Orijinal | rust-anything ilə |
| --- | ---: | ---: |
| x18n-in yan panel axtarışı, 50,000 açar (TypeScript, Node) | sorğu başına 10 ms | **0.5 ms: 20x daha sürətli** |
| Eyni axtarış brauzerdə (wasm, bir thread) | 10 ms | **0.95 ms: 11.5x** |
| 20,000 string üzərində `slugify` (Python) | 98 ms | **17x daha sürətli** |
| Ruby-nin standart kitabxanasından `Shellwords.shellescape`, 50,000 dəyər | 88 ms | **11.8x daha sürətli** |
| 50,000 string üzərində `Slugify` (Go) | 49 ms | **4x daha sürətli** |
| 50,000 string üzərində `slugify` (Java) | 43 ms | **3x daha sürətli** |

4 nüvədə ölçülüb; hər rəqəmin [`demo/`](../demo) qovluğunda əvvəlcə nəticələrin eyni olduğunu
yoxlayan bir benchmark-ı var. Hər kiçik funksiya üçün Rust-u ayrıca çağırmaq adətən JIT-dən *daha
yavaşdır*; rust-anything köçürməyə dəyən dövrü tapır və onu köçürür.

> rust-anything müstəqil layihədir, Rust Project və ya Rust Foundation ilə əlaqəli deyil və onlar
> tərəfindən dəstəklənmir. "Rust" Rust Foundation-ın əmtəə nişanıdır.

## Sürətli başlanğıc

Bunu Claude Code, Codex, Cursor və ya Gemini CLI-a yapışdırın və quraşdırmanı agentinizə həvalə edin:

```text
rust-anything-i quraşdır: `cargo install rust-anything`, sonra `rust-anything setup` işə sal.
Səni nə vaxt yenidən başlatmalı olduğumu de.
```

Və ya özünüz:

```sh
cargo install rust-anything   # crates.io-dan
rust-anything setup           # Claude Code, Codex, Cursor və Gemini CLI-da qeydiyyatdan keçirir
```

Hələ Rust toolchain-iniz yoxdur? macOS, Linux və Windows üçün hazır binary fayllar hər
[GitHub release](https://github.com/erkamyaman/rust-anything/releases)-ə əlavə olunub, JavaScript
layihələri üçün isə `npm install -g rust-anything` eyni binary-ni quraşdırır.

Claude Code-da onu plugin kimi də quraşdıra bilərsiniz (MCP server və skill; yuxarıdakı CLI
`PATH`-da olmalıdır):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` tapdığı hər agentə MCP serveri əlavə edir və iş axını skill-ini agentin skill-ləri oxuduğu
yerə quraşdırır. Digər ayarlarınızı saxlayır, yenidən işə salmaq təhlükəsizdir, `--remove` isə
etdiklərini geri qaytarır. Sonra agentinizdən, məsələn, bunları istəyin:

- *"Bu CLI-ı rust-anything ilə başdan-başa Rust-da yenidən yaz və eyni davrandığını sübut et."*
- *"Bu axtarış yavaş görünür. rust-anything ilə profilini çıxar və isti dövrü Rust-a köçür."*
- *"`src/parser/`-in rust-anything ilə Rust-a miqrasiyasını planlaşdır; ilk vahidi port et və sübut et."*
- *"`rust/text-rs`-dəki Rust portunu orijinala qarşı benchmark et və onu buraxmağa dəyib-dəymədiyini de."*

### Dəstəklənən agentlər

| Agent | `rust-anything setup` əlavə edir |
| --- | --- |
| Claude Code | `~/.claude.json`-da MCP server, `~/.claude/skills/`-də skill |
| Codex | `~/.codex/config.toml`-da MCP server, `~/.codex/skills/`-də skill |
| Cursor | `~/.cursor/mcp.json`-da MCP server |
| Gemini CLI | `~/.gemini/settings.json`-da MCP server |
| İstənilən digər MCP müştərisi | `rust-anything mcp`-ni əllə stdio server kimi əlavə edin (bax [Quraşdırma](#quraşdırma)) |

Mövcud faylı dəyişməzdən əvvəl `setup` onun yanında bir surətini saxlayır (`<file>.rust-anything.bak`).

Və ya addımları özünüz icra edin:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile dövr daxilində fuzzyScore-u tapır, bridge --batch Rust crate-ini yaradır, gate 2000/2000 qeydə alınmış halla keçir və benchmark TS-dən 20.7x daha sürətli olduğunu göstərir." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # isti olan nədir və onu kim çağırır
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# src/port.rs-i yazın (və ya agentinizə yazdırın), sonra:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # hər qeydə alınmış hal uyğun gəlməlidir
rust-anything bench rust/fuzzy-rs                      # daha sürətlidir? hökm deyəcək
rust-anything gate rust/fuzzy-rs                       # hazırdır, yəni bu keçir
```

rust-anything kodu tərcümə etmir: Rust-u kodlaşdırma agentiniz (Claude Code, Codex, Cursor, ...) və ya
siz yazırsınız. rust-anything agentin etibarlı şəkildə təxmin edə bilmədiyini təmin edir: vaxtın hara
getdiyini, əvvəlcə nəyin və hansı ardıcıllıqla port ediləcəyini, kodun qalan hissəsinin Rust-u API-si
dəyişmədən çağıra bilməsi üçün körpünü (bridge), portun uyğun gəlməli olduğu dəqiq davranışı, onu
buraxmağın təhlükəsiz yolunu və portun nə vaxt hazır olduğunu deyən gate-i.

## Dillər

| Dil | Vahid | Körpü | Qeydə alan və təkrar oynadan |
| --- | --- | --- | --- |
| TypeScript/JavaScript | qovluq və ya fayl | yaradılmış binary wire ilə napi-rs və ya wasm-bindgen; siniflər və async daxil | `.ts` mənbələrini işlədən Node |
| Python | paket və ya modul | PyO3 (abi3), birbaşa çevirmə, tipli exception-lar | orijinalı import edən Python |
| C | `.c` faylı | orijinal adlarla `extern "C"` funksiyaları və header | paylaşılan kitabxana kimi kompilyasiya olunmuş orijinal, ctypes ilə çağırılır, hər hal üçün bir fork |
| Go | paket | orijinal API-li paketdə tipli cgo çağırışları və yaradılmış binary wire | öz modulu kimi qurulan yaradılmış Go drayveri |
| Ruby | modul funksiyalarından ibarət fayl və ya qovluq | orijinal modulların altında magnus genişlənməsi | yaradılmış Ruby drayveri |
| Java | `public static` metodlardan ibarət paket | orijinal metodlara malik wrapper siniflərdə tipli JNI və yaradılmış binary wire | yaradılmış reflection drayveri |
| PHP (önizləmə) | funksiyalardan və `public static` metodlardan ibarət qovluq | növbədə: C ABI üzərindən PHP FFI | bu gün bütöv tətbiqlər: CLI-lar və serverlər (`php -S`) üçün `app record`, `app replay` və front door |
| C# (önizləmə) | `public static` metodlardan ibarət qovluq | növbədə: C ABI üzərindən P/Invoke | bu gün bütöv tətbiqlər: CLI-lar və ASP.NET serverləri (`dotnet <app>.dll`) üçün `app record`, `app replay` və front door |

C-dən başqa hər dil batch sinifləri də alır (`--batch`): elementlər körpünü bir dəfə keçir və
Rust-da qalır, hər çağırış isə bütün nüvələrdə hamısının üzərində işləyir.

Dil repozitoriyadan müəyyən edilir (`go.mod`, `pom.xml`, `.csproj` və ya `.sln`, `pyproject.toml`,
`Gemfile`, `composer.json`, `package.json`, əks halda ən çox rast gəlinən mənbə faylları); `--lang`
bunu əvəz edir. Tiplər mənbədən gəlir: TS tipləri, Python type hint-ləri, C, Go, Java və C#
imzaları, Ruby YARD teqləri, PHP tipləri və phpdoc; rəqəm kimi istifadə olunan tipsiz parametrlər
rəqəm kimi müəyyən edilir.

PHP önizləmədədir: `analyze` PHP tətbiqini planlaşdırır (Composer paketləri və PSR-4 autoloading,
sərbəst müqayisə və tam ədədin float-a daşması kimi risklər, crate-lərə uyğunlaşdırılmış Composer
paketləri), PHP CLI və ya serveri isə qeydə alına, təkrar oynadıla və Rust front door-unun arxasına
qoyula bilər. Onun vahidlərini PHP-nin FFI-ı vasitəsilə Rust-a port etmək növbəti addımdır
([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# da eyni şəkildə önizləmədədir: `analyze` `.csproj` layihələrini və onların NuGet paketlərini
oxuyur (crate-lərə uyğunlaşdırılmış), `using` direktivlərini qovluqlara həll edir və C#-ın fərqli
etdiyi şeyləri işarələyir (`decimal`, `dynamic`, LINQ-in təxirə salınmış sorğuları, `Task`, `lock`,
reflection). C# CLI və ya ASP.NET serveri qeydə alına, təkrar oynadıla və Rust front door-unun
arxasına qoyula bilər; vahidləri P/Invoke vasitəsilə port etmək növbədədir.

## Necə işləyir

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 vaxt hara   əvvəlcə     Rust       orijinal    siz və ya   hər       daha       prod-da     hazırdır,
 gedir       nəyi port   crate-i    nə edir     agentiniz   qeydə     sürətli?   ikisi       yəni bu
             etməli      və wrapper             yazır       alınmış   hökm       yan-yana    keçir
                                                            hal
```

Orijinal həqiqət mənbəyi olaraq qalır: `record` onu kənar hallarla (və sizin girişlərinizlə) işə
salır və nə qaytardığını və ya hansı xətanı atdığını saxlayır; `diff` hər halı Rust-a qarşı təkrar
oynadır; hamısı uyğun gəlib `gate` keçənə qədər heç nə buraxılmır. Çağıranlar bütün müddət ərzində
orijinal API-dən istifadə etməyə davam edir.

Bütöv tətbiq də eyni dövrdən vahid-vahid keçir, bütün proqramı sübut edən çərçivənin içində
([Bütöv tətbiqi port etmək](#bütöv-tətbiqi-port-etmək)):

```
analyze --whole-app ──> app record ──> app front-door ──> hər vahid üçün: yuxarıdakı dövr, sonra app wire ──> app lift
 struktur, hər           tətbiqin       giriş nöqtəsi      gate keçir, vahid Rust-da cavab verir:           təmiz Rust,
 asılılıq, veriləcək     xaricdən       Rust-dadır;        replay 100%, fallback dərəcəsi azalır            replay ilə
 qərarlar                nə etdiyi      orijinal cavab                                                      sübut olunub
                                        verir
```

## Dövr

| Addım | Əmr | Nə edir |
| --- | --- | --- |
| 0. Profil | `rust-anything profile <repo> -- node bench.mjs` | Real iş yükünü dilin profiler-i altında işə salır (node, cProfile, `go test` pprof, JFR, Ruby tracer): daxil olan vaxta görə isti funksiyalar, onları çağıranlar və hansı dövrlərin batch-lənəcəyi; artıq kompilyasiya olunmuş kodu (numba, Cython, JAX) işarələyir, çünki orada Rust az qazandırır |
| 1. Plan | `rust-anything analyze <repo>` | Vahidlər, port ardıcıllığı, `file:line` ilə risklər, hər vahid üçün körpü, asılılıq-crate uyğunluğu, ən yaxşı ilk portlar; `--whole-app` giriş nöqtələrini və strukturu, crate-i ilə birlikdə hər asılılığı (import edilmiş və ya elan edilmiş), hissələri (bir-birini import edən vahidlər birlikdə köçür) və tövsiyə olunan cavabla nömrələnmiş qərarları əlavə edir |
| 2. Körpü | `rust-anything bridge <repo> <unit>` | Binding-ləri olan crate (`lib.rs` və mənbə dilin yüklədiyi wrapper) və port ediləcək stub-lar (`port.rs`); `--batch fn:param` çoxlu `param` dəyərini Rust-da saxlayan sinif əlavə edir |
| 3. Qeyd | `rust-anything record <crate>` | Orijinalı yaradılmış kənar hallarla (ASCII olmayan, emoji, `-0`, `NaN`, float gözlənilən yerdə int, ...) və hər parametrdəki hər semantik tələ ilə (string uzunluğu və hərf registri, işarəli bölmə, daşma sərhədləri, float çapı, map və sıralama ardıcıllığı) işə salır və `cases.jsonl`-i saxlayır; `--float-tolerance 1e-9` rəqəmsal kod üçün float-ların bu pay daxilində uyğun gəlməsinə icazə verir |
| 3. Qurma | `rust-anything build <crate>` | Rust tərəfini qurur: `.node`, wasm paketi, Python genişlənməsi və ya paylaşılan kitabxana |
| 3. Diff | `rust-anything diff <crate>` | Qeydə alınmış halları Rust-a qarşı, orijinalı çağıranların çağırdığı kimi təkrar oynadır; uyğunsuzluqları siyahıya alır |
| 3. Bench | `rust-anything bench <crate>` | Qeydə alınmış halların orijinalda və Rust-da, körpü daxil, vaxtını ölçür |
| 4. Shadow | `rust-anything shadow <crate>` | Hər ikisini işə salan, orijinalın nəticəsini qaytaran və uyğunsuzluqları bildirən drop-in; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, testlər, `unsafe` auditi, port edilməmiş heç nə qalmaması, orijinalın hər xəta yolu üçün qeydə alınmış uğursuz hal, orijinalın xəta qaytardığı yerdə `unwrap`/`expect`/`panic!` olmaması (`// INFALLIBLE: <why>` ilə işarələnməyibsə), qurma, API, davranış |
| Agentlər | `rust-anything setup` | MCP serveri (`rust-anything mcp`, hər addım alət kimi) və iş axını skill-ini ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) kodlaşdırma agentlərinizdə qeydiyyatdan keçirir |

## Bütöv tətbiqi port etmək

Məqsəd orijinal kimi davranan, orijinalı isə istinad kimi saxlanan təmiz Rust tətbiqidir. Rust-u
agentiniz yazır; rust-anything işi sıralayır, karkasını qurur və hər addımı sübut edir.
[Whole-app skill-i](../skills/rust-anything/whole-app.md) agenti bu prosesdən keçirir və yalnız sizin
verə biləcəyiniz qərarlardan başlayır:

- **Sorğu-sual (grilling)**: agent portun asılı olduğu hər qərar həll olunana qədər raundlarla, hər
  sualı tövsiyə etdiyi cavabla birlikdə soruşur və hər birini `rust/DECISIONS.md`-də ADR kimi yazır;
  `rust/GLOSSARY.md` isə orijinalın terminlərini Rust adlarına uyğunlaşdırır.
- **Araşdırma**: fon agentləri hər asılılığın ilkin mənbələrini oxuyur və tapdıqları hər semantik
  tələ ilə birlikdə `rust/research/<topic>.md` yazır.
- **Sessiyalar arası**: `rust/MAP.md` hər vahidi vəziyyəti ilə siyahıya alır; sessiya başlamazdan
  əvvəl bir vahidi götürür və hər yoxlama nöqtəsi növbəti sessiya üçün `rust/HANDOFF.md` qoyur. Eyni
  dalğadakı vahidlər subagent-lər tərəfindən paralel port edilə bilər.
- **Keçid (cutover)**: agent bacardığını edir və yalnız sizin edə biləcəyiniz addımlar (deploy-lar,
  DNS, secret-lər) üçün hər addımda geri dönüş yolu olan interaktiv skript, `rust/cutover.sh` yazır.

Sorğu-sual, araşdırma və bu təcrübələr
[Matt Pocock-un skill-lərindən](https://github.com/mattpocock/skills) uyğunlaşdırılıb.

Əvvəlcə planlaşdırın: `rust-anything analyze . --whole-app` tətbiqin strukturunu (CLI, server və ya
kitabxana) və giriş nöqtələrini, Rust crate-i və uyğunluğu ilə birlikdə hər xarici asılılığı (import
edilmiş və ya elan edilmiş), hissələr şəklində port ardıcıllığını (bir-birini import edən vahidlər
birlikdə köçür) və tövsiyə olunan cavabla nömrələnmiş qərarları əlavə edir: saxlanılacaq vahidlər,
bloklanmış vahidlər, crate-i olmayan və ya qismən olan asılılıqlar.

Sonra bütün proqramı xaricdən sübut edin. `record` və `diff` bir vahidi sübut edir; `app record`
və `app replay` isə tətbiqi, altı dilin istənilən birində olan CLI-lar və serverlər üçün sübut edir
(tətbiq qara qutudur):

```sh
rust-anything app record . -- python3 cli.py          # orijinalı işə salan əmr
rust-anything app replay .                            # orijinal 100% keçməlidir
rust-anything app replay . --build "target/release/mytool"
```

- `app record` orijinalı tətbiqin öz sənədləşdirilmiş nümunələri (Markdown və shell fayllarındakı
  `$ mytool ...` sətirləri, adını çəkdikləri fayllarla birlikdə), `--inputs` JSONL faylı
  (`{"name", "args", "stdin", "env", "files"}`) və bu hallardan törədilmiş semantik tələlərlə (ASCII
  olmayan və emoji string-lər, mənfi bölmə və modul, daşma, çox böyük və çox kiçik float-lar, map
  ardıcıllığı, çatışmayan fayllar) işə salır. Hər hal iki dəfə işləyir; iki işləmə arasında fərqlənən
  hissə `[..]` wildcard-ına çevrilir. `--normalize timestamps|uuids|key-order` və ya
  `--normalize name=regex` hallarla birlikdə saxlanılan normalizer-lər əlavə edir.
- Hallar `rust/app-cases/`-dəki [trycmd](https://docs.rs/trycmd) fayllarıdır: `<case>.toml` (argv,
  env, çıxış kodu), `.stdin`, `.stdout`, `.stderr`, `.in/` (giriş faylları) və `.out/` (yazılmış
  fayllar). Onları əllə oxuyun və redaktə edin; portun binary-si olduqda Rust testi onları `trycmd`
  ilə işə sala bilər.
- `app replay` istənilən build-i hallara qarşı işə salır, `passed/total` çap edir, hər uğursuz hal
  üçün diff olan `rust/app-cases/replay-report.md` yazır və istənilən uyğunsuzluqda sıfırdan fərqli
  kodla çıxır. `RUST_ANYTHING_FALLBACK_LOG` ilə adı verilən fayla əlavə yazan build (orijinala hər
  fallback üçün bir sətir), aşağıdakı front door kimi, fallback dərəcəsini də hesabatda görür.
- `app replay --case <name>` hesabatın verdiyi adla bir halı yenidən işə salır: hər şeyi yenidən
  işlətməzdən əvvəl uyğunsuzluğu düzəltmək üçün sürətli, təkrarlana bilən dövr.

Sonra giriş nöqtəsini Rust-a köçürün və əmrləri ona vahid-vahid ötürün:

```sh
rust-anything app front-door .                            # rust/app: hər əmr orijinalı işə salır
rust-anything app wire . textkit --command upper          # textkit-rs gate-dən keçdikdən sonra
# yapışqan kodu rust/app/src/units/textkit.rs-də yazın, sonra:
rust-anything app wire . textkit                          # yenə 100%, daha aşağı fallback dərəcəsi
```

- `app front-door` `rust/app`-in karkasını qurur: tətbiqin adını daşıyan Rust binary-si; qeydə
  alınmış hallardakı əmrlər və flag-lar üçün clap parser, burada hər əmr orijinalı eyni argv, stdin
  və mühitlə işə salır, onun çıxışını və çıxış kodunu olduğu kimi ötürür. Hər fallback sayılır, buna
  görə də təzə front door-u təkrar oynatmaq 100% fallback ilə 100% keçid verir (bunu göstərmək üçün
  qurur və təkrar oynadır). `rust/app`-in üzərinə heç vaxt yazmır: o andan kod sizindir.
- `app wire <repo> <unit> --command <name>` vahid crate-i üzərində `gate` işə salır (yenicə keçibsə
  `--skip-gate`), onu `rust/app`-ə kitabxana kimi əlavə edir, sizin və ya agentinizin doldurması üçün
  `src/units/<unit>.rs`-i bir dəfə yazır (arqumentləri parse edin, `<crate>::port`-u çağırın,
  orijinalın çap etdiyini çap edin), əmrləri ona yönləndirir, sonra qurur və təkrar oynadır.
  `RUST_ANYTHING_UNIT_<NAME>=original` qoşulmuş vahidi lift-ə qədər orijinala geri göndərir.

Heç bir əmr adı olmayan argv üçün (arqumentsiz çağırış, naməlum əmrlər, istifadə xətaları) tətbiqin
öz adını əmr kimi qoşun (`--command mytool`).

Replay fallback dərəcəsi 0 ilə keçəndə və hər vahid gate-dən keçəndə onu təmiz Rust tətbiqinə
çevirin:

```sh
rust-anything app lift .
```

- `app lift` hər iki şərt ödənənə qədər imtina edir və nəyin mane olduğunu deyir: hələ də fallback-ə
  düşən hallar, hələ stub olan yapışqan kod, gate-dən keçməyən vahidlər.
- Əvvəlcə surət üzərində fallback yolunu və kill switch-ləri silir, hər vahid crate-ini `rust/app`-in
  adi kitabxanasına çevirir (`cdylib`, binding-lər və ya yaradılmış wrapper-lər olmadan) və
  `cargo test` zamanı `rust/app-cases`-i trycmd ilə işə salan `rust/app/tests/app_cases.rs` əlavə
  edir, beləliklə CI-a cargo-dan başqa heç nə lazım olmur.
- Sonra lift yoxlama siyahısını icra edir: hər vahiddə və `rust/app`-də fmt, clippy `-D warnings` və
  testlər; `rust/DECISIONS.md`-də adı çəkilən hər hədəfin quraşdırıldığı yerdə qurulması və ya
  yoxlanması; iş vaxtı oxunan fayllar və daxil edilməmiş asset qovluqları; və təmiz binary üzərində
  replay. Dəyişikliklər yalnız bunların hamısı keçəndə geri yazılır. Orijinala heç vaxt toxunulmur.

### Serverlər

Eyni əmrlər HTTP serverlərini də sübut edir. `--http` əmrin server başlatdığını bildirir; portu
`PORT`-dan və ya əmrdəki `{port}`-dan götürür (həmişə eyni portu dinləyən server üçün `--port`):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: hər route proxy edilir
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Sorğular tətbiqin sənədlərindəki `curl` sətirlərindən (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs`-dan (`{"name", "method", "path", "headers", "body"}`) və tələlərdən gəlir: path
  seqmentləri və query dəyərləri CLI arqumentləri ilə eyni tələlərlə əvəz olunur, body-lər mətn və
  JSON tələləri ilə, üstəlik naməlum bir route. Hər işləmə serveri təzədən başladır və sorğuları ad
  ardıcıllığı ilə göndərir, beləliklə sorğular arasındakı vəziyyət saxlanılır.
- Hallar `rust/app-cases/http/<case>.toml` (sorğu, status və vacib header-lər) və `<case>.body`
  fayllarıdır (cavab gövdəsi, iki işləmənin fərqləndiyi yerlərdə `[..]` ilə). Date, server və cavaba
  xas digər header-lər kənarda qalır; maraqlanmadığınız istənilən header sətrini silin.
- Front door orijinalı öz portunda başladan və heç bir vahidin cavab vermədiyi hər route-u proxy
  edən axum serveridir. `wire --route` axum route-larını qəbul edir: `METHOD /path/{param}`,
  istənilən metod üçün `/path`, qalan hər şey üçün `*`; yapışqan kod route-u, onun parametrlərini və
  sorğunu alır. `lift` proxy-ni silir; bundan sonra HTTP halları CI-da `app replay` ilə işləyir.

### Kitabxanalar

Kitabxananın təkrar oynadılacaq prosesi yoxdur: onun public API-si front door-dur, hər vahidin qeydə
alınmış halları isə sübutdur.

```sh
rust-anything app front-door .        # rust/app: public API-li Rust crate-i
# hər vahid dövrdən keçir: bridge, record, port.rs, build, diff, gate; sonra:
rust-anything app wire . textkit-rs   # rust/app-dən yenidən export edilir; orijinal onun shadow-unu import edir
rust-anything app replay .            # hər qoşulmuş vahidin halları; fallback = hələ orijinalda olan export-lar
rust-anything app lift .
```

- `app front-door` repozitoriyada `main` və server olmadıqda (əks halda `--library`) public API-ni
  (hər vahidin export-larını) tapır və `rust/app`-i kitabxana crate-i kimi qurur. Hər qoşulmuş vahid
  onun moduluna çevrilir: `pub use textkit_rs::port as textkit;`.
- `app wire` `bridge` ilə yaradılmış crate-i götürür, `gate` işə salır və vahidin shadow drop-in-ini
  yazır: orijinal paket vahidin yerinə onu import edir, beləliklə onu çağıranlar orijinal API-ni
  saxlayır və Rust-a çatır. `RUST_ANYTHING_UNIT_<NAME>=original` vahidi geri göndərir (C: shadow-un
  flag-ları olmadan qurun).
- `app replay` hər qoşulmuş vahidin qeydə alınmış hallarını onun binding-ləri vasitəsilə işə salır.
  Fallback dərəcəsi Rust-un hələ cavab vermədiyi public export-ların payıdır: qoşulmamış vahidlər və
  `bridge`-in mənbə dildə saxladığı export-lar.
- `app lift` fallback-in 0 olmasını və hər vahidin `gate`-dən keçməsini tələb edir; vahidlərdən
  binding-ləri, wrapper-ləri və shadow-ları çıxarır və `rust/app`-i vahid təmiz Rust kitabxanası kimi
  qoyur. Heç bir `port.rs`-ə toxunmur, buna görə binding-lər vasitəsilə uyğun gələn hallar onu hələ də
  təsvir edir; yoxlama siyahısı orijinalın hələ də shadow-ları import edən faylları barədə xəbərdarlıq
  edir.

Beşi də həm də MCP alətləridir: `app_record`, `app_replay`, `app_front_door`, `app_wire` və
`app_lift`.

## Real nümunə: x18n-in nüvəsi

x18n nüvəsinin API dəyişikliyi olmadan köçürülə bilən 29 funksiyasının hamısı rust-anything ilə port
edildi: hər gate keçir və 7,925 qeydə alınmış hal tam uyğun gəlir. Sonra `rust-anything bench`
göstərdi ki, JS-dən çağırılanda portlar TS-dən yavaşdır, çünki körpünün dəyəri görülən işdən çoxdur.
Tam hesabat: [`demo/x18n-core`](../demo/x18n-core/README.md). Dərs alətin özünə daxil edilib: portu
buraxmazdan əvvəl `bench` ilə ölçün.

## Hot path-lar: məlumatı Rust-da saxlayın

Hər element üçün bir dəfə çağırılan port körpünün haqqını da hər element üçün ödəyir və JIT-ə uduzur.
Qazandıran dövrü köçürməkdir: `profile` onu tapır, `--batch` isə elementləri bir dəfə qəbul edən və
hər çağırışda funksiyanı hamısının üzərində, bütün nüvələrdə işlədən, nəticələri typed array kimi
qaytaran sinif yaradır.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: işin dörddə biri, `matched` tərəfindən hər açar üçün çağırılır: batch edin
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // bir dəfə
const order = search.rank(query, 0)               // hər düymə basışında: indekslər, ən yaxşısı əvvəl
```

`port.rs`-dəki `FuzzyScoreIndex` struct-ı standart dövrü elementləri bir dəfə hazırlayan və özü
sıralaya bilən (`rank`) dövrlə əvəz edir: o, açarları hər biri üçün simvol maskası ilə kiçik hərflərə
çevrilmiş şəkildə, hər açarda hər geniş yayılmış simvolun ilk mövqeyini saxlayan cədvəli (bir hərfli
sorğu bir sütundur) və son sorğunun uyğunluqlarını saxlayır (`s`-dən sonra `se` yazmaq yalnız `s`-in
uyğun gəldiklərini yenidən qiymətləndirir). x18n-in 50,000 açar üzrə yan panel axtarışında, hərf-hərf
yazılaraq, eyni nəticələrlə:

| | Sorğu başına | TS ilə müqayisədə |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| İndekslə eyni daraltmanı edən TS | 4.1-5.4 ms | 2x |
| Eyni port, hər açar üçün çağırılmaqla | - | 0.2-0.4x |
| `FuzzyScoreBatch`, standart indeks (4 nüvə) | 5.1 ms | 1.7x |
| `FuzzyScoreIndex` ilə `FuzzyScoreBatch` (napi, 4 nüvə) | 0.45-0.56 ms | **18-22x** |
| Eynisi wasm ilə (bir thread) | 0.95 ms | **11.5x** |

Eyni daraltmanı edən TS-ə qarşı Rust hələ də 7-12x daha sürətlidir (wasm 5x). Qaytarılan indeksləri
adi dövrlə açarlara çevirin: `Array.from(order, i => keys[i])` 20x baha başa gəldi, 0.4 ms.

Hər dil batch-ləri alır və onlar hətta çağırış başına portların uduzduğu yerdə belə orijinalı
ötürlər. 4 nüvədə eyni iş, eyni nəticələr və xətalar (benchmark-lar hər demo qovluğundadır):

| Dil | İş yükü | Orijinal | Çağırış başına port / orijinal | Batch / orijinal |
| --- | --- | ---: | ---: | ---: |
| TS | x18n axtarışı, 50,000 açar | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 string | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 string | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 qarışıq dəyər | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 string | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 string | 43 ms | 0.68x | **3x** |

Kompilyasiya olunmuş orijinallar daha az qazanır: hər element üçün iş onsuz da sürətlidir, buna görə
batch nüvələrin sayı qədər qazanır. Batch crate-ləri yaddaşı mimalloc ilə ayırır: sistem allocator-u
ilə Go batch-i bir thread-dən yavaş idi. Demo: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Altı dildə real kod

Go-nun `path`-i, Ruby-nin `shellwords`-ü, Python-un `colorsys`-i, kiçik fasadların arxasındakı JDK və
glibc davranışı: hər port öz gate-indən keçir, cəmi 13,010 qeydə alınmış hal. Bu işləmələr
rust-anything-də xətaları tapıb düzəltdi (`serde_json` vasitəsilə bir ULP sürüşən float-lar, qeyd
zamanı C çökmələri, tipsiz kodun mənasız girişlər alması). Funksiya başına çağırılanda Ruby portu
Ruby-dən 4.4x, Python portu CPython-dan 1.35x daha sürətli işləyir, Go və Java-nın yarpaq funksiyaları
isə öz dillərində daha sürətli qalır; batch kimi hamısı qazanır (yuxarıdakı cədvələ baxın).
Hesabat: [`docs/real-world-languages.md`](./real-world-languages.md).

## Nümunə: x18n-dən real modul

[x18n](https://github.com/x18n-dev/x18n)-dən `packages/core/src/fuzzy.ts`, [`demo/`](../demo)-da hər
iki üsulla port edilib:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: hazır, wasm-bindgen (core brauzerlərdə işləyir)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# src/port.rs-i yazın
rust-anything gate demo/fuzzy-rs
```

Rust `char` ilə indeksləyən ilk port sadə testlərdən keçdi, amma `diff`-də uğursuz oldu:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS-in `indexOf`-u UTF-16 kod vahidlərini sayır, buna görə emoji iki mövqe tutur. `demo/*/src/port.rs`-dəki
port yaradılmış `utf16` köməkçilərindən istifadə edir və həm napi-rs (`demo/fuzzy-napi`), həm də
wasm-bindgen (`demo/fuzzy-rs`) kimi 2000/2000 haldan və gate-dən keçir.

rust-anything-in bütün x18n üçün yazdığı plan: [`docs/examples/x18n.md`](./examples/x18n.md).

## Quraşdırma

```sh
cargo install --path .
```

`record`, `diff` və `bench` orijinalı öz runtime-ında işə salır: TS üçün Node 22.6+ (`.ts`
mənbələrini birbaşa işlədir), Python və C (ctypes) üçün Python 3.9+, Go 1.21+, Ruby 3+, JDK 17+
(`javac` və `java`). C üçün həmçinin C kompilyatoru lazımdır. wasm körpüləri üçün əlavə olaraq
`rustup target add wasm32-unknown-unknown` və
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked` lazımdır;
dəqiq versiyanı `build` deyir.

Agentlər üçün `rust-anything setup` hər şeyi qeydiyyatdan keçirir (bax Sürətli başlanğıc). Bunun
əvəzinə MCP serveri bir layihəyə əllə əlavə etmək üçün (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` nəyə qərar verir

- Körpüdən keçə bilməyən export-lar səbəbi ilə birlikdə mənbə dildə qalır və shadow modulu orijinalı
  yenidən export edir. TS üçün:
  funksiya qəbul edən və ya qaytaran funksiyalar, generator-lar və iterator-lar, RegExp, `instanceof`
  yoxlamaları, generic-lər və tipləri (import-lar, yenidən export-lar və `extends` boyunca izlənməklə)
  funksiya saxlayan dəyərlər. `--keep "name: reason"` daha çoxunu saxlayır, məsələn `Intl` datasından
  asılı kod.
- TS tipləri Rust tiplərinə uyğunlaşdırılır; type alias-lar import-lar vasitəsilə həll olunur,
  parametr tipləri standart dəyərlərdən müəyyən edilir; strukturlaşdırılmış dəyərlər yaradılmış binary
  wire kimi keçir (JSON yalnız wire-ın modelləşdirmədiyi formalar üçün ehtiyat variantdır).
- JSON `undefined`, NaN, Infinity, -0 və ya tək surrogate-ləri ifadə edə bilmir: strukturlaşdırılmış
  dəyərlər yaradılmış `index.cjs`-in tərcümə etdiyi markerlər (`{"$undefined": true}`,
  `{"$num": "NaN"}`, `{"$utf16": [...]}`) daşıyır, köməkçilər isə crate-in `js.rs` faylındadır.

`record` TS mənbələrini olduğu kimi işə salır: Node resolve hook-u bundler üslublu import-ları izləyir
(`./errors`-dan `./errors.ts`-ə), repozitoriyada quraşdırılmış npm paketi yoxdursa `--resolve-from`
onları təmin edir, transformasiya tələb edən TS (enum-lar, parameter property-lər) isə
`--experimental-transform-types` ilə yenidən sınanır.

## `analyze` nəyə baxır

- Paketlər (`package.json`) və mənbə faylları; `node_modules`, build nəticələri, fixture-lar,
  playground-lar, alət konfiqurasiyaları ötürülür. Vue/Svelte/Astro `<script>` blokları import-lar
  üçün parse edilir.
- **Vahidlər**: mənbə fayllarından ibarət qovluq və ya paketin mənbə kökündəki fayl.
- **Dalğalar**: vahidin import etdikləri daha əvvəlki dalğalarda gəlir; import dövrləri birlikdə port
  edilir.
- **Körpü**: vahid və ya onun import etdiyi hər hansı şey Node tələb edirsə napi-rs; daşına bilən kod
  üçün wasm-bindgen; UI və redaktor kodu üçün JS-də saxla.
- **Hazırlıq** (nə qədər təhlükəsiz) və **prioritet** (təhlükəsiz və dəyərli: dövrlər və string işi, testlər, ölçü).

| Risk | Ciddilik | Nümunə |
| --- | --- | --- |
| String offset-ləri | yüksək | `slice`, `indexOf`, `matchAll`, `d` flag-ı: UTF-16 və UTF-8 |
| Regex sintaksisi | yüksək | lookaround, backreference-lər, `y`: `regex` crate-ində yoxdur |
| Dinamik regex | yüksək | `new RegExp(userPattern)`: iş vaxtı JS sintaksisi |
| Dinamik kod | yüksək | `eval`, `new Function`, hesablanan `import()` |
| Dinamik tipləşdirmə | orta | `any`, `'key' in value` |
| Sıralı kolleksiyalar | orta | `Map`, `Set`, `Object.keys`: əlavə edilmə ardıcıllığı |
| Async, generator-lar | orta | promise və generator sərhədləri |
| Sinif irsiliyi, reflection | orta | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback formalı API-lər | orta | funksiya tipli parametrlər və metodlar: çoxdanışan körpülər |
| Exception-lar, rəqəmlər, JSON | aşağı | `throw`, bit əməliyyatları, `JSON.stringify` ardıcıllığı |

## Layihənin inkişafı

```sh
cargo test                        # unit testlər, fixture repo, record/diff/shadow dövrü (node lazımdır), hər dil üçün app record/replay
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Dizayn qərarları və onların səbəbləri: [DECISIONS.md](../DECISIONS.md).

## Yeniləmə və ya silmə

```sh
cargo install rust-anything                                    # yenilə (Cargo)
npm install -g rust-anything@latest                            # yenilə (npm)
rust-anything setup                                            # agent ayarlarını yenilə
rust-anything setup --remove && cargo uninstall rust-anything  # sil (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # sil (npm)
```

`setup --remove` yalnız rust-anything-in qeydlərini çıxarır; onun saxladığı surətlər
(`<file>.rust-anything.bak`) siz silənə qədər qalır.

## Nəyi tuta bilmir

Keçmək o deməkdir ki, Rust qeydə alınmış hər hala uyğun gəlir, artıq heç nə. Yenidən yazmalarda əsl
problem adətən qeydin xaricində olur, ona görə sərhədlərin harada olduğunu bilin:

- **Heç kimin qeydə almadığı girişlər.** Yaradılmış hallar, tələlər və öz `--inputs`-unuz tavandır.
  Real girişlər əlavə edin (prod nümunələri, xəta hesabatları, orijinalın test fixture-ları); prod-u
  sındıran istifadəçi girişi nadir hallarda generatorun ağlına gələn olur.
- **Regex-lər.** `regex` crate-ində lookaround və backreference yoxdur, hətta kompilyasiya olunan
  pattern belə ASCII olmayan mətndə `\w`, `\b`, `\d` və registrdən asılı olmayan uyğunluğu JS, Python
  və ya Java-dan fərqli emal edə bilər. `fancy-regex`-ə keçmək və ya pattern-i yenidən yazmaq qeydə
  alınmış hər haldan keçib yenə də türk dilindəki nöqtəsiz `ı`-da və ya zero-width joiner-də fərqli
  ola bilər. `record` regex istifadə edən fayldakı hər funksiyaya regex tələləri əlavə edir (bunlar,
  Kelvin işarəsi, uzun s, ərəb-hind rəqəmləri, sətir ayırıcıları, son sigma), amma real
  pattern-lərinizi real mətnə qarşı da fuzz edin.
- **İşləmələr arasında dəyişənlər.** `record` orijinalı iki dəfə işə salır və nəyin fərqləndiyini
  ayırd edir: dəyişən dəyərlər (vaxtlar, id-lər) wildcard-a çevrilir; başqa ardıcıllıqla gələn eyni
  sətirlər (hash map-lər, paralellik) istənilən ardıcıllıqla müqayisə olunur, yəni port yenə də məhz
  həmin sətirləri çıxarmalıdır; fərqli sayda sətir `...` olur və hər şeyə uyğun gəlir. `record` hər
  növü siyahıya alır: hər birinə baxın, çünki hash ardıcıllığı və ya paralellik fərqi portda real
  olaraq dəyişə biləcək şeyin özüdür.
- **Float-lar.** Rəqəmin mətnə formatlanması dillər arasında fərqlidir (`1e21`, `-0`, rəqəmlərin
  sayı). Tələlər bu dəyərləri əhatə edir və onlar tam uyğun gəlməlidir; `--float-tolerance` yalnız
  yuvarlaqlaşdırmanı bağışlayır, formatlamanı heç vaxt.
- **Çıxışda olmayan hər şey.** Vaxt, yaddaş, yük altında paralellik və stdout, stderr, çıxış kodları,
  yazılmış fayllar və HTTP cavablarından başqa yan təsirlər (şəbəkə çağırışları, verilənlər bazaları,
  siqnallar) müqayisə edilmir.
- **Digər platformalar.** Qeyd davranışı yalnız onu işə salan maşında sübut edir. Nəticələri tip
  ölçülərindən, endianness-dən və ya kompilyatordan asılı olan C hədəfdə fərqli davrana bilər;
  `analyze` buna görə də aparatla işləyən C-ni C-də saxlayır.

## Tez-tez verilən suallar

**O, kodumu avtomatik yenidən yazır?** Xeyr. Nəyin köçürüləcəyini tapır, körpünü yaradır, orijinalın
nə etdiyini qeydə alır və Rust-u ona qarşı yoxlayır. Rust-u `port.rs`-də siz və ya agentiniz
yazırsınız; nə vaxt düzgün olduğuna `diff` və `gate` qərar verir.

**Tətbiqimin API-si dəyişəcək?** Xeyr. Çağıranlar eyni funksiyaları import edir (və ya siz əminlik
qazanana qədər hər ikisini işə salıb orijinalın nəticəsini qaytaran shadow modulunu).

**Rust həmişə daha sürətlidir?** Xeyr, rust-anything də bunu deyir. Hər element üçün bir dəfə
çağırılan kiçik funksiya Rust-da çox vaxt daha yavaşdır, çünki hər çağırış körpüdən keçir; V8, JVM və
Go belə funksiyaları nanosaniyələrlə işlədir. `profile` onun ətrafındakı dövrü tapır, `--batch`
bütün dövrü köçürür, `bench` isə buraxmazdan əvvəl hökm verir. numba, Cython və ya JAX ilə artıq
kompilyasiya olunmuş kod da maşın kodu kimi işləyir: `profile` və `analyze` onu işarələyir, çünki onu
port etmək az sürət qazandırır.

**Kodum rəqəmsaldır; float-lar tam uyğun gələcək?** Çox vaxt yox: əməliyyat ardıcıllığı, fused
multiply-add və riyaziyyat kitabxanası kompilyatorlar arasında fərqlənir. `--float-tolerance 1e-9`
ilə qeydə alın (`record` və ya `app record`), float-lar böyük dəyərin bu payı daxilində uyğun gələcək
(1-dən aşağıda mütləq). Tam ədədlər, mətn və struktur yenə də tam uyğun gəlməlidir.

**Yalnız APK, JAR və ya .exe kimi olan tətbiqi port edə bilər?** Xeyr. O, mənbə kodunu port edir:
funksiyaları parse edir, hər birinin nə etdiyini qeydə alır və Rust-u işləyən orijinala qarşı yoxlayır.
Kompilyasiya olunmuş tətbiqdə bunların heç biri yoxdur və `analyze` bunu deyir. Binary-nin görünən
davranışından yeni Rust tətbiqi yazmaq ayrı layihədir.

**Sınaqdan çıxmış C kodunu port etməliyəm?** Çox vaxt yox, `analyze` da harada olduğunu deyir. Aparat
registrlərinə toxunan, kompilyatorun tip ölçülərinə və ya yaddaş düzülüşünə əsaslanan, ya da inline
assembly istifadə edən C (`volatile`, bitfield-lər, packed struct-lar, `__asm__`, ünvana cast edilən
tam ədədlər) "C-də saxla" kimi işarələnir: sizin maşınınızdakı qeyd hədəf barədə heç nə sübut etmir,
stabil drayver və ya firmware kodu isə yenidən yazmaqdan az qazanır. Onun ətrafındakı daşına bilən
məntiq (parse etmə, protokollar, məlumat emalı) yaxşı köçən hissədir.

**Electron tətbiqimi port edə bilər?** Məntiqi, bəli; pəncərələr veb səhifə olaraq qalır. `analyze
--whole-app` Electron-u aşkarlayır və renderer olduğu kimi qalarkən main process-i hissə-hissə
planlaşdırır. UI-ı Tauri-yə (Rust backend üzərində eyni veb UI) köçürmək məntiq Rust olduqdan sonra
ayrıca addımdır.

**Bəs C#, Kotlin və ya Swift?** C# önizləmədədir (bax [Dillər](#dillər)); Kotlin və Swift hələ
dəstəklənmir. Hər dil üçün uçdan-uca test edilmiş parser, recorder, körpü və replay drayveri lazımdır.
Ehtiyacınız olan dil üçün issue açın (və ya mövcud olanına səs verin).

**Rust orijinaldan xeyli böyük olmayacaq?** Olmamalıdır. `gate` portun sətir sayını orijinalınkı ilə
müqayisə edir və 3x-dən yuxarıda (import-lar və imzalar üçün üstəgəl 50 sətir) uğursuz olur: bu
adətən crate-in artıq etdiyini əllə yazmaq və ya halları bir-bir emal etmək deməkdir. `analyze`
istifadə ediləcək crate-ləri siyahıya alır.

**Hissə-hissə port etmək Rust-u köhnə tətbiqin dizaynına bağlamırmı?** Yalnız ikisi yan-yana işlədiyi
müddətdə. Qeydlər davranışı tətbiqin daxili quruluşunda deyil, kənarlarında (CLI-ın çıxışı, serverin
cavabları, modulun export edilən funksiyaları) yoxlayır. Vahidlər hələ körpüdən keçərkən köhnə
strukturu təkrarlayın; `app lift` orijinalı sildikdən sonra Rust-u sərbəst yenidən strukturlaşdırın,
`app replay` davranışı yenə sübut edəcək. Heç nə orijinala geri çağırış da etmir: front door onu ayrı
proses kimi işə salır (və ya HTTP-ni ona yönləndirir), körpülənmiş vahidlər orijinal tərəfindən
çağırılır, əksinə heç vaxt, callback-lər isə mənbə dildə qalır.

**Kodum maşınımdan çıxır?** Xeyr: rust-anything lokal işləyir və kodunuzun heç bir hissəsini heç yerə
göndərmir. Cargo crate-ləri həmişəki kimi yükləyir, agentinizin model provayderi isə agentinizin ona
göndərdiyini öz siyasəti çərçivəsində görür.

**Nə quraşdırılmalıdır?** Rust və port etdiyiniz dilin runtime-ı (bax
[Quraşdırma](#quraşdırma)).

**Nəsə sındı.** Əmri, onun çıxışını və platformanızı göstərərək issue açın.

## Sponsorlar

rust-anything pulsuz və açıq mənbəlidir. Əgər işinizə yarayırsa, lütfən ona sponsorluq etməyi düşünün. Dəstəyiniz inkişafın davam etməsinə kömək edir.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="GitHub-da rust-anything-ə sponsor olun" /></a>
</p>

### Şirkət sponsorları

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Fərdi sponsorlar

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

## Töhfə vermək

Issue-lar və pull request-lər xoş qarşılanır; [CONTRIBUTING.md](../CONTRIBUTING.md) quraşdırmanı,
testlərin harada yerləşdiyini və yeni dilin necə əlavə edildiyini izah edir. Dizayn qərarları və
onların səbəbləri [DECISIONS.md](../DECISIONS.md)-dədir. Real portların nümunə araşdırmaları xüsusilə
xoş qarşılanır. Təhlükəsizlik problemlərini lütfən gizli bildirin ([SECURITY.md](../SECURITY.md)) və
[davranış kodeksinə](../CODE_OF_CONDUCT.md) baxın.

## Lisenziya

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Repozitoriyanızdakı portlar və yaradılmış kod sizindir.
