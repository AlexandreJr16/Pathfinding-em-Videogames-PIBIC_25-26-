"""A6 — Subotimalidade fina da heurística de fórmula.

A média de 12,19% esconde a distribuição. O que um desenvolvedor precisa saber é a
"taxa de desvio perceptível", não a média. Inclui um recorte que o briefing não
previa: a robustez também traz a subotimalidade da fórmula NO MAPA DEGRADADO
(path_deg_form contra path_deg_manh, que é ótimo por admissibilidade).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from scipy.stats import spearmanr

r = carregar_ratio()
print(f"linhas: {len(r)}")

# main.cpp:175 força ratio=1.0 quando o Dijkstra não acha caminho (path.size()<=1)
ruins = r[r.caminho_otimo < 1]
print(f"\npares com caminho_otimo < 1 (ratio forçado a 1,0 em main.cpp:175): {len(ruins)}")
print(f"  distribuição por mapa: {ruins.mapa.value_counts().to_dict()}")
r = r[r.caminho_otimo >= 1].copy()
print(f"  descartados da análise; restam {len(r)}")

print("\n=== Média agrupada vs escada por mapa (E2) ===")
por_mapa = r.groupby("mapa").ratio.mean()
print(f"  média aritmética agrupada        : {r.ratio.mean():.5f}  "
      f"(subotimalidade {100*(r.ratio.mean()-1):.2f}%)   <- valor do relatório")
print(f"  média das médias por mapa        : {por_mapa.mean():.5f}  "
      f"(subotimalidade {100*(por_mapa.mean()-1):.2f}%)")
lo, hi = bootstrap_bca_geom(por_mapa.values)
print(f"  IC 95% BCa sobre os 17 mapas     : [{100*(lo-1):.2f}%, {100*(hi-1):.2f}%]")

print("\n=== Taxa de desvio perceptível (o número acionável) ===")
lim = [1.0, 1.01, 1.05, 1.10, 1.25, 1.50, 2.0]
glob = {"ótimo (ρ=1)": (r.ratio <= 1.0000001).mean()}
for L in lim[1:]:
    glob[f"ρ > {L:.2f}"] = (r.ratio > L).mean()
for k, v in glob.items():
    print(f"  {k:<14}: {100*v:6.2f}% das instâncias")
pd.Series(glob).to_csv(TABELAS / "a6_taxas_desvio.csv")

print("\n=== Por categoria de mapa ===")
r["categoria"] = r.mapa.map(categoria)
cat = r.groupby("categoria").ratio.agg(
    n="size", media="mean", mediana="median",
    p95=lambda s: s.quantile(.95), p99=lambda s: s.quantile(.99), max="max")
cat["frac_otimo"] = r.groupby("categoria").ratio.apply(lambda s: (s <= 1.0000001).mean())
cat["frac_acima_1_1"] = r.groupby("categoria").ratio.apply(lambda s: (s > 1.1).mean())
print(cat.round(4).to_string())
cat.to_csv(TABELAS / "a6_por_categoria.csv")

print("\n=== Por mapa ===")
pm = r.groupby("mapa").ratio.agg(media="mean", mediana="median", max="max")
pm["frac_otimo"] = r.groupby("mapa").ratio.apply(lambda s: (s <= 1.0000001).mean())
pm["categoria"] = [categoria(m) for m in pm.index]
print(pm.sort_values("media", ascending=False).round(4).to_string())
pm.to_csv(TABELAS / "a6_por_mapa.csv")
print(f"\n  máximo global: ρ={r.ratio.max():.4f} em "
      f"{r.loc[r.ratio.idxmax(),'mapa']}  [relatório: 4,19 em den012d]")

print("\n=== O desvio cresce em caminhos longos? (hipótese do texto) ===")
r["faixa"] = pd.cut(r.caminho_otimo, [0, 25, 50, 100, 200, 400, 10000],
                    labels=["1-25", "26-50", "51-100", "101-200", "201-400", ">400"])
fx = r.groupby("faixa", observed=True).ratio.agg(
    n="size", media="mean", mediana="median", p95=lambda s: s.quantile(.95))
fx["frac_otimo"] = r.groupby("faixa", observed=True).ratio.apply(lambda s: (s <= 1.0000001).mean())
print(fx.round(4).to_string())
rho, p = spearmanr(r.caminho_otimo, r.ratio)
print(f"  Spearman(caminho_ótimo, ρ) = {rho:+.4f}  (p={p:.2e}, n={len(r)})")
fx.to_csv(TABELAS / "a6_por_comprimento.csv")

print("\n=== Subotimalidade no mapa DEGRADADO (não previsto no briefing) ===")
rob = carregar_robustez()
m = rob[rob.n_pivos == 10]
sub_o = (m.path_orig_form > m.path_orig_manh).mean()
sub_d = (m.path_deg_form > m.path_deg_manh).mean()
pior = (m.path_deg_form < m.path_deg_manh).sum()
print(f"  instâncias subótimas no mapa original  : {100*sub_o:.2f}%")
print(f"  instâncias subótimas no mapa degradado : {100*sub_d:.2f}%")
print(f"  desvios que são subestimativas (impossível se manh é ótimo): {pior}")
rr_o = (m.path_orig_form / m.path_orig_manh.clip(lower=1))
rr_d = (m.path_deg_form / m.path_deg_manh.clip(lower=1))
print(f"  ρ médio original {rr_o.mean():.4f} -> degradado {rr_d.mean():.4f}")
print(f"  ρ p99   original {rr_o.quantile(.99):.4f} -> degradado {rr_d.quantile(.99):.4f}")
tb = (m.assign(sub_deg=m.path_deg_form > m.path_deg_manh)
        .groupby(["tipo_degradacao", "porcentagem_bloqueio"]).sub_deg.mean().unstack())
print("\n  fração subótima por padrão x nível:")
print((100*tb).round(1).to_string())
tb.to_csv(TABELAS / "a6_subotimalidade_degradada.csv")
