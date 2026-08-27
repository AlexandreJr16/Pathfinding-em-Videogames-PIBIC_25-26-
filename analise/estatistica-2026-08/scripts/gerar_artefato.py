"""Gera analise/auditoria.html — a entrega compartilhável, com as figuras embutidas."""
import base64, sys
from pathlib import Path
RAIZ = Path(__file__).resolve().parent.parent

def b64(p):
    return "data:image/png;base64," + base64.b64encode((RAIZ / p).read_bytes()).decode()

FIG1, FIG2 = b64("figuras/fig1_diagrama_cd.png"), b64("figuras/fig2_ecdf.png")

CSS = """
:root{
  --ground:#F7F8FA; --panel:#FFFFFF; --ink:#191C22; --ink-2:#4A5160; --ink-3:#767E8E;
  --rule:#DDE1E8; --rule-2:#EDF0F4;
  --accent:#1E3A6E; --accent-soft:#E8EDF6;
  --confirma:#1F6B4E; --confirma-bg:#E7F2EC;
  --corrige:#8A5507; --corrige-bg:#FAF0DF;
  --contradiz:#98282B; --contradiz-bg:#FAEAEA;
  --serif:Georgia,"Iowan Old Style","Liberation Serif","DejaVu Serif",serif;
  --sans:system-ui,-apple-system,"Segoe UI",Cantarell,"Helvetica Neue",sans-serif;
  --mono:ui-monospace,"JetBrains Mono","DejaVu Sans Mono",SFMono-Regular,Menlo,monospace;
}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){
  --ground:#101318; --panel:#171B22; --ink:#E7E9EE; --ink-2:#AEB6C4; --ink-3:#7E8798;
  --rule:#2A303B; --rule-2:#1E242D;
  --accent:#8FB2E8; --accent-soft:#1A2333;
  --confirma:#6FC79C; --confirma-bg:#14251E;
  --corrige:#D9A441; --corrige-bg:#2A2113;
  --contradiz:#E28A8C; --contradiz-bg:#2B1719;
}}
:root[data-theme="dark"]{
  --ground:#101318; --panel:#171B22; --ink:#E7E9EE; --ink-2:#AEB6C4; --ink-3:#7E8798;
  --rule:#2A303B; --rule-2:#1E242D;
  --accent:#8FB2E8; --accent-soft:#1A2333;
  --confirma:#6FC79C; --confirma-bg:#14251E;
  --corrige:#D9A441; --corrige-bg:#2A2113;
  --contradiz:#E28A8C; --contradiz-bg:#2B1719;
}
*{box-sizing:border-box}
body{
  margin:0; background:var(--ground); color:var(--ink);
  font-family:var(--sans); font-size:16px; line-height:1.6;
  -webkit-font-smoothing:antialiased;
}
.wrap{max-width:960px; margin:0 auto; padding:0 24px 96px}
.prose{max-width:68ch}

/* cabeçalho: a textura é a grade 4-conectada dos mapas do Moving AI */
header.top{
  border-bottom:1px solid var(--rule); margin-bottom:44px;
  background-image:
    linear-gradient(to right,var(--rule-2) 1px,transparent 1px),
    linear-gradient(to bottom,var(--rule-2) 1px,transparent 1px);
  background-size:22px 22px; background-position:center bottom;
}
header.top .wrap{padding-top:56px; padding-bottom:40px}
.eyebrow{
  font-family:var(--mono); font-size:11px; letter-spacing:.14em;
  text-transform:uppercase; color:var(--ink-3); margin:0 0 14px;
}
h1{
  font-family:var(--serif); font-weight:600; font-size:clamp(30px,5.2vw,46px);
  line-height:1.12; letter-spacing:-.015em; margin:0 0 16px; text-wrap:balance;
}
.lede{font-size:18px; line-height:1.55; color:var(--ink-2); margin:0; max-width:60ch}
.meta{
  display:flex; flex-wrap:wrap; gap:8px 26px; margin-top:28px;
  font-family:var(--mono); font-size:12px; color:var(--ink-3);
}
.meta b{color:var(--ink-2); font-weight:500}

h2{
  font-family:var(--serif); font-weight:600; font-size:26px; line-height:1.2;
  letter-spacing:-.01em; margin:64px 0 6px; text-wrap:balance;
}
h2 + .sub{color:var(--ink-3); font-size:14px; margin:0 0 26px; max-width:64ch}
h3{font-family:var(--serif); font-weight:600; font-size:19px; margin:0 0 10px; line-height:1.3}
p{margin:0 0 14px}
a{color:var(--accent)}
code,.mono{font-family:var(--mono); font-size:.88em}
code{background:var(--rule-2); padding:.12em .38em; border-radius:3px; color:var(--ink-2)}
strong{font-weight:640; color:var(--ink)}

/* o par reportado -> corrigido: o elemento estrutural que a auditoria produz */
.swap{display:inline-flex; align-items:baseline; gap:9px; font-variant-numeric:tabular-nums; white-space:nowrap}
.swap .was{color:var(--ink-3); text-decoration:line-through; text-decoration-thickness:1px; font-family:var(--mono); font-size:.92em}
.swap .arrow{color:var(--ink-3); font-size:.8em}
.swap .now{font-family:var(--mono); font-weight:640; color:var(--ink)}

.chip{
  display:inline-block; font-family:var(--mono); font-size:10.5px; font-weight:600;
  letter-spacing:.08em; text-transform:uppercase; padding:3px 8px; border-radius:3px;
  white-space:nowrap; vertical-align:2px;
}
.c-confirma{background:var(--confirma-bg); color:var(--confirma)}
.c-corrige{background:var(--corrige-bg); color:var(--corrige)}
.c-contradiz{background:var(--contradiz-bg); color:var(--contradiz)}
.c-neutro{background:var(--rule-2); color:var(--ink-3)}

.callout{
  border-left:3px solid var(--accent); background:var(--accent-soft);
  padding:18px 22px; border-radius:0 5px 5px 0; margin:0 0 12px;
}
.callout p:last-child{margin-bottom:0}

.tabela{overflow-x:auto; margin:22px 0; border:1px solid var(--rule); border-radius:6px; background:var(--panel)}
table{border-collapse:collapse; width:100%; font-size:14px}
th,td{padding:10px 14px; text-align:left; border-bottom:1px solid var(--rule-2)}
thead th{
  font-family:var(--mono); font-size:10.5px; letter-spacing:.09em; text-transform:uppercase;
  color:var(--ink-3); font-weight:600; border-bottom:1px solid var(--rule); white-space:nowrap;
}
tbody tr:last-child td{border-bottom:0}
td.num,th.num{text-align:right; font-family:var(--mono); font-variant-numeric:tabular-nums; white-space:nowrap}
td.id{font-family:var(--mono); font-weight:640; color:var(--accent); white-space:nowrap}
tr.total td{border-top:1px solid var(--rule); color:var(--ink-3); font-style:italic}

/* os três achados que mudam o texto: faixa de severidade + painel */
.caso{
  background:var(--panel); border:1px solid var(--rule); border-left:4px solid var(--sev);
  border-radius:0 6px 6px 0; padding:24px 26px; margin:0 0 18px;
}
.caso.contradiz{--sev:var(--contradiz)}
.caso.corrige{--sev:var(--corrige)}
.caso-head{display:flex; flex-wrap:wrap; align-items:baseline; gap:12px; margin-bottom:12px}
.caso-id{font-family:var(--mono); font-size:13px; font-weight:700; color:var(--sev)}
.caso h3{margin:0; flex:1 1 320px}
.frase{
  font-family:var(--serif); font-size:16.5px; line-height:1.55; color:var(--ink-2);
  border-top:1px solid var(--rule-2); margin-top:16px; padding-top:16px;
}
.frase::before{
  content:"frase para o relatório"; display:block; font-family:var(--mono);
  font-size:10px; letter-spacing:.1em; text-transform:uppercase;
  color:var(--ink-3); margin-bottom:7px;
}

.grid2{display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px}
.card{background:var(--panel); border:1px solid var(--rule); border-radius:6px; padding:20px 22px}
.card h3{font-size:17px; display:flex; gap:10px; align-items:baseline; flex-wrap:wrap}
.card .kid{font-family:var(--mono); font-size:12px; color:var(--accent); font-weight:700}
.card p{font-size:14.5px; margin-bottom:10px; color:var(--ink-2)}
.card p:last-child{margin-bottom:0}
.card strong{color:var(--ink)}

figure{margin:0 0 8px; background:var(--panel); border:1px solid var(--rule); border-radius:6px; padding:20px}
figure img{display:block; width:100%; max-width:100%; height:auto}
figcaption{font-size:13.5px; color:var(--ink-2); margin-top:14px; padding-top:13px; border-top:1px solid var(--rule-2)}
figcaption b{font-family:var(--mono); font-size:11px; letter-spacing:.08em; text-transform:uppercase; color:var(--ink-3); display:block; margin-bottom:5px; font-weight:600}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]) figure img{filter:invert(1) hue-rotate(180deg)}}
:root[data-theme="dark"] figure img{filter:invert(1) hue-rotate(180deg)}

ul.lista{margin:0 0 14px; padding-left:20px}
ul.lista li{margin-bottom:7px; color:var(--ink-2)}
ul.lista li strong{color:var(--ink)}
footer{margin-top:72px; padding-top:24px; border-top:1px solid var(--rule); color:var(--ink-3); font-size:13.5px}
"""

