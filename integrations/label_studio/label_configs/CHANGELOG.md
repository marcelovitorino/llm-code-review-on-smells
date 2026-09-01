# Label Config Changelog

## v1 (initial)

Layout:

- Oracle banner with smell name, severity, granularity, code element name, line range, file path
- Focused snippet panel (max-height 300px, scrollable)
- Full file panel (max-height 400px, scrollable) with target lines highlighted via Pygments `hl_lines`
- LLM response box
- Collapsible decision tree (Section 6 of the labeling manual) — `<details>` block, between LLM response and Choices, populated via `decision_tree_html` task data field (constant defined in `integrations/label_studio/code_html.py:DECISION_TREE_HTML`)
- Single-choice classification (I/H/M/U) with hotkeys 1–4 (required) — stacked vertically, alias inclui o critério curto da Seção 8 do manual
- Optional checkbox `needs_review` (hotkey `d`) for ambiguous cases — defaults to off
- Free-text `comment` (6 rows) for synonyms, arbiter notes, justification

Cegamento: nenhuma exibição de `model_key`, `experiment_id`, `prompt_id`, `repetition`. Mapeamento de volta para essas chaves via `task_external_id` (`{llm_result_id}-{smell_occurrence_id}`) na tabela `evaluation_labels`.

### Refinamentos posteriores ao v1 (in place, antes da rotulagem começar)

- **Decision tree colapsável** + critério curto inline em cada Choice — adicionados depois da estrutura inicial, sem rotulagens persistidas anteriormente.
- **Oracle banner reorganizado**: `Smell-alvo: <nome>` em destaque (`font-size:1.35em`, azul escuro), o resto (severidade, granularidade, code name, line range, file path) movido pra `<details>` colapsável via `oracle_details_html` (gerado por `code_html.build_oracle_details_html`).
- **Árvore de decisão removida do painel** (in place, sem bump de versão): saíram o `<HyperText name="decision_tree">` do fim do `<View>`, os estilos `.decision-tree`/`.dt-title` e o campo `decision_tree_html` do task data novo. Mudança puramente de exibição — `decision_tree` não era `toName` de nenhum controle, então nenhuma annotation (`label`, `needs_review`, `comment`, todas em `llm_response`) foi afetada. As tasks já importadas continuam carregando `decision_tree_html` no `data`, agora sem uso. A árvore em si segue em `code_html.DECISION_TREE_HTML`.
