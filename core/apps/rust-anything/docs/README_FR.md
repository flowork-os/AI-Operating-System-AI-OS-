<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="Le crabe rust-anything, dont la bouche est une balise de code">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">par <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · Français · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · <a href="README_PT.md">Português</a></p>

<p align="center"><sub>Cette traduction est maintenue par la communauté et peut être en retard sur le <a href="../README.md">README anglais</a>.</sub></p>

<p align="center"><em>Réécrivez toute votre application en Rust. Gardez-la fonctionnelle tout du long.</em></p>

<p align="center"><em>CLI, serveurs et bibliothèques, morceau par morceau, vérifiés par rapport à l'original à chaque étape.</em></p>

<p align="center">Node.js et TypeScript · Python · C · Go · Ruby · Java · PHP et C# en aperçu</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="version crates.io"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="version npm"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 langages">
  <a href="#fonctionne-avec"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="Fonctionne avec 4 agents"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Tests"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="Licence MIT"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="Étoiles GitHub"></a>
</p>

<p align="center">jusqu'à 20x plus rapide · 38 251 cas enregistrés rejoués · 0 divergence · une seule commande</p>

<p align="center">
  <img src="assets/race.gif" alt="Saisie de user.profile dans la recherche de x18n sur 50 000 clés : TypeScript met 143 ms, le traitement par lots rust-anything met 6,9 ms, avec les mêmes résultats à chaque frappe." width="820">
</p>

**Réécrivez toute votre application en Rust, un morceau à la fois.** rust-anything enregistre ce que
fait aujourd'hui votre application Node.js (TypeScript/JavaScript), Python, C, Go, Ruby ou Java, puis
vérifie chaque morceau de la réécriture Rust par rapport à cet enregistrement avant de passer à la
suite, jusqu'à ce que l'application soit entièrement en Rust. CLI, serveurs HTTP et bibliothèques ;
votre agent de programmation (ou vous) écrit le code Rust. Il ne peut détecter que ce que
l'enregistrement couvre : voir [Ce qui lui échappe](#ce-qui-lui-échappe). Vous voulez seulement
accélérer la partie lente ? Ne portez que celle-ci, un chemin chaud à la fois :

| Charge réelle, mêmes résultats que l'original | Original | Avec rust-anything |
| --- | ---: | ---: |
| Recherche dans la barre latérale de x18n, 50 000 clés (TypeScript, Node) | 10 ms par requête | **0,5 ms : 20x plus rapide** |
| La même recherche dans le navigateur (wasm, un thread) | 10 ms | **0,95 ms : 11,5x** |
| `slugify` sur 20 000 chaînes (Python) | 98 ms | **17x plus rapide** |
| `Shellwords.shellescape` de la bibliothèque standard Ruby, 50 000 valeurs | 88 ms | **11,8x plus rapide** |
| `Slugify` sur 50 000 chaînes (Go) | 49 ms | **4x plus rapide** |
| `slugify` sur 50 000 chaînes (Java) | 43 ms | **3x plus rapide** |

Mesuré sur 4 cœurs ; chaque chiffre dispose d'un benchmark dans [`demo/`](../demo) qui vérifie d'abord
que les résultats sont identiques. Appeler Rust une fois par petite fonction est généralement *plus lent*
qu'un JIT ; rust-anything identifie la boucle qui vaut la peine d'être déplacée, et la déplace.

> rust-anything est un projet indépendant, qui n'est ni affilié au Rust Project ou à la Rust Foundation,
> ni approuvé par eux. « Rust » est une marque déposée de la Rust Foundation.

## Démarrage rapide

Collez ceci dans Claude Code, Codex, Cursor ou Gemini CLI et laissez votre agent l'installer :

```text
Installe rust-anything : exécute `cargo install rust-anything`, puis `rust-anything setup`.
Dis-moi quand je dois te redémarrer.
```

Ou faites-le vous-même :

```sh
cargo install rust-anything   # depuis crates.io
rust-anything setup           # l'enregistre auprès de Claude Code, Codex, Cursor et Gemini CLI
```

Pas encore de chaîne d'outils Rust ? Des binaires précompilés pour macOS, Linux et Windows sont joints
à chaque [release GitHub](https://github.com/erkamyaman/rust-anything/releases), et pour les projets
JavaScript, `npm install -g rust-anything` installe le même binaire.

Dans Claude Code, vous pouvez aussi l'installer en tant que plugin (le serveur MCP et le skill ; le CLI
ci-dessus doit se trouver dans votre `PATH`) :

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

`setup` ajoute le serveur MCP à chaque agent détecté et installe le skill de workflow là où l'agent
lit ses skills. Il conserve vos autres paramètres, peut être relancé sans risque, et `--remove` supprime
les entrées configurées (sans restaurer les anciennes valeurs éventuellement mises à jour par `setup`).
Demandez ensuite à votre agent, par exemple :

- *« Réécris ce CLI en Rust avec rust-anything, de bout en bout, et prouve qu'il se comporte à l'identique. »*
- *« Cette recherche semble lente. Profile-la avec rust-anything et déplace la boucle critique vers Rust. »*
- *« Planifie une migration de `src/parser/` vers Rust avec rust-anything ; porte la première unité et prouve-la. »*
- *« Compare les performances du portage Rust dans `rust/text-rs` face à l'original et dis-moi s'il faut le livrer. »*

### Fonctionne avec

