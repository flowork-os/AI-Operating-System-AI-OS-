<p align="center">
  <img src="assets/logo.svg" width="160" height="160" alt="O caranguejo do rust-anything, com uma tag de código na boca">
</p>

<h1 align="center">rust-anything</h1>

<p align="center">por <a href="https://github.com/erkamyaman">erKam Yaman</a></p>

<p align="center"><a href="../README.md">English</a> · <a href="README_TR.md">Türkçe</a> · <a href="README_ZH.md">简体中文</a> · <a href="README_ZH-TW.md">繁體中文</a> · <a href="README_DE.md">Deutsch</a> · <a href="README_FR.md">Français</a> · <a href="README_RU.md">Русский</a> · <a href="README_UK.md">Українська</a> · <a href="README_JA.md">日本語</a> · <a href="README_KO.md">한국어</a> · <a href="README_AZ.md">Azərbaycanca</a> · <a href="README_UZ.md">Oʻzbekcha</a> · <a href="README_KK.md">Қазақша</a> · <a href="README_KY.md">Кыргызча</a> · <a href="README_TK.md">Türkmençe</a> · <a href="README_TT.md">Татарча</a> · <a href="README_UG.md">ئۇيغۇرچە</a> · Português</p>

<p align="center"><sub>Esta tradução é mantida pela comunidade e pode estar desatualizada em relação ao <a href="../README.md">README em inglês</a>.</sub></p>

<p align="center"><em>Reescreva toda a sua aplicação em Rust. Mantenha-a funcional durante todo o processo.</em></p>

<p align="center"><em>CLIs, servidores e bibliotecas, peça por peça, comparados com o original em cada etapa.</em></p>

<p align="center">Node.js e TypeScript · Python · C · Go · Ruby · Java · PHP e C# em versão de pré-visualização</p>

<p align="center">
  <a href="https://crates.io/crates/rust-anything"><img src="https://img.shields.io/crates/v/rust-anything?color=E2862A&label=crates.io" alt="Versão no crates.io"></a>
  <a href="https://www.npmjs.com/package/rust-anything"><img src="https://img.shields.io/npm/v/rust-anything?color=E2862A&label=npm" alt="Versão no npm"></a>
  <img src="https://img.shields.io/badge/languages-6-E2862A" alt="6 linguagens">
  <a href="#compatibilidade-com-agentes"><img src="https://img.shields.io/badge/works%20with-4%20agents-E2862A" alt="Compatível com 4 agentes"></a>
  <a href="https://github.com/erkamyaman/rust-anything/actions/workflows/ci.yml"><img src="https://img.shields.io/github/actions/workflow/status/erkamyaman/rust-anything/ci.yml?branch=main&label=tests" alt="Testes"></a>
  <a href="../LICENSE"><img src="https://img.shields.io/badge/license-MIT-E2862A" alt="Licença MIT"></a>
  <a href="https://github.com/erkamyaman/rust-anything"><img src="https://img.shields.io/github/stars/erkamyaman/rust-anything?style=social" alt="Estrelas no GitHub"></a>
</p>

<p align="center">Até 20x mais rápido · 38.251 casos registados e reproduzidos · 0 divergências · um único comando</p>

<p align="center">
  <img src="assets/race.gif" alt="Pesquisa de user.profile no x18n entre 50.000 chaves: TypeScript demora 143 ms, enquanto o processamento em lote do rust-anything demora 6,9 ms, com os mesmos resultados em cada tecla." width="820">
</p>

**Reescreva toda a sua aplicação em Rust, uma peça de cada vez.** O rust-anything regista o comportamento atual da sua aplicação Node.js (TypeScript/JavaScript), Python, C, Go, Ruby ou Java e, em seguida, compara cada parte da reescrita em Rust com esse registo antes de avançar, até que a aplicação seja totalmente escrita em Rust.

