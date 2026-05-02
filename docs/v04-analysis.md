# V04

## Análise da V04

A V04 evolui o Meta Prompting da V03 em quatro direções:

1. **Persona elevada**: de "software reviewer" para "senior software developer". A mudança reflete o perfil dos revisores reais cujos comentários foram usados como base para os few-shot examples — committers de projetos Apache com anos de experiência no codebase.

2. **Definições completas de Fowler**: as definições resumidas da V03 foram substituídas pelos textos originais do capítulo 3 ("Bad Smells in Code") de Fowler, M. *Refactoring: Improving the Design of Existing Code*, 2nd ed., Addison-Wesley, 2018. Isso dá ao modelo o contexto completo das heurísticas, incluindo nuances e exceções (e.g., Strategy e Visitor como padrões que intencionalmente violam Feature Envy), em vez de resumos que perdem a riqueza do original.

3. **Instrução de compreensão prévia**: o prompt agora pede que o modelo entenda o propósito da classe, o relacionamento entre métodos e as responsabilidades antes de identificar problemas. Isso induz o modelo a demonstrar compreensão contextual na abertura da review, alinhando o comportamento com o de um reviewer humano que lê o código antes de comentar.

4. **Few-shot com código real**: os exemplos sintéticos da V03 foram substituídos por trechos de código extraídos de projetos Apache open-source (syncope, tez), com reviews adaptadas de comentários reais de code review identificados nesses repositórios. Isso expõe o modelo a código com complexidade de produção, em vez de exemplos didáticos onde o smell é evidente por construção.

**Comportamento esperado:**

- A review abre com uma contextualização do que o arquivo faz, antes de apontar problemas
- O modelo lida melhor com código real (nomes de domínio, condicionais compostas, múltiplos métodos) sem forçar smells onde não existem
- Redução de falsos positivos, já que os few-shot demonstram foco seletivo em meio a código "normal"

**Limitação a investigar:**

Os recortes de código nos few-shot não incluem o arquivo completo (omitem imports e package declarations), enquanto o input real via <code file> é o arquivo inteiro. Esse mismatch de formato entre exemplo e input pode ou não afetar o comportamento — é um ponto a validar experimentalmente.


## Mudanças em relação à V03

Persona: V03 usava "software reviewer". V04 usa "senior software developer".

Definições dos smells: V03 usava resumos de 2-3 linhas. V04 usa texto original de Fowler (cap. 3, Refactoring, 2nd ed., 2018).

Instrução de compreensão: Ausente na V03. V04 pede que o modelo entenda a classe antes de identificar problemas.

Few-shot (código): V03 usava código sintético (5-15 linhas). V04 usa código real extraído de projetos Apache open-source.

Few-shot (reviews): V03 tinha reviews escritas sem base empírica. V04 tem reviews adaptadas de comentários reais de code review.

Seções IMPORTANT e OUTPUT: inalteradas.


## Referências bibliográficas

Fowler, M. Refactoring: Improving the Design of Existing Code, 2nd ed., Addison-Wesley, 2018. Capítulo 3: "Bad Smells in Code". Definições de Long Method, Feature Envy e Data Class utilizadas integralmente na seção CODE SMELLS (DEFINITIONS) do prompt.

Catálogo online de refactorings referenciado nos few-shot examples: https://refactoring.com/catalog/


## Referências dos Few-Shot Examples


### Example 1 — Long Method

Smell: Long Method
Repositório: apache/syncope — git@github.com:apache/syncope.git
Arquivo fonte: core/logic/src/main/java/org/apache/syncope/core/logic/LoggerLogic.java
Pull Request: #52 — SYNCOPE-1144: configurable audit appenders with message rewrite option (https://github.com/apache/syncope/pull/52)
Autor do PR: @andrea-patricelli — https://github.com/andrea-patricelli (2017-07-12)
Review comment: discussion_r126933815 — https://github.com/apache/syncope/pull/52#discussion_r126933815
Autor do review: @ilgrosso — https://github.com/ilgrosso (2017-07-12)
Citação original: "Isn't this code a copy of what inserted in LoggerLoader? If so, please extract it into a public method in LoggerLoader and invoke that from here too."
Adaptação: Review expandida para formato de prosa: descreve o propósito da classe, identifica as múltiplas responsabilidades de setLevel, sugere Extract Method.