def caso(cid, sev, titulo, corpo, frase):
    return f"""<div class="caso {sev}">
  <div class="caso-head"><span class="caso-id">{cid}</span><h3>{titulo}</h3>
  <span class="chip c-{sev}">{sev}</span></div>
  {corpo}
  <div class="frase">{frase}</div>
</div>"""

HTML = f"""<title>Auditoria PIBIC 25-26</title>
<style>{CSS}</style>
<header class="top"><div class="wrap">
  <p class="eyebrow">Revisão estatística · relatório final PIBIC/PAIC</p>
  <h1>Doze análises, três números que o relatório não pode mais afirmar</h1>
  <p class="lede">Auditoria dos dados do estudo de heurísticas sintetizadas para A* em 17 mapas
  do <i>Dragon Age Origins</i>. Cada resultado é confrontado com o que o texto afirma hoje:
  confirma, corrige ou contradiz.</p>
  <div class="meta">
    <span><b>116.050</b> instâncias pareadas</span>
    <span><b>17</b> mapas · <b>5</b> sementes</span>
    <span><b>6</b> configurações</span>
    <span>semente <b>20260820</b></span>
  </div>
</div></header>

<div class="wrap">

<div class="callout prose">
  <p><strong>A regra que muda quase todos os números.</strong> Razões agregam por média
  <strong>geométrica</strong>; expansões normalizam por mapa antes de agrupar; e a unidade de
  replicação para generalizar é o <strong>mapa (n&nbsp;=&nbsp;17)</strong>, não a instância
  (n&nbsp;=&nbsp;116.050) — instâncias do mesmo mapa não são independentes.</p>
  <p>Uma checagem que só a média geométrica passa, e que serve de defesa em arguição:
  2,799 (Manhattan÷Fórmula) × 2,811 (Fórmula÷Memória-100) = <strong>7,866</strong>, exatamente
  a razão Manhattan÷Memória-100 medida em separado. Médias aritméticas de razões não fecham assim.</p>
</div>

<h2>Placar</h2>
<p class="sub">Doze análises. As três primeiras mudam o que o texto pode afirmar; as demais
sustentam afirmações que hoje estão sem prova.</p>
<div class="tabela"><table>
<thead><tr><th>#</th><th>Achado</th><th>Veredito</th><th>No relatório</th></tr></thead>
<tbody>
<tr><td class="id">A0</td><td>A memória <b>é</b> reprocessada sob degradação: 93,4% das distâncias mudam</td><td><span class="chip c-contradiz">contradiz</span></td><td>§4.3 e §5.4</td></tr>
<tr><td class="id">A3</td><td>O 51,98× compara memória de uma população com Manhattan de outra</td><td><span class="chip c-corrige">corrige</span></td><td>Tabela 4</td></tr>
<tr><td class="id">A11</td><td>O desvio de 138,44 é colapso de pivô em bolsão desconexo</td><td><span class="chip c-contradiz">contradiz</span></td><td>§5.1 + nota</td></tr>
<tr><td class="id">A1</td><td>Interação estratégia × padrão: η²ₚ = 0,241, p ≤ 0,005</td><td><span class="chip c-confirma">confirma</span></td><td>1 frase</td></tr>
<tr><td class="id">A2</td><td>Inversão de hierarquia entre estático e degradado</td><td><span class="chip c-confirma">confirma</span></td><td><b>Figura 1</b></td></tr>
<tr><td class="id">A4</td><td>Memória-50 tem a 2ª melhor mediana e p99 no teto do Dijkstra</td><td><span class="chip c-neutro">revela</span></td><td><b>Figura 2</b></td></tr>
<tr><td class="id">A5</td><td>Quatro pares, correção de Holm, δ de Cliff de 0,33 a 0,87</td><td><span class="chip c-neutro">resolve E3–E5</span></td><td>meia frase</td></tr>
<tr><td class="id">A6</td><td>Só <b>18,5%</b> dos caminhos são ótimos; 44,9% excedem 1,10</td><td><span class="chip c-confirma">confirma</span></td><td>1 frase</td></tr>
<tr><td class="id">A7</td><td>109 MB num só mapa; a síntese custa 777×–12.197× os pivôs</td><td><span class="chip c-corrige">corrige</span></td><td>tabela</td></tr>
<tr><td class="id">A8</td><td>A regularização é inerte: λ‖T‖ ≤ 1,6% da aptidão</td><td><span class="chip c-contradiz">contradiz</span></td><td>§3.4</td></tr>
<tr><td class="id">A12</td><td>A fórmula viola admissibilidade em <b>99,9%</b> dos pares — e isso não prevê subotimalidade</td><td><span class="chip c-contradiz">contradiz</span></td><td>sim, 1 frase</td></tr>
<tr><td class="id">A9</td><td>A síntese não é reprodutível; a duplicata de <code>arena</code> não prova estabilidade</td><td><span class="chip c-corrige">corrige</span></td><td>limitação</td></tr>
<tr><td class="id">A10</td><td>89% a 99% dos pares são descartados, sem contabilização</td><td><span class="chip c-neutro">resolve E7</span></td><td>limitação</td></tr>
</tbody></table></div>

<h2>Os três que mudam o texto</h2>
<p class="sub">Nenhum deles derruba a tese do trabalho. Dois deles a reforçam.</p>

{caso("A0", "contradiz", "O relatório diz que a memória não é reprocessada; o código a reprocessa por inteiro", """
<p><code>main.cpp:227</code> troca o grid pelo degradado e <code>main.cpp:244</code> chama
<code>computarDistPivosFixos</code>, que roda <code>bfsPivo</code> sobre o grid já degradado.
Medido nos 17 mapas: <strong>93,4% das distâncias pré-computadas mudam</strong> (mediana;
intervalo interquartil 81,9%–98,0%, e em <strong>97% das medições</strong> a mudança passa de
metade das células), e <strong>87,5% das células ficam inalcançáveis a partir do pivô</strong>.
Só as <i>posições</i> dos pivôs ficam congeladas — em 100% das medições. As 6 medições em que
nada muda são todas de <code>brc201d</code>, onde os pivôs colapsados do A11 ficaram num bolsão
que a degradação nunca alcançou — corroboração independente daquele mecanismo.</p>
<p>A causa real da degradação está medida e é outra: pivôs inalcançáveis são <strong>pulados</strong>
por <code>heuristicaMemoryBased</code>, e a estimativa colapsa para zero. O efeito troca de sinal —
sob padrão <b>linear</b> recalcular a BFS <strong>piora</strong> δ em 2,3–2,8× (os pivôs ficam do
lado errado da barreira); sob <b>estocástico</b>, melhora em 2,3–2,7×.</p>
<p><strong>Reforça a tese:</strong> a fórmula é a menos degradada em <strong>5 de 5</strong> padrões
sendo a única que não recebe reprocessamento algum.</p>""",
"""&ldquo;As posições dos pivôs permanecem fixas sob degradação, mas as distâncias a partir deles são
recalculadas sobre o mapa modificado; a comparação de robustez concede à heurística de memória uma
atualização completa de suas tabelas, e seus fatores de degradação devem ser lidos como um limite
superior.&rdquo;""")}

{caso("A3", "corrige", "O speedup de 51,98× compara duas populações de instâncias", """
<p>O script de análise monta as linhas de memória da Tabela 4 a partir de
<code>resultados_robustez.csv</code>, enquanto Manhattan e Fórmula vêm de
<code>resultados_base.csv</code>. A robustez só contém as <strong>23.906 instâncias (20,5%)</strong>
que sobreviveram ao filtro de conectividade em 30% — os pares mais curtos. Sobre esses mesmos pares,
<strong>o próprio Manhattan expande 2.148,79 nós, não 7.472,95</strong>. As 12 células da tabela
reproduzem exatamente sob essa regra, o que fecha o diagnóstico.</p>
<div class="tabela"><table>
<thead><tr><th>Configuração</th><th class="num">Relatório</th><th class="num">Corrigido</th><th class="num">IC 95% (17 mapas)</th></tr></thead>
<tbody>
<tr><td>Fórmula</td><td class="num">3,10×</td><td class="num"><b>2,80×</b></td><td class="num">[2,32; 3,30]</td></tr>
<tr><td>Memória-10</td><td class="num">17,25×</td><td class="num"><b>4,70×</b></td><td class="num">[3,30; 5,43]</td></tr>
<tr><td>Memória-20</td><td class="num">30,78×</td><td class="num"><b>5,94×</b></td><td class="num">[3,94; 6,95]</td></tr>
<tr><td>Memória-50</td><td class="num">33,50×</td><td class="num"><b>7,32×</b></td><td class="num">[4,64; 8,69]</td></tr>
<tr><td>Memória-100</td><td class="num">51,98×</td><td class="num"><b>7,87×</b></td><td class="num">[4,92; 9,39]</td></tr>
</tbody></table></div>
<p>O fator está inflado <strong>6,6×</strong> para 100 pivôs. <strong>E elimina uma anomalia:</strong>
a hierarquia passa a ser monotônica (<span class="mono">4,70 &lt; 5,94 &lt; 7,32 &lt; 7,87</span>),
então o parágrafo sobre o &ldquo;comportamento não monotônico&rdquo; dos 50 pivôs sai inteiro.</p>""",
"""&ldquo;As heurísticas de memória reduzem as expansões em 7,87× em relação a Manhattan com 100
pivôs (IC 95% [4,92; 9,39] sobre os 17 mapas), contra 2,80× [2,32; 3,30] da heurística de
fórmula.&rdquo;""")}

{caso("A11", "contradiz", "O desvio de 138,44 tem causa geométrica exata e previsível", """
<p><code>generatePivots</code> sorteia o <strong>primeiro</strong> pivô uniformemente entre as
células transitáveis. Se ele cai num bolsão desconexo, todos os pivôs ficam presos lá,
<code>dS == dG == -1</code> em quase toda consulta, <strong>h ≡ 0 e o A* degenera em Dijkstra</strong>.</p>
<div class="tabela"><table>
<thead><tr><th>Mapa</th><th class="num">Componentes</th><th class="num">Fora da maior</th><th class="num">Colapsos</th><th class="num">Esperado</th></tr></thead>
<tbody>
<tr><td class="mono">brc201d</td><td class="num">167</td><td class="num">17,9%</td><td class="num"><b>5 de 20</b></td><td class="num">3,6</td></tr>
<tr><td class="mono">brc000d</td><td class="num">2</td><td class="num">5,4%</td><td class="num"><b>2 de 20</b></td><td class="num">1,1</td></tr>
<tr class="total"><td>outros 15</td><td class="num">1</td><td class="num">0%</td><td class="num">0</td><td class="num">0</td></tr>
</tbody></table></div>
<p><strong>7 colapsos previstos, 7 observados, as mesmas 7 células</strong> — todas com o primeiro
pivô fora da maior componente e h ≡ 0 em 99,3%–100% das consultas. Teste binomial contra a taxa
prevista: p = 0,241. A nota da Tabela 4 exclui só <code>(brc000d, 50)</code> e mantém caladas
<code>(brc201d, 10)</code> nas sementes 123 e 456 e <code>(brc201d, 50)</code> nas sementes 42, 456 e
789, onde a memória fica <strong>pior que Manhattan</strong> (13.290 contra 7.163 expansões).</p>
<p>Correção de código: sortear o primeiro pivô na maior componente conexa. Uma linha.</p>""",
"""&ldquo;O desvio de 138,44 não reflete ruído amostral: <span class="mono">brc201d</span> tem 167
componentes conexas, com 17,9% das células fora da maior, e o sorteio uniforme do primeiro pivô cai
nesse conjunto com probabilidade proporcional — em 7 dos 340 sorteios, todos os pivôs ficaram
confinados a um bolsão e a heurística colapsou para h ≡ 0.&rdquo;""")}

<h2>As duas figuras do relatório</h2>
<p class="sub">Orçamento apertado: 20 páginas no total, e a estatística inferencial cabe em cerca de
meia página mais duas figuras. Estas são as duas.</p>

<figure>
  <img src="{FIG1}" alt="Dois diagramas de diferença crítica empilhados. No cenário estático,
  Memória-100 ocupa o primeiro posto (1,06) e Manhattan o último (5,94). Sob degradação, a ordem se
  inverte: Fórmula assume o primeiro posto (1,35) e Memória-10 vai para o último (5,88).">
  <figcaption><b>Figura 1 · diagrama de diferença crítica</b>
  Friedman sobre 17 mapas × 6 configurações. Estático χ²&nbsp;=&nbsp;70,98
  (p&nbsp;=&nbsp;6,4·10⁻¹⁴); degradado χ²&nbsp;=&nbsp;67,42 (p&nbsp;=&nbsp;3,5·10⁻¹³); distância
  crítica de Nemenyi&nbsp;=&nbsp;1,83. Memória-100 sai de 1,06 para 2,82 e a Fórmula, de 4,47 para
  1,35 — variação maior que a distância crítica nos dois sentidos. O δ de Cliff entre as duas
  troca de sinal: +0,917 no estático, −0,813 sob degradação, ambos de magnitude &ldquo;grande&rdquo;.</figcaption>
</figure>

<figure>
  <img src="{FIG2}" alt="Distribuição acumulada empírica das expansões normalizadas pelo teto do
  Dijkstra, em escala logarítmica. As curvas de Memória-10 e Memória-50 estacionam em torno de 0,93
  a 0,96 e só alcançam 1,0 no extremo direito, revelando uma cauda pesada que as demais não têm.">
  <figcaption><b>Figura 2 · função de distribuição acumulada</b>
  Expansões divididas pelo teto do Dijkstra (h&nbsp;=&nbsp;0, medido agora). Memória-50 tem a segunda
  melhor mediana de todas (0,025) e ainda assim percentil 99 no teto — 39 vezes a própria mediana.
  Essa cauda vem <b>inteiramente</b> do colapso de pivôs do A11: sem as células afetadas, o p99 cai
  de 1,000 para 0,167.</figcaption>
</figure>

<h2>As demais análises</h2>
<p class="sub">Sustentam afirmações que hoje estão no texto sem prova, ou revelam o que ele ainda não diz.</p>

<div class="grid2">

<div class="card"><h3><span class="kid">A1</span> A tese central, testada</h3>
<p>Interação estratégia × padrão: <strong>F(20; 7.544) = 119,48</strong>, η²ₚ&nbsp;=&nbsp;<strong>0,241</strong>.
Principais: estratégia 0,494; nível 0,309; padrão 0,264. Na permutação — com o rótulo de estratégia
embaralhado <i>dentro</i> da instância — o F observado é <strong>82× o máximo de 200 permutações
nulas</strong>. No estrato de dificuldade comum aos 5 padrões a interação <strong>sobrevive</strong>
(η²ₚ&nbsp;=&nbsp;0,123), o que mostra que não é artefato do viés de seleção.</p>
<p>Precisão importante: a interação <strong>não é troca de vencedor</strong> — a fórmula é a menos
degradada nos 5 padrões. É a reordenação das demais: Manhattan vai do posto 2 sob bloqueio linear ao
posto 4 sob estocástico.</p></div>

<div class="card"><h3><span class="kid">A10</span> Os descartes que ninguém contou</h3>
<p>O código seleciona os pares pela conectividade <b>no estado de 30%</b> e usa esse conjunto nos três
níveis — por isso o descarte não é separável por nível.</p>
<div class="tabela"><table>
<thead><tr><th>Padrão</th><th class="num">Sobrevivem</th><th class="num">Caminho mediano</th></tr></thead>
<tbody>
<tr><td>Linear</td><td class="num"><b>0,75%</b></td><td class="num">5</td></tr>
<tr><td>Sparse</td><td class="num">4,31%</td><td class="num">44</td></tr>
<tr><td>Organic</td><td class="num">4,69%</td><td class="num">37</td></tr>
<tr><td>Radial</td><td class="num">9,55%</td><td class="num">70</td></tr>
<tr><td>Stochastic</td><td class="num">10,73%</td><td class="num">111</td></tr>
<tr class="total"><td>todos os pares</td><td class="num">100%</td><td class="num">328</td></tr>
</tbody></table></div>
<p>Interseção dos 5 padrões: <strong>71 instâncias</strong>. A comparação entre <i>estratégias</i>
segue válida — é pareada na mesma linha do CSV. A comparação entre <i>padrões</i> fica comprometida.</p></div>

<div class="card"><h3><span class="kid">A6</span> A média de 12,19% esconde o resultado</h3>
<p>Confirmada (ρ médio 1,1226), e o máximo de 4,19 em <code>den012d</code> também. Mas só
<strong>18,5% dos caminhos são ótimos</strong>; 62,97% excedem 1,05 e <strong>44,94% excedem
1,10</strong>. A hipótese do contorno se confirma: a fração de caminhos ótimos cai de 97,2% em
trajetos de até 25 células para 1,1% acima de 400 (Spearman&nbsp;=&nbsp;<strong>+0,494</strong>).</p>
<p><strong>Inédito:</strong> no mapa degradado a subotimalidade sobe de 37,8% para
<strong>49,3%</strong> das instâncias.</p></div>

<div class="card"><h3><span class="kid">A7</span> Memória, preparação e Pareto</h3>
<p><code>bfsPivo</code> aloca a <strong>grade inteira</strong>, não só as células transitáveis:
<strong>4,1× o teórico</strong>, até 8,2× em mapas esparsos, chegando a <strong>109&nbsp;MB num único
mapa</strong>. A pré-computação dos pivôs, nunca instrumentada, custa
<span class="swap"><span class="now">12–103 ms</span></span> — contra 4&nbsp;s a 2.025&nbsp;s de
síntese, ou seja, <strong>777× a 12.197×</strong>.</p>
<p>As <strong>6 configurações são não-dominadas</strong> no espaço expansões × memória ×
subotimalidade × robustez: prova de dominância para o &ldquo;não há estratégia universalmente
superior&rdquo; da conclusão. Mas em geração procedural a estratégia inviável é a fórmula, não a
memória — o texto conclui o contrário.</p></div>

<div class="card"><h3><span class="kid">A8</span> A regularização não faz o que o texto diz</h3>
<p>ASTs com <strong>mediana de 39 nós</strong>, máximo <strong>78</strong>, profundidade até 26; 1 de
17 é simétrica em Δx/Δy. A penalidade λ‖T‖ vale no máximo <strong>1,56%</strong> da aptidão; para
chegar a 10%, λ teria de ser <strong>19× maior</strong>. E
<strong>Spearman(tamanho, aptidão) = +0,487</strong> (p&nbsp;=&nbsp;0,047): tamanho <i>aumenta</i> a
aptidão.</p>
<p>O comentário do próprio código diz o oposto do relatório:
<code>lambda = 0.0005; // Penalidade por tamanho baixíssima para permitir fórmulas complexas</code>.
De quebra, responde um trabalho futuro: a correlação entre complexidade da AST e subotimalidade
<strong>não existe</strong> (ρ&nbsp;=&nbsp;−0,014).</p></div>

<div class="card"><h3><span class="kid">A5</span> Tamanho de efeito ao lado de todo p</h3>
<p>Quatro pares pré-registrados, correção de Holm, nos dois níveis. Com 116.050 pares pareados todo p
fica abaixo do menor float representável — o que separa é a magnitude.</p>
<div class="tabela"><table>
<thead><tr><th>Par</th><th class="num">δ de Cliff</th><th class="num">Razão (17 mapas)</th></tr></thead>
<tbody>
<tr><td>Manh × Fórmula</td><td class="num">+0,550</td><td class="num">2,80×</td></tr>
<tr><td>Manh × Mem-100</td><td class="num">+0,868</td><td class="num">7,87×</td></tr>
<tr><td>Fórmula × Mem-10</td><td class="num">+0,333</td><td class="num">1,68×</td></tr>
<tr><td>Fórmula × Mem-100</td><td class="num">+0,665</td><td class="num">2,81×</td></tr>
</tbody></table></div></div>

<div class="card"><h3><span class="kid">A12</span> Admissibilidade, medida pela primeira vez</h3>
<p>O relatório caracteriza a admissibilidade das três classes de forma teórica, mas nunca a mede.
Comparando h(s,g) com a distância ótima d*(s,g) do Dijkstra em todos os pares: a fórmula viola
admissibilidade em <strong>mais de 99% dos pares nos 17 mapas</strong>, com superestimação
<strong>mediana de 270×</strong> e máximo de 6.711×. Controle: Manhattan viola em
<strong>0,0000%</strong>, como manda a construção.</p>
<p><strong>O achado:</strong> violar admissibilidade <strong>não prevê</strong> caminho subótimo
(ρ&nbsp;=&nbsp;−0,003; p&nbsp;=&nbsp;0,99). No <code>arena</code>, h superestima em 99,2% dos pares
— fator mediano de 19× — e ainda assim 100% dos caminhos saem ótimos: num mapa sem obstáculos
internos, a ordem de expansão de uma estimativa inflada mas monótona coincide com a do caminho
ótimo. O que determina a subotimalidade é a geometria, não a magnitude do erro.</p></div>

<div class="card"><h3><span class="kid">A9</span> A síntese não é reprodutível</h3>
<p><code>GeneticAlgorithm.cpp</code> semeia a população inicial e a seleção de pais com
<code>std::random_device</code>. A duplicata de <code>arena</code> — fórmula e aptidão idênticas,
expansões idênticas em 100% dos pares — <strong>não é evidência de estabilidade do AG</strong>.</p>
<p>Nas sínteses semeadas, <code>arena</code> reconverge (é o menor e mais fácil mapa), mas
<code>arena2</code> e <code>brc000d</code> produzem fórmulas <strong>diferentes</strong>: aptidão
4,724 contra 4,884 e 4,310 contra 4,333; ASTs de 65 contra 44 e 48 contra 45 nós.</p></div>

</div>

<h2>O que não deu para computar</h2>
<p class="sub">Registrado por inteiro em <span class="mono">LIMITACOES.md</span>. O essencial:</p>
<ul class="lista prose">
<li><strong>O descarte não é separável por nível.</strong> Os pares válidos são escolhidos uma única
vez, no estado de 30%; quantos sobreviveriam a 10% ou 20% nunca foi gravado.</li>
<li><strong>A comparação entre padrões não tem conserto pleno.</strong> Cada padrão sobrevive com uma
população diferente e não aninhada, e a interseção dos cinco tem 71 instâncias. O reajuste por
estrato de dificuldade sustenta a <i>existência</i> da interação, não a comparabilidade das
magnitudes.</li>
<li><strong><code>tempo_ms</code> não é medição confiável.</strong> Uma leitura por instância, sem
aquecimento nem isolamento de CPU. Re-executar não conserta sem um protocolo de benchmark — por isso
toda a análise lidera com expansões de nós, que são determinísticas.</li>
<li><strong>As fórmulas publicadas continuam sendo amostras de tamanho 1.</strong> As 85 sínteses
semeadas caracterizam a distribuição, mas não tornam reprodutíveis os números já reportados.</li>
</ul>

<footer><div class="prose">
<p>Entregáveis completos no repositório: <span class="mono">RESUMO.md</span>,
<span class="mono">LIMITACOES.md</span>, <span class="mono">CORRECOES_TEXTO.md</span> (redação
sugerida trecho a trecho), 33 tabelas agregadas, as figuras em vetor e os scripts que reproduzem
tudo do zero.</p>
<p>Critério aplicado em toda parte: <strong>se o aluno não sabe explicar o número numa arguição, ele
não entra no relatório</strong> — por mais bonito que seja.</p>
</div></footer>

</div>
"""

(RAIZ / "auditoria.html").write_text(HTML, encoding="utf-8")
print(f"auditoria.html: {len(HTML)//1024} KB")
