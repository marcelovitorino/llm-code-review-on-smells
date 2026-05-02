from html import escape
from typing import Optional, Tuple

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound


def render_code_html(
    source: str,
    language: str = "java",
    highlight_lines: Optional[Tuple[int, int]] = None,
    line_anchors: bool = True,
    inline_styles: bool = True,
) -> str:
    if source is None:
        return ""

    try:
        lexer = get_lexer_by_name(language, stripall=False)
    except ClassNotFound:
        lexer = get_lexer_by_name("text", stripall=False)

    hl_lines = []
    if highlight_lines is not None:
        start_line, end_line = highlight_lines
        if start_line and end_line and start_line <= end_line:
            hl_lines = list(range(start_line, end_line + 1))

    formatter = HtmlFormatter(
        linenos="inline",
        lineanchors="L" if line_anchors else "",
        anchorlinenos=line_anchors,
        hl_lines=hl_lines,
        cssclass="ls-code",
        nobackground=True,
        noclasses=inline_styles,
        style="default",
    )
    return highlight(source, lexer, formatter)


def get_pygments_css(cssclass: str = "ls-code") -> str:
    return HtmlFormatter(cssclass=cssclass, nobackground=True, style="default").get_style_defs(f".{cssclass}")


def build_oracle_details_html(
    severity: Optional[str],
    granularity: Optional[str],
    code_name: Optional[str],
    start_line: Optional[int],
    end_line: Optional[int],
    file_path: Optional[str],
) -> str:
    location = ""
    if granularity or code_name:
        location = f"{escape(granularity or '')} {escape(code_name or '')}".strip()
    line_range = ""
    if start_line and end_line:
        line_range = f"L{start_line}–L{end_line}"

    summary_parts = [escape(severity) for severity in [severity] if severity]
    if location:
        summary_parts.append(location)
    if line_range:
        summary_parts.append(line_range)
    summary_line = " · ".join(summary_parts)

    return (
        "<div class='oracle-meta'>"
        f"<div>{summary_line}</div>"
        f"<div class='oracle-path'>{escape(file_path or '')}</div>"
        "</div>"
    )


DECISION_TREE_HTML = """<div class="decision-tree">
<div class="dt-title">Árvore de decisão (em caso de dúvida)</div>
<pre>1. A resposta do LLM nomeia o smell-alvo (ou um sinônimo aceito)?
   ├── SIM →  Vá para 2.
   └── NÃO →  Vá para 4.

2. O intervalo de linhas indicado está contido na granularidade do oracle?
   ├── SIM →  Vá para 3.
   └── NÃO →  Classificar como HELPFUL.

3. A descrição é coerente E a refatoração sugerida é compatível com Fowler?
   ├── SIM →  Classificar como INSTRUMENTAL.
   └── NÃO →  Classificar como HELPFUL.

4. A resposta aponta de forma genérica para o problema do smell-alvo
   (mesmo sem nomeá-lo)?
   ├── SIM →  Classificar como HELPFUL.
   └── NÃO →  Vá para 5.

5. A resposta nega a presença de smells, está vazia/malformada,
   ou afirma fatos incorretos sobre o código?
   ├── SIM →  Classificar como MISLEADING.
   └── NÃO →  Vá para 6.

6. A resposta aponta um smell diferente do alvo (entre os 3 avaliados)
   que é plausível no contexto do snippet?
   ├── SIM →  Classificar como UNCERTAIN.
   └── NÃO →  Classificar como MISLEADING.</pre>
</div>"""


CODEBOOK_HTML = """<table class="codebook">
<thead><tr><th>Categoria</th><th>Critério curto</th></tr></thead>
<tbody>
<tr><td><b>I — Instrumental</b></td><td>Tipo correto + localização contida + descrição coerente + refatoração compatível com Fowler</td></tr>
<tr><td><b>H — Helpful</b></td><td>Aponta para o smell-alvo, mas com imprecisão de tipo, localização, descrição ou refatoração</td></tr>
<tr><td><b>M — Misleading</b></td><td>Nega o smell, falha na tarefa, ou afirma fatos incorretos</td></tr>
<tr><td><b>U — Uncertain</b></td><td>Aponta outro smell (entre os 3 avaliados) plausível, sem mencionar o alvo</td></tr>
</tbody>
</table>"""
