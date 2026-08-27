"""Gera analise/correcoes.html — CORRECOES_TEXTO.md na identidade visual da auditoria."""
import html, re, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent
CSS = (RAIZ / "auditoria.html").read_text(encoding="utf-8")
CSS = CSS[CSS.index("<style>") + 7:CSS.index("</style>")]

EXTRA = """
.wrap{max-width:860px}
h2{border-top:1px solid var(--rule); padding-top:26px; margin-top:52px}
h2:first-of-type{border-top:0}
.verdicts{display:flex; gap:8px; flex-wrap:wrap; margin:-2px 0 18px}
blockquote{margin:16px 0; padding:14px 20px; border-left:3px solid var(--corrige);
  background:var(--corrige-bg); border-radius:0 5px 5px 0; color:var(--ink-2); font-size:15px}
blockquote p:last-child{margin-bottom:0}
.sugerida{border-left:3px solid var(--accent); background:var(--accent-soft);
  padding:16px 20px; border-radius:0 5px 5px 0; margin:16px 0;
  font-family:var(--serif); font-size:16px; line-height:1.55; color:var(--ink-2)}
.sugerida::before{content:"redação sugerida"; display:block; font-family:var(--mono);
  font-size:10px; letter-spacing:.1em; text-transform:uppercase; color:var(--ink-3);
  margin-bottom:8px; font-weight:600}
hr{border:0; border-top:1px solid var(--rule); margin:42px 0}
ul.lista li code, p code{white-space:nowrap}
.aviso{background:var(--panel); border:1px solid var(--rule); border-radius:6px;
  padding:22px 24px; margin:0 0 16px}
"""

def inline(t):
    t = html.escape(t)
    t = re.sub(r'`([^`]+)`', r'<code>\1</code>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', t)
    t = t.replace('&quot;', '"')
    return t

def render(md):
    out, i, linhas = [], 0, md.split("\n")
    while i < len(linhas):
        l = linhas[i]
        if l.startswith("## "):
            out.append(f"<h2>{inline(l[3:])}</h2>"); i += 1
        elif l.startswith("# "):
            i += 1                                   # o <title> cuida disso
        elif l.startswith("---"):
            out.append("<hr>"); i += 1
        elif l.startswith("|"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith("|"):
                bloco.append(linhas[i]); i += 1
            cels = lambda r: [c.strip() for c in r.strip().strip("|").split("|")]
            cab, corpo = cels(bloco[0]), bloco[2:]
            t = ['<div class="tabela"><table><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in cab]
            t.append("</tr></thead><tbody>")
            for r in corpo:
                t.append("<tr>" + "".join(
                    f'<td>{inline(c)}</td>' for c in cels(r)) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
        elif l.startswith(">"):
            bloco = []
            while i < len(linhas) and linhas[i].startswith(">"):
                bloco.append(linhas[i].lstrip("> ").rstrip()); i += 1
            out.append(f"<blockquote><p>{inline(' '.join(bloco))}</p></blockquote>")
        elif l.startswith("- "):
            bloco = []
            while i < len(linhas) and (linhas[i].startswith("- ") or
                                       (linhas[i].startswith("  ") and linhas[i].strip())):
                if linhas[i].startswith("- "): bloco.append(linhas[i][2:])
                else: bloco[-1] += " " + linhas[i].strip()
                i += 1
            out.append("<ul class='lista'>" + "".join(
                f"<li>{inline(x)}</li>" for x in bloco) + "</ul>")
        elif l.strip() == "":
            i += 1
        else:
            bloco = []
            while i < len(linhas) and linhas[i].strip() and not linhas[i][0] in "#|->" \
                    and not linhas[i].startswith("---"):
                bloco.append(linhas[i]); i += 1
            txt = " ".join(bloco)
            # "Redação sugerida:" vira o bloco destacado
            m = re.match(r'\*\*Redação sugerida[^:]*:\*\*\s*(.*)', txt, re.S)
            if m:
                out.append(f'<div class="sugerida">{inline(m.group(1))}</div>')
            else:
                out.append(f"<p>{inline(txt)}</p>")
    return "\n".join(out)

md = (RAIZ / "CORRECOES_TEXTO.md").read_text(encoding="utf-8")
corpo = render(md)

HTML = f"""<title>Correções do main.tex</title>
<style>{CSS}{EXTRA}</style>
<header class="top"><div class="wrap">
  <p class="eyebrow">Companheiro da auditoria estatística · PIBIC 25-26</p>
  <h1>Dez trechos do relatório a corrigir, com a redação pronta</h1>
  <p class="lede">Cada item traz o que o texto diz hoje, o que os dados dizem e uma
  redação sugerida, com o número de linha do <code>main.tex</code>. Ordem: do mais grave
  para o menos.</p>
  <div class="meta">
    <span><b>3</b> contradizem o texto</span>
    <span><b>4</b> corrigem números</span>
    <span><b>3</b> confirmam e acrescentam</span>
  </div>
</div></header>
<div class="wrap">
{corpo}
<footer><div class="prose">
<p>Números, tabelas e figuras que sustentam cada item estão no
<span class="mono">RESUMO.md</span>; o que não foi computável, e por quê, em
<span class="mono">LIMITACOES.md</span>. Ambos, mais as 33 tabelas e as figuras em vetor,
já estão em <span class="mono">analise_estatistica/</span> dentro do repositório do
relatório.</p>
</div></footer>
</div>
"""
(RAIZ / "correcoes.html").write_text(HTML, encoding="utf-8")
print(f"correcoes.html: {len(HTML)//1024} KB")
