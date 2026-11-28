<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="Die rust-anything-Krabbe mit einem Code-Tag als Mund">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">von <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · Deutsch · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>Diese Übersetzung wird von der Community gepflegt und kann hinter dem <a href="../README.md">englischen README</a> zurückliegen.</sub></p>

<p align="center"><em>Schreibe deine gesamte App in Rust neu. Halte sie dabei durchgehend lauffähig.</em></p>

<p align="center"><em>CLIs, Server und Bibliotheken – Stück für Stück, bei jedem Schritt gegen das Original geprüft.</em></p>

<p align="center">Node.js und TypeScript · Python · C · Go · Ruby · Java · PHP und C# in der Vorschau</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="crates.io-Version"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="npm-Version"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 Sprachen">
  <a href="#funktioniert-mit"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="Funktioniert mit 4 Agenten"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Tests"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="MIT-Lizenz"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="GitHub-Sterne"></a>
</p>

<p align="center">bis zu 20× schneller · 38.251 aufgezeichnete Fälle wiedergegeben · 0 Abweichungen · ein Befehl</p>

<p align="center">
  <img src="assets/race.gif" alt="Eingabe von user.profile in die x18n-Suche über 50.000 Schlüssel: TypeScript benötigt 143 ms, der rust-anything-Batch 6,9 ms – bei jedem Tastenanschlag mit exakt denselben Ergebnissen." width="820">
</p>

