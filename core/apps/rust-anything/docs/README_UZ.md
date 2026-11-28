<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="Og'zi kod tegidan iborat rust-anything qisqichbaqasi">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">Muallif: <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · Oʻzbekcha · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>
<p align="center"><sub>Bu tarjima hamjamiyat tomonidan yuritiladi va <a href="../README.md">inglizcha README</a>dan ortda qolishi mumkin.</sub></p>

<p align="center"><em>Butun ilovangizni Rust'da qayta yozing. Butun yo'l davomida u ishlab tursin.</em></p>

<p align="center"><em>CLI'lar, serverlar va kutubxonalar, qismma-qism, har qadamda asl nusxa bilan tekshirilgan holda.</em></p>

<p align="center">Node.js va TypeScript · Python · C · Go · Ruby · Java · PHP va C# preview'da</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io versiyasi"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm versiyasi"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 til">
  <a href="#qollab-quvvatlanadigan-agentlar"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 ta agent bilan ishlaydi"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Testlar"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT litsenziyasi"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub yulduzlari"></a>
</p>

<p align="center">20x gacha tezroq · 38,251 ta yozib olingan holat qayta ijro etildi · 0 ta nomuvofiqlik · bitta buyruq</p>

<p align="center">
  <img src="assets/race.gif" alt="x18n'ning 50,000 kalit bo'yicha qidiruviga user.profile yozilmoqda: TypeScript 143 ms sarflaydi, rust-anything batch'i 6.9 ms, har bir tugma bosilganda bir xil natijalar bilan." width="820">
</p>

