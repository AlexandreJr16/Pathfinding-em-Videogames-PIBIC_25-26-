"""A2 — Ranking honesto entre as 6 configurações (Demšar, 2006).

6 configurações × 17 mapas: Friedman sobre os postos por mapa, pós-teste de
Nemenyi, diagrama de diferença crítica. Feito duas vezes — cenário estático e
sob degradação — e o contraste entre os dois diagramas é a evidência visual da
tese do A1.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from figuras_comum import *
from scipy.stats import friedmanchisquare, wilcoxon

# ---------------------------------------------- escore estático por mapa
w = base_larga_cache()
dij = carregar_dijkstra().set_index(["mapa", "id_problema"]).exp_dijkstra
w["dij"] = dij.reindex(pd.MultiIndex.from_arrays([w.mapa, w.id_problema])).values
print(f"instâncias com baseline Dijkstra: {w.dij.notna().mean():.1%}")

est = {}
for c in CONFIGS:                       # expansões normalizadas pelo teto (h=0)
    r = w[c] / w.dij
    est[ROTULOS[c]] = (pd.DataFrame({"mapa": w.mapa, "semente": w.semente, "r": r})
                       .groupby(["mapa", "semente"]).r.apply(media_geometrica)
                       .groupby("mapa").apply(media_geometrica))
est = pd.DataFrame(est)
print("\n=== Estático: expansões / expansões do Dijkstra (menor = melhor) ===")
print(est.round(3).to_string())
est.to_csv(TABELAS / "a2_escore_estatico.csv")

# ---------------------------------------------- escore sob degradação
rob = carregar_robustez()
partes = {}
mm = rob[rob.n_pivos == 10]
partes["Manhattan"] = mm.assign(d=mm.delta_manh)
partes["Fórmula"] = mm.assign(d=mm.delta_form)
for n in (10, 20, 50, 100):
    s = rob[rob.n_pivos == n]; partes[f"Memória-{n}"] = s.assign(d=s.delta_mem)
deg = {}
for lab, df in partes.items():
    # média geométrica por (mapa, padrão) e depois entre os 5 padrões com peso igual,
    # para que Radial/Stochastic (mais sobreviventes) não dominem — ver A10.
    g = df.groupby(["mapa", "tipo_degradacao"]).d.apply(media_geometrica)
    deg[lab] = g.groupby("mapa").apply(media_geometrica)
deg = pd.DataFrame(deg)
print("\n=== Degradação: fator δ (menor = melhor), padrões com peso igual ===")
print(deg.round(3).to_string())
deg.to_csv(TABELAS / "a2_escore_degradado.csv")

# ---------------------------------------------- Friedman + Nemenyi
def analisa(tab, nome):
    tab = tab[[ROTULOS[c] for c in CONFIGS]]
    chi, p = friedmanchisquare(*[tab[c].values for c in tab.columns])
    postos = tab.rank(axis=1).mean()
    cd = nemenyi_cd(tab.shape[1], tab.shape[0])
    print(f"\n--- Friedman ({nome}): χ²={chi:.2f}, p={p:.3e}, n={len(tab)} mapas ---")
    print("postos médios:", "  ".join(f"{k}={v:.2f}" for k, v in postos.sort_values().items()))
    print(f"distância crítica de Nemenyi (α=0,05): {cd:.3f}")
    dif = pd.DataFrame(np.abs(postos.values[:, None] - postos.values[None, :]),
                       index=postos.index, columns=postos.index)
    print(f"pares NÃO separados pela DC: "
          f"{[(a,b) for i,a in enumerate(postos.index) for b in postos.index[i+1:] if dif.loc[a,b] <= cd]}")
    return postos, cd, chi, p

p_est, cd_est, chi_e, pe = analisa(est, "estático")
p_deg, cd_deg, chi_d, pd_ = analisa(deg, "degradado")
pd.DataFrame({"posto_estatico": p_est, "posto_degradado": p_deg,
              "variacao": p_deg - p_est}).to_csv(TABELAS / "a2_postos.csv")

print("\n=== A inversão da hierarquia (o resultado central) ===")
cmp = pd.DataFrame({"posto_estático": p_est, "posto_degradado": p_deg})
cmp["Δposto"] = cmp.posto_degradado - cmp.posto_estático
print(cmp.sort_values("posto_estático").round(2).to_string())

# Wilcoxon pareado sobre os 17 mapas, fórmula vs memória-100, nos dois cenários
for nome, tab in (("estático", est), ("degradado", deg)):
    st, pw = wilcoxon(tab["Fórmula"], tab["Memória-100"])
    d = cliffs_delta(tab["Fórmula"], tab["Memória-100"])
    print(f"  Fórmula vs Memória-100 ({nome}): Wilcoxon p={pw:.4f}, "
          f"Cliff δ={d:+.3f} ({magnitude_cliff(d)})")

# ---------------------------------------------- Figura 1
fig, axes = plt.subplots(2, 1, figsize=(3.35, 2.9))
diagrama_cd(axes[0], p_est.values, cd_est, p_est.index.tolist(),
            "(a) Cenário estático")
diagrama_cd(axes[1], p_deg.values, cd_deg, p_deg.index.tolist(),
            "(b) Sob degradação estrutural")
fig.subplots_adjust(hspace=0.30)
salvar(fig, "fig1_diagrama_cd", FIGURAS)