CLIs, servidores HTTP e bibliotecas; o seu agente de programação (ou você) escreve o código Rust. A ferramenta só consegue detetar aquilo que o registo abrange: consulte [O que não consegue detetar](#o-que-nao-consegue-detetar).

Só precisa de acelerar a parte mais lenta? Migre apenas essa parte, um caminho crítico de cada vez:

| Carga de trabalho real, mesmos resultados do original | Original | Com rust-anything |
| --- | ---: | ---: |
| Pesquisa na barra lateral do x18n, 50.000 chaves (TypeScript, Node) | 10 ms por consulta | **0,5 ms: 20x mais rápido** |
| A mesma pesquisa no navegador (wasm, uma thread) | 10 ms | **0,95 ms: 11,5x** |
| `slugify` em 20.000 strings (Python) | 98 ms | **17x mais rápido** |
| `Shellwords.shellescape` da biblioteca padrão do Ruby, 50.000 valores | 88 ms | **11,8x mais rápido** |
| `Slugify` em 50.000 strings (Go) | 49 ms | **4x mais rápido** |
| `slugify` em 50.000 strings (Java) | 43 ms | **3x mais rápido** |

Medições realizadas em 4 núcleos; cada valor tem um benchmark em [`demo/`](../demo) que primeiro verifica se os resultados são idênticos.

Chamar Rust uma vez por cada pequena função costuma ser *mais lento* do que utilizar um JIT; o rust-anything identifica o ciclo que realmente vale a pena migrar e transfere-o.

> O rust-anything é um projeto independente, sem qualquer afiliação ou aprovação do Rust Project ou da Rust Foundation. "Rust" é uma marca registada da Rust Foundation.

## Início rápido

Cole isto no Claude Code, Codex, Cursor ou Gemini CLI e deixe o seu agente instalá-lo:

```text
Install rust-anything: run `cargo install rust-anything`, then `rust-anything setup`.
Tell me when to restart you.
```

Ou faça a instalação manualmente:

```sh
cargo install rust-anything   # a partir do crates.io
rust-anything setup           # regista a ferramenta no Claude Code, Codex, Cursor e Gemini CLI
```

Ainda não tem a toolchain do Rust? Os binários pré-compilados para macOS, Linux e Windows estão disponíveis em cada [lançamento no GitHub](https://github.com/erkamyaman/rust-anything/releases). Para projetos JavaScript, `npm install -g rust-anything` instala o mesmo binário.

No Claude Code, também pode instalá-lo como plugin (o servidor MCP e a skill; a CLI acima deve estar disponível no seu `PATH`):

```text
/plugin install rust-anything --marketplace erkamyaman/rust-anything
```

O comando `setup` adiciona o servidor MCP a cada agente que encontrar e instala a skill do fluxo de trabalho no local onde o agente procura as suas skills.

Preserva as suas outras configurações, pode ser executado novamente em segurança e `--remove` desfaz as alterações.

Depois, peça ao seu agente algo como:

- *"Reescreve esta CLI em Rust com rust-anything, de ponta a ponta, e comprova que se comporta da mesma forma."*
- *"Esta pesquisa parece lenta. Analisa o desempenho com rust-anything e transfere o ciclo mais pesado para Rust."*
- *"Planeia a migração de `src/parser/` para Rust com rust-anything; migra a primeira unidade e comprova que funciona."*
- *"Compara o port Rust em `rust/text-rs` com o original e diz-me se está pronto para produção."*

### Compatibilidade com agentes

| Agente | O que `rust-anything setup` adiciona |
| --- | --- |
| Claude Code | Servidor MCP em `~/.claude.json`, skill em `~/.claude/skills/` |
| Codex | Servidor MCP em `~/.codex/config.toml`, skill em `~/.codex/skills/` |
| Cursor | Servidor MCP em `~/.cursor/mcp.json` |
| Gemini CLI | Servidor MCP em `~/.gemini/settings.json` |
| Qualquer outro cliente MCP | Adicione manualmente `rust-anything mcp` como servidor stdio (consulte [Instalação](#instalacao)) |

Antes de modificar um ficheiro existente, `setup` guarda uma cópia ao lado dele (`<file>.rust-anything.bak`).

Ou execute as etapas manualmente:

<p align="center">
  <img src="assets/terminal.gif" alt="O perfil do rust-anything encontra fuzzyScore num ciclo, bridge --batch gera o crate Rust, gate é aprovado com 2000/2000 casos registados e o benchmark mostra um desempenho 20,7x superior ao TypeScript." width="820">
</p>

```sh
rust-anything profile . -- node bench.mjs              # o que está lento e quem o chama
rust-anything bridge . src/fuzzy.ts --batch fuzzyScore:text
# escreva src/port.rs (ou deixe o seu agente fazê-lo) e depois:
rust-anything record rust/fuzzy-rs && rust-anything build rust/fuzzy-rs
rust-anything diff rust/fuzzy-rs                       # todos os casos registados devem corresponder
rust-anything bench rust/fuzzy-rs                      # está mais rápido? o resultado dirá
rust-anything gate rust/fuzzy-rs                       # concluído significa que este teste passa
```

O rust-anything não traduz código: o seu agente de programação (Claude Code, Codex, Cursor, ...) ou você escreve o código Rust.

O rust-anything fornece aquilo que um agente não consegue adivinhar de forma fiável: onde o tempo é gasto, o que deve ser migrado primeiro e em que ordem, uma ponte para que o restante código continue a chamar Rust com a mesma API, o comportamento exato que a migração deve preservar, uma forma segura de disponibilizar a nova implementação e uma verificação que determina quando a migração está concluída.

## Linguagens

| Linguagem | Unidade | Ponte | Registado e reproduzido por |
| --- | --- | --- | --- |
| TypeScript/JavaScript | Pasta ou ficheiro | napi-rs ou wasm-bindgen com um protocolo binário gerado; inclui classes e operações assíncronas | Node, executando diretamente os ficheiros `.ts` |
| Python | Pacote ou módulo | PyO3 (abi3), conversão direta, exceções tipadas | Python, importando o original |
| C | Ficheiro `.c` | Funções `extern "C"` com os nomes originais e um header | O original compilado como biblioteca partilhada, chamado através de ctypes, uma execução independente por caso |
| Go | Pacote | Chamadas cgo tipadas e um protocolo binário gerado, num pacote com a API original | Um driver Go gerado, compilado como módulo independente |
| Ruby | Ficheiro ou pasta de funções de módulo | Uma extensão magnus nos módulos originais | Um driver Ruby gerado |
| Java | Pacote de métodos `public static` | JNI tipado e um protocolo binário gerado, em classes wrapper com os métodos originais | Um driver de reflexão gerado |
| PHP (pré-visualização) | Pasta de funções e métodos `public static` | Próximo passo: PHP FFI através de uma ABI C | Aplicações completas atualmente: `app record`, `app replay` e a front door, para CLIs e servidores (`php -S`) |
| C# (pré-visualização) | Pasta de métodos `public static` | Próximo passo: P/Invoke através de uma ABI C | Aplicações completas atualmente: `app record`, `app replay` e a front door, para CLIs e servidores ASP.NET (`dotnet <app>.dll`) |

Todas as linguagens, exceto C, PHP e C#, também recebem classes de processamento em lote (`--batch`): os elementos atravessam a ponte uma única vez e permanecem em Rust, e cada chamada processa todos eles em todos os núcleos.

A linguagem é detetada a partir do repositório (`go.mod`, `pom.xml`, um `.csproj` ou `.sln`, `pyproject.toml`, `Gemfile`, `composer.json`, `package.json` ou, caso contrário, os ficheiros de código-fonte mais comuns). A opção `--lang` permite substituir essa deteção.

Os tipos são obtidos a partir do código-fonte: tipos de TS, anotações de Python, assinaturas de C, Go, Java e C#, tags YARD de Ruby, tipos PHP e phpdoc. Parâmetros sem tipo que são utilizados como números são inferidos como números.

O PHP está em pré-visualização: `analyze` planeia uma aplicação PHP (pacotes Composer e carregamento automático PSR-4, riscos como comparações flexíveis e overflow de inteiros para floats, pacotes Composer associados a crates).

Uma CLI ou servidor PHP pode ser registado, reproduzido e colocado atrás de uma front door em Rust. A migração das suas unidades para Rust através do FFI do PHP será o próximo passo ([issue #2](https://github.com/erkamyaman/rust-anything/issues/2)).

O C# está em pré-visualização da mesma forma: `analyze` lê projetos `.csproj` e os respetivos pacotes NuGet (associados a crates), resolve diretivas `using` para pastas e identifica diferenças do C# (`decimal`, `dynamic`, consultas adiadas do LINQ, `Task`, `lock` e reflexão).

Uma CLI C# ou um servidor ASP.NET pode ser registado, reproduzido e colocado atrás de uma front door em Rust. A migração de unidades através de P/Invoke será implementada posteriormente.

## Como funciona

```text
profile ──> analyze ──> bridge ──> record ──> port.rs ──> diff ──> bench ──> shadow ──> gate
 onde o       o que       o crate     o que o      você ou       cada      mais        ambos lado    concluído
 tempo é      migrar      Rust e      original     o seu agente  caso      rápido?     a lado em     significa
 gasto        primeiro    o wrapper   faz          escreve       registado resultado  produção      que passa
```

O original continua a ser a fonte de verdade: `record` executa-o com casos extremos (e os seus próprios dados de entrada) e guarda o que devolve ou lança; `diff` reproduz cada caso contra a implementação Rust. Nada é disponibilizado até que todos os casos correspondam e `gate` seja aprovado.

Os componentes que chamam o código continuam a utilizar a API original durante todo o processo.

Uma aplicação completa passa pelo mesmo ciclo, unidade por unidade, dentro de uma estrutura que comprova o funcionamento de todo o programa ([Migrar uma aplicação completa](#migrar-uma-aplicacao-completa)):

```text
analyze --whole-app ──> app record ──> app front-door ──> por unidade: o ciclo acima, depois app wire ──> app lift
 formato, cada          o que a aplicação  Rust controla o       gate aprovado, a unidade responde em      Rust puro,
 dependência e as       faz a partir       ponto de entrada;     Rust: reprodução a 100%, taxa de          comprovado
 decisões necessárias  do exterior        o original responde  fallback reduzida                     pela reprodução
```

## O ciclo

| Etapa | Comando | O que faz |
| --- | --- | --- |
| 0. Analisar desempenho | `rust-anything profile <repo> -- node bench.mjs` | Executa uma carga de trabalho real com o profiler da linguagem (node, cProfile, `go test` pprof, JFR, um tracer Ruby): funções mais pesadas por tempo inclusivo, os seus chamadores e os ciclos que devem ser processados em lote; identifica código que já está compilado (numba, Cython, JAX), onde Rust oferece poucos ganhos |
| 1. Planear | `rust-anything analyze <repo>` | Unidades, ordem de migração, riscos com `file:line`, ponte por unidade, compatibilidade entre dependências e crates, melhores unidades para começar; `--whole-app` adiciona pontos de entrada e estrutura, todas as dependências (importadas ou declaradas) com o respetivo crate, grupos de unidades que se importam mutuamente e decisões numeradas com respostas recomendadas |
| 2. Criar a ponte | `rust-anything bridge <repo> <unit>` | Cria um crate com os bindings (`lib.rs`, mais o wrapper carregado pela linguagem de origem) e estruturas iniciais para migrar (`port.rs`); `--batch fn:param` adiciona uma classe que mantém muitos valores de `param` em Rust |
| 3. Registar | `rust-anything record <crate>` | Executa o original com casos extremos gerados (caracteres não ASCII, emojis, `-0`, `NaN`, inteiros onde se esperam floats, ...) e com todas as armadilhas semânticas de cada parâmetro (comprimento e maiúsculas/minúsculas de strings, divisão com sinal, limites de overflow, impressão de floats, ordem de mapas e ordenação), guardando `cases.jsonl`; `--float-tolerance 1e-9` permite que floats correspondam dentro dessa margem em código numérico |
| 3. Compilar | `rust-anything build <crate>` | Compila a parte Rust: `.node`, pacote wasm, extensão Python ou biblioteca partilhada |
| 3. Comparar | `rust-anything diff <crate>` | Reproduz os casos registados contra Rust, chamado da mesma forma que os componentes do original o chamam; apresenta as divergências |
| 3. Benchmark | `rust-anything bench <crate>` | Mede o tempo dos casos registados no original e em Rust, incluindo a ponte |
| 4. Shadow | `rust-anything shadow <crate>` | Implementação substituta que executa ambas as versões, devolve o resultado original e comunica divergências; `RUST_ANYTHING_MODE=old\|shadow\|new` |
| 5. Verificação | `rust-anything gate <crate>` | fmt, clippy `-D warnings`, testes, auditoria de `unsafe`, nenhuma parte por migrar, um caso registado que falha para cada caminho de erro do original, sem `unwrap`/`expect`/`panic!` onde o original devolve um erro (a menos que esteja marcado como `// INFALLIBLE: <why>`), compilação, API e comportamento |
| Agentes | `rust-anything setup` | Regista o servidor MCP (`rust-anything mcp`, cada etapa como uma ferramenta) e a skill do fluxo de trabalho ([`skills/rust-anything/SKILL.md`](../skills/rust-anything/SKILL.md)) nos seus agentes de programação |

## Migrar uma aplicação completa

O objetivo é obter uma aplicação totalmente escrita em Rust que se comporte como a original, mantendo a original como referência.

O seu agente escreve o código Rust; o rust-anything organiza o trabalho, cria a estrutura inicial e comprova cada etapa.

A [skill de migração de aplicações completas](../skills/rust-anything/whole-app.md) orienta o agente durante o processo, começando pelas decisões que só você pode tomar:

- **Definição de requisitos**: o agente faz perguntas por etapas, cada uma acompanhada da resposta recomendada, até que todas as decisões das quais a migração depende estejam resolvidas. Regista cada decisão como um ADR em `rust/DECISIONS.md`, juntamente com `rust/GLOSSARY.md`, que associa os termos originais aos nomes utilizados em Rust.
- **Investigação**: agentes auxiliares consultam as fontes primárias de cada dependência e escrevem `rust/research/<topic>.md`, incluindo todas as armadilhas semânticas encontradas.
- **Entre sessões**: `rust/MAP.md` lista todas as unidades e o respetivo estado; uma sessão assume uma unidade antes de começar e cada ponto de controlo deixa um `rust/HANDOFF.md` para a sessão seguinte. As unidades de uma mesma fase podem ser migradas em paralelo por subagentes.
- **Transição**: o agente faz tudo o que consegue e escreve `rust/cutover.sh`, um script interativo para as etapas que só você pode executar (deploys, DNS, secrets), com uma forma de reverter cada etapa.

A definição de requisitos, a investigação e estas práticas foram adaptadas das [skills de Matt Pocock](https://github.com/mattpocock/skills).

Comece pelo planeamento: `rust-anything analyze . --whole-app` adiciona a estrutura da aplicação (CLI, servidor ou biblioteca) e os pontos de entrada, todas as dependências externas (importadas ou declaradas) com o respetivo crate Rust e a sua compatibilidade, a ordem de migração organizada em grupos (unidades que se importam mutuamente são migradas em conjunto) e decisões numeradas com respostas recomendadas: unidades que devem ser mantidas, unidades bloqueadas e dependências sem crate ou com suporte parcial.

Depois, comprove o funcionamento de todo o programa a partir do exterior. `record` e `diff` comprovam uma unidade; `app record` e `app replay` comprovam a aplicação, para CLIs e servidores nas seis linguagens (a aplicação é tratada como uma caixa-preta):

```sh
rust-anything app record . -- python3 cli.py          # o comando que executa o original
rust-anything app replay .                            # o original deve passar a 100%
rust-anything app replay . --build "target/release/mytool"
```

- `app record` executa o original com os exemplos documentados da própria aplicação (linhas `$ mytool ...` nos ficheiros Markdown e shell, juntamente com os ficheiros que mencionam), um ficheiro JSONL `--inputs` (`{"name", "args", "stdin", "env", "files"}`) e armadilhas semânticas derivadas desses casos (strings não ASCII e emojis, divisão e módulo negativos, overflow, floats grandes e pequenos, ordem de mapas e ficheiros inexistentes). Cada caso é executado duas vezes; aquilo que for diferente entre as duas execuções transforma-se num wildcard `[..]`. `--normalize timestamps|uuids|key-order` ou `--normalize name=regex` adiciona normalizadores, guardados juntamente com os casos.
- Os casos são ficheiros [trycmd](https://docs.rs/trycmd) em `rust/app-cases/`: `<case>.toml` (argv, env, código de saída), `.stdin`, `.stdout`, `.stderr`, `.in/` (ficheiros de entrada) e `.out/` (ficheiros escritos). Leia-os e edite-os manualmente; um teste Rust pode executá-los com `trycmd` quando a migração já tiver um binário.
- `app replay` executa qualquer compilação contra os casos, apresenta `passed/total`, escreve `rust/app-cases/replay-report.md` com uma comparação para cada caso que falhou e termina com um código diferente de zero perante qualquer divergência. Uma compilação que acrescenta entradas ao ficheiro indicado por `RUST_ANYTHING_FALLBACK_LOG` (uma linha por cada fallback para o original), como faz a front door abaixo, também tem a sua taxa de fallback apresentada.
- `app replay --case <name>` volta a executar um único caso pelo nome indicado no relatório: o ciclo rápido e repetível para corrigir uma divergência antes de executar tudo novamente.

Depois, transfira o ponto de entrada para Rust e atribua-lhe os comandos, uma unidade de cada vez:

```sh
rust-anything app front-door .                            # rust/app: todos os comandos executam o original
rust-anything app wire . textkit --command upper          # depois de textkit-rs passar no gate
# escreva o código de ligação em rust/app/src/units/textkit.rs e depois:
rust-anything app wire . textkit                          # novamente a 100%, com menor taxa de fallback
```

- `app front-door` cria `rust/app`, um binário Rust com o nome da aplicação: um parser clap para os comandos e flags presentes nos casos registados, em que cada comando executa o original com os mesmos argv, stdin e ambiente, transmitindo o respetivo resultado e código de saída. Cada fallback é contabilizado, pelo que reproduzir a nova front door resulta em 100% de aprovação e 100% de fallback (a ferramenta compila e reproduz para demonstrá-lo). Nunca substitui `rust/app`: a partir daí, o código pertence-lhe.
- `app wire <repo> <unit> --command <name>` executa `gate` no crate da unidade (`--skip-gate` se já tiver passado), adiciona-o a `rust/app` como biblioteca, cria `src/units/<unit>.rs` para você ou para o seu agente preencher (analisar os argumentos, chamar `<crate>::port`, apresentar o que o original apresenta), encaminha os comandos para essa unidade e depois compila e reproduz. `RUST_ANYTHING_UNIT_<NAME>=original` envia uma unidade ligada de volta para o original até à sua migração completa.

Ligue também o próprio nome da aplicação como um comando (`--command mytool`) para os casos em que o argv não especifica nenhum comando: sem argumentos, comandos desconhecidos e erros de utilização.

Quando a reprodução passar com uma taxa de fallback de 0 e todas as unidades passarem no gate, transforme-a numa aplicação totalmente escrita em Rust:

```sh
rust-anything app lift .
```

- `app lift` recusa-se a continuar até que ambas as condições sejam cumpridas e indica o que está a impedir a conclusão: casos que ainda recorrem ao original, código de ligação que continua por implementar ou unidades que falham no gate.
- Primeiro, numa cópia, remove o caminho de fallback e os interruptores de emergência, transforma cada crate de unidade numa biblioteca simples de `rust/app` (sem `cdylib`, bindings ou wrappers gerados) e adiciona `rust/app/tests/app_cases.rs`, que executa `rust/app-cases` com trycmd através de `cargo test`, para que o CI precise apenas de cargo.
- Depois executa a lista de verificação da migração: fmt, clippy `-D warnings` e testes em cada unidade e em `rust/app`, todos os destinos indicados em `rust/DECISIONS.md` compilados ou verificados onde estão instalados, ficheiros lidos em tempo de execução e pastas de recursos não incorporadas no binário, e reprodução no binário puro. As alterações só são gravadas quando tudo passa. O original nunca é alterado.

### Servidores

Os mesmos comandos também comprovam o funcionamento de servidores HTTP.

`--http` indica que o comando inicia um servidor; a ferramenta obtém a porta a partir de `PORT` ou de `{port}` no comando (`--port` para servidores que escutam sempre na mesma porta):

```sh
rust-anything app record . --http -- node server.js
rust-anything app replay .
rust-anything app front-door .                                    # axum: todas as rotas encaminhadas
rust-anything app wire . api --route 'GET /users/{id}' --route '*'
rust-anything app lift .
```

- Os pedidos vêm de linhas `curl` na documentação da aplicação (`curl -X POST -d ... http://localhost:8080/x`), de `--inputs` (`{"name", "method", "path", "headers", "body"}`) e de casos extremos: segmentos de caminho e valores de query substituídos pelas mesmas armadilhas utilizadas nos argumentos CLI, corpos para casos de texto e JSON e uma rota desconhecida. Cada execução inicia o servidor de novo e envia os pedidos por ordem de nome, preservando o estado entre pedidos.
- Os casos ficam em `rust/app-cases/http/<case>.toml` (o pedido, o estado e os cabeçalhos relevantes) e `<case>.body` (o corpo da resposta, com `[..]` onde duas execuções foram diferentes). Os cabeçalhos de data, servidor e outros que variam por resposta são omitidos; elimine qualquer linha de cabeçalho que não lhe interesse.
- A front door é um servidor axum que inicia o original numa porta própria e encaminha todas as rotas que nenhuma unidade responde. `wire --route` utiliza rotas axum: `METHOD /path/{param}`, `/path` para qualquer método e `*` para tudo o resto; o código de ligação recebe a rota, os seus parâmetros e o pedido. `lift` remove o proxy; os casos HTTP passam então a ser executados no CI com `app replay`.

### Bibliotecas

Uma biblioteca não tem um processo para reproduzir: a sua API pública é a front door, e os casos registados de cada unidade constituem a prova.

```sh
rust-anything app front-door .        # rust/app: um crate Rust com a API pública
# cada unidade passa pelo ciclo: bridge, record, port.rs, build, diff, gate; depois:
rust-anything app wire . textkit-rs   # reexportado por rust/app; o original importa o seu shadow
rust-anything app replay .            # casos de todas as unidades ligadas; fallback = exports ainda no original
rust-anything app lift .
```

- `app front-door` encontra a API pública (os exports de todas as unidades) quando o repositório não tem `main` nem servidor (`--library` caso contrário) e cria `rust/app` como um crate de biblioteca. Cada unidade ligada torna-se um módulo: `pub use textkit_rs::port as textkit;`.
- `app wire` recebe um crate criado por `bridge`, executa `gate` e escreve a implementação shadow substituta da unidade: o pacote original importa-a no lugar da unidade, pelo que os seus chamadores mantêm a API original e passam a utilizar Rust. `RUST_ANYTHING_UNIT_<NAME>=original` envia novamente a unidade para o original (C: compilar sem as flags da shadow).
- `app replay` executa os casos registados de todas as unidades ligadas através dos seus bindings. A taxa de fallback representa a proporção de exports públicos que Rust ainda não consegue responder: unidades não ligadas e exports que `bridge` mantém na linguagem original.
- `app lift` exige fallback 0 e que todas as unidades tenham passado no `gate`; remove os bindings, wrappers e shadows das unidades e deixa `rust/app` como uma única biblioteca Rust pura. Não altera nenhum `port.rs`, pelo que os casos que passaram através dos bindings continuam a descrevê-lo; a lista de verificação avisa sobre ficheiros do original que ainda importam as shadows.

As cinco operações também estão disponíveis como ferramentas MCP: `app_record`, `app_replay`, `app_front_door`, `app_wire` e `app_lift`.

## Estudo de caso: o núcleo do x18n

Todas as 29 funções do núcleo do x18n que podem ser migradas sem alterar a API foram migradas com rust-anything: todos os gates passam e 7.925 casos registados correspondem exatamente.

O `rust-anything bench` mostrou depois que as migrações são mais lentas do que TypeScript quando chamadas a partir de JavaScript, porque o custo da ponte é superior ao trabalho realizado.

Relatório completo: [`demo/x18n-core`](../demo/x18n-core/README.md).

A lição está integrada na ferramenta: meça com `bench` antes de disponibilizar uma migração.

## Caminhos críticos: mantenha os dados em Rust

Uma migração chamada uma vez por elemento paga o custo da ponte uma vez por elemento e perde para um JIT.

O que funciona é transferir o ciclo inteiro: `profile` identifica-o e `--batch` gera uma classe que recebe os elementos uma única vez e executa a função sobre todos eles por chamada, utilizando todos os núcleos e resultados em typed arrays.

```sh
rust-anything profile ../x18n -- node --experimental-strip-types $PWD/demo/x18n-search/search.ts .
# -> fuzzyScore: um quarto da execução, chamado por cada chave através de `matched`: processar em lote
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --batch fuzzyScore:text
```

```js
const search = new FuzzyScoreBatch(keys)          // uma vez
const order = search.rank(query, 0)               // por tecla: índices, melhores primeiro
```

Uma estrutura `FuzzyScoreIndex` em `port.rs` substitui o ciclo padrão por outro que prepara os elementos uma única vez e consegue classificá-los de forma autónoma (`rank`).

Mantém as chaves em minúsculas, cada uma com uma máscara de caracteres, uma tabela com a primeira posição de cada carácter comum em cada chave (uma consulta de uma letra corresponde a uma coluna) e as correspondências da última consulta (ao escrever `se` depois de `s`, volta a classificar apenas aquilo que correspondeu a `s`).

Na pesquisa da barra lateral do x18n, com 50.000 chaves, escrevendo letra por letra e obtendo resultados idênticos:

| | Por consulta | Em comparação com TS |
| --- | ---: | ---: |
| TS: `map(fuzzyScore)`, filter, sort | 10 ms | 1x |
| TS com a mesma redução de pesquisa utilizada pelo índice | 4,1–5,4 ms | 2x |
| A mesma migração, chamada por chave | - | 0,2–0,4x |
| `FuzzyScoreBatch`, índice padrão (4 núcleos) | 5,1 ms | 1,7x |
| `FuzzyScoreBatch` com `FuzzyScoreIndex` (napi, 4 núcleos) | 0,45–0,56 ms | **18–22x** |
| O mesmo com wasm (uma thread) | 0,95 ms | **11,5x** |

Em comparação com TS a realizar a mesma redução de pesquisa, Rust continua a ser 7–12x mais rápido (wasm 5x).

Transformar os índices devolvidos em chaves através de um ciclo simples tem um custo 20x superior: `Array.from(order, i => keys[i])` demora 0,4 ms.

Todas as linguagens, exceto C, PHP e C#, recebem processamento em lote, que supera o original mesmo quando as migrações por chamada perdem.

O mesmo trabalho em 4 núcleos, com resultados e erros idênticos (benchmarks em cada pasta de demonstração):

| Linguagem | Carga de trabalho | Original | Migração por chamada vs. original | Lote vs. original |
| --- | --- | ---: | ---: | ---: |
| TS | Pesquisa x18n, 50.000 chaves | 10 ms | 0,2–0,4x | **20x** |
| Python | `slugify`, 20.000 strings | 98 ms | - | **17x** |
| Ruby | `slugify`, 20.000 strings | 110 ms | - | **12,7x** |
| Ruby | `shellescape` (stdlib), 50.000 valores mistos | 88 ms | - | **11,8x** |
| Go | `Slugify`, 50.000 strings | 49 ms | 0,93x | **4x** |
| Java | `slugify`, 50.000 strings | 43 ms | 0,68x | **3x** |

Os programas originais compilados ganham menos: o trabalho por elemento já é rápido, pelo que o processamento em lote ganha sobretudo através do número de núcleos.

Os crates de processamento em lote alocam memória com mimalloc: com o alocador do sistema, o processamento em lote do Go era mais lento do que utilizar uma única thread.

Demonstração: [`demo/x18n-search`](../demo/x18n-search/README.md).

## Código real em seis linguagens

O `path` do Go, o `shellwords` do Ruby, o `colorsys` do Python e comportamentos do JDK e glibc por trás de pequenas interfaces: todas as migrações passam no respetivo gate, com 13.010 casos registados no total.

As execuções identificaram e corrigiram erros no próprio rust-anything (floats com diferenças de uma ULP através de `serde_json`, falhas do C durante o registo e código sem tipos a receber dados de entrada inválidos).

Quando chamadas por função, a migração Ruby executa 4,4x mais rápido do que Ruby e a migração Python 1,35x mais rápido do que CPython, enquanto as funções individuais de Go e Java continuam mais rápidas nas respetivas linguagens.

Como processamento em lote, todas ganham (consulte a tabela acima).

Relatório: [`docs/real-world-languages.md`](real-world-languages.md).

## Exemplo: um módulo real do x18n

`packages/core/src/fuzzy.ts` do [x18n](https://github.com/x18n-dev/x18n), migrado das duas formas em [`demo/`](../demo):

```sh
rust-anything analyze ../x18n                                      # fuzzy.ts: pronto, wasm-bindgen (o core funciona em navegadores)
rust-anything bridge ../x18n packages/core/src/fuzzy.ts --out demo/fuzzy-rs
rust-anything record demo/fuzzy-rs --count 2000
# escreva src/port.rs
rust-anything gate demo/fuzzy-rs
```

Uma primeira migração que utilizava o `char` do Rust para indexação passou nos testes simples, mas falhou no `diff`:

```text
198/200 cases match
- fuzzyScore("b😀", "a😀b😀c"): expected {"ok":1997}, got {"ok":1998}
```

O `indexOf` do JS conta unidades de código UTF-16, pelo que um emoji ocupa duas posições.

A migração em `demo/*/src/port.rs` utiliza os helpers `utf16` gerados e passa nos 2000/2000 casos e no gate, tanto com napi-rs (`demo/fuzzy-napi`) como com wasm-bindgen (`demo/fuzzy-rs`).

O plano que o rust-anything gera para todo o x18n: [`docs/examples/x18n.md`](examples/x18n.md).

## Instalação

Para instalar a partir de um clone, execute o comando na raiz do checkout do rust-anything:

```sh
cargo install --path .
```

Para instalar sem clonar o repositório, use `cargo install rust-anything`.

`record`, `diff` e `bench` executam o original no seu próprio ambiente de execução: Node 22.6+ para TS (executa diretamente os ficheiros `.ts`), Python 3.9+ para Python e C (ctypes), Go 1.21+, Ruby 3+ e JDK 17+ (`javac` e `java`).

`profile` no Node necessita de Node 24+, que permite utilizar `--cpu-prof` em `NODE_OPTIONS`.

C também necessita de um compilador C.

As pontes wasm também precisam de `rustup target add wasm32-unknown-unknown` e `cargo install wasm-bindgen-cli --version <the crate's wasm-bindgen version> --locked`; `build` indica a versão exata.

### Windows

O CI nativo do Windows utiliza o destino Rust `x86_64-pc-windows-msvc`.

Instale a toolchain MSVC estável e o Visual Studio Build Tools com a carga de trabalho **Desenvolvimento para desktop com C++**; o compilador e o linker C são necessários para pontes C e extensões Rust nativas.

Instale o ambiente de execução da linguagem de origem que está a migrar.

Python pode estar disponível como `python3` ou `python`; o rust-anything deteta ambos.

O destino GNU do Windows não é testado pelo CI.

Execute a suite de integração de pontes nativas a partir de um Developer PowerShell:

```powershell
rustup default stable-x86_64-pc-windows-msvc
cargo test --locked --test native -- --nocapture
```

A suite compila e carrega extensões Node e Python reais baseadas em DLL, bem como as pontes nativas suportadas para cada ambiente de execução presente no `PATH`.

Os ambientes de execução opcionais em falta são indicados como ignorados; Cargo, a biblioteca padrão Rust ativa e o linker MSVC são obrigatórios.

Se Cargo indicar que não consegue encontrar `std`, reinstale o destino ativo com:

```powershell
rustup target remove x86_64-pc-windows-msvc
rustup target add x86_64-pc-windows-msvc
```

Se a ligação falhar, execute a partir de um Visual Studio Developer PowerShell e confirme que `where.exe link` encontra o linker MSVC.

Os testes utilizam pastas temporárias, incluindo um caminho com espaços e caracteres Unicode, e removem os artefactos gerados após uma execução bem-sucedida.

Para agentes, `rust-anything setup` regista tudo (consulte Início rápido).

Para adicionar manualmente o servidor MCP a um único projeto (`.mcp.json`):

```json
{ "mcpServers": { "rust-anything": { "command": "rust-anything", "args": ["mcp"] } } }
```

## O que `bridge` decide

- Os exports que não conseguem atravessar uma ponte permanecem na linguagem de origem, com a respetiva justificação, e o módulo shadow reexporta o original. Para TS: funções que recebem ou devolvem funções, generators e iterators, RegExp, verificações `instanceof`, generics e valores cujos tipos (acompanhados através de imports, reexports e `extends`) contêm funções. `--keep "name: reason"` mantém mais elementos, por exemplo código que depende de dados `Intl`.
- Os tipos TS são associados a tipos Rust, com aliases de tipos resolvidos através de imports e tipos de parâmetros inferidos a partir dos valores predefinidos; os valores estruturados atravessam a ponte através de um protocolo binário gerado (JSON apenas como alternativa para estruturas que o protocolo não suporta).
- JSON não consegue representar `undefined`, NaN, Infinity, -0 ou surrogates isolados: os valores estruturados transportam marcadores (`{"$undefined": true}`, `{"$num": "NaN"}`, `{"$utf16": [...]}`) que o `index.cjs` gerado traduz, com helpers em `js.rs` do crate.

`record` executa os ficheiros TS diretamente: um hook de resolução do Node segue imports ao estilo de bundlers (`./errors` para `./errors.ts`), `--resolve-from` fornece pacotes npm quando o repositório não tem nenhum instalado e TS que necessita de transformação (enums, propriedades de parâmetros) é novamente executado com `--experimental-transform-types`.

## O que `analyze` analisa

- Pacotes (`package.json`) e ficheiros de código-fonte; ignora `node_modules`, ficheiros de compilação, fixtures, playgrounds e configurações de ferramentas. Blocos `<script>` de Vue/Svelte/Astro são analisados para identificar imports.
- **Unidades**: uma pasta de ficheiros de código-fonte ou um ficheiro na raiz do código-fonte de um pacote.
- **Fases**: os imports de uma unidade surgem em fases anteriores; ciclos de imports são migrados em conjunto.
- **Ponte**: napi-rs quando a unidade ou qualquer elemento importado necessita de Node; wasm-bindgen para código portátil; manter em JS para código de interface e editores.
- **Prontidão** (nível de segurança) e **prioridade** (segurança e benefício: ciclos e processamento de strings, testes e dimensão).

| Risco | Gravidade | Exemplo |
| --- | --- | --- |
| Deslocamentos de strings | alta | `slice`, `indexOf`, `matchAll`, a flag `d`: UTF-16 vs UTF-8 |
| Sintaxe de regex | alta | lookaround, backreferences, `y`: não suportados pelo crate `regex` |
| Regex dinâmica | alta | `new RegExp(userPattern)`: sintaxe JS em tempo de execução |
| Código dinâmico | alta | `eval`, `new Function`, `import()` calculado |
| Tipagem dinâmica | média | `any`, `'key' in value` |
| Coleções ordenadas | média | `Map`, `Set`, `Object.keys`: ordem de inserção |
| Async, generators | média | limites de promises e generators |
| Herança de classes e reflexão | média | `extends`, `Proxy`, `Reflect`, `Symbol` |
| APIs baseadas em callbacks | média | parâmetros e métodos tipados como funções: pontes com muitas chamadas |
| Exceções, números e JSON | baixa | `throw`, operações bitwise, ordem de `JSON.stringify` |

## Desenvolvimento

```sh
cargo test                        # testes unitários, repositório fixture, ciclo record/diff/shadow (necessita de node), app record/replay por linguagem
cargo clippy --all-targets -- -D warnings
cargo fmt
```

Decisões de design e respetivas justificações: [DECISIONS.md](../DECISIONS.md).

## Atualizar ou remover

```sh
cargo install rust-anything                                    # atualizar (Cargo)
npm install -g rust-anything@latest                            # atualizar (npm)
rust-anything setup                                            # atualizar configurações dos agentes
rust-anything setup --remove && cargo uninstall rust-anything  # remover (Cargo)
rust-anything setup --remove && npm uninstall -g rust-anything # remover (npm)
```

`setup --remove` remove apenas as entradas do rust-anything; as cópias guardadas (`<file>.rust-anything.bak`) permanecem até serem eliminadas manualmente.

## O que não consegue detetar

Passar significa que Rust corresponde a todos os casos registados, nada mais.

Os problemas das reescritas costumam estar fora do registo, por isso é importante conhecer os limites:

- **Entradas que ninguém registou.** Os casos gerados, as armadilhas e os seus próprios `--inputs` representam o limite. Adicione entradas reais (amostras de produção, relatórios de erros e fixtures de teste do original); a entrada de um utilizador que causa problemas em produção raramente é aquela em que um gerador pensa.
- **Expressões regulares.** O crate `regex` não tem lookaround nem backreferences e até um padrão que compila pode tratar `\w`, `\b`, `\d` e a correspondência sem distinção entre maiúsculas e minúsculas em texto não ASCII de forma diferente de JS, Python ou Java. Substituir por `fancy-regex` ou reescrever o padrão pode fazer passar todos os casos registados e ainda assim produzir resultados diferentes para um `ı` turco sem ponto ou um zero-width joiner. `record` adiciona armadilhas de regex (incluindo esses caracteres, o sinal Kelvin, o s longo, algarismos indo-arábicos, separadores de linha e sigma final) a todas as funções de um ficheiro que utilize regexes, mas também deve testar os seus padrões reais com texto real.
- **O que muda entre execuções.** `record` executa o original duas vezes e identifica o que mudou: valores variáveis (horas, IDs) tornam-se wildcards; as mesmas linhas noutra ordem (hash maps, concorrência) são comparadas em qualquer ordem, pelo que uma migração ainda tem de produzir exatamente essas linhas; um número diferente de linhas transforma-se em `...`, que corresponde a qualquer coisa. `record` apresenta cada tipo: examine todos, porque diferenças na ordem de hashes ou concorrência são precisamente aquilo que pode mudar numa migração real.
- **Floats.** A formatação de números para texto difere entre linguagens (`1e21`, `-0`, número de dígitos). Os casos extremos incluem esses valores e têm de corresponder exatamente; `--float-tolerance` permite apenas diferenças de arredondamento, nunca de formatação.
- **Tudo o que não aparece na saída.** Tempo de execução, memória, concorrência sob carga e efeitos secundários que não sejam stdout, stderr, códigos de saída, ficheiros escritos e respostas HTTP (chamadas de rede, bases de dados e sinais) não são comparados.
- **Outras plataformas.** Um registo comprova o comportamento na máquina onde foi executado. C cujos resultados dependem do tamanho dos tipos, da ordem dos bytes ou do compilador pode comportar-se de forma diferente no destino; `analyze` mantém em C o código que interage com o hardware por essa razão.

## Perguntas frequentes

**Reescreve automaticamente o meu código?**

Não. Identifica o que deve ser migrado, gera a ponte, regista o comportamento do original e compara Rust com ele. Você ou o seu agente escreve o código Rust em `port.rs`; `diff` e `gate` determinam quando está correto.

**A API da minha aplicação vai mudar?**

Não. Os componentes que chamam o código importam as mesmas funções (ou o módulo shadow, que executa ambas as versões e devolve o resultado do original enquanto ganha confiança).

**Rust é sempre mais rápido?**

Não, e o rust-anything deixa isso claro.

Uma pequena função chamada uma vez por elemento é frequentemente mais lenta em Rust, porque cada chamada atravessa uma ponte; V8, a JVM e Go executam essas funções em nanossegundos.

`profile` encontra o ciclo à sua volta, `--batch` transfere o ciclo inteiro e `bench` apresenta um resultado antes de disponibilizar a migração.

O código já compilado por numba, Cython ou JAX também é executado como código de máquina: `profile` e `analyze` identificam-no, porque migrá-lo oferece poucos ganhos de velocidade.

**O meu código é numérico; os floats vão corresponder exatamente?**

Muitas vezes, não: a ordem das operações, fused multiply-add e a biblioteca matemática diferem entre compiladores.

Registe com `--float-tolerance 1e-9` (`record` ou `app record`), e os floats serão considerados correspondentes dentro dessa proporção do maior valor (valor absoluto abaixo de 1).

Inteiros, texto e estruturas continuam a ter de corresponder exatamente.

**Consigo migrar uma aplicação que só tenho como APK, JAR ou .exe?**

Não. A ferramenta migra código-fonte: analisa as funções, regista o comportamento de cada uma e compara Rust com o original em execução.

Uma aplicação compilada não disponibiliza esses elementos para análise, e `analyze` indica isso.

Criar uma nova aplicação Rust a partir do comportamento visível de um binário é um projeto diferente.

**Devo migrar código C já testado e comprovado?**

Muitas vezes, não, e `analyze` indica onde.

Código C que acede a registos de hardware, depende do tamanho dos tipos ou da organização da memória do compilador ou utiliza assembly inline (`volatile`, bitfields, packed structs, `__asm__`, inteiros convertidos em endereços) é marcado como "manter em C": um registo na sua máquina não comprova nada sobre o destino, e código estável de drivers ou firmware ganha pouco com uma reescrita.

A lógica portátil à sua volta (análise de dados, protocolos e processamento de informação) é a parte que pode ser migrada com bons resultados.

**Consigo migrar a minha aplicação Electron?**

A lógica, sim; as janelas continuam a ser páginas web.

`analyze --whole-app` identifica Electron e planeia a migração do processo principal peça por peça, enquanto o renderer permanece como está.

Transferir a interface para Tauri (a mesma interface web com um backend Rust) é uma etapa separada, depois de a lógica estar em Rust.

**E quanto a C#, Kotlin ou Swift?**

C# está em pré-visualização (consulte [Linguagens](#linguagens)); Kotlin e Swift ainda não são suportados.

Cada linguagem necessita de um parser, um sistema de registo, uma ponte e um driver de reprodução, todos testados de ponta a ponta.

Abra uma issue (ou vote numa já existente) para a linguagem de que precisa.

**O código Rust não vai ficar muito maior do que o original?**

Não deveria.

`gate` compara as linhas da migração com as do original e falha quando ultrapassa 3x (mais 50 linhas para imports e assinaturas): normalmente isso significa escrever manualmente aquilo que um crate já faz ou tratar os casos um por um.

`analyze` apresenta os crates que devem ser utilizados.

**Migrar peça por peça não vai prender Rust à arquitetura antiga da aplicação?**

Apenas enquanto ambas as versões funcionam lado a lado.

Os registos verificam o comportamento nos limites da aplicação (a saída de uma CLI, as respostas de um servidor ou as funções exportadas de um módulo), não os seus detalhes internos.

Replique a estrutura antiga enquanto as unidades ainda atravessam a ponte; depois de `app lift` remover o original, reorganize livremente o código Rust, e `app replay` continuará a comprovar o comportamento.

Nada chama o original de volta também: a front door executa-o como um processo separado (ou encaminha pedidos HTTP para ele), as unidades ligadas são chamadas pelo original e nunca o contrário, e os callbacks permanecem na linguagem de origem.

**O meu código sai da minha máquina?**

Não. O rust-anything é executado localmente e não envia o seu código para lado nenhum.

Cargo descarrega crates normalmente, e o fornecedor do modelo utilizado pelo seu agente vê aquilo que o agente lhe envia, de acordo com a política desse fornecedor.

**O que preciso de ter instalado?**

Rust, juntamente com o ambiente de execução da linguagem que pretende migrar (consulte [Instalação](#instalacao)).

**Algo deixou de funcionar.**

Abra uma issue com o comando utilizado, a respetiva saída e a sua plataforma.

## Patrocinadores

O rust-anything é gratuito e de código aberto.

Se for útil para o seu trabalho, considere patrociná-lo. O seu apoio ajuda a manter o desenvolvimento.

<p>
  <a href="https://github.com/sponsors/erkamyaman"><img src="https://img.shields.io/badge/Sponsor-%E2%9D%A4-db61a2?logo=githubsponsors&logoColor=white" alt="Patrocinar rust-anything no GitHub" /></a>
</p>

### Patrocinadores empresariais

<!-- prettier-ignore-start -->
<a href="https://coderabbit.ai"><img src="https://github.com/coderabbitai.png?size=120" width="120" height="120" alt="CodeRabbit" /></a>
<!-- prettier-ignore-end -->

### Patrocinadores individuais

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

## Contribuir

Issues e pull requests são bem-vindos; [CONTRIBUTING.md](../CONTRIBUTING.md) explica a configuração, onde colocar os testes e como adicionar uma linguagem.

As decisões de design e as respetivas justificações estão em [DECISIONS.md](../DECISIONS.md).

Estudos de caso de migrações reais são especialmente bem-vindos.

Por favor, comunique problemas de segurança de forma privada ([SECURITY.md](../SECURITY.md)) e consulte o [código de conduta](../CODE_OF_CONDUCT.md).

## Licença

[MIT](../LICENSE) © [Erkam Yaman](https://github.com/erkamyaman).

As migrações e o código gerado no seu repositório pertencem-lhe.