**Butun ilovangizni Rust'da, qismma-qism qayta yozing.** rust-anything Node.js
(TypeScript/JavaScript), Python, C, Go, Ruby yoki Java ilovangiz bugun nima qilayotganini yozib oladi,
so'ng Rust'da qayta yozilgan har bir qismni keyingisiga o'tishdan oldin shu yozuv bilan tekshiradi,
toki ilova to'liq Rust bo'lguncha. CLI'lar, HTTP serverlar va kutubxonalar; Rust kodini kodlash
agentingiz (yoki o'zingiz) yozadi. U faqat yozuv qamrab olgan narsani ushlay oladi:
[Nimalarni aniqlay olmaydi](#nimalarni-aniqlay-olmaydi) bo'limiga qarang. Faqat sekin qismni
tezlashtirish kerakmi? Faqat uni, bir vaqtda bitta hot path'dan port qiling:

| Haqiqiy ish yuki, asl nusxa bilan bir xil natijalar | Asl nusxa | rust-anything bilan |
| --- | ---: | ---: |
| x18n'ning yon panel qidiruvi, 50,000 kalit (TypeScript, Node) | har so'rovga 10 ms | **0.5 ms: 20x tezroq** |
| Xuddi shu qidiruv brauzerda (wasm, bitta thread) | 10 ms | **0.95 ms: 11.5x** |
| 20,000 string ustida `slugify` (Python) | 98 ms | **17x tezroq** |
| Ruby standart kutubxonasidan `Shellwords.shellescape`, 50,000 qiymat | 88 ms | **11.8x tezroq** |
| 50,000 string ustida `Slugify` (Go) | 49 ms | **4x tezroq** |
| 50,000 string ustida `slugify` (Java) | 43 ms | **3x tezroq** |

4 yadroda o'lchangan; har bir raqamning [`demo/`](../demo) ichida avval natijalar bir xilligini
tekshiradigan benchmark'i bor. Har bir kichik funksiya uchun Rust'ni alohida chaqirish odatda JIT'dan
*sekinroq*; rust-anything ko'chirishga arziydigan siklni topadi va uni ko'chiradi.

> rust-anything mustaqil loyiha bo'lib, Rust Project yoki Rust Foundation bilan bog'liq emas va ular
> tomonidan qo'llab-quvvatlanmaydi. "Rust" Rust Foundation'ning savdo belgisidir.

## Tezkor boshlash

Buni Claude Code, Codex, Cursor yoki Gemini CLI'ga joylashtiring va o'rnatishni agentingizga topshiring:

```text
rust-anything'ni o'rnat: `cargo install rust-anything`, so'ng `rust-anything setup` ni ishga tushir.
Seni qachon qayta ishga tushirishim kerakligini ayt.
```

Yoki o'zingiz:

```sh
cargo install rust-anything   # crates.io'dan
rust-anything setup           # uni Claude Code, Codex, Cursor va Gemini CLI'da ro'yxatdan o'tkazadi
```

Hali Rust toolchain'ingiz yo'qmi? macOS, Linux va Windows uchun tayyor binary fayllar har bir
[GitHub release](https://github.com/erkamyaman/rust-anything/releases)'ga biriktirilgan, JavaScript
loyihalari uchun esa `npm install -g rust-anything` xuddi shu binary'ni o'rnatadi.

Claude Code'da uni plugin sifatida ham o'rnatishingiz mumkin (MCP server va skill; yuqoridagi CLI
`PATH` ichida bo'lishi kerak):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` topgan har bir agentiga MCP serverni qo'shadi va workflow skill'ini agent skill'larni o'qiydigan
joyga o'rnatadi. U boshqa sozlamalaringizni saqlaydi, qayta ishga tushirish xavfsiz, `--remove` esa
qilganlarini bekor qiladi. So'ng agentingizdan, masalan, quyidagilarni so'rang:

- *"Bu CLI'ni rust-anything bilan boshidan oxirigacha Rust'da qayta yoz va u xuddi shunday ishlashini isbotla."*
- *"Bu qidiruv sekin tuyulyapti. rust-anything bilan profilini ol va issiq siklni Rust'ga ko'chir."*
- *"`src/parser/` ni rust-anything bilan Rust'ga ko'chirishni rejalashtir; birinchi birlikni port qil va isbotla."*
- *"`rust/text-rs` dagi Rust portini asl nusxaga qarshi benchmark qil va uni chiqarish kerakmi, ayt."*

### Qo'llab-quvvatlanadigan agentlar

| Agent | `rust-anything setup` qo'shadi |
| --- | --- |
| Claude Code | `~/.claude.json` da MCP server, `~/.claude/skills/` da skill |
| Codex | `~/.codex/config.toml` da MCP server, `~/.codex/skills/` da skill |
| Cursor | `~/.cursor/mcp.json` da MCP server |
| Gemini CLI | `~/.gemini/settings.json` da MCP server |
| Istalgan boshqa MCP mijozi | `rust-anything mcp` ni qo'lda stdio server sifatida qo'shing ([O'rnatish](#ornatish) ga qarang) |

Mavjud faylni o'zgartirishdan oldin `setup` uning yoniga nusxasini saqlaydi (`<file>.rust-anything.bak`).

Yoki qadamlarni o'zingiz bajaring:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile sikl ichida fuzzyScore'ni topadi, bridge --batch Rust crate'ini yaratadi, gate 2000/2000 yozib olingan holat bilan o'tadi va benchmark TS'dan 20.7x tezroq ekanini ko'rsatadi." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # nima issiq va uni kim chaqiradi
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# src/port.rs ni yozing (yoki agentingizga yozdiring), so'ng:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # har bir yozib olingan holat mos kelishi kerak
rust-anything bench rust/fuzzy-rs                      # tezroqmi? hukm aytadi
rust-anything gate rust/fuzzy-rs                       # tayyor degani, bu o'tadi degani
```

rust-anything kodni tarjima qilmaydi: Rust'ni kodlash agentingiz (Claude Code, Codex, Cursor, ...)
yoki o'zingiz yozasiz. rust-anything agent ishonchli taxmin qila olmaydigan narsalarni beradi: vaqt
qayerga ketayotganini, avval nimani va qanday tartibda port qilishni, kodning qolgan qismi Rust'ni
API'si o'zgarmagan holda chaqirishi uchun ko'prikni (bridge), port mos kelishi shart bo'lgan aniq
xatti-harakatni, uni chiqarishning xavfsiz yo'lini va port qachon tayyor ekanini aytadigan gate'ni.

## Tillar

| Til | Birlik | Ko'prik | Yozib oluvchi va qayta ijro etuvchi |
| --- | --- | --- | --- |
| TypeScript/JavaScript | papka yoki fayl | generatsiya qilingan binary wire bilan napi-rs yoki wasm-bindgen; klasslar va async ham | `.ts` manbalarini ishga tushiradigan Node |
| Python | paket yoki modul | PyO3 (abi3), to'g'ridan-to'g'ri konvertatsiya, tiplangan exception'lar | asl nusxani import qiladigan Python |
| C | `.c` fayl | asl nomlar bilan `extern "C"` funksiyalar va header | umumiy kutubxona sifatida kompilyatsiya qilingan asl nusxa, ctypes orqali chaqiriladi, har bir holat uchun bitta fork |
| Go | paket | asl API'li paketda tiplangan cgo chaqiruvlari va generatsiya qilingan binary wire | o'z moduli sifatida build qilinadigan generatsiya qilingan Go drayveri |
| Ruby | modul funksiyalaridan iborat fayl yoki papka | asl modullar ostida magnus kengaytmasi | generatsiya qilingan Ruby drayveri |
| Java | `public static` metodlardan iborat paket | asl metodlarga ega wrapper klasslarda tiplangan JNI va generatsiya qilingan binary wire | generatsiya qilingan reflection drayveri |
| PHP (preview) | funksiyalar va `public static` metodlardan iborat papka | navbatda: C ABI orqali PHP FFI | bugun butun ilovalar: CLI'lar va serverlar (`php -S`) uchun `app record`, `app replay` va front door |
| C# (preview) | `public static` metodlardan iborat papka | navbatda: C ABI orqali P/Invoke | bugun butun ilovalar: CLI'lar va ASP.NET serverlari (`dotnet <app>.dll`) uchun `app record`, `app replay` va front door |

C'dan tashqari har bir til batch klasslarini ham oladi (`--batch`): elementlar ko'prikdan bir marta
o'tadi va Rust'da qoladi, har bir chaqiruv esa barcha yadrolarda ularning hammasi ustida ishlaydi.

Til repozitoriydan aniqlanadi (`go.mod`, `pom.xml`, `.csproj` yoki `.sln`, `pyproject.toml`,
`Gemfile`, `composer.json`, `package.json`, aks holda eng ko'p uchraydigan manba fayllari); `--lang`
buni almashtiradi. Tiplar manbadan olinadi: TS tiplari, Python type hint'lari, C, Go, Java va C#
signaturalari, Ruby YARD teglari, PHP tiplari va phpdoc; son sifatida ishlatilgan tipsiz parametrlar
son deb aniqlanadi.

PHP preview'da: `analyze` PHP ilovasini rejalashtiradi (Composer paketlari va PSR-4 autoloading,
erkin taqqoslash va butun sonning float'ga to'lib o'tishi kabi xavflar, crate'larga moslangan Composer
paketlari), PHP CLI yoki serverini esa yozib olish, qayta ijro etish va Rust front door'i ortiga qo'yish
mumkin. Uning birliklarini PHP FFI orqali Rust'ga port qilish keyingi qadam
([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# ham xuddi shunday preview'da: `analyze` `.csproj` loyihalarini va ularning NuGet paketlarini
o'qiydi (crate'larga moslangan), `using` direktivalarini papkalarga bog'laydi va C# boshqacha
qiladigan narsalarni belgilaydi (`decimal`, `dynamic`, LINQ'ning kechiktirilgan so'rovlari, `Task`,
`lock`, reflection). C# CLI yoki ASP.NET serverini yozib olish, qayta ijro etish va Rust front door'i
ortiga qo'yish mumkin; birliklarni P/Invoke orqali port qilish navbatda.

## Qanday ishlaydi

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 vaqt        avval       Rust       asl nusxa   siz yoki    har bir   tezroqmi?  prod'da     tayyor
 qayerga     nimani      crate va   nima        agentingiz  yozib     hukm       ikkalasi    degani,
 ketadi      port qilish wrapper    qiladi      yozadi      olingan              yonma-yon   bu o'tadi
                                                            holat
```

Asl nusxa haqiqat manbai bo'lib qoladi: `record` uni chegaraviy holatlar (va o'zingizning
kiritmalaringiz) bilan ishga tushiradi va nima qaytarganini yoki qanday xato otganini saqlaydi;
`diff` har bir holatni Rust'ga qarshi qayta ijro etadi; hammasi mos kelib, `gate` o'tmaguncha hech
narsa chiqarilmaydi. Chaqiruvchilar butun jarayon davomida asl API'dan foydalanishda davom etadi.

Butun ilova ham xuddi shu sikldan birlikma-birlik o'tadi, butun dasturni isbotlaydigan ramka ichida
([Butun ilovani port qilish](#butun-ilovani-port-qilish)):

```
analyze --whole-app ──> app record ──> app front-door ──> har bir birlik: yuqoridagi sikl, so'ng app wire ──> app lift
 tuzilma, har bir        ilova tashqa-  kirish nuqtasi     gate o'tadi, birlik Rust'da javob beradi:        sof Rust,
 bog'liqlik, qabul       ridan nima     Rust'da; asl       replay 100%, fallback ulushi kamayadi            replay bilan
 qilinadigan qarorlar    qiladi         nusxa javob beradi                                                  isbotlangan
```

## Sikl

| Qadam | Buyruq | Nima qiladi |
| --- | --- | --- |
| 0. Profil | `rust-anything profile <repo> -- node bench.mjs` | Haqiqiy ish yukini tilning profiler'i ostida ishga tushiradi (node, cProfile, `go test` pprof, JFR, Ruby tracer): umumiy vaqt bo'yicha issiq funksiyalar, ularni chaqiruvchilar va qaysi sikllarni batch qilish kerakligi; allaqachon kompilyatsiya qilingan kodni (numba, Cython, JAX) belgilaydi, chunki u yerda Rust kam foyda beradi |
| 1. Reja | `rust-anything analyze <repo>` | Birliklar, port tartibi, `file:line` bilan xavflar, har bir birlik uchun ko'prik, bog'liqlik va crate mosligi, eng yaxshi birinchi portlar; `--whole-app` kirish nuqtalari va tuzilmani, crate'i bilan har bir bog'liqlikni (import qilingan yoki e'lon qilingan), qismlarni (bir-birini import qiladigan birliklar birga ko'chadi) va tavsiya etilgan javobli raqamlangan qarorlarni qo'shadi |
| 2. Ko'prik | `rust-anything bridge <repo> <unit>` | Binding'lar bilan crate (`lib.rs` hamda manba til yuklaydigan wrapper) va port qilinadigan stub'lar (`port.rs`); `--batch fn:param` ko'plab `param` qiymatlarini Rust'da saqlaydigan klass qo'shadi |
| 3. Yozib olish | `rust-anything record <crate>` | Asl nusxani generatsiya qilingan chegaraviy holatlar (ASCII bo'lmagan, emoji, `-0`, `NaN`, float kutilgan joyda int, ...) va har bir parametrdagi har bir semantik tuzoq (string uzunligi va registri, ishorali bo'lish, to'lib ketish chegaralari, float chop etish, map va saralash tartibi) bilan ishga tushiradi va `cases.jsonl` ni saqlaydi; `--float-tolerance 1e-9` sonli kod uchun float'larning shu ulush ichida mos kelishiga ruxsat beradi |
| 3. Build | `rust-anything build <crate>` | Rust tomonini build qiladi: `.node`, wasm paketi, Python kengaytmasi yoki umumiy kutubxona |
| 3. Diff | `rust-anything diff <crate>` | Yozib olingan holatlarni Rust'ga qarshi, asl nusxani chaqiruvchilar qanday chaqirsa shunday qayta ijro etadi; nomuvofiqliklarni sanab beradi |
| 3. Bench | `rust-anything bench <crate>` | Yozib olingan holatlarning asl nusxada va Rust'da, ko'prik bilan birga, vaqtini o'lchaydi |
| 4. Shadow | `rust-anything shadow <crate>` | Ikkalasini ishga tushiradigan, asl nusxa natijasini qaytaradigan va nomuvofiqliklarni xabar qiladigan drop-in; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, testlar, `unsafe` auditi, port qilinmagan narsa qolmagani, asl nusxaning har bir xato yo'li uchun yozib olingan muvaffaqiyatsiz holat, asl nusxa xato qaytaradigan joyda `unwrap`/`expect`/`panic!` yo'qligi (`// INFALLIBLE: <why>` bilan belgilanmagan bo'lsa), build, API, xatti-harakat |
| Agentlar | `rust-anything setup` | MCP serverni (`rust-anything mcp`, har bir qadam alohida tool sifatida) va workflow skill'ini ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) kodlash agentlaringizda ro'yxatdan o'tkazadi |

## Butun ilovani port qilish

Maqsad asl nusxa kabi ishlaydigan, asl nusxa esa namuna sifatida saqlanadigan sof Rust ilovasi.
Rust'ni agentingiz yozadi; rust-anything ishni tartiblaydi, skeletini quradi va har bir qadamni
isbotlaydi. [Whole-app skill'i](../skills/rust-anything/whole-app.md) agentni bu jarayondan olib
o'tadi va faqat siz qabul qila oladigan qarorlardan boshlaydi:

- **So'roq (grilling)**: agent port bog'liq bo'lgan har bir qaror hal bo'lmaguncha raundlarda, har
  bir savolni tavsiya etilgan javobi bilan so'raydi va har birini `rust/DECISIONS.md` ga ADR sifatida
  yozadi; `rust/GLOSSARY.md` esa asl nusxa atamalarini Rust nomlariga moslaydi.
- **Tadqiqot**: fon agentlari har bir bog'liqlikning birlamchi manbalarini o'qiydi va topgan har bir
  semantik tuzoqlari bilan `rust/research/<topic>.md` ni yozadi.
- **Sessiyalar orasida**: `rust/MAP.md` har bir birlikni holati bilan sanab beradi; sessiya boshlanishidan
  oldin bitta birlikni egallaydi va har bir nazorat nuqtasi keyingi sessiya uchun `rust/HANDOFF.md`
  qoldiradi. Bitta to'lqindagi birliklarni subagent'lar parallel port qilishi mumkin.
- **O'tish (cutover)**: agent qo'lidan kelganini qiladi va faqat siz bajara oladigan qadamlar
  (deploy'lar, DNS, secret'lar) uchun har bir qadamda orqaga qaytish yo'li bor interaktiv skript,
  `rust/cutover.sh` ni yozadi.

So'roq, tadqiqot va bu amaliyotlar
[Matt Pocock'ning skill'laridan](https://github.com/mattpocock/skills) moslashtirilgan.

Avval rejalashtiring: `rust-anything analyze . --whole-app` ilovaning tuzilmasini (CLI, server yoki
kutubxona) va kirish nuqtalarini, Rust crate'i va mosligi bilan har bir tashqi bog'liqlikni (import
qilingan yoki e'lon qilingan), qismlar ko'rinishidagi port tartibini (bir-birini import qiladigan
birliklar birga ko'chadi) va tavsiya etilgan javobli raqamlangan qarorlarni qo'shadi: saqlanadigan
birliklar, bloklangan birliklar, crate'i yo'q yoki qisman bo'lgan bog'liqliklar.

So'ng butun dasturni tashqaridan isbotlang. `record` va `diff` bitta birlikni isbotlaydi; `app record`
va `app replay` esa ilovani, olti tilning istalganidagi CLI'lar va serverlar uchun isbotlaydi
(ilova qora quti hisoblanadi):

```sh
rust-anything app record . -- python3 cli.py          # asl nusxani ishga tushiradigan buyruq
rust-anything app replay .                            # asl nusxa 100% o'tishi kerak
rust-anything app replay . --build "target/release/mytool"
```

- `app record` asl nusxani ilovaning o'z hujjatlashtirilgan misollari (Markdown va shell fayllaridagi
  `$ mytool ...` qatorlari, ular nomlagan fayllar bilan), `--inputs` JSONL fayli
  (`{"name", "args", "stdin", "env", "files"}`) va shu holatlardan kelib chiqqan semantik tuzoqlar
  (ASCII bo'lmagan va emoji string'lar, manfiy bo'lish va modul, to'lib ketish, juda katta va juda
  kichik float'lar, map tartibi, yo'q fayllar) bilan ishga tushiradi. Har bir holat ikki marta
  ishlaydi; ikki ishga tushirish orasida farq qilgan narsa `[..]` wildcard'iga aylanadi.
  `--normalize timestamps|uuids|key-order` yoki `--normalize name=regex` holatlar bilan birga
  saqlanadigan normalizer'lar qo'shadi.
- Holatlar `rust/app-cases/` dagi [trycmd](https://docs.rs/trycmd) fayllaridir: `<case>.toml` (argv,
  env, chiqish kodi), `.stdin`, `.stdout`, `.stderr`, `.in/` (kiruvchi fayllar) va `.out/` (yozilgan
  fayllar). Ularni qo'lda o'qing va tahrirlang; port binary'ga ega bo'lgach, Rust testi ularni
  `trycmd` bilan ishga tushira oladi.
- `app replay` istalgan build'ni holatlarga qarshi ishga tushiradi, `passed/total` ni chiqaradi, har
  bir muvaffaqiyatsiz holat uchun diff bilan `rust/app-cases/replay-report.md` ni yozadi va har qanday
  nomuvofiqlikda noldan farqli kod bilan chiqadi. `RUST_ANYTHING_FALLBACK_LOG` nomlagan faylga
  yozuv qo'shadigan build (asl nusxaga har bir fallback uchun bitta qator), quyidagi front door kabi,
  o'zining fallback ulushini ham hisobotda oladi.
- `app replay --case <name>` hisobot bergan nom bo'yicha bitta holatni qayta ishga tushiradi: hammasini
  qayta ishga tushirishdan oldin nomuvofiqlikni tuzatish uchun tez, takrorlanadigan sikl.

So'ng kirish nuqtasini Rust'ga ko'chiring va buyruqlarni unga birlikma-birlik topshiring:

```sh
rust-anything app front-door .                            # rust/app: har bir buyruq asl nusxani ishga tushiradi
rust-anything app wire . textkit --command upper          # textkit-rs gate'dan o'tgandan keyin
# bog'lovchi kodni rust/app/src/units/textkit.rs ga yozing, so'ng:
rust-anything app wire . textkit                          # yana 100%, fallback ulushi pastroq
```

- `app front-door` `rust/app` skeletini quradi: ilova nomi bilan atalgan Rust binary'si; yozib
  olingan holatlardagi buyruqlar va flag'lar uchun clap parser, bunda har bir buyruq asl nusxani
  xuddi shu argv, stdin va muhit bilan ishga tushiradi, uning chiqishi va chiqish kodini o'zgarishsiz
  uzatadi. Har bir fallback sanaladi, shuning uchun yangi front door'ni qayta ijro etish 100% fallback
  bilan 100% o'tish beradi (buni ko'rsatish uchun u build qiladi va qayta ijro etadi). U `rust/app`
  ustiga hech qachon yozmaydi: shu paytdan kod sizniki.
- `app wire <repo> <unit> --command <name>` birlik crate'ida `gate` ni ishga tushiradi (hozirgina
  o'tgan bo'lsa `--skip-gate`), uni `rust/app` ga kutubxona sifatida qo'shadi, siz yoki agentingiz
  to'ldirishi uchun `src/units/<unit>.rs` ni bir marta yozadi (argumentlarni parse qiling,
  `<crate>::port` ni chaqiring, asl nusxa chop etganini chop eting), buyruqlarni unga yo'naltiradi, so'ng
  build qiladi va qayta ijro etadi. `RUST_ANYTHING_UNIT_<NAME>=original` ulangan birlikni lift'gacha
  asl nusxaga qaytarib yuboradi.

Hech qanday buyruq nomi bo'lmagan argv uchun (argumentsiz chaqiruv, noma'lum buyruqlar, foydalanish
xatolari) ilovaning o'z nomini buyruq sifatida ulang (`--command mytool`).

Replay fallback ulushi 0 bilan o'tganda va har bir birlik gate'dan o'tganda, uni sof Rust ilovasiga
aylantiring:

```sh
rust-anything app lift .
```

- `app lift` ikkala shart bajarilmaguncha rad etadi va nima to'sqinlik qilayotganini aytadi: hali ham
  fallback'ga tushayotgan holatlar, hali stub bo'lgan bog'lovchi kod, gate'dan o'tmagan birliklar.
- Avval nusxada fallback yo'lini va kill switch'larni olib tashlaydi, har bir birlik crate'ini
  `rust/app` ning oddiy kutubxonasiga aylantiradi (`cdylib`, binding'lar yoki generatsiya qilingan
  wrapper'larsiz) va `cargo test` paytida `rust/app-cases` ni trycmd bilan ishga tushiradigan
  `rust/app/tests/app_cases.rs` ni qo'shadi, shunda CI'ga cargo'dan boshqa hech narsa kerak bo'lmaydi.
- So'ng lift tekshiruv ro'yxatini bajaradi: har bir birlikda va `rust/app` da fmt, clippy
  `-D warnings` va testlar; `rust/DECISIONS.md` da nomlangan har bir target o'rnatilgan joyda build
  yoki tekshirilishi; ish vaqtida o'qiladigan fayllar va embed qilinmagan asset papkalari; hamda sof
  binary ustida replay. O'zgarishlar faqat bularning hammasi o'tgandagina qayta yoziladi. Asl nusxaga
  hech qachon tegilmaydi.

### Serverlar

Xuddi shu buyruqlar HTTP serverlarni ham isbotlaydi. `--http` buyruq server ishga tushirishini
bildiradi; u portni `PORT` dan yoki buyruqdagi `{port}` dan oladi (har doim bir xil portni
tinglaydigan server uchun `--port`):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: har bir route proxy qilinadi
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- So'rovlar ilova hujjatlaridagi `curl` qatorlaridan (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs` dan (`{"name", "method", "path", "headers", "body"}`) va tuzoqlardan olinadi: path
  segmentlari va query qiymatlari CLI argumentlari bilan bir xil tuzoqlarga almashtiriladi, body'lar
  matn va JSON tuzoqlariga, qo'shimcha ravishda bitta noma'lum route. Har bir ishga tushirish serverni
  yangidan boshlaydi va so'rovlarni nom tartibida yuboradi, shuning uchun so'rovlar orasidagi holat
  saqlanadi.
- Holatlar `rust/app-cases/http/<case>.toml` (so'rov, status va muhim header'lar) va `<case>.body`
  fayllaridir (javob tanasi, ikki ishga tushirish farq qilgan joylarda `[..]` bilan). Date, server va
  javobga xos boshqa header'lar chiqarib tashlanadi; sizga ahamiyatsiz har qanday header qatorini
  o'chiring.
- Front door asl nusxani o'zining alohida portida ishga tushiradigan va hech bir birlik javob
  bermaydigan har bir route'ni proxy qiladigan axum serveridir. `wire --route` axum route'larini qabul
  qiladi: `METHOD /path/{param}`, istalgan metod uchun `/path`, qolgan hamma narsa uchun `*`; bog'lovchi
  kod route'ni, uning parametrlarini va so'rovni oladi. `lift` proxy'ni olib tashlaydi; shundan so'ng
  HTTP holatlari CI'da `app replay` bilan ishlaydi.

### Kutubxonalar

Kutubxonada qayta ijro etiladigan jarayon yo'q: uning public API'si front door, har bir birlikning
yozib olingan holatlari esa isbotdir.

```sh
rust-anything app front-door .        # rust/app: public API'ga ega Rust crate'i
# har bir birlik sikldan o'tadi: bridge, record, port.rs, build, diff, gate; so'ng:
rust-anything app wire . textkit-rs   # rust/app'dan qayta eksport qilinadi; asl nusxa uning shadow'ini import qiladi
rust-anything app replay .            # har bir ulangan birlik holatlari; fallback = hali asl nusxadagi eksportlar
rust-anything app lift .
```

- `app front-door` repozitoriyda `main` va server bo'lmaganda (aks holda `--library`) public API'ni
  (har bir birlikning eksportlarini) topadi va `rust/app` ni kutubxona crate'i sifatida quradi. Har bir
  ulangan birlik uning moduliga aylanadi: `pub use textkit_rs::port as textkit;`.
- `app wire` `bridge` yaratgan crate'ni oladi, `gate` ni ishga tushiradi va birlikning shadow
  drop-in'ini yozadi: asl paket birlik o'rniga uni import qiladi, shunda uni chaqiruvchilar asl API'ni
  saqlab qoladi va Rust'ga yetib boradi. `RUST_ANYTHING_UNIT_<NAME>=original` birlikni qaytarib
  yuboradi (C: shadow flag'larisiz build qiling).
- `app replay` har bir ulangan birlikning yozib olingan holatlarini uning binding'lari orqali ishga
  tushiradi. Fallback ulushi Rust hali javob bermaydigan public eksportlar ulushidir: ulanmagan
  birliklar va `bridge` manba tilda qoldiradigan eksportlar.
- `app lift` fallback 0 bo'lishini va har bir birlik `gate` dan o'tishini talab qiladi; birliklardan
  binding'lar, wrapper'lar va shadow'larni olib tashlaydi va `rust/app` ni bitta sof Rust kutubxonasi
  sifatida qoldiradi. U hech qaysi `port.rs` ga tegmaydi, shuning uchun binding'lar orqali mos kelgan
  holatlar uni hali ham tavsiflaydi; tekshiruv ro'yxati asl nusxaning hali ham shadow'larni import
  qiladigan fayllari haqida ogohlantiradi.

Beshalasi ham MCP tool'laridir: `app_record`, `app_replay`, `app_front_door`, `app_wire` va
`app_lift`.

## Amaliy misol: x18n yadrosi

x18n yadrosining API o'zgarishisiz ko'chirilishi mumkin bo'lgan barcha 29 funksiyasi rust-anything
bilan port qilindi: har bir gate o'tadi va 7,925 ta yozib olingan holat aynan mos keladi. So'ng
`rust-anything bench` JS'dan chaqirilganda portlar TS'dan sekinroq ekanini ko'rsatdi, chunki
ko'prikning narxi bajariladigan ishdan qimmatroq. To'liq hisobot:
[`demo/x18n-core`](../demo/x18n-core/README.md). Saboq vositaning o'ziga kiritilgan: portni
chiqarishdan oldin `bench` bilan o'lchang.

## Hot path'lar: ma'lumotni Rust'da saqlang

Har bir element uchun bir marta chaqiriladigan port ko'prik narxini ham har bir element uchun to'laydi
va JIT'ga yutqazadi. Yutadigan narsa siklni ko'chirish: `profile` uni topadi, `--batch` esa
elementlarni bir marta qabul qiladigan va har bir chaqiruvda funksiyani ularning hammasi ustida,
barcha yadrolarda ishga tushiradigan, natijalarni typed array sifatida qaytaradigan klass yaratadi.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: ishning to'rtdan biri, `matched` tomonidan har bir kalit uchun chaqiriladi: batch qiling
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // bir marta
const order = search.rank(query, 0)               // har bir tugma bosilganda: indekslar, eng yaxshisi birinchi
```

`port.rs` dagi `FuzzyScoreIndex` struct'i standart siklni elementlarni bir marta tayyorlaydigan va
o'zi saralay oladigan (`rank`) sikl bilan almashtiradi: u kalitlarni har biriga belgi maskasi bilan
kichik harfga o'tkazilgan holda, har bir kalitda har bir keng tarqalgan belgining birinchi o'rnini
saqlaydigan jadvalni (bir harfli so'rov bitta ustun bo'ladi) va oxirgi so'rovning mosliklarini saqlaydi
(`s` dan keyin `se` yozish faqat `s` mos kelganlarni qayta baholaydi). x18n'ning 50,000 kalit bo'yicha
yon panel qidiruvida, harfma-harf yozilganda, bir xil natijalar bilan:

| | Har so'rovga | TS'ga nisbatan |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| Indeks kabi toraytirishni bajaradigan TS | 4.1-5.4 ms | 2x |
| Xuddi shu port, har bir kalit uchun chaqirilganda | - | 0.2-0.4x |
| `FuzzyScoreBatch`, standart indeks (4 yadro) | 5.1 ms | 1.7x |
| `FuzzyScoreIndex` bilan `FuzzyScoreBatch` (napi, 4 yadro) | 0.45-0.56 ms | **18-22x** |
| Xuddi shunisi wasm bilan (bitta thread) | 0.95 ms | **11.5x** |

Xuddi shunday toraytirishni bajaradigan TS'ga qarshi ham Rust hali 7-12x tezroq (wasm 5x). Qaytarilgan
indekslarni oddiy sikl bilan kalitlarga aylantiring: `Array.from(order, i => keys[i])` 20x qimmatroq
tushdi, 0.4 ms.

Har bir til batch'larni oladi va ular hatto chaqiruv bo'yicha portlar yutqazadigan joyda ham asl
nusxadan o'zib ketadi. 4 yadroda bir xil ish, bir xil natijalar va xatolar (benchmark'lar har bir demo
papkasida):

| Til | Ish yuki | Asl nusxa | Chaqiruv bo'yicha port / asl nusxa | Batch / asl nusxa |
| --- | --- | ---: | ---: | ---: |
| TS | x18n qidiruvi, 50,000 kalit | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 string | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 string | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 aralash qiymat | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 string | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 string | 43 ms | 0.68x | **3x** |

Kompilyatsiya qilingan asl nusxalar kamroq yutadi: har bir element uchun ish allaqachon tez, shuning
uchun batch yadrolar soni qadar yutadi. Batch crate'lari xotirani mimalloc bilan ajratadi: tizim
allocator'i bilan Go batch'i bitta thread'dan sekinroq edi. Demo:
[`demo/x18n-search`](../demo/x18n-search/README.md).

## Olti tilda haqiqiy kod

Go'ning `path`'i, Ruby'ning `shellwords`'i, Python'ning `colorsys`'i, kichik fasadlar ortidagi JDK va
glibc xatti-harakati: har bir port o'z gate'idan o'tadi, jami 13,010 ta yozib olingan holat. Bu
ishga tushirishlar rust-anything'dagi xatolarni topib tuzatdi (`serde_json` orqali bir ULP'ga siljigan
float'lar, yozib olish paytidagi C qulashlari, tipsiz kodga ma'nosiz kiritmalar berilishi). Funksiya
bo'yicha chaqirilganda Ruby porti Ruby'dan 4.4x, Python porti CPython'dan 1.35x tezroq ishlaydi, Go va
Java'ning barg funksiyalari esa o'z tilida tezroq qoladi; batch sifatida hammasi yutadi (yuqoridagi
jadvalga qarang). Hisobot: [`docs/real-world-languages.md`](./real-world-languages.md).

## Misol: x18n'dan haqiqiy modul

[x18n](https://github.com/x18n-dev/x18n)'dan `packages/core/src/fuzzy.ts`, [`demo/`](../demo) ichida
ikkala usulda ham port qilingan:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: tayyor, wasm-bindgen (core brauzerlarda ishlaydi)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# src/port.rs ni yozing
rust-anything gate demo/fuzzy-rs
```

Rust `char` bo'yicha indekslagan birinchi port oddiy testlardan o'tdi, ammo `diff` da muvaffaqiyatsiz
bo'ldi:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS'dagi `indexOf` UTF-16 kod birliklarini sanaydi, shuning uchun emoji ikki o'rinni egallaydi.
`demo/*/src/port.rs` dagi port generatsiya qilingan `utf16` yordamchilaridan foydalanadi va napi-rs
(`demo/fuzzy-napi`) hamda wasm-bindgen (`demo/fuzzy-rs`) sifatida 2000/2000 holatdan va gate'dan o'tadi.

rust-anything butun x18n uchun yozgan reja: [`docs/examples/x18n.md`](./examples/x18n.md).

## O'rnatish

```sh
cargo install --path .
```

`record`, `diff` va `bench` asl nusxani uning o'z runtime'ida ishga tushiradi: TS uchun Node 22.6+
(`.ts` manbalarini to'g'ridan-to'g'ri ishga tushiradi), Python va C (ctypes) uchun Python 3.9+,
Go 1.21+, Ruby 3+, JDK 17+ (`javac` va `java`). C uchun yana C kompilyatori kerak. wasm ko'priklari
uchun qo'shimcha ravishda `rustup target add wasm32-unknown-unknown` va
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked` kerak;
aniq versiyani `build` aytadi.

Agentlar uchun `rust-anything setup` hamma narsani ro'yxatdan o'tkazadi (Tezkor boshlash'ga qarang).
Buning o'rniga MCP serverni bitta loyihaga qo'lda qo'shish uchun (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` nimani hal qiladi

- Ko'prikdan o'ta olmaydigan eksportlar sababi bilan birga manba tilda qoladi va shadow moduli asl
  nusxani qayta eksport qiladi. TS uchun:
  funksiya qabul qiladigan yoki qaytaradigan funksiyalar, generator'lar va iterator'lar, RegExp,
  `instanceof` tekshiruvlari, generic'lar va tiplari (import'lar, qayta eksportlar va `extends` orqali
  kuzatilganda) funksiya saqlaydigan qiymatlar. `--keep "name: reason"` ko'proq narsani qoldiradi,
  masalan `Intl` ma'lumotlariga bog'liq kodni.
- TS tiplari Rust tiplariga moslanadi; type alias'lar import'lar orqali aniqlanadi, parametr tiplari
  standart qiymatlardan chiqariladi; tuzilmali qiymatlar generatsiya qilingan binary wire sifatida
  o'tadi (JSON faqat wire modellashtirmaydigan shakllar uchun zaxira variant).
- JSON `undefined`, NaN, Infinity, -0 yoki yolg'iz surrogate'larni ifodalay olmaydi: tuzilmali
  qiymatlar generatsiya qilingan `index.cjs` tarjima qiladigan markerlarni (`{"$undefined": true}`,
  `{"$num": "NaN"}`, `{"$utf16": [...]}`) olib yuradi, yordamchilar esa crate'ning `js.rs` faylida.

`record` TS manbalarini qanday bo'lsa shunday ishga tushiradi: Node resolve hook'i bundler uslubidagi
import'larni kuzatadi (`./errors` dan `./errors.ts` ga), repozitoriyda o'rnatilgan npm paketlari
bo'lmasa `--resolve-from` ularni taqdim etadi, transformatsiya talab qiladigan TS (enum'lar,
parameter property'lar) esa `--experimental-transform-types` bilan qayta urinib ko'riladi.

## `analyze` nimalarga qaraydi

- Paketlar (`package.json`) va manba fayllari; `node_modules`, build natijalari, fixture'lar,
  playground'lar, tool konfiguratsiyalari o'tkazib yuboriladi. Vue/Svelte/Astro `<script>` bloklari
  import'lar uchun parse qilinadi.
- **Birliklar**: manba fayllaridan iborat papka yoki paketning manba ildizidagi fayl.
- **To'lqinlar**: birlik import qiladigan narsalar oldingi to'lqinlarda keladi; import sikllari birga
  port qilinadi.
- **Ko'prik**: birlik yoki u import qiladigan biror narsa Node talab qilsa napi-rs; ko'chma kod uchun
  wasm-bindgen; UI va muharrir kodi uchun JS'da qoldiriladi.
- **Tayyorlik** (qanchalik xavfsiz) va **ustuvorlik** (xavfsiz va arziydi: sikllar va string ishi, testlar, hajm).

| Xavf | Jiddiylik | Misol |
| --- | --- | --- |
| String offset'lari | yuqori | `slice`, `indexOf`, `matchAll`, `d` flag'i: UTF-16 va UTF-8 |
| Regex sintaksisi | yuqori | lookaround, backreference'lar, `y`: `regex` crate'ida yo'q |
| Dinamik regex | yuqori | `new RegExp(userPattern)`: ish vaqtidagi JS sintaksisi |
| Dinamik kod | yuqori | `eval`, `new Function`, hisoblangan `import()` |
| Dinamik tiplash | o'rta | `any`, `'key' in value` |
| Tartiblangan kolleksiyalar | o'rta | `Map`, `Set`, `Object.keys`: qo'shilish tartibi |
| Async, generator'lar | o'rta | promise va generator chegaralari |
| Klass merosi, reflection | o'rta | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback shaklidagi API'lar | o'rta | funksiya tipidagi parametrlar va metodlar: sergap ko'priklar |
| Exception'lar, sonlar, JSON | past | `throw`, bit amallari, `JSON.stringify` tartibi |

## Ishlab chiqish

```sh
cargo test                        # unit testlar, fixture repo, record/diff/shadow sikli (node kerak), har bir til uchun app record/replay
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Dizayn qarorlari va ularning sabablari: [DECISIONS.md](../DECISIONS.md).

## Yangilash yoki o'chirish

```sh
cargo install rust-anything                                    # yangilash (Cargo)
npm install -g rust-anything@latest                            # yangilash (npm)
rust-anything setup                                            # agent sozlamalarini yangilash
rust-anything setup --remove && cargo uninstall rust-anything  # o'chirish (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # o'chirish (npm)
```

`setup --remove` faqat rust-anything yozuvlarini olib tashlaydi; u saqlagan nusxalar
(`<file>.rust-anything.bak`) siz o'chirmaguningizcha qoladi.

## Nimalarni aniqlay olmaydi

O'tish Rust yozib olingan har bir holatga mos kelishini anglatadi, boshqa hech narsani emas. Qayta
yozishlarda asl muammo odatda yozuvdan tashqarida bo'ladi, shuning uchun chegaralar qayerda ekanini
biling:

- **Hech kim yozib olmagan kiritmalar.** Generatsiya qilingan holatlar, tuzoqlar va o'zingizning
  `--inputs` ingiz shiftdir. Haqiqiy kiritmalarni qo'shing (prod'dan namunalar, xato hisobotlari, asl
  nusxaning test fixture'lari); prod'ni buzadigan foydalanuvchi kiritmasi kamdan-kam hollarda generator
  o'ylab topadigan narsa bo'ladi.
- **Regex'lar.** `regex` crate'ida lookaround va backreference yo'q, hatto kompilyatsiya bo'ladigan
  pattern ham ASCII bo'lmagan matnda `\w`, `\b`, `\d` va registrga sezgir bo'lmagan moslikni JS, Python
  yoki Java'dan boshqacha talqin qilishi mumkin. `fancy-regex` ga o'tish yoki pattern'ni qayta yozish
  yozib olingan har bir holatdan o'tib, baribir turkchadagi nuqtasiz `ı` yoki zero-width joiner'da farq
  qilishi mumkin. `record` regex ishlatadigan fayldagi har bir funksiyaga regex tuzoqlarini qo'shadi
  (yuqoridagilar, Kelvin belgisi, uzun s, arab-hind raqamlari, qator ajratkichlari, oxirgi sigma),
  lekin haqiqiy pattern'laringizni haqiqiy matnga qarshi fuzz ham qiling.
- **Ishga tushirishlar orasida o'zgaradigan narsalar.** `record` asl nusxani ikki marta ishga tushiradi
  va nima farq qilganini ajratadi: o'zgargan qiymatlar (vaqtlar, id'lar) wildcard'ga aylanadi; boshqa
  tartibdagi bir xil qatorlar (hash map'lar, parallellik) istalgan tartibda solishtiriladi, ya'ni port
  baribir aynan o'sha qatorlarni chiqarishi kerak; boshqa sondagi qatorlar `...` ga aylanadi va u hamma
  narsaga mos keladi. `record` har bir turni sanab beradi: har biriga qarang, chunki hash tartibi yoki
  parallellik farqi aynan portda haqiqatda o'zgarishi mumkin bo'lgan narsadir.
- **Float'lar.** Sonni matnga formatlash tillar orasida farq qiladi (`1e21`, `-0`, raqamlar soni).
  Tuzoqlar bu qiymatlarni o'z ichiga oladi va ular aynan mos kelishi kerak; `--float-tolerance` faqat
  yaxlitlashni kechiradi, formatlashni hech qachon.
- **Chiqishda bo'lmagan har qanday narsa.** Vaqt, xotira, yuk ostidagi parallellik hamda stdout,
  stderr, chiqish kodlari, yozilgan fayllar va HTTP javoblaridan tashqari yon ta'sirlar (tarmoq
  chaqiruvlari, ma'lumotlar bazalari, signallar) solishtirilmaydi.
- **Boshqa platformalar.** Yozuv xatti-harakatni faqat uni ishga tushirgan mashinada isbotlaydi.
  Natijalari tip o'lchamlari, endianness yoki kompilyatorga bog'liq bo'lgan C target'da boshqacha
  ishlashi mumkin; shu sababli `analyze` apparat bilan ishlaydigan C'ni C'da qoldiradi.

## Ko'p so'raladigan savollar

**U kodimni avtomatik qayta yozadimi?** Yo'q. U nimani ko'chirish kerakligini topadi, ko'prikni
generatsiya qiladi, asl nusxa nima qilishini yozib oladi va Rust'ni unga qarshi tekshiradi. Rust'ni
`port.rs` da siz yoki agentingiz yozasiz; qachon to'g'ri ekaniga `diff` va `gate` qaror qiladi.

**Ilovamning API'si o'zgaradimi?** Yo'q. Chaqiruvchilar xuddi shu funksiyalarni import qiladi (yoki siz
ishonch hosil qilguningizcha ikkalasini ishga tushirib, asl nusxa natijasini qaytaradigan shadow
modulini).

**Rust har doim tezroqmi?** Yo'q, rust-anything ham buni aytadi. Har bir element uchun bir marta
chaqiriladigan kichik funksiya Rust'da ko'pincha sekinroq, chunki har bir chaqiruv ko'prikdan o'tadi;
V8, JVM va Go bunday funksiyalarni nanosekundlarda bajaradi. `profile` uning atrofidagi siklni topadi,
`--batch` butun siklni ko'chiradi, `bench` esa chiqarishdan oldin hukm beradi. numba, Cython yoki JAX
bilan allaqachon kompilyatsiya qilingan kod ham mashina kodi sifatida ishlaydi: `profile` va `analyze`
uni belgilaydi, chunki uni port qilish kam tezlik beradi.

**Kodim sonli; float'lar aynan mos keladimi?** Ko'pincha yo'q: amallar tartibi, fused multiply-add va
matematika kutubxonasi kompilyatorlar orasida farq qiladi. `--float-tolerance 1e-9` bilan yozib oling
(`record` yoki `app record`), shunda float'lar kattaroq qiymatning shu ulushi ichida mos keladi (1 dan
pastda mutlaq). Butun sonlar, matn va tuzilma baribir aynan mos kelishi kerak.

**Faqat APK, JAR yoki .exe ko'rinishida bo'lgan ilovani port qila oladimi?** Yo'q. U manba kodini port
qiladi: funksiyalarni parse qiladi, har biri nima qilishini yozib oladi va Rust'ni ishlayotgan asl
nusxaga qarshi tekshiradi. Kompilyatsiya qilingan ilovada bularning hech biri yo'q va `analyze` buni
aytadi. Binary'ning ko'rinadigan xatti-harakatidan yangi Rust ilovasini yozish alohida loyiha.

**Sinovdan o'tgan C kodini port qilishim kerakmi?** Ko'pincha yo'q, `analyze` esa qayerda ekanini
aytadi. Apparat registrlariga tegadigan, kompilyatorning tip o'lchamlari yoki xotira joylashuviga
tayanadigan yoki inline assembly ishlatadigan C (`volatile`, bitfield'lar, packed struct'lar,
`__asm__`, manzilga cast qilingan butun sonlar) "C'da qoldirish" deb belgilanadi: sizning
mashinangizdagi yozuv target haqida hech narsani isbotlamaydi, barqaror drayver yoki firmware kodi
esa qayta yozishdan kam foyda oladi. Uning atrofidagi ko'chma mantiq (parse qilish, protokollar,
ma'lumotlarni qayta ishlash) yaxshi ko'chadigan qismdir.

**Electron ilovamni port qila oladimi?** Mantiqni, ha; oynalar veb sahifa bo'lib qoladi. `analyze
--whole-app` Electron'ni aniqlaydi va renderer o'z holicha qolgan holda main process'ni qismma-qism
rejalashtiradi. UI'ni Tauri'ga (Rust backend ustidagi xuddi shu veb UI) ko'chirish mantiq Rust bo'lgandan
keyingi alohida qadam.

**C#, Kotlin yoki Swift-chi?** C# preview'da ([Tillar](#tillar) ga qarang); Kotlin va Swift hozircha
qo'llab-quvvatlanmaydi. Har bir til uchun boshidan oxirigacha test qilingan parser, recorder, ko'prik
va replay drayveri kerak. O'zingizga kerakli til uchun issue oching (yoki mavjudiga ovoz bering).

**Rust asl nusxadan ancha katta bo'lib ketmaydimi?** Bo'lmasligi kerak. `gate` port qatorlarini asl
nusxanikilari bilan solishtiradi va 3x dan oshganda (import'lar va signaturalar uchun qo'shimcha
50 qator) muvaffaqiyatsiz tugaydi: bu odatda crate allaqachon qiladigan narsani qo'lda yozish yoki
holatlarni birma-bir ishlashni anglatadi. `analyze` ishlatiladigan crate'larni sanab beradi.

**Qismma-qism port qilish Rust'ni eski ilova dizayniga bog'lab qo'ymaydimi?** Faqat ikkalasi yonma-yon
ishlayotgan paytda. Yozuvlar xatti-harakatni ilovaning ichki tuzilishida emas, chegaralarida (CLI
chiqishi, server javoblari, modulning eksport qilingan funksiyalari) tekshiradi. Birliklar hali
ko'prikdan o'tayotganda eski tuzilmani takrorlang; `app lift` asl nusxani olib tashlagach, Rust'ni
erkin qayta tuzing, `app replay` esa xatti-harakatni baribir isbotlaydi. Hech narsa asl nusxaga qaytib
chaqiruv ham qilmaydi: front door uni alohida jarayon sifatida ishga tushiradi (yoki HTTP'ni unga
yo'naltiradi), ko'priklangan birliklarni asl nusxa chaqiradi, hech qachon aksincha emas, callback'lar
esa manba tilda qoladi.

**Kodim mashinamdan tashqariga chiqadimi?** Yo'q: rust-anything lokal ishlaydi va kodingizning hech
bir qismini hech qayerga yubormaydi. Cargo crate'larni odatdagidek yuklab oladi, agentingizning model
provayderi esa agentingiz unga yuborgan narsani o'z siyosati doirasida ko'radi.

**Nimalar o'rnatilgan bo'lishi kerak?** Rust va siz port qilayotgan tilning runtime'i
([O'rnatish](#ornatish) ga qarang).

**Nimadir buzildi.** Buyruq, uning chiqishi va platformangizni ko'rsatib issue oching.

## Homiylar

rust-anything bepul va ochiq manbali. Agar u ishingizga yordam bersa, iltimos, unga homiylik qilishni o'ylab ko'ring. Qo'llab-quvvatlashingiz ishlab chiqishni davom ettirishga yordam beradi.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="GitHub'da rust-anything'ga homiylik qiling" /></a>
</p>

### Kompaniya homiylari

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Shaxsiy homiylar

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

## Hissa qo'shish

Issue'lar va pull request'lar mamnuniyat bilan qabul qilinadi; [CONTRIBUTING.md](../CONTRIBUTING.md)
sozlash, testlar qayerga joylashishi va yangi til qanday qo'shilishini tushuntiradi. Dizayn qarorlari va
ularning sabablari [DECISIONS.md](../DECISIONS.md) da. Haqiqiy portlar bo'yicha amaliy misollar ayniqsa
mamnuniyat bilan qabul qilinadi. Xavfsizlik muammolari haqida iltimos maxfiy xabar bering
([SECURITY.md](../SECURITY.md)) va [xulq-atvor kodeksi](../CODE_OF_CONDUCT.md) bilan tanishing.

## Litsenziya

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Repozitoriyingizdagi portlar va generatsiya qilingan kod sizniki.
