<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="Ağzı bir kod etiketi olan rust-anything yengeci">
</p>

<h1 align="center">rust-anything</h1>

<p align="center"><a href="https://github.com/erkamyaman">erKam Yaman</a> tarafından</p>

<p align="center"><a href="../README.md">English</a> · Türkçe · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>
<p align="center"><sub>Bu çeviri topluluk tarafından sürdürülmektedir ve <a href="../README.md">İngilizce README</a>'nin gerisinde kalabilir.</sub></p>

<p align="center"><em>Uygulamanızın tamamını Rust ile yeniden yazın. Yol boyunca çalışır durumda kalsın.</em></p>

<p align="center"><em>CLI'lar, sunucular ve kütüphaneler, parça parça, her adımda orijinaline karşı doğrulanarak.</em></p>

<p align="center">Node.js ve TypeScript · Python · C · Go · Ruby · Java · PHP ve C# önizlemede</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io sürümü"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm sürümü"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 dil">
  <a href="#desteklenen-ajanlar"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="4 ajanla çalışır"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Testler"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT lisansı"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub yıldızları"></a>
</p>

<p align="center">20x'e kadar daha hızlı · 38,251 kayıtlı vaka yeniden oynatıldı · 0 uyuşmazlık · tek komut</p>

<p align="center">
  <img src="assets/race.gif" alt="x18n'in 50,000 anahtar üzerindeki aramasına user.profile yazılıyor: TypeScript 143 ms harcıyor, rust-anything batch'i 6.9 ms, her tuş vuruşunda aynı sonuçlarla." width="820">
</p>