| Agent | Ce que `rust-anything setup` ajoute |
| --- | --- |
| Claude Code | Serveur MCP dans `~/.claude.json`, skill dans `~/.claude/skills/` |
| Codex | Serveur MCP dans `~/.codex/config.toml`, skill dans `~/.codex/skills/` |
| Cursor | Serveur MCP dans `~/.cursor/mcp.json` |
| Gemini CLI | Serveur MCP dans `~/.gemini/settings.json` |
| Tout autre client MCP | ajouter `rust-anything mcp` manuellement comme serveur stdio (voir [Installation](#installation)) |

Avant de modifier un fichier existant, `setup` en enregistre une copie à côté (`<file>.rust-anything.bak`).

Ou exécutez les étapes vous-même :

<p align="center">
  <img src="assets/terminal.gif" alt="rust-anything profile repère fuzzyScore dans une boucle, bridge --batch génère la crate Rust, gate passe avec 2000/2000 cas enregistrés, et le benchmark affiche 20,7x plus rapide que TS." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # ce qui consomme du temps, et qui l'appelle
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# écrivez src/port.rs (ou laissez votre agent le faire), puis :
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # chaque cas enregistré doit correspondre
rust-anything bench rust/fuzzy-rs                      # plus rapide ? le verdict tranche
rust-anything gate rust/fuzzy-rs                       # terminé signifie que ce contrôle passe
```

rust-anything ne traduit pas le code automatiquement : votre agent de programmation (Claude Code, Codex,
Cursor, ...) ou vous-même écrivez le Rust. rust-anything fournit ce qu'un agent ne peut pas deviner de
manière fiable : où passe le temps, quoi porter en premier et dans quel ordre, un pont pour que le reste
du code appelle le Rust sans changer son API, le comportement exact que le portage doit reproduire, un
moyen sûr de le déployer et un contrôle final indiquant quand un portage est terminé.

## Langages

| Langage | Unité | Pont | Enregistré et rejoué par |
| --- | --- | --- | --- |
| TypeScript/JavaScript | dossier ou fichier | napi-rs ou wasm-bindgen avec un protocole binaire généré ; classes et asynchrone inclus | Node, en exécutant les sources `.ts` |
| Python | paquet ou module | PyO3 (abi3), conversion directe, exceptions typées | Python, en important l'original |
| C | fichier `.c` | fonctions `extern "C"` portant les noms d'origine et un fichier d'en-tête | l'original compilé en bibliothèque partagée, appelé via ctypes, un fork par cas |
| Go | paquet | appels cgo typés et protocole binaire généré, dans un paquet conservant l'API d'origine | un pilote Go généré, compilé comme son propre module |
| Ruby | fichier ou dossier de fonctions de module | une extension magnus sous les modules d'origine | un pilote Ruby généré |
| Java | paquet de méthodes `public static` | JNI typé et protocole binaire généré, dans des classes enveloppes conservant les méthodes d'origine | un pilote par réflexion généré |
| PHP (aperçu) | dossier de fonctions et de méthodes `public static` | à venir : PHP FFI sur une ABI C | applications complètes dès aujourd'hui : `app record`, `app replay` et la porte d'entrée, pour les CLI et les serveurs (`php -S`) |
| C# (aperçu) | dossier de méthodes `public static` | à venir : P/Invoke sur une ABI C | applications complètes dès aujourd'hui : `app record`, `app replay` et la porte d'entrée, pour les CLI et les serveurs ASP.NET (`dotnet <app>.dll`) |

Chaque langage sauf C obtient également des classes de traitement par lots (`--batch`) : les éléments
traversent la frontière une seule fois et restent en Rust, et chaque appel s'exécute sur l'ensemble des
éléments sur tous les cœurs.

Le langage est détecté à partir du dépôt (`go.mod`, `pom.xml`, un `.csproj` ou `.sln`, `pyproject.toml`,
`Gemfile`, `composer.json`, `package.json`, sinon les fichiers sources les plus courants) ; `--lang`
permet de le forcer. Les types proviennent des sources : types TS, annotations Python, signatures C, Go,
Java et C#, balises Ruby YARD, types PHP et phpdoc ; les paramètres non typés utilisés comme des nombres
sont inférés comme nombres.

PHP est en aperçu : `analyze` planifie une application PHP (paquets Composer et chargement automatique
PSR-4, risques tels que la comparaison souple et le débordement d'entiers en flottants, paquets Composer
mappés vers des crates), et un CLI ou serveur PHP peut être enregistré, rejoué et placé derrière une porte
d'entrée Rust. Le portage de ses unités en Rust via la FFI de PHP est l'étape suivante
([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

C# est en aperçu de la même manière : `analyze` lit les projets `.csproj` et leurs paquets NuGet (mappés
vers des crates), résout les directives `using` vers les dossiers correspondants et signale ce que C# gère
différemment (`decimal`, `dynamic`, requêtes différées LINQ, `Task`, `lock`, réflexion). Un CLI C# ou un
serveur ASP.NET peut être enregistré, rejoué et placé derrière une porte d'entrée Rust ; le portage
d'unités via P/Invoke viendra ensuite.

## Fonctionnement

```
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 où passe    quoi        la crate   ce que     vous ou     chaque   plus      les deux    terminé si
 le temps    porter      Rust et    l'original votre       cas      rapide ?  côte à      ce contrôle
             d'abord     l'enveloppe fait      agent       testé    le        côte en     passe
                                               l'écrit              verdict   production
```

L'original reste la source de vérité : `record` l'exécute sur des cas limites (et sur vos propres
entrées) et sauvegarde ce qu'il retourne ou lève ; `diff` rejoue chaque cas sur le Rust ; rien n'est
livré tant que tout ne correspond pas et que `gate` ne passe pas. Les appelants conservent l'API d'origine
tout du long.

Une application entière suit la même boucle unité par unité, à l'intérieur d'un cadre qui prouve le
programme complet ([Porter toute une application](#porter-toute-une-application)) :

```
analyze --whole-app ──> app record ──> app front-door ──> par unité : la boucle ci-dessus, puis app wire ──> app lift
 forme, chaque           ce que         Rust détient le    gate passe, donc l'unité répond en                 pur Rust,
 dépendance, les         l'app fait     point d'entrée ;   Rust : rejeu à 100 %, taux de repli                prouvé par
 décisions à prendre     de l'extérieur l'original répond  en baisse                                          le rejeu
```

## La boucle

| Étape | Commande | Ce qu'elle fait |
| --- | --- | --- |
| 0. Profilage | `rust-anything profile <repo> -- node bench.mjs` | Exécute une charge réelle sous le profileur du langage (node, cProfile, `go test` pprof, JFR, un traceur Ruby) : fonctions chaudes par temps inclusif, leurs appelants, et quelles boucles traiter par lots ; signale le code déjà compilé (numba, Cython, JAX), où Rust apporte peu |
| 1. Planification | `rust-anything analyze <repo>` | Unités, ordre de portage, risques avec `file:line`, pont par unité, correspondance dépendance-crate, meilleurs premiers portages ; `--whole-app` ajoute les points d'entrée et la forme, chaque dépendance (importée ou déclarée) avec sa crate, les blocs (les unités qui s'importent mutuellement bougent ensemble) et des décisions numérotées avec une réponse recommandée |
| 2. Pont | `rust-anything bridge <repo> <unit>` | Crate contenant les liaisons (`lib.rs`, plus l'enveloppe chargée par le langage source) et les ébauches à porter (`port.rs`) ; `--batch fn:param` ajoute une classe qui conserve de nombreuses valeurs `param` en Rust |
| 3. Enregistrement | `rust-anything record <crate>` | Exécute l'original sur des cas limites générés (non-ASCII, emoji, `-0`, `NaN`, entiers là où des flottants sont attendus, ...) et sur chaque piège sémantique de chaque paramètre (longueur et casse de chaîne, division signée, bords de débordement, affichage des flottants, ordre des maps et tris), et enregistre `cases.jsonl` ; `--float-tolerance 1e-9` autorise une marge relative sur les flottants pour le code numérique |
| 3. Compilation | `rust-anything build <crate>` | Compile la partie Rust : `.node`, paquet wasm, extension Python ou bibliothèque partagée |
| 3. Comparaison | `rust-anything diff <crate>` | Rejoue les cas enregistrés sur le Rust, appelé exactement comme le font les appelants de l'original ; liste les divergences |
| 3. Benchmark | `rust-anything bench <crate>` | Chronomètre les cas enregistrés sur l'original et sur le Rust, pont inclus |
| 4. Mode shadow | `rust-anything shadow <crate>` | Remplacement transparent qui exécute les deux, retourne le résultat de l'original et signale les divergences ; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Contrôle | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, tests, audit `unsafe`, rien de non porté, un cas d'échec enregistré pour chaque chemin d'erreur de l'original, aucun `unwrap`/`expect`/`panic!` là où l'original renvoie une erreur (sauf mention `// INFALLIBLE: <pourquoi>`), compilation, API, comportement |
| Agents | `rust-anything setup` | Enregistre le serveur MCP (`rust-anything mcp`, chaque étape exposée comme outil) et le skill de workflow ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) auprès de vos agents de programmation |

## Porter toute une application

L'objectif est une application en pur Rust qui se comporte comme l'original, tout en conservant l'original
comme référence. Votre agent écrit le Rust ; rust-anything ordonne le travail, génère l'ossature et
prouve chaque étape. Le [skill pour application complète](../skills/rust-anything/whole-app.md) guide
l'agent tout au long du processus, en commençant par les décisions que vous seul pouvez prendre :

- **Cadrage (Grilling)** : l'agent pose des questions par séries, chaque question accompagnée de sa réponse
  recommandée, jusqu'à ce que toutes les décisions dont dépend le portage soient tranchées, et consigne
  chacune sous forme d'ADR dans `rust/DECISIONS.md`, avec `rust/GLOSSARY.md` associant les termes de
  l'original aux noms Rust.
- **Recherche** : des agents en arrière-plan lisent les sources primaires de chaque dépendance et rédigent
  `rust/research/<topic>.md`, avec chaque piège sémantique identifié.
- **D'une session à l'autre** : `rust/MAP.md` liste chaque unité avec son état ; une session revendique une
  unité avant de démarrer, et chaque point de contrôle laisse un fichier `rust/HANDOFF.md` pour la session
  suivante. Les unités d'une même vague peuvent être portées en parallèle par des sous-agents.
- **Bascule (Cutover)** : l'agent fait ce qu'il peut et écrit `rust/cutover.sh`, un script interactif pour
  les étapes que vous seul pouvez effectuer (déploiements, DNS, secrets), avec un retour arrière possible à
  chaque étape.

Le cadrage, la recherche et ces pratiques sont adaptés des
[skills de Matt Pocock](https://github.com/mattpocock/skills).

Planifiez d'abord : `rust-anything analyze . --whole-app` ajoute la forme de l'application (CLI, serveur ou
bibliothèque) et les points d'entrée, chaque dépendance externe (importée ou déclarée) avec sa crate Rust et
son adéquation, l'ordre de portage sous forme de blocs (les unités qui s'importent mutuellement bougent
ensemble), et des décisions numérotées avec une réponse recommandée : unités à conserver, unités bloquées,
dépendances sans crate ou avec une crate partielle.

Prouvez ensuite le programme entier de l'extérieur. `record` et `diff` prouvent une unité ; `app record` et
`app replay` prouvent l'application, pour les CLI et serveurs dans n'importe lequel des six langages
(l'application est une boîte noire) :

```sh
rust-anything app record . -- python3 cli.py          # la commande qui lance l'original
rust-anything app replay .                            # l'original doit passer à 100 %
rust-anything app replay . --build "target/release/mytool"
```

- `app record` exécute l'original sur les exemples documentés de l'application elle-même (lignes
  `$ mytool ...` dans ses fichiers Markdown et shell, avec les fichiers qu'ils nomment), un fichier JSONL
  `--inputs` (`{"name", "args", "stdin", "env", "files"}`), et des pièges sémantiques dérivés de ces cas
  (chaînes non-ASCII et emoji, division et modulo négatifs, débordement, flottants très grands ou très
  petits, ordre des maps, fichiers manquants). Chaque cas s'exécute deux fois ; ce qui diffère entre les
  deux exécutions devient un joker `[..]`. `--normalize timestamps|uuids|key-order` ou
  `--normalize name=regex` ajoute des normaliseurs, enregistrés avec les cas.
- Les cas sont des fichiers [trycmd](https://docs.rs/trycmd) dans `rust/app-cases/` : `<case>.toml` (argv,
  env, code de sortie), `.stdin`, `.stdout`, `.stderr`, `.in/` (fichiers en entrée) et `.out/` (fichiers
  écrits). Lisez-les et modifiez-les à la main ; un test Rust peut les exécuter avec `trycmd` dès que le
  portage dispose d'un binaire.
- `app replay` exécute n'importe quel binaire compilé sur ces cas, affiche `passed/total`, écrit
  `rust/app-cases/replay-report.md` avec un diff par cas en échec, et quitte avec un code non nul au moindre
  écart. Un binaire qui ajoute des lignes au fichier indiqué par `RUST_ANYTHING_FALLBACK_LOG` (une ligne par
  repli vers l'original), comme le fait la porte d'entrée ci-dessous, voit également son taux de repli
  rapporté.
- `app replay --case <name>` relance un seul cas à partir du nom indiqué dans le rapport : une boucle rapide
  et reproductible pour corriger une divergence avant de tout relancer.

Déplacez ensuite le point d'entrée vers Rust et confiez-lui les commandes une unité à la fois :

```sh
rust-anything app front-door .                            # rust/app : chaque commande exécute l'original
rust-anything app wire . textkit --command upper          # une fois que textkit-rs passe gate
# écrivez le code de liaison dans rust/app/src/units/textkit.rs, puis :
rust-anything app wire . textkit                          # à nouveau 100 %, taux de repli plus bas
```

- `app front-door` génère `rust/app`, un binaire Rust portant le nom de l'application : un analyseur clap
  pour les commandes et options des cas enregistrés, où chaque commande exécute l'original avec les mêmes
  argv, stdin et environnement et transmet sa sortie et son code de sortie. Chaque repli est compté, si bien
  que rejouer la porte d'entrée fraîchement générée donne 100 % de réussite pour 100 % de repli (elle se
  compile et se rejoue pour le démontrer). Elle n'écrase jamais `rust/app` : le code vous appartient dès
  lors.
- `app wire <repo> <unit> --command <name>` exécute `gate` sur la crate de l'unité (`--skip-gate` s'il
  vient de passer), l'ajoute à `rust/app` comme bibliothèque, génère une fois `src/units/<unit>.rs` pour que
  vous ou votre agent le remplissiez (analyser les arguments, appeler `<crate>::port`, afficher ce que
  l'original affiche), y dirige les commandes, puis recompile et rejoue. `RUST_ANYTHING_UNIT_<NAME>=original`
  renvoie une unité raccordée vers l'original jusqu'à la bascule finale.

Raccordez le nom même de l'application comme commande (`--command mytool`) pour les appels sans nom de
commande : sans argument, commandes inconnues, erreurs d'usage.

Lorsque le rejeu passe avec un taux de repli de 0 et que chaque unité passe `gate`, transformez-la en une
application pur Rust :

```sh
rust-anything app lift .
```

- `app lift` refuse tant que les deux conditions ne sont pas réunies, et indique ce qui bloque : les cas qui
  se replient encore sur l'original, les codes de liaison encore à l'état d'ébauche, les unités qui échouent
  à `gate`.
- Sur une copie d'abord, il supprime le chemin de repli et les interrupteurs d'urgence, transforme chaque crate
  d'unité en une simple bibliothèque de `rust/app` (sans `cdylib`, liaisons ni enveloppes générées), et
  ajoute `rust/app/tests/app_cases.rs`, qui exécute `rust/app-cases` avec trycmd lors de `cargo test`, de
  sorte que la CI n'a besoin que de cargo.
- Puis il exécute la liste de vérification finale : fmt, clippy `-D warnings` et tests sur chaque unité et sur
  `rust/app`, compilation ou vérification de chaque cible nommée dans `rust/DECISIONS.md` lorsqu'elle est
  installée, fichiers lus à l'exécution et dossiers de ressources non embarqués, et rejeu sur le binaire pur.
  Ce n'est que lorsque tout passe que les modifications sont réécrites. L'original n'est jamais touché.

### Serveurs

Les mêmes commandes prouvent les serveurs HTTP. `--http` indique que la commande démarre un serveur ; il
récupère son port depuis `PORT` ou `{port}` dans la commande (`--port` pour un serveur qui écoute toujours
sur le même port) :

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum : chaque route est relayée par proxy
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Les requêtes proviennent des lignes `curl` dans la documentation de l'application
  (`curl -X POST -d ... http://localhost:8080/x`), de `--inputs` (`{"name", "method", "path", "headers", "body"}`)
  et de pièges : segments de chemin et paramètres de requête remplacés par les mêmes pièges que les
  arguments CLI, corps de requêtes remplacés par des pièges texte et JSON, et une route inconnue. Chaque
  exécution redémarre le serveur à neuf et envoie les requêtes par ordre de nom, de sorte que l'état entre
  requêtes est conservé.
- Les cas sont `rust/app-cases/http/<case>.toml` (la requête, le statut et les en-têtes qui comptent) et
  `<case>.body` (le corps de réponse, avec `[..]` là où deux exécutions ont différé). Date, serveur et
  autres en-têtes propres à chaque réponse sont omis ; supprimez toute ligne d'en-tête qui ne vous intéresse
  pas.
- La porte d'entrée est un serveur axum qui lance l'original sur son propre port et relaie par proxy chaque
  route qu'aucune unité ne traite. `wire --route` accepte les routes axum : `METHOD /path/{param}`, `/path`
  pour n'importe quelle méthode, `*` pour tout le reste ; le code de liaison reçoit la route, ses paramètres
  et la requête. `lift` supprime le proxy ; les cas HTTP s'exécutent alors en CI avec `app replay`.

### Bibliothèques

Une bibliothèque n'a pas de processus à rejouer : son API publique est la porte d'entrée, et les cas
enregistrés de chaque unité constituent la preuve.

```sh
rust-anything app front-door .        # rust/app : une crate Rust avec l'API publique
# chaque unité suit la boucle : bridge, record, port.rs, build, diff, gate ; puis :
rust-anything app wire . textkit-rs   # réexportée depuis rust/app ; l'original importe son module shadow
rust-anything app replay .            # les cas de chaque unité raccordée ; repli = exports encore dans l'original
rust-anything app lift .
```

- `app front-door` détecte l'API publique (les exports de chaque unité) lorsque le dépôt n'a ni `main` ni
  serveur (`--library` sinon), et génère `rust/app` en tant que crate de bibliothèque. Chaque unité raccordée
  en devient un module : `pub use textkit_rs::port as textkit;`.
- `app wire` prend une crate créée par `bridge`, exécute `gate`, et écrit le module de remplacement shadow
  de l'unité : le paquet d'origine l'importe à la place de l'unité, si bien que ses appelants conservent
  l'API d'origine et atteignent le Rust. `RUST_ANYTHING_UNIT_<NAME>=original` renvoie l'unité vers l'original
  (C : compilez sans les options du shadow).
- `app replay` exécute les cas enregistrés de chaque unité raccordée à travers ses liaisons. Le taux de
  repli est la part des exports publics auxquels Rust ne répond pas encore : unités non raccordées, et
  exports que `bridge` garde dans le langage d'origine.
- `app lift` exige un repli à 0 et que chaque unité passe `gate` ; il retire les liaisons, enveloppes et
  modules shadow des unités et laisse `rust/app` comme une seule bibliothèque pur Rust. Il ne touche à aucun
  `port.rs`, donc les cas qui correspondaient via les liaisons la décrivent toujours ; la vérification signale
  les fichiers de l'original qui importent encore les modules shadow.

Les cinq sont aussi des outils MCP : `app_record`, `app_replay`, `app_front_door`, `app_wire` et
`app_lift`.

## Étude de cas : le cœur de x18n

Les 29 fonctions du cœur de x18n qui peuvent être déplacées sans changement d'API ont toutes été portées avec
rust-anything : chaque `gate` passe et 7 925 cas enregistrés correspondent exactement. `rust-anything bench`
a ensuite montré que les portages sont plus lents que le TS appelé depuis JS, car le pont coûte plus cher
que le travail effectué. Rapport complet : [`demo/x18n-core`](../demo/x18n-core/README.md). La leçon est
intégrée à l'outil : mesurez avec `bench` avant de livrer un portage.

## Chemins chauds : garder les données en Rust

Un portage appelé une fois par élément paie le coût du pont à chaque élément, et perd face à un JIT. Ce qui
gagne, c'est de déplacer la boucle : `profile` la trouve, et `--batch` génère une classe qui prend les
éléments une fois et exécute la fonction sur tous en un seul appel, sur tous les cœurs, avec des résultats
en tableaux typés.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore : un quart de l'exécution, appelé par clé par `matched` : passez-le en lot
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // une seule fois
const order = search.rank(query, 0)               // à chaque frappe : indices, les meilleurs d'abord
```

Une structure `FuzzyScoreIndex` dans `port.rs` remplace la boucle par défaut par une implémentation qui
prépare les éléments une fois, et peut classer directement (`rank`) : elle conserve les clés en minuscules
avec un masque de caractères pour chacune, une table de la première position de chaque caractère courant
dans chaque clé (une requête d'une lettre ne lit qu'une colonne), et les correspondances de la dernière
requête (taper `se` après `s` ne recalcule le score que sur ce que `s` a trouvé). Sur la recherche de la
barre latérale de x18n sur 50 000 clés, tapées lettre par lettre, avec des résultats identiques :

| | Par requête | vs TS |
| --- | ---: | ---: |
| TS : `map(fuzzyScore)`, filtre, tri | 10 ms | 1x |
| TS avec le même filtrage progressif que l'index | 4,1-5,4 ms | 2x |
| Le même portage, appelé par clé | - | 0,2-0,4x |
| `FuzzyScoreBatch`, index par défaut (4 cœurs) | 5,1 ms | 1,7x |
| `FuzzyScoreBatch` avec `FuzzyScoreIndex` (napi, 4 cœurs) | 0,45-0,56 ms | **18-22x** |
| Le même avec wasm (un thread) | 0,95 ms | **11,5x** |

Face au TS effectuant le même filtrage progressif, Rust reste 7 à 12x plus rapide (wasm 5x). Convertissez les
indices retournés en clés avec une simple boucle : `Array.from(order, i => keys[i])` coûtait 20x plus cher,
0,4 ms.

Chaque langage dispose de traitements par lots, et ils battent l'original même là où les portages appelés
unité par unité perdent. Le même travail sur 4 cœurs, résultats et erreurs identiques (benchmarks dans
chaque dossier demo) :

| Langage | Charge de travail | Original | Portage par appel vs original | Lot vs original |
| --- | --- | ---: | ---: | ---: |
| TS | recherche x18n, 50 000 clés | 10 ms | 0,2-0,4x | **20x** |
| Python | `slugify`, 20 000 chaînes | 98 ms | - | **17x** |
| Ruby | `slugify`, 20 000 chaînes | 110 ms | - | **12,7x** |
| Ruby | `shellescape` (stdlib), 50 000 valeurs mixtes | 88 ms | - | **11,8x** |
| Go | `Slugify`, 50 000 chaînes | 49 ms | 0,93x | **4x** |
| Java | `slugify`, 50 000 chaînes | 43 ms | 0,68x | **3x** |

Les langages compilés d'origine gagnent moins : le travail par élément est déjà rapide, donc le traitement
par lots gagne grâce au nombre de cœurs. Les crates de lots allouent avec mimalloc : avec l'allocateur
système, le lot Go était plus lent qu'un seul thread. Démo : [`demo/x18n-search`](../demo/x18n-search/README.md).

## Du code réel dans six langages

`path` de Go, `shellwords` de Ruby, `colorsys` de Python, ainsi que des comportements du JDK et de la glibc
derrière de petites façades : chaque portage passe son contrôle `gate`, 13 010 cas enregistrés au total. Ces
exécutions ont révélé et corrigé des bogues dans rust-anything (flottants décalés d'un ULP via `serde_json`,
plantages en C pendant l'enregistrement, code non typé recevant des entrées invalides). Appelé par fonction,
le portage Ruby tourne 4,4x plus vite que Ruby et le portage Python 1,35x plus vite que CPython, tandis que
les fonctions feuilles Go et Java restent plus rapides dans leur propre langage ; en lots, tous gagnent
(voir le tableau ci-dessus). Rapport : [`docs/real-world-languages.md`](./real-world-languages.md).

## Exemple : un vrai module de x18n

`packages/core/src/fuzzy.ts` de [x18n](https://github.com/x18n-dev/x18n), porté des deux façons dans
[`demo/`](../demo) :

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts : prêt, wasm-bindgen (core tourne dans les navigateurs)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# écrivez src/port.rs
rust-anything gate demo/fuzzy-rs
```

Un premier portage qui indexait par `char` Rust passait des tests simples mais échouait à `diff` :

```
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

`indexOf` en JS compte les unités de code UTF-16, donc un emoji compte pour deux positions. Le portage dans
`demo/*/src/port.rs` utilise les assistants `utf16` générés et passe 2000/2000 cas ainsi que le contrôle
`gate`, en napi-rs (`demo/fuzzy-napi`) comme en wasm-bindgen (`demo/fuzzy-rs`).

Le plan généré par rust-anything pour l'ensemble de x18n : [`docs/examples/x18n.md`](./examples/x18n.md).

## Installation

```sh
cargo install --path .
```

`record`, `diff` et `bench` exécutent l'original dans son propre environnement d'exécution : Node 22.6+
pour TS (il exécute directement les sources `.ts`), Python 3.9+ pour Python et C (ctypes), Go 1.21+, Ruby
3+, JDK 17+ (`javac` et `java`). C nécessite aussi un compilateur C. Les ponts wasm nécessitent également
`rustup target add wasm32-unknown-unknown` et
`cargo install wasm-bindgen-cli --version <version de wasm-bindgen de la crate> --locked` ; `build` indique
la version exacte.

Pour les agents, `rust-anything setup` enregistre tout (voir Démarrage rapide). Pour ajouter plutôt
manuellement le serveur MCP à un seul projet (`.mcp.json`) :

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## Ce que décide `bridge`

- Les exports qui ne peuvent pas traverser un pont restent dans le langage source, avec la raison, et le
  module shadow réexporte l'original. Pour TS :
  les fonctions qui prennent ou renvoient des fonctions, les générateurs et itérateurs, RegExp, les
  vérifications `instanceof`, les génériques, et les valeurs dont les types (suivis à travers les imports,
  réexports et `extends`) contiennent des fonctions. `--keep "name: reason"` en garde davantage, par ex. du
  code dépendant des données `Intl`.
- Les types TS sont convertis en types Rust, avec résolution des alias de types à travers les imports et
  inférence des types de paramètres à partir des valeurs par défaut ; les valeurs structurées passent par un
  protocole binaire généré (JSON uniquement en repli pour les formes que le protocole ne modélise pas).
- JSON ne peut pas exprimer `undefined`, NaN, Infinity, -0 ni les substituts isolés (lone surrogates) : les
  valeurs structurées transportent des marqueurs (`{"$undefined": true}`, `{"$num": "NaN"}`,
  `{"$utf16": [...]}`) que le fichier généré `index.cjs` traduit, avec des assistants dans `js.rs` de la
  crate.

`record` exécute les sources TS telles quelles : un hook de résolution Node suit les imports de style
bundler (`./errors` vers `./errors.ts`), `--resolve-from` fournit les paquets npm lorsque le dépôt n'en a
aucun d'installé, et le TS nécessitant une transformation (enums, propriétés de paramètres) est relancé avec
`--experimental-transform-types`.

## Ce qu'analyse `analyze`

- Les paquets (`package.json`) et fichiers sources ; ignore `node_modules`, les sorties de compilation, les
  fixtures, les playgrounds, les configurations d'outils. Les blocs `<script>` Vue/Svelte/Astro sont analysés
  pour les imports.
- **Unités** : un dossier de fichiers sources, ou un fichier à la racine source d'un paquet.
- **Vagues** : les imports d'une unité apparaissent dans des vagues antérieures ; les cycles d'imports sont
  portés ensemble.
- **Pont** : napi-rs lorsque l'unité ou tout ce qu'elle importe nécessite Node ; wasm-bindgen pour le code
  portable ; conserver en JS pour le code d'interface et d'éditeur.
- **Préparation** (niveau de sûreté) et **priorité** (sûr et rentable : boucles et manipulation de chaînes,
  tests, taille).

| Risque | Gravité | Exemple |
| --- | --- | --- |
| Décalages de chaînes | élevée | `slice`, `indexOf`, `matchAll`, le drapeau `d` : UTF-16 vs UTF-8 |
| Syntaxe regex | élevée | lookaround, références arrière, `y` : absents de la crate `regex` |
| Regex dynamique | élevée | `new RegExp(userPattern)` : syntaxe JS à l'exécution |
| Code dynamique | élevée | `eval`, `new Function`, `import()` calculé |
| Typage dynamique | moyenne | `any`, `'key' in value` |
| Collections ordonnées | moyenne | `Map`, `Set`, `Object.keys` : ordre d'insertion |
| Asynchrone, générateurs | moyenne | frontières des promesses et générateurs |
| Héritage de classe, réflexion | moyenne | `extends`, `Proxy`, `Reflect`, `Symbol` |
| API à base de callbacks | moyenne | paramètres et méthodes de type fonction : ponts bavards |
| Exceptions, nombres, JSON | faible | `throw`, opérations bit à bit, ordre `JSON.stringify` |

## Développement

```sh
cargo test                        # tests unitaires, dépôt de test, boucle record/diff/shadow (nécessite node), app record/replay par langage
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Choix de conception et leurs raisons : [DECISIONS.md](../DECISIONS.md).

## Mettre à jour ou supprimer

```sh
cargo install rust-anything                                    # mise à jour (Cargo)
npm install -g rust-anything@latest                            # mise à jour (npm)
rust-anything setup                                            # actualiser les réglages des agents
rust-anything setup --remove && cargo uninstall rust-anything  # supprimer (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # supprimer (npm)
```

`setup --remove` ne retire que les entrées de rust-anything ; avant d'écrire, il sauvegarde le fichier
actuel vers `<file>.rust-anything.bak` (ce qui remplace la sauvegarde précédente créée lors du `setup`),
et cette copie reste en place jusqu'à ce que vous la supprimiez.

## Ce qui lui échappe

Passer la vérification signifie que le Rust correspond à chaque cas enregistré, rien de plus. Ce qui piège
les réécritures se cache généralement hors de l'enregistrement, sachez donc où sont les limites :

- **Les entrées que personne n'a enregistrées.** Les cas générés, les pièges et vos propres `--inputs`
  forment le plafond. Ajoutez de vraies entrées (échantillons de production, rapports de bogues, fixtures de
  tests de l'original) ; l'entrée utilisateur qui casse la prod est rarement celle à laquelle pense un
  générateur.
- **Les expressions régulières.** La crate `regex` n'a ni lookaround ni références arrière, et même un motif
  qui compile peut traiter `\w`, `\b`, `\d` et la correspondance insensible à la casse sur du texte non-ASCII
  différemment de JS, Python ou Java. Passer à `fancy-regex` ou réécrire le motif peut passer tous les cas
  enregistrés et pourtant diverger sur un `ı` turc sans point ou un liant sans chasse (ZWJ). `record` ajoute
  des pièges regex (ceux-là, le signe Kelvin, le s long, les chiffres arabo-indiens, les séparateurs de
  ligne, le sigma final) à chaque fonction d'un fichier qui utilise des regex, mais testez aussi par fuzzing
  vos vrais motifs sur du texte réel.
- **Ce qui change d'une exécution à l'autre.** `record` exécute l'original deux fois et classe ce qui a
  changé : les valeurs variables (horodatages, identifiants) deviennent des jokers ; les mêmes lignes dans
  un autre ordre (tables de hachage, concurrence) sont comparées dans n'importe quel ordre, donc un portage
  doit tout de même produire exactement ces lignes ; un nombre différent de lignes devient `...`, qui
  correspond à n'importe quoi. `record` liste chaque catégorie : examinez chacune d'elles, car une
  différence d'ordre de hachage ou de concurrence est précisément ce qui peut vraiment changer dans un
  portage.
- **Les flottants.** Le formatage nombre-vers-texte diffère selon les langages (`1e21`, `-0`, nombre de
  chiffres). Les pièges incluent ces valeurs, et elles doivent correspondre exactement ; `--float-tolerance`
  tolère uniquement l'arrondi, jamais le formatage.
- **Tout ce qui n'est pas dans la sortie.** Les temps d'exécution, la mémoire, la concurrence sous charge,
  et les effets de bord autres que stdout, stderr, les codes de sortie, les fichiers écrits et les réponses
  HTTP (appels réseau, bases de données, signaux) ne sont pas comparés.
- **Les autres plateformes.** Un enregistrement prouve le comportement sur la machine qui l'a exécuté. Du C
  dont les résultats dépendent de la taille des types, du boutisme ou du compilateur peut se comporter
  différemment sur la cible ; `analyze` garde le C proche du matériel en C pour cette raison.

## FAQ

**Réécrit-il mon code automatiquement ?** Non. Il identifie quoi déplacer, génère le pont, enregistre ce que
fait l'original et vérifie le Rust par rapport à cela. Vous ou votre agent écrivez le Rust dans `port.rs` ;
`diff` et `gate` décident quand il est correct.

**L'API de mon application va-t-elle changer ?** Non. Les appelants importent les mêmes fonctions (ou le
module shadow, qui exécute les deux et renvoie le résultat de l'original le temps de prendre confiance).

**Rust est-il toujours plus rapide ?** Non, et rust-anything le dit clairement. Une petite fonction appelée
une fois par élément est souvent plus lente en Rust, car chaque appel traverse un pont ; V8, la JVM et Go
exécutent ce genre de fonctions en quelques nanosecondes. `profile` trouve la boucle qui l'entoure,
`--batch` déplace toute la boucle, et `bench` rend un verdict avant que vous ne livriez. Le code déjà
compilé par numba, Cython ou JAX s'exécute déjà en code machine : `profile` et `analyze` le signalent, car
le porter rapporte peu de vitesse.

**Mon code fait du calcul numérique ; les flottants correspondront-ils exactement ?** Souvent non : l'ordre
des opérations, la multiplication-accumulation fusionnée (FMA) et la bibliothèque mathématique diffèrent
selon les compilateurs. Enregistrez avec `--float-tolerance 1e-9` (`record` ou `app record`), et les
flottants correspondront dans cette proportion de la plus grande valeur (absolue en dessous de 1). Les
entiers, le texte et la structure doivent toujours correspondre exactement.

**Peut-il porter une application dont je n'ai qu'un APK, un JAR ou un .exe ?** Non. Il porte du code
source : il analyse les fonctions, enregistre ce que chacune fait et vérifie le Rust face à l'original en
cours d'exécution. Une application compilée n'offre rien de tel sur lequel travailler, et `analyze` le
signale. Écrire une nouvelle application Rust à partir du comportement visible d'un binaire est un autre
projet.

**Dois-je porter du code C éprouvé ?** Souvent non, et `analyze` vous indique où. Le C qui touche aux
registres matériels, dépend des tailles de types ou de la disposition mémoire de son compilateur, ou
utilise de l'assembleur en ligne (`volatile`, champs de bits, structures `packed`, `__asm__`, entiers
convertis en adresses) est marqué « conserver en C » : un enregistrement sur votre machine ne prouve rien
pour la cible, et un code de pilote ou de firmware stable gagne peu à être réécrit. La logique portable
autour (analyse syntaxique, protocoles, traitement de données) est ce qui se déplace bien.

**Peut-il porter mon application Electron ?** La logique, oui ; les fenêtres restent des pages web.
`analyze --whole-app` repère Electron et planifie le processus principal morceau par morceau pendant que le
moteur de rendu reste tel quel. Basculer l'interface vers Tauri (la même interface web sur un backend Rust)
est une étape distincte une fois la logique en Rust.

**Qu'en est-il de C#, Kotlin ou Swift ?** C# est en aperçu (voir [Langages](#langages)) ; Kotlin et Swift
ne sont pas encore pris en charge. Chaque langage nécessite un analyseur syntaxique, un enregistreur, un
pont et un pilote de rejeu, tous testés de bout en bout. Ouvrez une issue (ou votez pour une issue
existante) pour le langage dont vous avez besoin.

**Le code Rust ne risque-t-il pas d'être beaucoup plus gros que l'original ?** Il ne devrait pas. `gate`
compare les lignes du portage à celles de l'original et échoue au-delà de 3x (plus 50 lignes pour les
imports et signatures) : cela signifie généralement que l'on réécrit à la main ce qu'une crate fait déjà, ou
que l'on traite les cas un par un. `analyze` liste les crates à utiliser.

**Porter morceau par morceau n'enferme-t-il pas le Rust dans la conception de l'ancienne application ?**
Seulement tant que les deux tournent côte à côte. Les enregistrements vérifient le comportement aux bords
de l'application (la sortie d'un CLI, les réponses d'un serveur, les fonctions exportées d'un module), pas
ses rouages internes. Reflétez l'ancienne structure tant que des unités traversent encore le pont ; une fois
que `app lift` a retiré l'original, restructurez le Rust librement, et `app replay` prouve toujours le
comportement. Rien ne rappelle non plus l'original : la porte d'entrée l'exécute comme un processus séparé
(ou lui transfère le HTTP), les unités pontées sont appelées par l'original et jamais l'inverse, et les
callbacks restent dans le langage source.

**Est-ce que mon code quitte ma machine ?** Non : rust-anything s'exécute localement et n'envoie aucune
partie de votre code où que ce soit. Cargo télécharge les crates comme d'habitude, et le fournisseur de
modèle de votre agent voit ce que votre agent lui envoie, selon sa propre politique.

**Que faut-il d'installé ?** Rust, plus l'environnement d'exécution du langage que vous portez (voir
[Installation](#installation)).

**Quelque chose a cassé.** Ouvrez une issue avec la commande, sa sortie et votre plateforme.

## Sponsors

rust-anything est gratuit et open source. S'il vous aide dans votre travail, envisagez de le sponsoriser. Votre soutien permet de poursuivre le développement.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Sponsor rust-anything on GitHub" /></a>
</p>

### Entreprises sponsors

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Sponsors individuels

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

## Contribuer

Les issues et pull requests sont les bienvenues ; [CONTRIBUTING.md](../CONTRIBUTING.md) couvre la mise en
place, l'emplacement des tests et la manière d'ajouter un langage. Les choix de conception et leurs raisons
se trouvent dans [DECISIONS.md](../DECISIONS.md). Les études de cas de portages réels sont particulièrement
appréciées. Merci de signaler les failles de sécurité en privé ([SECURITY.md](../SECURITY.md)), et de
consulter le [code de conduite](../CODE_OF_CONDUCT.md).

## Licence

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman). Les portages et le code généré dans votre dépôt vous appartiennent.
