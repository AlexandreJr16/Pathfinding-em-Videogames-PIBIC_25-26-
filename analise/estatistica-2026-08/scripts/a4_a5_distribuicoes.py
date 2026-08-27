"""A4 — Distribuições e cauda (E6).  A5 — Testes pareados e tamanho de efeito (E3,E4,E5).

A4: em jogo, o que estoura o orçamento de quadro não é a busca média, é a pior
    busca do segundo. Nenhuma média da Tabela 4 captura isso.
A5: com n=116.050 qualquer diferença é significativa; o que importa é a magnitude.
    Por isso todo p vem acompanhado do δ de Cliff, e os testes são feitos nos dois
    níveis — instância (p barato) e mapa (n=17, o IC honesto).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from figuras_comum import *
from scipy.stats import wilcoxon

w = base_larga_cache()
dij = carregar_dijkstra().set_index(["mapa", "id_problema"]).exp_dijkstra
w["dij"] = dij.reindex(pd.MultiIndex.from_arrays([w.mapa, w.id_problema])).values
for c in CONFIGS:
    w["n_" + c] = w[c] / w.dij          # adimensional em (0,1]: fração do teto h=0

# ------------------------------------------------------------------ A4
print("=== A4: expansões normalizadas pelo teto do Dijkstra ===")
qs = [.5, .75, .9, .95, .99, 1.0]
lin = []
for c in CONFIGS:
    x = w["n_" + c]
    d = dict(config=ROTULOS[c], media=x.mean(), mediana=x.median(),
             IQR=x.quantile(.75) - x.quantile(.25))
    for q in qs[2:]:
        d[f"p{int(q*100)}" if q < 1 else "max"] = x.quantile(q)
    d["razao_p99_mediana"] = x.quantile(.99) / x.median()
    lin.append(d)
t = pd.DataFrame(lin)
print(t.round(3).to_string(index=False))
t.to_csv(TABELAS / "a4_distribuicao_normalizada.csv", index=False)

print("\n--- o mesmo em expansões absolutas (o que o jogo sente) ---")
lin = []
for c in CONFIGS:
    x = w[c]
    lin.append(dict(config=ROTULOS[c], mediana=x.median(), p90=x.quantile(.9),
                    p99=x.quantile(.99), max=x.max(), media=x.mean()))
ta = pd.DataFrame(lin)
ta["p99/mediana"] = ta.p99 / ta.mediana
print(ta.round(1).to_string(index=False))
ta.to_csv(TABELAS / "a4_distribuicao_absoluta.csv", index=False)

# quem tem média boa mas cauda ruim?
print("\n--- posto pela média vs posto pelo p99 (normalizado) ---")
r = pd.DataFrame({"media": t.set_index("config").media.rank(),
                  "p99": t.set_index("config").p99.rank()})
r["Δ"] = r.p99 - r.media
print(r.to_string())

print("\n--- a cauda é intrínseca ou vem do colapso de pivôs do A11? ---")
_deg = celulas_degeneradas()
lin = []
for c in CONFIGS:
    n = int(c.replace("memory","")) if c.startswith("memory") else None
    mau = {(m,s) for (m,s,k) in _deg if k == n} if n else set()
    ok = ~pd.MultiIndex.from_arrays([w.mapa, w.semente]).isin(mau)
    lin.append(dict(config=ROTULOS[c], p99_todas=w["n_"+c].quantile(.99),
                    p99_sem_colapso=w.loc[ok, "n_"+c].quantile(.99),
                    celulas_removidas=len(mau)))
tc = pd.DataFrame(lin)
print(tc.round(3).to_string(index=False))
tc.to_csv(TABELAS / "a4_cauda_vs_colapso.csv", index=False)

fig, ax = plt.subplots(figsize=(3.35, 2.3))
for i, c in enumerate(CONFIGS):
    x = np.sort(w["n_" + c].dropna().values)
    y = np.arange(1, len(x) + 1) / len(x)
    p = np.unique(np.linspace(0, len(x) - 1, 3000).astype(int))
    ax.plot(x[p], y[p], linestyle=TRACOS[i], color=CINZAS[i], label=ROTULOS[c])
ax.set_xscale("log")
ax.set_xlabel("Expansões / expansões do Dijkstra (escala log)")
ax.set_ylabel("Fração acumulada de instâncias")
ax.set_ylim(0, 1.01); ax.grid(alpha=.25, lw=.4)
ax.axhline(.99, color="0.55", lw=.5, ls=":")
ax.text(ax.get_xlim()[1] * 0.92, .972, "p99", fontsize=6, color="0.35", ha="right")
ax.legend(loc="lower right", frameon=False, ncol=1, labelspacing=.25,
          handlelength=2.6, borderpad=.2)
salvar(fig, "fig2_ecdf", FIGURAS)

# ------------------------------------------------------------------ A5
print("\n=== A5: testes pareados (4 pares pré-registrados, correção de Holm) ===")
PARES = [("manhattan", "formula"), ("manhattan", "memory100"),
         ("formula", "memory10"), ("formula", "memory100")]
deg = celulas_degeneradas()

def limpa(cfg):
    n = int(cfg.replace("memory", "")) if cfg.startswith("memory") else None
    mau = {(m, s) for (m, s, k) in deg if k == n} if n else set()
    return ~pd.MultiIndex.from_arrays([w.mapa, w.semente]).isin(mau)

lin = []
for a, b in PARES:
    m = limpa(a) & limpa(b)
    xa, xb = w.loc[m, "n_" + a], w.loc[m, "n_" + b]
    st, p_i = wilcoxon(xa, xb)
    d_i = cliffs_delta(xa, xb)
    # nível mapa: média geométrica da razão por mapa (n=17)
    ra = (pd.DataFrame({"mapa": w.loc[m, "mapa"], "r": xa / xb})
          .groupby("mapa").r.apply(media_geometrica))
    st2, p_m = wilcoxon(np.log(ra))
    lo, hi = bootstrap_bca_geom(ra.values)
    lin.append(dict(par=f"{ROTULOS[a]} vs {ROTULOS[b]}", n_inst=int(m.sum()),
                    p_instancia=p_i, cliff=d_i, magnitude=magnitude_cliff(d_i),
                    razao_geom=media_geometrica(ra), ic_lo=lo, ic_hi=hi,
                    n_mapas=len(ra), p_mapa=p_m))
t5 = pd.DataFrame(lin)
t5["p_inst_holm"] = holm(t5.p_instancia)
t5["p_mapa_holm"] = holm(t5.p_mapa)
print(t5[["par", "n_inst", "p_instancia", "p_inst_holm", "cliff", "magnitude"]]
      .to_string(index=False))
print()
print(t5[["par", "razao_geom", "ic_lo", "ic_hi", "n_mapas", "p_mapa", "p_mapa_holm"]]
      .round(4).to_string(index=False))
t5.to_csv(TABELAS / "a5_testes_pareados.csv", index=False)
print("\n>>> com n=%d, todo p de instância é < 1e-300; o que separa os pares é o δ."
      % t5.n_inst.max())
