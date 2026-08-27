"""A7 — Custo de memória dos pivôs (E8) e fronteira de Pareto.

O relatório caracteriza o custo como O(|P|·|S|) mas nunca o mede (main.tex:703).
Detalhe que muda o número: bfsPivo (heuristics.cpp) devolve
`vector<vector<int>> dists(height, vector<int>(width, -1))` — a grade INTEIRA,
não só as células transitáveis. O consumo real é |P|·altura·largura·4 B.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *

cel = celulas_transitaveis().set_index("mapa")
piv = carregar_pivos()

print("=== Memória das tabelas de distância, por mapa (MB) ===")
lin = []
for m, row in cel.iterrows():
    d = dict(mapa=m, S=row.S, grade=row.altura * row.largura,
             densidade=row.S / (row.altura * row.largura))
    for n in (10, 20, 50, 100):
        d[f"teorico_{n}"] = n * row.S * 4 / 2**20              # |P|·|S|·4 B
        d[f"real_{n}"] = n * row.altura * row.largura * 4 / 2**20  # o que o código aloca
    lin.append(d)
mem = pd.DataFrame(lin).set_index("mapa")
print(mem[["S", "grade", "densidade", "teorico_100", "real_100"]].round(3).to_string())
print(f"\n  desperdício por armazenar células bloqueadas: "
      f"{(mem.real_100/mem.teorico_100).min():.1f}x a {(mem.real_100/mem.teorico_100).max():.1f}x "
      f"(mediana {(mem.real_100/mem.teorico_100).median():.1f}x)")
print(f"  total 100 pivôs, 17 mapas: teórico {mem.teorico_100.sum():.0f} MB, "
      f"real {mem.real_100.sum():.0f} MB")
print(f"  pior caso individual (100 pivôs): {mem.real_100.max():.0f} MB em {mem.real_100.idxmax()}")
mem.to_csv(TABELAS / "a7_memoria_por_mapa.csv")

print("\n=== Tempo de pré-computação dos pivôs (E9 — nunca instrumentado) ===")
tp = piv.groupby("n_pivos").tempo_precomp_ms.agg(["mean", "std", "min", "max"])
print(tp.round(2).to_string())
sint = carregar_sintese().drop_duplicates("mapa").set_index("mapa")
cmp = pd.DataFrame({
    "precomp_100piv_ms": piv[piv.n_pivos == 100].groupby("mapa").tempo_precomp_ms.mean(),
    "sintese_ms": sint.tempo_sintese_ms})
cmp["sintese/precomp"] = cmp.sintese_ms / cmp.precomp_100piv_ms
print("\n  custo de preparação por mapa:")
print(cmp.round(1).sort_values("sintese/precomp").to_string())
print(f"\n  >>> a síntese custa de {cmp['sintese/precomp'].min():.0f}x a "
      f"{cmp['sintese/precomp'].max():.0f}x o pré-processamento de 100 pivôs")
cmp.to_csv(TABELAS / "a7_custo_preparacao.csv")

print("\n=== Fronteira de Pareto entre as 6 configurações ===")
# eixos: expansões normalizadas (menor melhor), memória MB (menor), subotimalidade
# (menor), robustez δ (menor). Valores médios entre os 17 mapas.
est = pd.read_csv(TABELAS / "a2_escore_estatico.csv", index_col=0)
deg = pd.read_csv(TABELAS / "a2_escore_degradado.csv", index_col=0)
rat = pd.read_csv(TABELAS / "a6_por_mapa.csv", index_col=0)
crit = []
for c in CONFIGS:
    lab = ROTULOS[c]
    n = int(c.replace("memory", "")) if c.startswith("memory") else 0
    crit.append(dict(config=lab,
                     expansoes=est[lab].mean(),
                     memoria_MB=mem[f"real_{n}"].mean() if n else 0.0,
                     subotimalidade=rat.media.mean() - 1 if c == "formula" else 0.0,
                     robustez=deg[lab].mean(),
                     preparacao_ms=(piv[piv.n_pivos == n].tempo_precomp_ms.mean() if n
                                    else (sint.tempo_sintese_ms.mean() if c == "formula" else 0.0))))
P = pd.DataFrame(crit).set_index("config")
EIXOS = ["expansoes", "memoria_MB", "subotimalidade", "robustez", "preparacao_ms"]

def dominadas(P, eixos):
    dom = {}
    for a in P.index:
        quem = [b for b in P.index if b != a
                and (P.loc[b, eixos] <= P.loc[a, eixos]).all()
                and (P.loc[b, eixos] < P.loc[a, eixos]).any()]
        dom[a] = quem
    return dom

for nome, eixos in [("4 eixos (sem custo de preparação)", EIXOS[:4]), ("5 eixos", EIXOS)]:
    print(f"\n--- {nome} ---")
    print(P[eixos].round(4).to_string())
    d = dominadas(P, eixos)
    for a, quem in d.items():
        print(f"  {a:<12}: {'NÃO-DOMINADA' if not quem else 'dominada por ' + ', '.join(quem)}")
P.to_csv(TABELAS / "a7_pareto.csv")