**Uygulamanızın tamamını Rust ile, parça parça yeniden yazın.** rust-anything, Node.js
(TypeScript/JavaScript), Python, C, Go, Ruby veya Java uygulamanızın bugün ne yaptığını kaydeder,
ardından Rust ile yeniden yazılan her parçayı bir sonrakine geçmeden önce bu kayda karşı kontrol
eder; ta ki uygulama tamamen Rust olana kadar. CLI'lar, HTTP sunucuları ve kütüphaneler; Rust'ı
kodlama ajanınız (ya da siz) yazar. Yalnızca kaydın kapsadığını yakalayabilir: bkz.
[Neyi yakalayamaz](#neyi-yakalayamaz). Sadece yavaş kısmın hızlanması mı gerekiyor? Yalnızca onu,
her seferinde bir hot path olacak şekilde port edin:

| Gerçek iş yükü, orijinaliyle aynı sonuçlar | Orijinal | rust-anything ile |
| --- | ---: | ---: |
| x18n'in kenar çubuğu araması, 50,000 anahtar (TypeScript, Node) | sorgu başına 10 ms | **0.5 ms: 20x daha hızlı** |
| Aynı arama tarayıcıda (wasm, tek thread) | 10 ms | **0.95 ms: 11.5x** |
| 20,000 string üzerinde `slugify` (Python) | 98 ms | **17x daha hızlı** |
| Ruby standart kütüphanesinden `Shellwords.shellescape`, 50,000 değer | 88 ms | **11.8x daha hızlı** |
| 50,000 string üzerinde `Slugify` (Go) | 49 ms | **4x daha hızlı** |
| 50,000 string üzerinde `slugify` (Java) | 43 ms | **3x daha hızlı** |

4 çekirdekte ölçülmüştür; her sayının [`demo/`](../demo) içinde, önce sonuçların aynı olduğunu
kontrol eden bir benchmark'ı vardır. Her küçük fonksiyon için Rust'ı ayrı ayrı çağırmak genellikle
bir JIT'ten *daha yavaştır*; rust-anything taşımaya değer döngüyü bulur ve onu taşır.

> rust-anything bağımsız bir projedir; Rust Project veya Rust Foundation ile bağlantılı değildir ve
> onlar tarafından desteklenmez. "Rust", Rust Foundation'ın ticari markasıdır.

## Hızlı başlangıç

Bunu Claude Code, Codex, Cursor veya Gemini CLI'a yapıştırın ve kurulumu ajanınıza bırakın:

```text
rust-anything'i kur: `cargo install rust-anything`, ardından `rust-anything setup` çalıştır.
Seni ne zaman yeniden başlatmam gerektiğini söyle.
```

Ya da kendiniz:

```sh
cargo install rust-anything   # crates.io'dan
rust-anything setup           # Claude Code, Codex, Cursor ve Gemini CLI'a kaydeder
```

Henüz Rust toolchain'iniz yok mu? macOS, Linux ve Windows için hazır derlenmiş binary'ler her
[GitHub release](https://github.com/erkamyaman/rust-anything/releases)'e eklenmiştir; JavaScript
projeleri için `npm install -g rust-anything` aynı binary'yi kurar.

Claude Code'da bunu bir plugin olarak da kurabilirsiniz (MCP sunucusu ve skill; yukarıdaki CLI
`PATH` içinde olmalıdır):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup`, bulduğu her ajana MCP sunucusunu ekler ve iş akışı skill'ini ajanın skill'leri okuduğu
yere kurar. Diğer ayarlarınızı korur, tekrar çalıştırmak güvenlidir ve `--remove` yaptıklarını geri alır.
Ardından ajanınıza örneğin şunları sorun:

- *"Bu CLI'ı rust-anything ile baştan sona Rust'ta yeniden yaz ve aynı davrandığını kanıtla."*
- *"Bu arama yavaş geliyor. rust-anything ile profilini çıkar ve sıcak döngüyü Rust'a taşı."*
- *"`src/parser/`'ın rust-anything ile Rust'a geçişini planla; ilk birimi port et ve kanıtla."*
- *"`rust/text-rs` içindeki Rust portunu orijinaline karşı benchmark'la ve yayınlamaya değer mi söyle."*

### Desteklenen ajanlar

| Ajan | `rust-anything setup` şunları ekler |
| --- | --- |
| Claude Code | `~/.claude.json` içinde MCP sunucusu, `~/.claude/skills/` içinde skill |
| Codex | `~/.codex/config.toml` içinde MCP sunucusu, `~/.codex/skills/` içinde skill |
| Cursor | `~/.cursor/mcp.json` içinde MCP sunucusu |
| Gemini CLI | `~/.gemini/settings.json` içinde MCP sunucusu |
| Diğer herhangi bir MCP istemcisi | `rust-anything mcp`'yi elle stdio sunucusu olarak ekleyin (bkz. [Kurulum](#kurulum)) |

Var olan bir dosyayı değiştirmeden önce `setup` yanına bir kopyasını kaydeder (`<file>.rust-anything.bak`).

Ya da adımları kendiniz çalıştırın:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile bir döngü içinde fuzzyScore'u buluyor, bridge --batch Rust crate'ini üretiyor, gate 2000/2000 kayıtlı vakayla geçiyor ve benchmark TS'ten 20.7x daha hızlı olduğunu gösteriyor." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # sıcak olan ne, onu kim çağırıyor
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# src/port.rs'i yazın (ya da ajanınıza yazdırın), ardından:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # kaydedilen her vaka eşleşmeli
rust-anything bench rust/fuzzy-rs                      # daha mı hızlı? karar söyler
rust-anything gate rust/fuzzy-rs                       # bitti demek, bunun geçmesi demek
```

rust-anything kodu çevirmez: Rust'ı kodlama ajanınız (Claude Code, Codex, Cursor, ...) ya da siz
yazarsınız. rust-anything, bir ajanın güvenilir biçimde tahmin edemeyeceği şeyleri sağlar: zamanın
nereye gittiğini, önce neyin ve hangi sırayla port edileceğini, kodun geri kalanının Rust'ı API'si
değişmeden çağırabilmesi için bir köprüyü (bridge), portun eşleşmesi gereken davranışın tam halini,
onu yayına almanın güvenli bir yolunu ve bir portun ne zaman bittiğini söyleyen bir gate'i.

## Diller

| Dil | Birim | Köprü | Kaydeden ve yeniden oynatan |
| --- | --- | --- | --- |
| TypeScript/JavaScript | klasör veya dosya | üretilmiş bir binary wire ile napi-rs veya wasm-bindgen; sınıflar ve async dahil | `.ts` kaynaklarını çalıştıran Node |
| Python | paket veya modül | PyO3 (abi3), doğrudan dönüşüm, tipli exception'lar | orijinali import eden Python |
| C | `.c` dosyası | orijinal adlarla `extern "C"` fonksiyonlar ve bir header | paylaşımlı kütüphane olarak derlenmiş orijinal, ctypes üzerinden çağrılır, vaka başına bir fork |
| Go | paket | orijinal API'ye sahip bir pakette tipli cgo çağrıları ve üretilmiş bir binary wire | kendi modülü olarak derlenen, üretilmiş bir Go sürücüsü |
| Ruby | modül fonksiyonlarından oluşan dosya veya klasör | orijinal modüllerin altında bir magnus eklentisi | üretilmiş bir Ruby sürücüsü |
| Java | `public static` metotlardan oluşan paket | orijinal metotlara sahip wrapper sınıflarda tipli JNI ve üretilmiş bir binary wire | üretilmiş bir reflection sürücüsü |
| PHP (önizleme) | fonksiyonlar ve `public static` metotlardan oluşan klasör | sırada: C ABI üzerinden PHP FFI | bugün bütün uygulamalar: CLI'lar ve sunucular (`php -S`) için `app record`, `app replay` ve front door |
| C# (önizleme) | `public static` metotlardan oluşan klasör | sırada: C ABI üzerinden P/Invoke | bugün bütün uygulamalar: CLI'lar ve ASP.NET sunucuları (`dotnet <app>.dll`) için `app record`, `app replay` ve front door |

C hariç her dil batch sınıfları da alır (`--batch`): öğeler köprüyü bir kez geçer ve Rust'ta kalır,
her çağrı tüm çekirdeklerde hepsinin üzerinden çalışır.

Dil, repodan tespit edilir (`go.mod`, `pom.xml`, bir `.csproj` veya `.sln`, `pyproject.toml`,
`Gemfile`, `composer.json`, `package.json`, aksi halde en yaygın kaynak dosyalar); `--lang` bunu
geçersiz kılar. Tipler kaynaktan gelir: TS tipleri, Python type hint'leri, C, Go, Java ve C#
imzaları, Ruby YARD etiketleri, PHP tipleri ve phpdoc; sayı olarak kullanılan tipsiz parametreler
sayı olarak çıkarılır.

PHP önizlemededir: `analyze` bir PHP uygulamasını planlar (Composer paketleri ve PSR-4 autoloading,
gevşek karşılaştırma ve tam sayı taşmasının float'a dönüşmesi gibi riskler, crate'lere eşlenmiş
Composer paketleri) ve bir PHP CLI'ı ya da sunucusu kaydedilebilir, yeniden oynatılabilir ve bir
Rust front door'unun arkasına konabilir. Birimlerini PHP'nin FFI'ı üzerinden Rust'a port etmek bir
sonraki adımdır ([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# da aynı şekilde önizlemededir: `analyze` `.csproj` projelerini ve NuGet paketlerini okur
(crate'lere eşlenmiş olarak), `using` yönergelerini klasörlere çözümler ve C#'ın farklı yaptığı
şeyleri işaretler (`decimal`, `dynamic`, LINQ'in ertelenmiş sorguları, `Task`, `lock`, reflection).
Bir C# CLI'ı veya ASP.NET sunucusu kaydedilebilir, yeniden oynatılabilir ve bir Rust front door'unun
arkasına konabilir; birimleri P/Invoke üzerinden port etmek sırada.

## Nasıl çalışır

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 zaman       önce neyi   Rust       orijinal    siz ya da   kayıtlı   daha mı    canlıda     bitti demek
 nereye      port        crate'i    ne yapıyor  ajanınız    her vaka  hızlı?     ikisi yan   bunun geçmesi
 gidiyor     etmeli      ve wrapper             yazar                 karar      yana        demek
```

Orijinal, doğruluğun kaynağı olarak kalır: `record` onu uç durumlarla (ve sizin girdilerinizle)
çalıştırır ve döndürdüğünü ya da fırlattığını kaydeder; `diff` her vakayı Rust'a karşı yeniden
oynatır; hepsi eşleşip `gate` geçene kadar hiçbir şey yayına girmez. Çağıranlar baştan sona orijinal
API'yi kullanmaya devam eder.

Bütün bir uygulama da aynı döngüden birim birim geçer; tüm programı kanıtlayan bir çerçevenin
içinde ([Tüm uygulamayı port etmek](#tüm-uygulamayı-port-etmek)):

```
analyze --whole-app ──> app record ──> app front-door ──> birim başına: yukarıdaki döngü, sonra app wire ──> app lift
 yapı, her               uygulamanın    giriş noktası      gate geçer, birim Rust'ta yanıt verir:          saf Rust,
 bağımlılık,             dışarıdan      Rust'ta; orijinal  replay %100, fallback oranı düşer               replay ile
 verilecek kararlar      ne yaptığı     yanıt verir                                                        kanıtlanmış
```

## Döngü

| Adım | Komut | Ne yapar |
| --- | --- | --- |
| 0. Profil | `rust-anything profile <repo> -- node bench.mjs` | Gerçek bir iş yükünü dilin profiler'ı altında çalıştırır (node, cProfile, `go test` pprof, JFR, bir Ruby tracer): kapsayıcı süreye göre sıcak fonksiyonlar, onları çağıranlar ve hangi döngülerin batch'leneceği; zaten derlenmiş kodu (numba, Cython, JAX) işaretler, çünkü orada Rust az kazandırır |
| 1. Plan | `rust-anything analyze <repo>` | Birimler, port sırası, `file:line` ile riskler, birim başına köprü, bağımlılık-crate uyumu, en iyi ilk portlar; `--whole-app` giriş noktalarını ve yapıyı, crate'iyle birlikte her bağımlılığı (import edilen ya da beyan edilen), parçaları (birbirini import eden birimler birlikte taşınır) ve önerilen cevabıyla numaralı kararları ekler |
| 2. Köprü | `rust-anything bridge <repo> <unit>` | Binding'leri içeren crate (`lib.rs` ve kaynak dilin yüklediği wrapper) ile port edilecek stub'lar (`port.rs`); `--batch fn:param` birçok `param` değerini Rust'ta tutan bir sınıf ekler |
| 3. Kayıt | `rust-anything record <crate>` | Orijinali üretilmiş uç durumlarla (ASCII olmayan, emoji, `-0`, `NaN`, float beklenen yerde int, ...) ve her parametredeki her anlamsal tuzakla (string uzunluğu ve harf büyüklüğü, işaretli bölme, taşma sınırları, float yazdırma, map ve sıralama düzeni) çalıştırır ve `cases.jsonl`'i kaydeder; `--float-tolerance 1e-9`, sayısal kod için float'ların bu oran içinde eşleşmesine izin verir |
| 3. Derleme | `rust-anything build <crate>` | Rust tarafını derler: `.node`, wasm paketi, Python eklentisi ya da paylaşımlı kütüphane |
| 3. Diff | `rust-anything diff <crate>` | Kayıtlı vakaları Rust'a karşı, orijinali çağıranların çağırdığı şekilde yeniden oynatır; uyuşmazlıkları listeler |
| 3. Bench | `rust-anything bench <crate>` | Kayıtlı vakaları orijinalde ve Rust'ta, köprü dahil, zamanlar |
| 4. Shadow | `rust-anything shadow <crate>` | İkisini de çalıştıran, orijinalin sonucunu döndüren ve uyuşmazlıkları raporlayan drop-in; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, testler, `unsafe` denetimi, port edilmemiş bir şey kalmaması, orijinalin her hata yolu için kayıtlı başarısız bir vaka, orijinalin hata döndürdüğü yerde `unwrap`/`expect`/`panic!` olmaması (`// INFALLIBLE: <why>` ile işaretlenmedikçe), derleme, API, davranış |
| Ajanlar | `rust-anything setup` | MCP sunucusunu (`rust-anything mcp`, her adım bir araç olarak) ve iş akışı skill'ini ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) kodlama ajanlarınıza kaydeder |

## Tüm uygulamayı port etmek

Hedef, orijinaliyle aynı davranan, orijinali referans olarak saklanan saf bir Rust uygulamasıdır.
Rust'ı ajanınız yazar; rust-anything işi sıraya koyar, iskeletini kurar ve her adımı kanıtlar.
[Whole-app skill'i](../skills/rust-anything/whole-app.md) ajana süreci adım adım anlatır; işe
yalnızca sizin verebileceğiniz kararlarla başlar:

- **Sorgulama (grilling)**: ajan, portun bağlı olduğu her karar netleşene kadar turlar halinde, her
  soruyu önerdiği cevapla birlikte sorar ve her birini `rust/DECISIONS.md` içine bir ADR olarak
  yazar; `rust/GLOSSARY.md` ise orijinalin terimlerini Rust adlarına eşler.
- **Araştırma**: arka plan ajanları her bağımlılığın birincil kaynaklarını okur ve buldukları her
  anlamsal tuzakla birlikte `rust/research/<topic>.md` yazar.
- **Oturumlar arası**: `rust/MAP.md` her birimi durumuyla listeler; bir oturum başlamadan önce bir
  birimi üstlenir ve her kontrol noktası bir sonraki oturum için bir `rust/HANDOFF.md` bırakır. Aynı
  dalgadaki birimler subagent'lar tarafından paralel port edilebilir.
- **Geçiş (cutover)**: ajan yapabildiğini yapar ve yalnızca sizin yapabileceğiniz adımlar (deploy,
  DNS, secret'lar) için her adımda geri dönüş yolu olan etkileşimli bir betik, `rust/cutover.sh` yazar.

Sorgulama, araştırma ve bu uygulamalar
[Matt Pocock'un skill'lerinden](https://github.com/mattpocock/skills) uyarlanmıştır.

Önce planlayın: `rust-anything analyze . --whole-app` uygulamanın yapısını (CLI, sunucu veya
kütüphane) ve giriş noktalarını, Rust crate'i ve uyumuyla birlikte her harici bağımlılığı (import
edilen ya da beyan edilen), parçalar halinde port sırasını (birbirini import eden birimler birlikte
taşınır) ve önerilen cevabıyla numaralı kararları ekler: tutulacak birimler, engellenen birimler,
crate'i olmayan ya da kısmi olan bağımlılıklar.

Sonra tüm programı dışarıdan kanıtlayın. `record` ve `diff` tek bir birimi kanıtlar; `app record`
ve `app replay` ise uygulamayı, altı dilin herhangi birindeki CLI'lar ve sunucular için kanıtlar
(uygulama bir kara kutudur):

```sh
rust-anything app record . -- python3 cli.py          # orijinali çalıştıran komut
rust-anything app replay .                            # orijinal %100 geçmeli
rust-anything app replay . --build "target/release/mytool"
```

- `app record` orijinali uygulamanın kendi belgelenmiş örnekleriyle (Markdown ve shell
  dosyalarındaki `$ mytool ...` satırları, adını verdikleri dosyalarla birlikte), bir `--inputs`
  JSONL dosyasıyla (`{"name", "args", "stdin", "env", "files"}`) ve bu vakalardan türetilen anlamsal
  tuzaklarla (ASCII olmayan ve emoji string'ler, negatif bölme ve mod, taşma, çok büyük ve çok küçük
  float'lar, map sırası, eksik dosyalar) çalıştırır. Her vaka iki kez çalışır; iki çalıştırma arasında
  farklı olan şey bir `[..]` joker karakterine dönüşür. `--normalize timestamps|uuids|key-order` veya
  `--normalize name=regex` vakalarla birlikte kaydedilen normalizer'lar ekler.
- Vakalar `rust/app-cases/` içindeki [trycmd](https://docs.rs/trycmd) dosyalarıdır: `<case>.toml`
  (argv, env, çıkış kodu), `.stdin`, `.stdout`, `.stderr`, `.in/` (girdi dosyaları) ve `.out/`
  (yazılan dosyalar). Onları elle okuyup düzenleyin; port bir binary'ye sahip olduğunda bir Rust testi
  onları `trycmd` ile çalıştırabilir.
- `app replay` herhangi bir derlemeyi vakalara karşı çalıştırır, `passed/total` yazdırır, başarısız
  her vaka için bir diff içeren `rust/app-cases/replay-report.md` dosyasını yazar ve herhangi bir
  uyuşmazlıkta sıfırdan farklı bir kodla çıkar. `RUST_ANYTHING_FALLBACK_LOG` ile adı verilen dosyaya
  ekleme yapan bir derleme (orijinale her fallback için bir satır), aşağıdaki front door'un yaptığı
  gibi, fallback oranını da raporlatır.
- `app replay --case <name>` raporun verdiği adla tek bir vakayı yeniden çalıştırır: her şeyi tekrar
  çalıştırmadan önce bir uyuşmazlığı düzeltmek için hızlı, tekrarlanabilir döngü.

Ardından giriş noktasını Rust'a taşıyın ve komutları ona birer birim halinde devredin:

```sh
rust-anything app front-door .                            # rust/app: her komut orijinali çalıştırır
rust-anything app wire . textkit --command upper          # textkit-rs gate'i geçtikten sonra
# yapıştırıcı kodu rust/app/src/units/textkit.rs içine yazın, ardından:
rust-anything app wire . textkit                          # yine %100, daha düşük fallback oranı
```

- `app front-door`, `rust/app`'in iskeletini kurar: uygulamanın adını taşıyan bir Rust binary'si;
  kayıtlı vakalardaki komutlar ve flag'ler için bir clap ayrıştırıcısı, burada her komut orijinali
  aynı argv, stdin ve ortamla çalıştırır, çıktısını ve çıkış kodunu olduğu gibi geçirir. Her fallback
  sayılır, bu yüzden yeni front door'u yeniden oynatmak %100 fallback ile %100 başarı verir (bunu
  göstermek için derler ve yeniden oynatır). `rust/app`'in üzerine asla yazmaz: o andan itibaren kod
  sizindir.
- `app wire <repo> <unit> --command <name>` birim crate'i üzerinde `gate` çalıştırır (az önce geçtiyse
  `--skip-gate`), onu `rust/app`'e bir kütüphane olarak ekler, sizin ya da ajanınızın doldurması için
  `src/units/<unit>.rs` dosyasını bir kez yazar (argümanları ayrıştırın, `<crate>::port`'u çağırın,
  orijinalin yazdırdığını yazdırın), komutları ona yönlendirir, sonra derler ve yeniden oynatır.
  `RUST_ANYTHING_UNIT_<NAME>=original`, bağlanmış bir birimi lift'e kadar orijinale geri gönderir.

Hiçbir komut adı içermeyen argv için (argümansız çağrılar, bilinmeyen komutlar, kullanım hataları)
uygulamanın kendi adını bir komut olarak bağlayın (`--command mytool`).

Replay fallback oranı 0 ile geçtiğinde ve her birim gate'i geçtiğinde, onu saf bir Rust uygulamasına
dönüştürün:

```sh
rust-anything app lift .
```

- `app lift` ikisi de sağlanana kadar reddeder ve neyin engellediğini söyler: hâlâ fallback'e düşen
  vakalar, hâlâ stub olan yapıştırıcı kod, gate'i geçemeyen birimler.
- Önce bir kopya üzerinde, fallback yolunu ve kill switch'leri kaldırır, her birim crate'ini
  `rust/app`'in düz bir kütüphanesine dönüştürür (`cdylib`, binding'ler veya üretilmiş wrapper'lar
  olmadan) ve `cargo test` sırasında `rust/app-cases`'i trycmd ile çalıştıran
  `rust/app/tests/app_cases.rs` dosyasını ekler; böylece CI'ın cargo dışında hiçbir şeye ihtiyacı kalmaz.
- Ardından lift kontrol listesini çalıştırır: her birimde ve `rust/app` üzerinde fmt, clippy
  `-D warnings` ve testler; `rust/DECISIONS.md` içinde adı geçen her hedefin kurulu olduğu yerde
  derlenmesi veya kontrol edilmesi; çalışma zamanında okunan dosyalar ve gömülmemiş asset klasörleri;
  ve saf binary üzerinde replay. Değişiklikler ancak bunların hepsi geçtiğinde geri yazılır. Orijinale
  asla dokunulmaz.

### Sunucular

Aynı komutlar HTTP sunucularını da kanıtlar. `--http`, komutun bir sunucu başlattığını belirtir;
portunu `PORT`'tan veya komuttaki `{port}`'tan alır (hep aynı portu dinleyen bir sunucu için
`--port`):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: her route proxy'lenir
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- İstekler uygulamanın belgelerindeki `curl` satırlarından (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs`'tan (`{"name", "method", "path", "headers", "body"}`) ve tuzaklardan gelir: path
  segmentleri ve query değerleri CLI argümanlarıyla aynı tuzaklarla değiştirilir, body'ler metin ve
  JSON tuzaklarıyla değiştirilir, bir de bilinmeyen bir route eklenir. Her çalıştırma sunucuyu sıfırdan
  başlatır ve istekleri ad sırasıyla gönderir, böylece istekler arasındaki durum korunur.
- Vakalar `rust/app-cases/http/<case>.toml` (istek, durum kodu ve önemli header'lar) ve
  `<case>.body` dosyalarıdır (yanıt gövdesi, iki çalıştırmanın farklı olduğu yerlerde `[..]` ile).
  Date, server ve diğer yanıta özgü header'lar dışarıda bırakılır; önemsemediğiniz header satırlarını
  silin.
- Front door, orijinali kendine ait bir portta başlatan ve hiçbir birimin yanıtlamadığı her route'u
  proxy'leyen bir axum sunucusudur. `wire --route` axum route'ları alır: `METHOD /path/{param}`,
  herhangi bir metot için `/path`, geri kalan her şey için `*`; yapıştırıcı kod route'u, parametrelerini
  ve isteği alır. `lift` proxy'yi kaldırır; HTTP vakaları bundan sonra CI'da `app replay` ile çalışır.

### Kütüphaneler

Bir kütüphanenin yeniden oynatılacak bir süreci yoktur: front door onun public API'sidir ve her
birimin kayıtlı vakaları kanıttır.

```sh
rust-anything app front-door .        # rust/app: public API'ye sahip bir Rust crate'i
# her birim döngüden geçer: bridge, record, port.rs, build, diff, gate; ardından:
rust-anything app wire . textkit-rs   # rust/app'ten yeniden export edilir; orijinal onun shadow'unu import eder
rust-anything app replay .            # bağlanmış her birimin vakaları; fallback = hâlâ orijinalde olan export'lar
rust-anything app lift .
```

- `app front-door`, repoda `main` ve sunucu olmadığında (aksi halde `--library`) public API'yi (her
  birimin export'larını) bulur ve `rust/app`'i bir kütüphane crate'i olarak kurar. Bağlanan her birim
  onun bir modülü olur: `pub use textkit_rs::port as textkit;`.
- `app wire`, `bridge` ile üretilmiş bir crate alır, `gate` çalıştırır ve birimin shadow drop-in'ini
  yazar: orijinal paket birimin yerine onu import eder, böylece onu çağıranlar orijinal API'yi korur
  ve Rust'a ulaşır. `RUST_ANYTHING_UNIT_<NAME>=original` birimi geri gönderir (C: shadow'un flag'leri
  olmadan derleyin).
- `app replay`, bağlanmış her birimin kayıtlı vakalarını binding'leri üzerinden çalıştırır. Fallback
  oranı, Rust'ın henüz yanıtlamadığı public export'ların payıdır: bağlanmamış birimler ve `bridge`'in
  kaynak dilde bıraktığı export'lar.
- `app lift` fallback'in 0 olmasını ve her birimin `gate`'ten geçmesini ister; birimlerden binding'leri,
  wrapper'ları ve shadow'ları çıkarır ve `rust/app`'i tek bir saf Rust kütüphanesi olarak bırakır.
  Hiçbir `port.rs`'e dokunmaz, böylece binding'ler üzerinden eşleşen vakalar onu hâlâ tanımlar; kontrol
  listesi, orijinalde hâlâ shadow'ları import eden dosyalar için uyarır.

Beşi de aynı zamanda MCP araçlarıdır: `app_record`, `app_replay`, `app_front_door`, `app_wire` ve
`app_lift`.

## Vaka çalışması: x18n'in çekirdeği

x18n çekirdeğinin API değişikliği olmadan taşınabilen 29 fonksiyonunun tamamı rust-anything ile port
edildi: her gate geçiyor ve 7,925 kayıtlı vaka birebir eşleşiyor. Ardından `rust-anything bench`,
JS'ten çağrıldıklarında portların TS'ten daha yavaş olduğunu gösterdi, çünkü köprünün maliyeti
yapılan işten fazla. Tam rapor: [`demo/x18n-core`](../demo/x18n-core/README.md). Ders araca gömülü:
bir portu yayına almadan önce `bench` ile ölçün.

## Hot path'ler: veriyi Rust'ta tutun

Öğe başına bir kez çağrılan bir port, köprünün bedelini de öğe başına öder ve bir JIT'e kaybeder.
Kazandıran şey döngüyü taşımaktır: `profile` onu bulur, `--batch` ise öğeleri bir kez alan ve her
çağrıda fonksiyonu hepsinin üzerinde, tüm çekirdeklerde çalıştıran, sonuçları typed array olarak
döndüren bir sınıf üretir.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: çalışmanın dörtte biri, `matched` tarafından anahtar başına çağrılıyor: batch'leyin
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // bir kez
const order = search.rank(query, 0)               // her tuş vuruşunda: index'ler, en iyisi önce
```

`port.rs` içindeki bir `FuzzyScoreIndex` struct'ı, varsayılan döngüyü öğeleri bir kez hazırlayan ve
kendi başına sıralayabilen (`rank`) bir döngüyle değiştirir: anahtarları her birinin karakter maskesiyle
birlikte küçük harfe çevrilmiş halde, her anahtarda her yaygın karakterin ilk konumunu tutan bir
tabloyu (tek harfli bir sorgu tek bir sütundur) ve son sorgunun eşleşmelerini tutar (`s`'den sonra
`se` yazmak yalnızca `s`'nin eşleştirdiklerini yeniden puanlar). x18n'in 50,000 anahtar üzerindeki
kenar çubuğu aramasında, harf harf yazılarak, birebir aynı sonuçlarla:

| | Sorgu başına | TS'e göre |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| Index ile aynı daraltmayı yapan TS | 4.1-5.4 ms | 2x |
| Aynı port, anahtar başına çağrılarak | - | 0.2-0.4x |
| `FuzzyScoreBatch`, varsayılan index (4 çekirdek) | 5.1 ms | 1.7x |
| `FuzzyScoreIndex` ile `FuzzyScoreBatch` (napi, 4 çekirdek) | 0.45-0.56 ms | **18-22x** |
| Aynısı wasm ile (tek thread) | 0.95 ms | **11.5x** |

Aynı daraltmayı yapan TS'e karşı bile Rust hâlâ 7-12x daha hızlı (wasm 5x). Döndürülen index'leri
düz bir döngüyle anahtarlara dönüştürün: `Array.from(order, i => keys[i])` 20x daha pahalıydı, 0.4 ms.

Her dil batch'leri alır ve çağrı başına portların kaybettiği yerlerde bile orijinali geçerler. 4
çekirdekte aynı iş, birebir aynı sonuçlar ve hatalar (benchmark'lar her demo klasöründe):

| Dil | İş yükü | Orijinal | Çağrı başına port / orijinal | Batch / orijinal |
| --- | --- | ---: | ---: | ---: |
| TS | x18n araması, 50,000 anahtar | 10 ms | 0.2-0.4x | **20x** |
| Python | `slugify`, 20,000 string | 98 ms | - | **17x** |
| Ruby | `slugify`, 20,000 string | 110 ms | - | **12.7x** |
| Ruby | `shellescape` (stdlib), 50,000 karışık değer | 88 ms | - | **11.8x** |
| Go | `Slugify`, 50,000 string | 49 ms | 0.93x | **4x** |
| Java | `slugify`, 50,000 string | 43 ms | 0.68x | **3x** |

Derlenmiş orijinaller daha az kazanır: öğe başına iş zaten hızlıdır, bu yüzden batch çekirdek sayısı
kadar kazanır. Batch crate'leri mimalloc ile bellek ayırır: sistem allocator'ıyla Go batch'i tek
thread'den daha yavaştı. Demo: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Altı dilde gerçek kod

Go'nun `path`'i, Ruby'nin `shellwords`'ü, Python'un `colorsys`'i, küçük cephelerin arkasındaki JDK ve
glibc davranışları: her port kendi gate'ini geçiyor, toplamda 13,010 kayıtlı vaka. Bu çalışmalar
rust-anything'deki hataları bulup düzeltti (`serde_json` üzerinden bir ULP kayan float'lar, kayıt
sırasında C çökmeleri, tipsiz kodun anlamsız girdiler alması). Fonksiyon başına çağrıldığında Ruby
portu Ruby'den 4.4x, Python portu CPython'dan 1.35x daha hızlı çalışır; Go ve Java'nın yaprak
fonksiyonları ise kendi dillerinde daha hızlı kalır; batch olarak hepsi kazanır (yukarıdaki tabloya bakın).
Rapor: [`docs/real-world-languages.md`](./real-world-languages.md).

## Örnek: x18n'den gerçek bir modül

[x18n](https://github.com/x18n-dev/x18n)'den `packages/core/src/fuzzy.ts`, [`demo/`](../demo)
içinde iki şekilde de port edildi:

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: hazır, wasm-bindgen (core tarayıcılarda çalışır)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# src/port.rs'i yazın
rust-anything gate demo/fuzzy-rs
```

Rust `char` ile index'leyen ilk port basit testleri geçti ama `diff`'te başarısız oldu:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS'teki `indexOf` UTF-16 kod birimlerini sayar, bu yüzden bir emoji iki konum kaplar.
`demo/*/src/port.rs` içindeki port üretilmiş `utf16` yardımcılarını kullanır ve hem napi-rs
(`demo/fuzzy-napi`) hem de wasm-bindgen (`demo/fuzzy-rs`) olarak 2000/2000 vakayı ve gate'i geçer.

rust-anything'in x18n'in tamamı için yazdığı plan: [`docs/examples/x18n.md`](./examples/x18n.md).

## Kurulum

```sh
cargo install --path .
```

`record`, `diff` ve `bench` orijinali kendi runtime'ında çalıştırır: TS için Node 22.6+ (`.ts`
kaynaklarını doğrudan çalıştırır), Python ve C (ctypes) için Python 3.9+, Go 1.21+, Ruby 3+, JDK 17+
(`javac` ve `java`). C ayrıca bir C derleyicisi gerektirir. wasm köprüleri ayrıca
`rustup target add wasm32-unknown-unknown` ve
`cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked` gerektirir;
tam sürümü `build` söyler.

Ajanlar için `rust-anything setup` her şeyi kaydeder (bkz. Hızlı başlangıç). Bunun yerine MCP
sunucusunu tek bir projeye elle eklemek için (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## `bridge` neye karar verir

- Köprüyü geçemeyen export'lar nedeniyle birlikte kaynak dilde kalır ve shadow modülü orijinali
  yeniden export eder. TS için:
  fonksiyon alan veya döndüren fonksiyonlar, generator'lar ve iterator'lar, RegExp, `instanceof`
  kontrolleri, generic'ler ve tipleri (import'lar, yeniden export'lar ve `extends` üzerinden izlenerek)
  fonksiyon içeren değerler. `--keep "name: reason"` daha fazlasını tutar, örneğin `Intl` verisine
  bağlı kod.
- TS tipleri Rust tiplerine eşlenir; type alias'lar import'lar üzerinden çözümlenir, parametre tipleri
  varsayılan değerlerden çıkarılır; yapılandırılmış değerler üretilmiş bir binary wire olarak geçer
  (JSON yalnızca wire'ın modellemediği şekiller için yedek olarak).
- JSON `undefined`, NaN, Infinity, -0 veya tek başına surrogate'leri ifade edemez: yapılandırılmış
  değerler, üretilmiş `index.cjs`'in çevirdiği işaretçiler (`{"$undefined": true}`, `{"$num": "NaN"}`,
  `{"$utf16": [...]}`) taşır; yardımcılar crate'in `js.rs` dosyasındadır.

`record` TS kaynaklarını olduğu gibi çalıştırır: bir Node resolve hook'u bundler tarzı import'ları
takip eder (`./errors`'tan `./errors.ts`'e), repoda kurulu npm paketi yoksa `--resolve-from` onları
sağlar ve dönüştürme gerektiren TS (enum'lar, parameter property'ler)
`--experimental-transform-types` ile yeniden denenir.

## `analyze` neye bakar

- Paketler (`package.json`) ve kaynak dosyalar; `node_modules`, derleme çıktısı, fixture'lar,
  playground'lar ve araç yapılandırmaları atlanır. Vue/Svelte/Astro `<script>` blokları import'lar
  için ayrıştırılır.
- **Birimler**: kaynak dosyalardan oluşan bir klasör ya da bir paketin kaynak kökündeki bir dosya.
- **Dalgalar**: bir birimin import ettikleri daha önceki dalgalarda gelir; import döngüleri birlikte
  port edilir.
- **Köprü**: birim ya da onun import ettiği herhangi bir şey Node gerektiriyorsa napi-rs; taşınabilir
  kod için wasm-bindgen; UI ve editör kodu için JS'te tut.
- **Hazırlık** (ne kadar güvenli) ve **öncelik** (güvenli ve değer: döngüler ve string işleri, testler, boyut).

| Risk | Önem | Örnek |
| --- | --- | --- |
| String offset'leri | yüksek | `slice`, `indexOf`, `matchAll`, `d` flag'i: UTF-16 ve UTF-8 |
| Regex sözdizimi | yüksek | lookaround, backreference'lar, `y`: `regex` crate'inde yok |
| Dinamik regex | yüksek | `new RegExp(userPattern)`: çalışma zamanında JS sözdizimi |
| Dinamik kod | yüksek | `eval`, `new Function`, hesaplanan `import()` |
| Dinamik tipleme | orta | `any`, `'key' in value` |
| Sıralı koleksiyonlar | orta | `Map`, `Set`, `Object.keys`: ekleme sırası |
| Async, generator'lar | orta | promise ve generator sınırları |
| Sınıf kalıtımı, reflection | orta | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback biçimli API'ler | orta | fonksiyon tipli parametreler ve metotlar: geveze köprüler |
| Exception'lar, sayılar, JSON | düşük | `throw`, bitsel işlemler, `JSON.stringify` sırası |

## Geliştirme

```sh
cargo test                        # birim testleri, fixture repo, record/diff/shadow döngüsü (node gerekir), dil başına app record/replay
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Tasarım kararları ve gerekçeleri: [DECISIONS.md](../DECISIONS.md).

## Güncelleme veya kaldırma

```sh
cargo install rust-anything                                    # güncelle (Cargo)
npm install -g rust-anything@latest                            # güncelle (npm)
rust-anything setup                                            # ajan ayarlarını yenile
rust-anything setup --remove && cargo uninstall rust-anything  # kaldır (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # kaldır (npm)
```

`setup --remove` yalnızca rust-anything'in girdilerini çıkarır; kaydettiği kopyalar
(`<file>.rust-anything.bak`) siz silene kadar kalır.

## Neyi yakalayamaz

Geçmek, Rust'ın kaydedilen her vakayla eşleştiği anlamına gelir, fazlası değil. Yeniden yazımları
asıl ısıran şey genellikle kaydın dışında yaşar, bu yüzden sınırların nerede olduğunu bilin:

- **Kimsenin kaydetmediği girdiler.** Üretilen vakalar, tuzaklar ve kendi `--inputs`'unuz tavandır.
  Gerçek girdiler ekleyin (canlı ortamdan örnekler, hata raporları, orijinalin test fixture'ları);
  canlıyı bozan kullanıcı girdisi nadiren bir üretecin aklına gelen türdendir.
- **Regex'ler.** `regex` crate'inde lookaround ve backreference yoktur; derlenen bir pattern bile
  ASCII olmayan metinde `\w`, `\b`, `\d` ve büyük/küçük harf duyarsız eşleşmeyi JS, Python veya
  Java'dan farklı ele alabilir. `fancy-regex`'e geçmek ya da pattern'i yeniden yazmak kaydedilen her
  vakayı geçip yine de Türkçedeki noktasız `ı`'da veya bir zero-width joiner'da farklı davranabilir.
  `record`, regex kullanan bir dosyadaki her fonksiyona regex tuzakları ekler (bunlar, Kelvin işareti,
  uzun s, Arap-Hint rakamları, satır ayırıcılar, son sigma), ama gerçek pattern'lerinizi gerçek
  metne karşı da fuzz edin.
- **Çalıştırmalar arasında değişenler.** `record` orijinali iki kez çalıştırır ve neyin farklı olduğunu
  ayıklar: değişen değerler (zamanlar, id'ler) joker karaktere dönüşür; başka sırada gelen aynı
  satırlar (hash map'ler, eşzamanlılık) herhangi bir sırada karşılaştırılır, yani bir portun yine de
  tam olarak bu satırları üretmesi gerekir; farklı sayıda satır `...` olur ve her şeyle eşleşir.
  `record` her türü listeler: her birine bakın, çünkü hash sırası ya da eşzamanlılık farkı tam da bir
  portta gerçekten değişebilecek şeydir.
- **Float'lar.** Sayıdan metne biçimlendirme diller arasında farklıdır (`1e21`, `-0`, basamak sayıları).
  Tuzaklar bu değerleri içerir ve birebir eşleşmeleri gerekir; `--float-tolerance` yalnızca yuvarlamayı
  affeder, biçimlendirmeyi asla.
- **Çıktıda olmayan her şey.** Zamanlama, bellek, yük altında eşzamanlılık ve stdout, stderr, çıkış
  kodları, yazılan dosyalar ve HTTP yanıtları dışındaki yan etkiler (ağ çağrıları, veritabanları,
  sinyaller) karşılaştırılmaz.
- **Diğer platformlar.** Bir kayıt, davranışı yalnızca onu çalıştıran makinede kanıtlar. Sonuçları tip
  boyutlarına, endianness'a veya derleyiciye bağlı olan C kodu hedefte farklı davranabilir; `analyze`
  bu nedenle donanıma dönük C'yi C'de tutar.

## SSS

**Kodumu otomatik olarak yeniden mi yazıyor?** Hayır. Neyin taşınacağını bulur, köprüyü üretir,
orijinalin ne yaptığını kaydeder ve Rust'ı ona karşı kontrol eder. Rust'ı `port.rs` içinde siz ya da
ajanınız yazar; ne zaman doğru olduğuna `diff` ve `gate` karar verir.

**Uygulamamın API'si değişecek mi?** Hayır. Çağıranlar aynı fonksiyonları import eder (ya da siz
güven kazanırken ikisini de çalıştırıp orijinalin sonucunu döndüren shadow modülünü).

**Rust her zaman daha mı hızlı?** Hayır, rust-anything de bunu söyler. Öğe başına bir kez çağrılan
küçük bir fonksiyon Rust'ta çoğu zaman daha yavaştır, çünkü her çağrı bir köprüyü geçer; V8, JVM ve Go
bu tür fonksiyonları nanosaniyeler içinde çalıştırır. `profile` etrafındaki döngüyü bulur, `--batch`
tüm döngüyü taşır ve `bench` yayına almadan önce bir karar verir. numba, Cython veya JAX ile zaten
derlenmiş kod da makine kodu olarak çalışır: `profile` ve `analyze` onu işaretler, çünkü onu port etmek
pek hız kazandırmaz.

**Kodum sayısal; float'lar birebir eşleşecek mi?** Çoğu zaman hayır: işlem sırası, fused
multiply-add ve matematik kütüphanesi derleyiciler arasında farklıdır. `--float-tolerance 1e-9` ile
kaydedin (`record` veya `app record`); float'lar büyük olan değerin bu oranı içinde eşleşir (1'in
altında mutlak). Tam sayılar, metin ve yapı yine birebir eşleşmek zorundadır.

**Elimde yalnızca APK, JAR veya .exe olan bir uygulamayı port edebilir mi?** Hayır. Kaynak kodu port
eder: fonksiyonları ayrıştırır, her birinin ne yaptığını kaydeder ve Rust'ı çalışan orijinale karşı
kontrol eder. Derlenmiş bir uygulamada bunların hiçbiri yoktur ve `analyze` bunu söyler. Bir binary'nin
görünen davranışından yeni bir Rust uygulaması yazmak ayrı bir projedir.

**Savaşta sınanmış C kodunu port etmeli miyim?** Çoğu zaman hayır, ve `analyze` size nerede olduğunu
söyler. Donanım register'larına dokunan, derleyicinin tip boyutlarına veya bellek düzenine dayanan ya
da inline assembly kullanan C (`volatile`, bitfield'lar, packed struct'lar, `__asm__`, adrese cast
edilen tam sayılar) "C'de tut" olarak işaretlenir: sizin makinenizdeki bir kayıt hedef hakkında hiçbir
şey kanıtlamaz, kararlı sürücü veya firmware kodu da yeniden yazımdan pek bir şey kazanmaz. Etrafındaki
taşınabilir mantık (ayrıştırma, protokoller, veri işleme) iyi taşınan kısımdır.

**Electron uygulamamı port edebilir mi?** Mantığı evet; pencereler web sayfası olarak kalır. `analyze
--whole-app` Electron'u fark eder ve renderer olduğu gibi kalırken main process'i parça parça planlar.
UI'ı Tauri'ye (Rust backend üzerinde aynı web UI) taşımak, mantık Rust olduktan sonraki ayrı bir adımdır.

**Peki C#, Kotlin veya Swift?** C# önizlemede (bkz. [Diller](#diller)); Kotlin ve Swift henüz
desteklenmiyor. Her dil, uçtan uca test edilmiş bir ayrıştırıcı, bir kaydedici, bir köprü ve bir
replay sürücüsü gerektirir. İhtiyacınız olan dil için bir issue açın (ya da var olanı oylayın).

**Rust orijinalinden çok daha büyük olmaz mı?** Olmamalı. `gate` portun satır sayısını orijinalinkiyle
karşılaştırır ve 3x'in üzerinde (import'lar ve imzalar için artı 50 satır) başarısız olur: bu
genellikle bir crate'in zaten yaptığı şeyi elle yazmak ya da vakaları tek tek ele almak demektir.
`analyze` kullanılacak crate'leri listeler.

**Parça parça port etmek Rust'ı eski uygulamanın tasarımına kilitlemez mi?** Yalnızca ikisi yan yana
çalıştığı sürece. Kayıtlar davranışı uygulamanın iç yapısında değil, kenarlarında (bir CLI'ın çıktısı,
bir sunucunun yanıtları, bir modülün export edilen fonksiyonları) kontrol eder. Birimler hâlâ köprüyü
geçerken eski yapıyı yansıtın; `app lift` orijinali kaldırdıktan sonra Rust'ı özgürce yeniden
yapılandırın, `app replay` davranışı yine kanıtlar. Hiçbir şey orijinale geri çağrı da yapmaz: front
door onu ayrı bir süreç olarak çalıştırır (ya da HTTP'yi ona iletir), köprülenen birimler orijinal
tarafından çağrılır, asla tersi değil, ve callback'ler kaynak dilde kalır.

**Kodum makinemden çıkıyor mu?** Hayır: rust-anything yerelde çalışır ve kodunuzun hiçbir kısmını
hiçbir yere göndermez. Cargo crate'leri her zamanki gibi indirir; ajanınızın model sağlayıcısı ise
ajanınızın ona gönderdiğini kendi politikası çerçevesinde görür.

**Neyin kurulu olması gerekiyor?** Rust ve port ettiğiniz dilin runtime'ı (bkz.
[Kurulum](#kurulum)).

**Bir şey bozuldu.** Komutu, çıktısını ve platformunuzu içeren bir issue açın.

## Sponsorlar

rust-anything ücretsiz ve açık kaynaklıdır. İşinize yarıyorsa lütfen sponsor olmayı düşünün. Desteğiniz geliştirmenin sürmesini sağlar.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="GitHub'da rust-anything'e sponsor olun" /></a>
</p>

### Şirket sponsorları

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Bireysel sponsorlar

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

## Katkıda bulunma

Issue'lar ve pull request'ler memnuniyetle karşılanır; [CONTRIBUTING.md](../CONTRIBUTING.md) kurulumu,
testlerin nereye gittiğini ve yeni bir dilin nasıl ekleneceğini anlatır. Tasarım kararları ve
gerekçeleri [DECISIONS.md](../DECISIONS.md) içindedir. Gerçek portların vaka çalışmaları özellikle
memnuniyetle karşılanır. Lütfen güvenlik sorunlarını gizli olarak bildirin ([SECURITY.md](../SECURITY.md))
ve [davranış kurallarına](../CODE_OF_CONDUCT.md) göz atın.

## Lisans

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Reponuzdaki portlar ve üretilmiş kod sizindir.