### Example 2 — Feature Envy

Smell: Feature Envy
Repositório: apache/tez — git@github.com:apache/tez.git
Arquivo fonte: tez-dag/src/main/java/org/apache/tez/dag/app/dag/impl/DAGImpl.java
Pull Request: #60 — TEZ-3363: Delete intermediate data at the vertex level for Shuffle Handler (https://github.com/apache/tez/pull/60)
Autor do PR: @shameersss1 — https://github.com/shameersss1 (2020-02-20)
Review comment (principal): discussion_r820285137 — https://github.com/apache/tez/pull/60#discussion_r820285137
Review comment (follow-up): discussion_r825298428 — https://github.com/apache/tez/pull/60#discussion_r825298428
Autor do review: @abstractdog — https://github.com/abstractdog (2022-03-06)
Citação original: "this part needs a bit of refactoring I think — ancestors+children parse should go into VertexImpl, as it has nothing to do with DAGImpl"
Citação follow-up: "what about putting all this to VertexImpl, like: vertex.initShuffleDeletionContext(deletionHeight)? that way you don't have to expose the init logic to DagImpl"
Adaptação: Review expandida para formato de prosa: descreve o papel de DAGImpl, identifica que parseVertexEdges opera em dados de VertexImpl, sugere Move Method.


### Example 3 — Data Class

Smell: Data Class
Repositório: apache/tez — git@github.com:apache/tez.git
Arquivo fonte: tez-api/src/main/java/org/apache/tez/client/registry/AMRecord.java
Pull Request: #427 — TEZ-4007: Introduce AmExtensions and Zookeeper-based FrameworkServices (https://github.com/apache/tez/pull/427)
Autor do PR: @abstractdog — https://github.com/abstractdog (2025-09-06)
Review comment 1: discussion_r2548941272 — https://github.com/apache/tez/pull/427#discussion_r2548941272 — "this is same as getHost() and nobody uses it"
Autor do review 1: @ayushtkn — https://github.com/ayushtkn (2025-11-21)
Review comment 2: discussion_r2669024497 — https://github.com/apache/tez/pull/427#discussion_r2669024497 — "I think there is no 'before setting the values' scenario given only final fields"
Autor do review 2: @abstractdog — https://github.com/abstractdog (2026-01-07)
Review comment 3: discussion_r2548957822 — https://github.com/apache/tez/pull/427#discussion_r2548957822 — "this looks unnecessarily costly, where do you use it?"
Autor do review 3: @ayushtkn — https://github.com/ayushtkn (2025-11-21)
Adaptação: Review expandida para formato de prosa: descreve AMRecord como container de metadados de AM, identifica ausência de comportamento além de armazenamento/serialização, sugere Encapsulate Field.


## Metodologia de coleta dos few-shot examples

Os few-shot examples foram obtidos através de busca automatizada nos inline review comments (API GitHub GET /repos/{owner}/{repo}/pulls/comments) dos repositórios apache/syncope, apache/tez, apache/tomcat e apache/tapestry-5. Os comentários foram filtrados com padrões regex que capturam linguagem informal comumente usada por revisores para descrever cada tipo de smell:

Long Method: "too (long|big|complex|large)", "split (this|the|it)", "extract .{0,20}(method|function)", "hard to (follow|read|understand)"

Feature Envy: "(should|could) (be|belong|move).{0,20}(class|object)", "move (this|the|it) to", "belongs (to|in)", "encapsulat"

Data Class: "(only|just).{0,20}(getter|setter|field)", "no .{0,15}(behavior|logic)", "anemic", "data (holder|container)"

Os resultados foram validados manualmente: cada comentário foi lido no contexto completo do PR (diff, thread de discussão, resposta do autor) para confirmar que o conteúdo discutido corresponde ao smell catalogado por Fowler. As reviews nos few-shot foram escritas no formato de prosa natural exigido pelo prompt, ancoradas no diagnóstico do reviewer humano original — preservando a essência do que foi apontado, mas expandindo para o formato de review completa com contextualização, evidência, impacto e sugestão de refactoring.

O repositório apache/tapestry-5 não possui inline review comments no GitHub (o projeto usa JIRA e mailing lists para code review). O repositório apache/tomcat retornou poucos resultados relevantes, com a maioria dos matches de "too long" referindo-se a comprimento de linhas de código ou HTTP headers, não a métodos.