**Schreibe deine gesamte App Stück für Stück in Rust neu.** rust-anything zeichnet auf, was deine
Node.js- (TypeScript/JavaScript), Python-, C-, Go-, Ruby- oder Java-App heute tut, und prüft dann
jeden Teil der Rust-Neuimplementierung gegen diese Aufzeichnung, bevor es weitergeht – bis die App
reines Rust ist. CLIs, HTTP-Server und Bibliotheken; dein Coding-Agent (oder du selbst) schreibt
das Rust. Es kann nur erfassen, was die Aufzeichnung abdeckt: siehe
[Was es nicht abfangen kann](#was-es-nicht-abfangen-kann). Du brauchst nur den langsamen Teil schnell?
Portiere genau diesen, einen Hot Path nach dem anderen:

| Reale Arbeitslast, gleiche Ergebnisse wie das Original | Original | Mit rust-anything |
| --- | ---: | ---: |
| x18n-Seitenleistensuche, 50.000 Schlüssel (TypeScript, Node) | 10 ms pro Anfrage | **0,5 ms: 20× schneller** |
| Dieselbe Suche im Browser (wasm, ein Thread) | 10 ms | **0,95 ms: 11,5×** |
| `slugify` über 20.000 Strings (Python) | 98 ms | **17× schneller** |
| `Shellwords.shellescape` aus Rubys Standardbibliothek, 50.000 Werte | 88 ms | **11,8× schneller** |
| `Slugify` über 50.000 Strings (Go) | 49 ms | **4× schneller** |
| `slugify` über 50.000 Strings (Java) | 43 ms | **3× schneller** |

Gemessen auf 4 Kernen; zu jedem Wert gibt es einen Benchmark in [`demo/`](../demo), der zuerst
prüft, dass die Ergebnisse identisch sind. Rust für jede kleine Funktion einzeln aufzurufen ist meist
*langsamer* als ein JIT; rust-anything findet die Schleife, deren Auslagerung sich lohnt, und
verschiebt sie.

> rust-anything ist ein unabhängiges Projekt und steht in keiner Verbindung zum Rust Project oder
> der Rust Foundation und wird von diesen nicht unterstützt. „Rust“ ist eine Marke der Rust Foundation.

## Schnellstart

Füge dies in Claude Code, Codex, Cursor oder Gemini CLI ein und lass deinen Agenten es installieren:

```text
Installiere rust-anything: Führe `cargo install rust-anything` aus und danach `rust-anything setup`.
Sag mir Bescheid, wann ich dich neu starten soll.
```

Oder selbst:

```sh
cargo install rust-anything   # von crates.io
rust-anything setup           # registriert es bei Claude Code, Codex, Cursor und Gemini CLI
```

Noch keine Rust-Toolchain? Vorgefertigte Binärdateien für macOS, Linux und Windows hängen an jedem
[GitHub-Release](https://github.com/erkamyaman/rust-anything/releases), und für JavaScript-Projekte
installiert `npm install -g rust-anything` dieselbe Binärdatei.

In Claude Code kannst du es auch als Plugin installieren (der MCP-Server und der Skill; das obige CLI
muss in deinem `PATH` liegen):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` trägt den MCP-Server bei jedem gefundenen Agenten ein und installiert den Workflow-Skill dort,
wo der Agent Skills einliest. Deine übrigen Einstellungen bleiben erhalten, ein erneutes Ausführen ist
gefahrlos und `--remove` löscht die eingetragenen Konfigurationen wieder (ohne frühere Werte von
Einträgen wiederherzustellen, die `setup` aktualisiert hat). Frage deinen Agenten anschließend zum Beispiel:

- *"Schreibe dieses CLI mit rust-anything vollständig in Rust neu und beweise, dass es sich identisch verhält."*
- *"Diese Suche fühlt sich langsam an. Erstelle ein Profil mit rust-anything und verlagere die Hot Loop nach Rust."*
- *"Plane mit rust-anything eine Migration von `src/parser/` nach Rust; portiere die erste Einheit und verifiziere sie."*
- *"Vergleiche die Rust-Portierung in `rust/text-rs` im Benchmark mit dem Original und sag mir, ob wir sie ausliefern können."*

### Funktioniert mit

| Agent | `rust-anything setup` ergänzt |
| --- | --- |
| Claude Code | MCP-Server in `~/.claude.json`, Skill in `~/.claude/skills/` |
| Codex | MCP-Server in `~/.codex/config.toml`, Skill in `~/.codex/skills/` |
| Cursor | MCP-Server in `~/.cursor/mcp.json` |
| Gemini CLI | MCP-Server in `~/.gemini/settings.json` |
| Jeder andere MCP-Client | `rust-anything mcp` manuell als stdio-Server hinzufügen (siehe [Installation](#installation)) |

Bevor eine bestehende Datei geändert wird, legt `setup` daneben eine Kopie an (`<file>.rust-anything.bak`).

Oder führe die Schritte selbst aus:

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile findet fuzzyScore in einer Schleife, bridge --batch erzeugt das Rust-Crate, gate besteht mit 2000/2000 aufgezeichneten Fällen, und der Benchmark zeigt 20,7× schneller als TS." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # was heiß läuft und wer es aufruft
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# src/port.rs schreiben (oder vom Agenten schreiben lassen), dann:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # jeder aufgezeichnete Fall muss übereinstimmen
rust-anything bench rust/fuzzy-rs                      # schneller? Das Urteil sagt es dir
rust-anything gate rust/fuzzy-rs                       # bestanden heißt: bereit
```

rust-anything übersetzt keinen Code automatisch: Dein Coding-Agent (Claude Code, Codex, Cursor, …) oder
du selbst schreibst das Rust. rust-anything liefert genau das, was ein Agent nicht verlässlich erraten
kann: wo die Zeit bleibt, was zuerst und in welcher Reihenfolge portiert werden sollte, eine Bridge,
damit der übrige Code das Rust mit unveränderter API aufruft, das exakte Verhalten, dem die Portierung
entsprechen muss, einen sicheren Weg zur Auslieferung und ein Gate, das anzeigt, wann eine Portierung
fertig ist.

## Sprachen

| Sprache | Einheit | Bridge | Aufgezeichnet und wiedergegeben durch |
| --- | --- | --- | --- |
| TypeScript/JavaScript | Ordner oder Datei | napi-rs oder wasm-bindgen mit einem generierten binären Wire-Format; Klassen und async inklusive | Node, führt die `.ts`-Quellen direkt aus |
| Python | Paket oder Modul | PyO3 (abi3), direkte Konvertierung, typisierte Exceptions | Python, importiert das Original |
| C | `.c`-Datei | `extern "C"`-Funktionen mit den Originalnamen und einem Header | das Original, kompiliert als Shared Library, aufgerufen über ctypes, ein Fork pro Fall |
| Go | Paket | typisierte cgo-Aufrufe und ein generiertes binäres Wire-Format in einem Paket mit der Original-API | einen generierten Go-Treiber, gebaut als eigenes Modul |
| Ruby | Datei oder Ordner mit Modulfunktionen | eine magnus-Erweiterung unter den ursprünglichen Modulen | einen generierten Ruby-Treiber |
| Java | Paket mit `public static`-Methoden | typisiertes JNI und ein generiertes binäres Wire-Format in Wrapper-Klassen mit den Originalmethoden | einen generierten Reflection-Treiber |
| PHP (Vorschau) | Ordner mit Funktionen und `public static`-Methoden | als Nächstes geplant: PHP FFI über ein C-ABI | heute schon ganze Apps: `app record`, `app replay` und die Front Door, für CLIs und Server (`php -S`) |
| C# (Vorschau) | Ordner mit `public static`-Methoden | als Nächstes geplant: P/Invoke über ein C-ABI | heute schon ganze Apps: `app record`, `app replay` und die Front Door, für CLIs und ASP.NET-Server (`dotnet <app>.dll`) |

Jede Sprache außer C erhält außerdem Batch-Klassen (`--batch`): Die Elemente überqueren die Grenze
einmalig und bleiben in Rust, und jeder Aufruf verarbeitet sie alle auf allen Kernen.

Die Sprache wird anhand des Repositorys erkannt (`go.mod`, `pom.xml`, eine `.csproj` oder `.sln`,
`pyproject.toml`, `Gemfile`, `composer.json`, `package.json`, sonst die häufigsten Quelldateien);
`--lang` überschreibt dies. Typen stammen aus dem Quellcode: TS-Typen, Python-Type-Hints, C-, Go-,
Java- und C#-Signaturen, Ruby-YARD-Tags, PHP-Typen und phpdoc; untypisierte Parameter, die als Zahlen
verwendet werden, werden als Zahlen abgeleitet.

PHP ist in der Vorschau: `analyze` plant eine PHP-App (Composer-Pakete und PSR-4-Autoloading, Risiken
wie lose Vergleiche und Integer-Überläufe in Floats, Zuordnung von Composer-Paketen zu Crates), und ein
PHP-CLI oder -Server lässt sich aufzeichnen, wiedergeben und hinter eine Rust-Front-Door stellen. Das
Portieren einzelner Einheiten nach Rust über das PHP-FFI ist der nächste Schritt
([Issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# ist auf dieselbe Weise in der Vorschau: `analyze` liest `.csproj`-Projekte und ihre NuGet-Pakete
(auf Crates abgebildet), löst `using`-Direktiven zu Ordnern auf und markiert C#-Eigenheiten
(`decimal`, `dynamic`, verzögerte LINQ-Abfragen, `Task`, `lock`, Reflection). Ein C#-CLI oder
ASP.NET-Server lässt sich aufzeichnen, wiedergeben und hinter eine Rust-Front-Door stellen; das
Portieren einzelner Einheiten über P/Invoke folgt als Nächstes.

## So funktioniert es

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 wo die      was zuerst  Rust-Crate was das    du oder     jeder    schneller? beide       bestanden =
 Zeit        portiert    und        Original   dein Agent  aufgez.  das        parallel    wirklich
 bleibt      wird        Wrapper    tut        schreibt es Fall     Urteil     im Betrieb  fertig
```

Das Original bleibt die maßgebliche Referenz (Source of Truth): `record` führt es mit Randfällen (und
deinen eigenen Eingaben) aus und speichert, was es zurückgibt oder wirft; `diff` spielt jeden Fall
gegen Rust ab; nichts wird ausgeliefert, bis alle Fälle übereinstimmen und `gate` besteht. Aufrufer
behalten durchgehend die ursprüngliche API.

Eine ganze App durchläuft dieselbe Schleife Einheit für Einheit, innerhalb eines Rahmens, der das
gesamte Programm beweist ([Eine ganze App portieren](#eine-ganze-app-portieren)):

```
analyze --whole-app ──> app record ──> app front-door ──> pro Einheit: obige Schleife, dann app wire ──> app lift
 Struktur, jede          was die App    Rust übernimmt     Gate bestanden, also antwortet die             reines Rust,
 Abhängigkeit, zu        von außen      den Einstiegspunkt; Einheit in Rust: Replay 100 %,                durch Replay
 treffende               tut            das Original       Fallback-Rate sinkt                            bewiesen
 Entscheidungen                         antwortet noch
```

## Die Schleife

| Schritt | Befehl | Was er tut |
| --- | --- | --- |
| 0. Profile | `rust-anything profile <repo> -- node bench.mjs` | Führt eine reale Arbeitslast unter dem Profiler der jeweiligen Sprache aus (node, cProfile, `go test` pprof, JFR, ein Ruby-Tracer): Hot Functions nach inklusiver Laufzeit, ihre Aufrufer und welche Schleifen sich für Batches eignen; markiert Code, der bereits kompiliert ist (numba, Cython, JAX), da Rust dort wenig bringt |
| 1. Planen | `rust-anything analyze <repo>` | Einheiten, Portierungsreihenfolge, Risiken mit `file:line`, Bridge pro Einheit, Passgenauigkeit von Abhängigkeiten zu Crates, beste Starteinheiten; `--whole-app` ergänzt Einstiegspunkte und Struktur, jede (importierte oder deklarierte) Abhängigkeit samt Crate, Gruppen (Einheiten, die sich gegenseitig importieren, wandern zusammen) sowie nummerierte Entscheidungen mit empfohlener Antwort |
| 2. Bridge | `rust-anything bridge <repo> <unit>` | Crate mit den Bindings (`lib.rs` sowie dem Wrapper, den die Quellsprache lädt) und Stubs zum Portieren (`port.rs`); `--batch fn:param` ergänzt eine Klasse, die viele `param`-Werte in Rust hält |
| 3. Aufzeichnen | `rust-anything record <crate>` | Führt das Original mit generierten Randfällen (Nicht-ASCII, Emoji, `-0`, `NaN`, Ganzzahlen statt erwarteter Floats, …) sowie jeder semantischen Falle in jedem Parameter (String-Länge und -Groß-/Kleinschreibung, vorzeichenbehaftete Division, Überlaufgrenzen, Float-Ausgabe, Map- und Sortierreihenfolge) aus und speichert `cases.jsonl`; `--float-tolerance 1e-9` erlaubt Abweichungen bei Floats innerhalb dieses relativen Anteils für numerischen Code |
| 3. Bauen | `rust-anything build <crate>` | Baut die Rust-Seite: `.node`, wasm-Paket, Python-Erweiterung oder Shared Library |
| 3. Abgleichen | `rust-anything diff <crate>` | Spielt die aufgezeichneten Fälle gegen Rust ab, aufgerufen wie von den Aufrufern des Originals; listet Abweichungen auf |
| 3. Benchmark | `rust-anything bench <crate>` | Misst die Laufzeit der aufgezeichneten Fälle auf dem Original und auf Rust inklusive Bridge |
| 4. Shadow | `rust-anything shadow <crate>` | Drop-in-Ersatz, der beide ausführt, das Ergebnis des Originals zurückgibt und Abweichungen meldet; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Gate | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, Tests, `unsafe`-Audit, nichts Unportiertes, ein aufgezeichneter Fehlerfall für jeden Fehlerpfad des Originals, kein `unwrap`/`expect`/`panic!`, wo das Original einen Fehler liefert (außer mit `// INFALLIBLE: <Grund>` markiert), Build, API, Verhalten |
| Agenten | `rust-anything setup` | Registriert den MCP-Server (`rust-anything mcp`, jeder Schritt als Tool) und den Workflow-Skill ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) bei deinen Coding-Agenten |

## Eine ganze App portieren

Das Ziel ist eine reine Rust-App, die sich genau wie das Original verhält – mit dem Original als Referenz.
Dein Agent schreibt das Rust; rust-anything ordnet die Arbeit, legt das Grundgerüst an und beweist
jeden Schritt. Der [Whole-App-Skill](../skills/rust-anything/whole-app.md) führt den Agenten
hindurch, beginnend mit den Entscheidungen, die nur du treffen kannst:

- **Grilling**: Der Agent fragt in Runden – jede Frage mit einer empfohlenen Antwort –, bis jede
  Entscheidung geklärt ist, von der die Portierung abhängt, und hält jede davon als ADR in
  `rust/DECISIONS.md` fest, ergänzt durch `rust/GLOSSARY.md` zur Zuordnung der Originalbegriffe zu
  Rust-Namen.
- **Recherche**: Hintergrund-Agenten lesen die Primärquellen jeder Abhängigkeit und schreiben
  `rust/research/<topic>.md` mit jeder gefundenen semantischen Falle.
- **Über Sitzungen hinweg**: `rust/MAP.md` listet jede Einheit samt Status; eine Sitzung beansprucht
  eine Einheit vor Beginn, und jeder Checkpoint hinterlässt eine `rust/HANDOFF.md` für die nächste
  Sitzung. Einheiten innerhalb einer Welle lassen sich parallel durch Subagenten portieren.
- **Cutover**: Der Agent erledigt alles Mögliche und schreibt `rust/cutover.sh`, ein interaktives
  Skript für die Schritte, die nur du ausführen kannst (Deployments, DNS, Secrets), mit einem
  Rückweg bei jedem Schritt.

Grilling, Recherche und diese Praktiken sind von
[Matt Pococks Skills](https://github.com/mattpocock/skills) übernommen.

Zuerst planen: `rust-anything analyze . --whole-app` ergänzt die App-Struktur (CLI, Server oder
Bibliothek) und Einstiegspunkte, jede externe Abhängigkeit (importiert oder deklariert) mit Rust-Crate
und Passgenauigkeit, die Portierungsreihenfolge in Gruppen (Einheiten, die sich gegenseitig importieren,
wandern zusammen) sowie nummerierte Entscheidungen mit einer empfohlenen Antwort: zu behaltende
Einheiten, blockierte Einheiten, Abhängigkeiten ohne oder mit nur teilweisem Crate.

Danach das gesamte Programm von außen beweisen. `record` und `diff` beweisen eine einzelne Einheit;
`app record` und `app replay` beweisen die App, für CLIs und Server in jeder der sechs Sprachen (die
App ist dabei eine Blackbox):

```sh
rust-anything app record . -- python3 cli.py          # der Befehl, der das Original startet
rust-anything app replay .                            # das Original muss zu 100 % bestehen
rust-anything app replay . --build "target/release/mytool"
```

- `app record` führt das Original mit den eigenen dokumentierten Beispielen der App (`$ mytool ...`-Zeilen
  in ihren Markdown- und Shell-Dateien samt den dort genannten Dateien), einer `--inputs`-JSONL-Datei
  (`{"name", "args", "stdin", "env", "files"}`) und daraus abgeleiteten semantischen Fallen
  (Nicht-ASCII- und Emoji-Strings, negative Division und Modulo, Überläufe, sehr große und winzige
  Floats, Map-Reihenfolge, fehlende Dateien) aus. Jeder Fall läuft zweimal; was zwischen den beiden
  Läufen abweicht, wird zu einem `[..]`-Platzhalter. `--normalize timestamps|uuids|key-order` oder
  `--normalize name=regex` fügt Normalisierer hinzu, die mit den Fällen gespeichert werden.
- Fälle sind [trycmd](https://docs.rs/trycmd)-Dateien in `rust/app-cases/`: `<case>.toml` (argv, env,
  Exit-Code), `.stdin`, `.stdout`, `.stderr`, `.in/` (Eingabedateien) und `.out/` (geschriebene Dateien).
  Du kannst sie von Hand lesen und bearbeiten; ein Rust-Test kann sie mit `trycmd` ausführen, sobald die
  Portierung ein Binary hat.
- `app replay` führt jeden beliebigen Build gegen die Fälle aus, gibt `passed/total` aus, schreibt
  `rust/app-cases/replay-report.md` mit einem Diff pro fehlgeschlagenem Fall und beendet sich bei jeder
  Abweichung mit einem Exit-Code ungleich null. Ein Build, der an die durch
  `RUST_ANYTHING_FALLBACK_LOG` benannte Datei anhängt (eine Zeile pro Fallback auf das Original) – wie
  es die Front Door unten tut –, erhält zusätzlich einen Bericht über seine Fallback-Rate.
- `app replay --case <name>` führt einen einzelnen Fall anhand des Namens aus dem Bericht erneut aus:
  die schnelle, wiederholbare Schleife zum Beheben einer Abweichung, bevor wieder alles läuft.

Danach den Einstiegspunkt nach Rust verlagern und ihm die Befehle Einheit für Einheit übergeben:

```sh
rust-anything app front-door .                            # rust/app: jeder Befehl startet das Original
rust-anything app wire . textkit --command upper          # nachdem textkit-rs das Gate bestanden hat
# Klebecode in rust/app/src/units/textkit.rs schreiben, dann:
rust-anything app wire . textkit                          # wieder 100 %, niedrigere Fallback-Rate
```

- `app front-door` legt das Grundgerüst für `rust/app` an, ein Rust-Binary benannt nach der App: ein
  clap-Parser für die Befehle und Flags aus den aufgezeichneten Fällen, bei dem jeder Befehl das
  Original mit denselben argv, stdin und Umgebungsvariablen ausführt und dessen Ausgabe sowie Exit-Code
  durchreicht. Jeder Fallback wird gezählt, sodass das Replay der frischen Front Door 100 % bestanden
  bei 100 % Fallback ergibt (es baut und führt das Replay zur Demonstration direkt aus). Es
  überschreibt `rust/app` niemals: Der Code gehört ab diesem Zeitpunkt dir.
- `app wire <repo> <unit> --command <name>` führt `gate` auf dem Crate der Einheit aus (`--skip-gate`,
  wenn es gerade bestanden hat), fügt es als Bibliothek zu `rust/app` hinzu, erzeugt einmalig
  `src/units/<unit>.rs`, damit du oder dein Agent es ausfüllen könnt (Argumente parsen, `<crate>::port`
  aufrufen, ausgeben, was das Original ausgibt), leitet die Befehle dorthin um, baut und führt das
  Replay aus. `RUST_ANYTHING_UNIT_<NAME>=original` schickt eine angebundene Einheit bis zum Lift zurück
  zum Original.

Binde den eigenen Namen der App als Befehl ein (`--command mytool`) für argv-Aufrufe ohne Befehlsnamen:
keine Argumente, unbekannte Befehle, Usage-Fehler.

Wenn das Replay mit Fallback-Rate 0 besteht und jede Einheit das Gate passiert, mache daraus eine reine
Rust-App:

```sh
rust-anything app lift .
```

- `app lift` verweigert die Ausführung, bis beides erfüllt ist, und nennt die Blocker: Fälle, die noch
  auf das Original zurückfallen, Stub-Klebecode oder Einheiten, die das Gate nicht bestehen.
- Zunächst auf einer Kopie entfernt es den Fallback-Pfad und die Kill-Switches, macht aus jedem
  Einheits-Crate eine gewöhnliche Bibliothek von `rust/app` (ohne `cdylib`, Bindings oder generierte
  Wrapper) und fügt `rust/app/tests/app_cases.rs` hinzu, das `rust/app-cases` bei `cargo test` über
  trycmd ausführt – sodass die CI nichts außer cargo braucht.
- Danach läuft die Lift-Checkliste: fmt, clippy `-D warnings` und Tests für jede Einheit und für
  `rust/app`, jedes in `rust/DECISIONS.md` genannte Target gebaut oder geprüft, sofern installiert,
  zur Laufzeit gelesene Dateien und nicht eingebettete Asset-Ordner sowie ein Replay auf dem reinen
  Binary. Erst wenn alles davon besteht, werden die Änderungen zurückgeschrieben. Das Original wird
  niemals angerührt.

### Server

Dieselben Befehle beweisen HTTP-Server. `--http` gibt an, dass der Befehl einen Server startet; er
bezieht seinen Port aus `PORT` oder `{port}` im Befehl (`--port` für Server, die immer auf demselben
Port lauschen):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: jede Route wird geproxyt
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Anfragen stammen aus `curl`-Zeilen in der App-Dokumentation (`curl -X POST -d ... http://localhost:8080/x`),
  `--inputs` (`{"name", "method", "path", "headers", "body"}`) und Fallen: Pfadsegmente und
  Query-Werte werden durch dieselben Fallen wie CLI-Argumente ersetzt, Bodys durch Text- und
  JSON-Fallen, plus eine unbekannte Route. Jeder Durchlauf startet den Server neu und sendet die
  Anfragen in Namensreihenfolge, sodass Zustand zwischen Anfragen erhalten bleibt.
- Fälle liegen in `rust/app-cases/http/<case>.toml` (die Anfrage, der Status und die relevanten Header)
  sowie `<case>.body` (der Response-Body, mit `[..]`, wo sich zwei Läufe unterschieden). `Date`,
  `Server` und andere pro Antwort wechselnde Header werden weggelassen; lösche jede Header-Zeile, die
  dich nicht interessiert.
- Die Front Door ist ein axum-Server, der das Original auf einem eigenen Port startet und jede Route
  weiterleitet, die keine Einheit beantwortet. `wire --route` akzeptiert axum-Routen:
  `METHOD /path/{param}`, `/path` für jede Methode, `*` für alles Weitere; der Klebecode erhält die
  Route, ihre Parameter und die Anfrage. `lift` entfernt den Proxy; HTTP-Fälle laufen dann in der CI
  über `app replay`.

### Bibliotheken

Eine Bibliothek hat keinen Prozess für ein Replay: Ihre öffentliche API ist die Front Door, und die
aufgezeichneten Fälle jeder Einheit sind der Beweis.

```sh
rust-anything app front-door .        # rust/app: ein Rust-Crate mit der öffentlichen API
# jede Einheit durch die Schleife: bridge, record, port.rs, build, diff, gate; dann:
rust-anything app wire . textkit-rs   # aus rust/app re-exportiert; das Original importiert sein Shadow-Modul
rust-anything app replay .            # Fälle jeder angebundenen Einheit; Fallback = noch im Original verbliebene Exporte
rust-anything app lift .
```

- `app front-door` ermittelt die öffentliche API (die Exporte jeder Einheit), wenn das Repository kein
  `main` und keinen Server besitzt (sonst `--library`), und legt `rust/app` als Library-Crate an. Jede
  angebundene Einheit wird darin ein Modul: `pub use textkit_rs::port as textkit;`.
- `app wire` nimmt ein von `bridge` erzeugtes Crate, führt `gate` aus und schreibt das Shadow-Drop-in
  der Einheit: Das Originalpaket importiert es anstelle der Einheit, sodass seine Aufrufer die
  Original-API behalten und Rust erreichen. `RUST_ANYTHING_UNIT_<NAME>=original` schaltet die Einheit
  zurück (C: ohne die Flags des Shadows bauen).
- `app replay` führt die aufgezeichneten Fälle jeder angebundenen Einheit über ihre Bindings aus. Die
  Fallback-Rate ist der Anteil öffentlicher Exporte, den Rust noch nicht beantwortet: nicht angebundene
  Einheiten sowie Exporte, die `bridge` in der Quellsprache belässt.
- `app lift` erfordert Fallback 0 und dass jede Einheit `gate` besteht; es entfernt die Bindings,
  Wrapper und Shadows aus den Einheiten und hinterlässt `rust/app` als eine reine Rust-Bibliothek. Es
  fasst keine `port.rs` an, sodass die Fälle, die über die Bindings passten, sie weiterhin beschreiben;
  die Checkliste warnt vor Dateien des Originals, die noch die Shadows importieren.

Alle fünf sind ebenfalls MCP-Tools: `app_record`, `app_replay`, `app_front_door`, `app_wire` und
`app_lift`.

## Fallstudie: Der Kern von x18n

Alle 29 Funktionen des Kerns von x18n, die ohne API-Änderung verschoben werden können, wurden mit
rust-anything portiert: Jedes Gate besteht und 7.925 aufgezeichnete Fälle stimmen exakt überein.
`rust-anything bench` zeigte daraufhin, dass die Portierungen beim Aufruf aus JS langsamer sind als das
TS, weil die Bridge mehr kostet als die eigentliche Arbeit. Vollständiger Bericht:
[`demo/x18n-core`](../demo/x18n-core/README.md). Die Lehre ist eingebaut: Vor der Auslieferung einer
Portierung immer mit `bench` messen.

## Hot Paths: Die Daten in Rust halten

Eine Portierung, die einmal pro Element aufgerufen wird, zahlt die Bridge-Kosten einmal pro Element und
verliert gegen ein JIT. Was gewinnt, ist das Verschieben der Schleife: `profile` findet sie, und
`--batch` generiert eine Klasse, die die Elemente einmalig entgegennimmt und die Funktion pro Aufruf
über alle hinweg ausführt – auf allen Kernen, mit Typed-Array-Ergebnissen.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: ein Viertel des Laufs, von `matched` pro Schlüssel aufgerufen: als Batch bündeln
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // einmalig
const order = search.rank(query, 0)               // pro Tastenanschlag: Indizes, beste zuerst
```

Eine `FuzzyScoreIndex`-Struct in `port.rs` ersetzt die Standardschleife durch eine, die die Elemente
einmal vorbereitet und selbst ranken kann (`rank`): Sie hält die kleingeschriebenen Schlüssel samt
Zeichenmaske pro Schlüssel, eine Tabelle der jeweils ersten Position jedes häufigen Zeichens pro
Schlüssel (eine Abfrage mit einem Buchstaben ist eine einzige Spalte) sowie die Treffer der letzten
Abfrage (wer `se` nach `s` tippt, bewertet nur das neu, was `s` getroffen hat). Bei der
Seitenleistensuche von x18n über 50.000 Schlüssel, Buchstabe für Buchstabe getippt, mit identischen
Ergebnissen:

| | Pro Anfrage | vs. TS |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1× |
| TS mit derselben Eingrenzung wie der Index | 4,1–5,4 ms | 2× |
| Dieselbe Portierung, pro Schlüssel aufgerufen | - | 0,2–0,4× |
| `FuzzyScoreBatch`, Standardindex (4 Kerne) | 5,1 ms | 1,7× |
| `FuzzyScoreBatch` mit `FuzzyScoreIndex` (napi, 4 Kerne) | 0,45–0,56 ms | **18–22×** |
| Dasselbe mit wasm (ein Thread) | 0,95 ms | **11,5×** |

Selbst gegenüber TS mit derselben Eingrenzung ist Rust noch 7–12× schneller (wasm 5×). Wandle die
zurückgegebenen Indizes mit einer einfachen Schleife in Schlüssel um: `Array.from(order, i => keys[i])`
kostete 20× mehr, 0,4 ms.

Jede Sprache erhält Batches, und sie schlagen das Original selbst dort, wo Einzelaufrufe verlieren.
Dieselbe Arbeit auf 4 Kernen, identische Ergebnisse und Fehler (Benchmarks in jedem Demo-Ordner):

| Sprache | Arbeitslast | Original | Einzelaufruf-Portierung vs. Original | Batch vs. Original |
| --- | --- | ---: | ---: | ---: |
| TS | x18n-Suche, 50.000 Schlüssel | 10 ms | 0,2–0,4× | **20×** |
| Python | `slugify`, 20.000 Strings | 98 ms | - | **17×** |
| Ruby | `slugify`, 20.000 Strings | 110 ms | - | **12,7×** |
| Ruby | `shellescape` (stdlib), 50.000 gemischte Werte | 88 ms | - | **11,8×** |
| Go | `Slugify`, 50.000 Strings | 49 ms | 0,93× | **4×** |
| Java | `slugify`, 50.000 Strings | 43 ms | 0,68× | **3×** |

Kompilierte Originale gewinnen weniger: Die Arbeit pro Element ist bereits schnell, also gewinnt der
Batch über die Anzahl der Kerne. Batch-Crates allozieren mit mimalloc: Mit dem System-Allocator war der
Go-Batch langsamer als ein einzelner Thread. Demo: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Echter Code in sechs Sprachen

Gos `path`, Rubys `shellwords`, Pythons `colorsys`, JDK- und glibc-Verhalten hinter kleinen Fassaden:
Jede Portierung besteht ihr Gate, insgesamt 13.010 aufgezeichnete Fälle. Die Durchläufe fanden und
behoben Bugs in rust-anything (Floats um einen ULP daneben über `serde_json`, C-Abstürze während der
Aufzeichnung, untypisierter Code, der Müll-Eingaben erhielt). Pro Funktion aufgerufen läuft die
Ruby-Portierung 4,4× schneller als Ruby und die Python-Portierung 1,35× schneller als CPython, während
Go- und Java-Blattfunktionen in ihrer eigenen Sprache schneller bleiben; als Batches gewinnen alle
(siehe Tabelle oben). Bericht: [`docs/real-world-languages.md`](./real-world-languages.md).

## Beispiel: Ein echtes Modul aus x18n

`packages/core/src/fuzzy.ts` aus [x18n](https://github.com/x18n-dev/x18n), auf beide Arten portiert in
[`demo/`](../demo):

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: bereit, wasm-bindgen (core läuft im Browser)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# src/port.rs schreiben
rust-anything gate demo/fuzzy-rs
```

Eine erste Portierung, die nach Rust-`char` indizierte, bestand einfache Tests, scheiterte aber an
`diff`:

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

JS `indexOf` zählt UTF-16-Code-Units, sodass ein Emoji zwei Positionen einnimmt. Die Portierung in
`demo/*/src/port.rs` nutzt die generierten `utf16`-Hilfsfunktionen und besteht 2000/2000 Fälle sowie
das Gate – sowohl als napi-rs (`demo/fuzzy-napi`) als auch als wasm-bindgen (`demo/fuzzy-rs`).

Der Plan, den rust-anything für ganz x18n erstellt: [`docs/examples/x18n.md`](./examples/x18n.md).

## Installation

```sh
cargo install --path .
```

`record`, `diff` und `bench` führen das Original in seiner eigenen Runtime aus: Node 22.6+ für TS
(führt `.ts`-Quellen direkt aus), Python 3.9+ für Python und C (ctypes), Go 1.21+, Ruby 3+, JDK 17+
(`javac` und `java`). C benötigt außerdem einen C-Compiler. wasm-Bridges benötigen zusätzlich
`rustup target add wasm32-unknown-unknown` und
`cargo install wasm-bindgen-cli --version <die wasm-bindgen-Version des Crates> --locked`; `build`
nennt die genaue Version.

Für Agenten registriert `rust-anything setup` alles automatisch (siehe Schnellstart). Um den MCP-Server
stattdessen von Hand für ein einzelnes Projekt hinzuzufügen (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## Was `bridge` entscheidet

- Exporte, die keine Bridge überqueren können, bleiben in der Quellsprache, mit Begründung, und das
  Shadow-Modul re-exportiert das Original. Für TS:
  Funktionen, die Funktionen annehmen oder zurückgeben, Generatoren und Iteratoren, RegExp,
  `instanceof`-Prüfungen, Generics sowie Werte, deren Typen (verfolgt über Imports, Re-Exporte und
  `extends`) Funktionen enthalten. `--keep "name: reason"` behält weitere, z. B. Code, der von
  `Intl`-Daten abhängt.
- TS-Typen werden auf Rust-Typen abgebildet, Typaliase über Imports aufgelöst und Parametertypen aus
  Standardwerten abgeleitet; strukturierte Werte überqueren die Grenze über ein generiertes binäres
  Wire-Format (JSON nur als Fallback für Strukturen, die das Wire-Format nicht modelliert).
- JSON kann `undefined`, NaN, Infinity, -0 oder einzelne Surrogate nicht ausdrücken: strukturierte
  Werte tragen Marker (`{"$undefined": true}`, `{"$num": "NaN"}`, `{"$utf16": [...]}`), die das
  generierte `index.cjs` übersetzt – mit Hilfsfunktionen in `js.rs` des Crates.

`record` führt TS-Quellen unverändert aus: Ein Node-Resolve-Hook folgt Bundler-artigen Imports
(`./errors` zu `./errors.ts`), `--resolve-from` stellt npm-Pakete bereit, wenn im Repo keine
installiert sind, und TS, das eine Transformation erfordert (Enums, Parameter-Properties), wird erneut
mit `--experimental-transform-types` versucht.

## Was `analyze` prüft

- Pakete (`package.json`) und Quelldateien; überspringt `node_modules`, Build-Ausgaben, Fixtures,
  Playgrounds, Tool-Konfigurationen. Vue-/Svelte-/Astro-`<script>`-Blöcke werden nach Imports geparst.
- **Einheiten**: ein Ordner mit Quelldateien oder eine Datei im Quellwurzelverzeichnis eines Pakets.
- **Wellen**: Die Imports einer Einheit kommen in frühere Wellen; Import-Zyklen werden gemeinsam portiert.
- **Bridge**: napi-rs, wenn die Einheit oder etwas, das sie importiert, Node benötigt; wasm-bindgen für
  portablen Code; in JS behalten für UI- und Editor-Code.
- **Readiness** (wie sicher) und **Priority** (sicher und lohnend: Schleifen und String-Verarbeitung,
  Tests, Größe).

| Risiko | Schweregrad | Beispiel |
| --- | --- | --- |
| String-Offsets | hoch | `slice`, `indexOf`, `matchAll`, das `d`-Flag: UTF-16 vs. UTF-8 |
| Regex-Syntax | hoch | Lookaround, Backreferences, `y`: nicht im `regex`-Crate |
| Dynamische Regex | hoch | `new RegExp(userPattern)`: JS-Syntax zur Laufzeit |
| Dynamischer Code | hoch | `eval`, `new Function`, berechnetes `import()` |
| Dynamische Typisierung | mittel | `any`, `'key' in value` |
| Geordnete Sammlungen | mittel | `Map`, `Set`, `Object.keys`: Einfügereihenfolge |
| Async, Generatoren | mittel | Promise- und Generator-Grenzen |
| Klassenvererbung, Reflection | mittel | `extends`, `Proxy`, `Reflect`, `Symbol` |
| Callback-basierte APIs | mittel | Funktions-Parameter und -Methoden: gesprächige Bridges |
| Exceptions, Zahlen, JSON | niedrig | `throw`, Bit-Operationen, `JSON.stringify`-Reihenfolge |

## Entwicklung

```sh
cargo test                        # Unit-Tests, Fixture-Repo, record/diff/shadow-Schleife (benötigt node), app record/replay je Sprache
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Design-Entscheidungen und ihre Gründe: [DECISIONS.md](../DECISIONS.md).

## Aktualisieren oder entfernen

```sh
cargo install rust-anything                                    # aktualisieren (Cargo)
npm install -g rust-anything@latest                            # aktualisieren (npm)
rust-anything setup                                            # Agenten-Einstellungen auffrischen
rust-anything setup --remove && cargo uninstall rust-anything  # entfernen (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # entfernen (npm)
```

`setup --remove` entfernt nur die Einträge von rust-anything; dabei wird die aktuelle Konfigurationsdatei
erneut als `<file>.rust-anything.bak` gesichert (wodurch das ursprüngliche `setup`-Backup überschrieben
wird) und bleibt erhalten, bis du sie löschst.

## Was es nicht abfangen kann

Bestanden bedeutet, dass Rust mit jedem aufgezeichneten Fall übereinstimmt – nicht mehr. Was bei
Neuimplementierungen beißt, lebt meist außerhalb der Aufzeichnung; kenne also die Grenzen:

- **Eingaben, die niemand aufgezeichnet hat.** Die generierten Fälle, die Fallen und deine eigenen
  `--inputs` bilden die Obergrenze. Ergänze echte Eingaben (Produktionsstichproben, Bug-Reports, die
  Test-Fixtures des Originals); die Nutzereingabe, die Produktion bricht, ist selten eine, an die ein
  Generator denkt.
- **Reguläre Ausdrücke.** Das `regex`-Crate hat weder Lookaround noch Backreferences, und selbst ein
  kompilierendes Muster kann `\w`, `\b`, `\d` sowie Groß-/Kleinschreibung bei Nicht-ASCII-Text anders
  behandeln als JS, Python oder Java. Ein Wechsel auf `fancy-regex` oder das Umschreiben des Musters
  kann jeden aufgezeichneten Fall bestehen und sich trotzdem bei einem türkischen punktlosen `ı` oder
  einem Zero-Width Joiner unterscheiden. `record` fügt jeder Funktion in einer Datei mit Regexen
  Regex-Fallen hinzu (diese, das Kelvin-Zeichen, langes s, arabisch-indische Ziffern, Zeilentrenner,
  Schluss-Sigma), aber fuzze deine echten Muster zusätzlich gegen echten Text.
- **Was sich zwischen Läufen ändert.** `record` führt das Original zweimal aus und sortiert, was sich
  unterschied: wechselnde Werte (Zeitstempel, IDs) werden zu Platzhaltern; gleiche Zeilen in anderer
  Reihenfolge (Hash-Maps, Nebenläufigkeit) werden in beliebiger Reihenfolge verglichen, sodass eine
  Portierung trotzdem exakt diese Zeilen erzeugen muss; eine abweichende Zeilenzahl wird zu `...`,
  was auf alles passt. `record` listet jede Art auf: Schau dir jede einzelne an, denn ein Unterschied
  durch Hash-Reihenfolge oder Nebenläufigkeit ist genau das, was sich in einer Portierung real
  verändern kann.
- **Floats.** Die Zahl-zu-Text-Formatierung unterscheidet sich zwischen Sprachen (`1e21`, `-0`,
  Nachkommastellen). Die Fallen enthalten diese Werte und sie müssen exakt übereinstimmen;
  `--float-tolerance` verzeiht nur Rundungsabweichungen, niemals Formatierung.
- **Alles außerhalb der Ausgabe.** Laufzeit, Speicherverbrauch, Nebenläufigkeit unter Last sowie
  Seiteneffekte außer stdout, stderr, Exit-Codes, geschriebenen Dateien und HTTP-Antworten
  (Netzwerkaufrufe, Datenbanken, Signale) werden nicht verglichen.
- **Andere Plattformen.** Eine Aufzeichnung beweist das Verhalten auf der Maschine, auf der sie lief.
  C-Code, dessen Ergebnisse von Typgrößen, Endianness oder dem Compiler abhängen, kann sich auf dem
  Zielsystem anders verhalten; `analyze` belässt hardwarenahes C aus diesem Grund in C.

## FAQ

**Schreibt es meinen Code automatisch um?** Nein. Es findet, was verschoben werden soll, generiert die
Bridge, zeichnet das Verhalten des Originals auf und prüft das Rust dagegen. Du oder dein Agent
schreibt das Rust in `port.rs`; `diff` und `gate` entscheiden, wann es stimmt.

**Wird sich die API meiner App ändern?** Nein. Aufrufer importieren dieselben Funktionen (oder das
Shadow-Modul, das beide ausführt und das Ergebnis des Originals zurückgibt, während du Vertrauen
aufbaust).

**Ist Rust immer schneller?** Nein, und rust-anything sagt das auch. Eine kleine Funktion, die einmal pro
Element aufgerufen wird, ist in Rust oft langsamer, weil jeder Aufruf eine Bridge überquert; V8, die
JVM und Go führen solche Funktionen in Nanosekunden aus. `profile` findet die Schleife darum herum,
`--batch` verschiebt die ganze Schleife, und `bench` liefert vor dem Ausliefern ein klares Urteil.
Code, der bereits von numba, Cython oder JAX kompiliert wurde, läuft ebenfalls als Maschinencode:
`profile` und `analyze` markieren ihn, da eine Portierung kaum Geschwindigkeit gewinnt.

**Mein Code ist numerisch; stimmen die Floats exakt überein?** Oft nicht: Auswertungsreihenfolge,
Fused Multiply-Add und die Mathe-Bibliothek unterscheiden sich zwischen Compilern. Zeichne mit
`--float-tolerance 1e-9` (`record` oder `app record`) auf, dann gelten Floats innerhalb dieses Anteils
des größeren Werts als passend (absolut unter 1). Ganzzahlen, Text und Struktur müssen weiterhin exakt
übereinstimmen.

**Kann es eine App portieren, die ich nur als APK, JAR oder .exe habe?** Nein. Es portiert Quellcode:
Es parst die Funktionen, zeichnet auf, was jede tut, und prüft das Rust gegen das laufende Original.
Eine kompilierte App bietet nichts davon, und `analyze` sagt das auch. Eine neue Rust-App anhand des
sichtbaren Verhaltens eines Binaries zu schreiben, ist ein anderes Projekt.

**Sollte ich kampferprobtes C portieren?** Oft nicht, und `analyze` zeigt dir, wo. C, das
Hardware-Register anfasst, auf Typgrößen oder Speicherlayout seines Compilers vertraut oder
Inline-Assembly nutzt (`volatile`, Bitfelder, packed Structs, `__asm__`, in Adressen gecastete
Ganzzahlen), wird als „keep in C“ markiert: Eine Aufzeichnung auf deinem Rechner beweist nichts über das
Zielsystem, und stabiler Treiber- oder Firmware-Code gewinnt wenig durch ein Umschreiben. Die portable
Logik drum herum (Parsing, Protokolle, Datenverarbeitung) lässt sich gut verlagern.

**Kann es meine Electron-App portieren?** Die Logik ja; die Fenster bleiben Webseiten. `analyze
--whole-app` erkennt Electron und plant den Main-Prozess Stück für Stück, während der Renderer bleibt,
wie er ist. Das UI zu Tauri zu verschieben (dieselbe Web-UI auf einem Rust-Backend) ist ein eigener
Schritt, sobald die Logik in Rust vorliegt.

**Was ist mit C#, Kotlin oder Swift?** C# ist in der Vorschau (siehe [Sprachen](#sprachen)); Kotlin und
Swift werden noch nicht unterstützt. Jede Sprache braucht einen Parser, einen Recorder, eine Bridge und
einen Replay-Treiber – alles End-to-End getestet. Eröffne ein Issue (oder stimme für eines ab) für die
Sprache, die du brauchst.

**Wird das Rust nicht viel umfangreicher als das Original?** Sollte es nicht. `gate` vergleicht die
Zeilenzahl der Portierung mit der des Originals und schlägt oberhalb von 3× (plus 50 Zeilen für Imports
und Signaturen) fehl: Das deutet meist darauf hin, von Hand zu schreiben, was ein Crate bereits
bietet, oder Fälle einzeln abzuhandeln. `analyze` listet die passenden Crates auf.

**Sperrt das stückweise Portieren das Rust nicht in das Design der alten App ein?** Nur solange beide
Seite an Seite laufen. Die Aufzeichnungen prüfen das Verhalten an den Außengrenzen der App (Ausgabe
eines CLIs, Antworten eines Servers, exportierte Funktionen eines Moduls), nicht ihre Interna. Spiegle
die alte Struktur, solange Einheiten noch die Bridge überqueren; sobald `app lift` das Original
entfernt hat, kannst du das Rust frei umstrukturieren, und `app replay` beweist weiterhin das Verhalten.
Es ruft auch nichts zurück ins Original: Die Front Door startet es als eigenen Prozess (oder leitet HTTP
dorthin weiter), überbrückte Einheiten werden vom Original aufgerufen und niemals umgekehrt, und
Callbacks bleiben in der Quellsprache.

**Verlässt mein Code meinen Rechner?** Nein: rust-anything läuft lokal und sendet nichts von deinem Code
irgendwohin. Cargo lädt wie gewohnt Crates herunter, und der Modellanbieter deines Agenten sieht, was
dein Agent ihm sendet, gemäß seiner eigenen Richtlinie.

**Was muss installiert sein?** Rust sowie die Runtime der Sprache, die du portierst (siehe
[Installation](#installation)).

**Etwas funktioniert nicht.** Eröffne ein Issue mit dem Befehl, seiner Ausgabe und deiner Plattform.

## Sponsoren

rust-anything ist kostenlos und Open Source. Wenn es dir bei der Arbeit hilft, ziehe bitte ein
Sponsoring in Betracht. Deine Unterstützung hält die Entwicklung am Laufen.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### Unternehmenssponsoren

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Einzelsponsoren

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

## Mitwirken

Issues und Pull Requests sind willkommen; [CONTRIBUTING.md](../CONTRIBUTING.md) behandelt die
Einrichtung, wohin Tests gehören und wie man eine Sprache hinzufügt. Design-Entscheidungen und ihre
Gründe stehen in [DECISIONS.md](../DECISIONS.md). Fallstudien echter Portierungen sind besonders
willkommen. Sicherheitsprobleme bitte vertraulich melden ([SECURITY.md](../SECURITY.md)), und beachte
den [Verhaltenskodex](../CODE_OF_CONDUCT.md).

## Lizenz

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Portierungen und generierter Code in
deinem Repository gehören dir.
