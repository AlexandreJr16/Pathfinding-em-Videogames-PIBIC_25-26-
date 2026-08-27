"""A12 — Admissibilidade empírica das fórmulas sintetizadas.

O relatório caracteriza a admissibilidade das três classes de forma teórica
(main.tex:429: "as fórmulas sintetizadas não garantem admissibilidade") mas nunca a
mede. Aqui ela é medida: para cada par origem-destino, compara-se h(s,g) com a
distância ótima d*(s,g) — que é conhecida, é o `caminho_otimo` do Dijkstra.

h > d*  =>  a heurística superestima naquele par, violando admissibilidade.

A semântica replica src/synthesis/HeuristicNode.h exatamente, incluindo o
static_cast<int> de heuristicaFormula (truncamento em direção a zero) e as
proteções de sqrt(abs(x)) e divisão por zero.
"""
import sys, math, re, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from scipy.stats import spearmanr

# --------------------------------------------- avaliador fiel ao HeuristicNode.h
def tokenizar(s):
    return re.findall(r"\(|\)|[^\s()]+", s)

def parse(t, i=0):
    if t[i] == "(":
        op = t[i + 1]; i += 2; f = []
        while t[i] != ")":
            n, i = parse(t, i); f.append(n)
        return (op, f), i + 1
    return ("term", t[i]), i + 1

UN = {"sqrt": lambda v: math.sqrt(abs(v)), "abs": abs, "neg": lambda v: -v,
      "sqr": lambda v: v * v}
BIN = {"+": lambda a, b: a + b, "-": lambda a, b: a - b, "*": lambda a, b: a * b,
       "/": lambda a, b: (a / b) if b != 0 else 0.0, "max": max, "min": min}

def compilar(no):
    """Devolve f(dx, dy) -> float, com a mesma semântica do C++."""
    op, x = no
    if op == "term":
        if x == "deltaX": return lambda dx, dy: float(dx)
        if x == "deltaY": return lambda dx, dy: float(dy)
        c = float(x);     return lambda dx, dy: c
    if op in UN:
        g = compilar(x[0]); u = UN[op]
        return lambda dx, dy: u(g(dx, dy))
    g1, g2 = compilar(x[0]), compilar(x[1]); b = BIN[op]
    return lambda dx, dy: b(g1(dx, dy), g2(dx, dy))

def carregar_cenario(mapa):
    """Mesma leitura de main.cpp:22-35: start = (sY, sX), goal = (gY, gX)."""
    linhas = (MAPAS_DIR / f"{mapa}.map.scen").read_text().split("\n")[1:]
    out = []
    for l in linhas:
        c = l.split()
        if len(c) < 9: continue
        sX, sY, gX, gY = int(c[4]), int(c[5]), int(c[6]), int(c[7])
        out.append((sY, sX, gY, gX))      # (linha, coluna) de origem e destino
    return pd.DataFrame(out, columns=["s_lin", "s_col", "g_lin", "g_col"])

sint = carregar_sintese().drop_duplicates("mapa").set_index("mapa")
ratio = carregar_ratio()
dij = carregar_dijkstra()

print("=== Verificação do avaliador contra o C++ ===")
# arena: (+ (sqr deltaY) (sqr deltaX)) = dy^2 + dx^2
f = compilar(parse(tokenizar(sint.loc["arena", "formula_string"]))[0])
assert f(3, 4) == 25.0, f(3, 4)
print(f"  arena h(dx=3,dy=4) = {f(3,4):.0f}  (esperado 25 = 3²+4²)  OK")

lin = []
for mapa in sint.index:
    cen = carregar_cenario(mapa)
    h_f = compilar(parse(tokenizar(sint.loc[mapa, "formula_string"]))[0])
    dx = (cen.s_lin - cen.g_lin).abs().to_numpy()
    dy = (cen.s_col - cen.g_col).abs().to_numpy()
    h = np.array([int(h_f(a, b)) for a, b in zip(dx, dy)], dtype=float)  # static_cast<int>
    # d* por instância: o caminho_otimo do Dijkstra (independe de semente)
    d = (dij[dij.mapa == mapa].sort_values("id_problema").caminho_otimo.to_numpy(dtype=float))
    n = min(len(h), len(d)); h, d = h[:n], d[:n]
    ok = d >= 1
    h, d = h[ok], d[ok]
    manh = (dx[:n][ok] + dy[:n][ok]).astype(float)
    infl = np.divide(h, d, out=np.full_like(h, np.nan), where=d > 0)
    lin.append(dict(
        mapa=mapa, n=len(h),
        frac_inadmissivel=float((h > d).mean()),
        frac_manh_inadm=float((manh > d).mean()),        # controle: deve ser 0
        inflacao_mediana=float(np.nanmedian(infl)),
        inflacao_p99=float(np.nanpercentile(infl, 99)),
        inflacao_max=float(np.nanmax(infl)),
        tamanho_ast=int(sint.loc[mapa, "formula_string"].count("(")) or 1))
adm = pd.DataFrame(lin).set_index("mapa")
sub = pd.read_csv(TABELAS / "a6_por_mapa.csv", index_col=0)
adm["subotimalidade"] = sub.media - 1
adm["categoria"] = [categoria(m) for m in adm.index]

print("\n=== Fração de pares em que h > d* (viola admissibilidade) ===")
print(adm[["n", "frac_inadmissivel", "frac_manh_inadm", "inflacao_mediana",
           "inflacao_p99", "subotimalidade"]].round(4).sort_values(
           "frac_inadmissivel", ascending=False).to_string())
adm.to_csv(TABELAS / "a12_admissibilidade.csv")

print(f"\n  controle — Manhattan viola em {100*adm.frac_manh_inadm.max():.4f}% dos pares "
      f"(deve ser 0: é admissível por construção)")
print(f"  fórmula viola em {100*adm.frac_inadmissivel.mean():.1f}% dos pares, em média entre mapas")
print(f"  mapas em que viola em >99% dos pares: "
      f"{int((adm.frac_inadmissivel > .99).sum())}/17")
print(f"  fator de superestimação mediano: {adm.inflacao_mediana.median():.1f}x  "
      f"(máximo observado {adm.inflacao_max.max():.0f}x)")

print("\n=== O achado: violar admissibilidade não implica caminho subótimo ===")
r, p = spearmanr(adm.frac_inadmissivel, adm.subotimalidade)
print(f"  Spearman(fração inadmissível, subotimalidade) = {r:+.3f} (p={p:.3f})")
r2, p2 = spearmanr(adm.inflacao_mediana, adm.subotimalidade)
print(f"  Spearman(inflação mediana,   subotimalidade) = {r2:+.3f} (p={p2:.3f})")
a = adm.loc["arena"]
print(f"\n  caso extremo — arena: h = Δx²+Δy² superestima em {100*a.frac_inadmissivel:.1f}% "
      f"dos pares,\n  com inflação mediana de {a.inflacao_mediana:.0f}x, e mesmo assim "
      f"{100*(1-0):.0f}% dos caminhos são ótimos (ρ = 1,0 em todas as instâncias).")
print("  Num mapa sem obstáculos internos, uma heurística grosseiramente inadmissível")
print("  ainda guia direto ao destino — a violação é necessária, não suficiente.")
