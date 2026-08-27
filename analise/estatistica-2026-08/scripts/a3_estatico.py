"""A3 — Cenário estático: reproduzir a Tabela 4, achar o defeito e corrigir.

Achado principal: analise.py:120-134 (script original) monta as linhas de memória
da Tabela 4 a partir de resultados_robustez.csv, enquanto Manhattan e Fórmula vêm
de resultados_base.csv. A robustez só contém as instâncias que sobreviveram ao
filtro de conectividade em 30% de bloqueio (main.cpp:217-224) — 20,5% do total, e
sistematicamente os pares mais curtos. O speedup reportado divide o Manhattan de
uma população pelo memória de outra.

Correções aplicadas: E1 (média geométrica de razões), E2 (normalizar por mapa),
E3 (unidade de replicação = mapa, n=17).
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import comum
from comum import *

REP_EXP = {"manhattan": 7472.95, "formula": 2412.69, "memory10": 441.53,
           "memory20": 251.46, "memory50": 280.71, "memory100": 145.20}
REP_SPD = {"manhattan": 1.00, "formula": 3.10, "memory10": 17.25,
           "memory20": 30.78, "memory50": 33.50, "memory100": 51.98}

# ---------------------------------------------------------- 1. reprodução
print("=== 1. Reprodução literal da Tabela 4 (regra de analise.py) ===")
base_raw = comum._csv_bruto("resultados_base.csv")
rob_raw = comum._csv_bruto("resultados_robustez.csv")
manh_s = base_raw[base_raw.heuristica == "manhattan"].groupby("semente").expansoes.mean()
rob_orig = rob_raw.drop_duplicates(subset=["mapa", "semente", "id_problema", "n_pivos"])
rob_orig = rob_orig[~((rob_orig.mapa == "brc000d") & (rob_orig.n_pivos == 50))]

rows = []
for c in CONFIGS:
    if c in ("manhattan", "formula"):
        p1 = base_raw[base_raw.heuristica == c].groupby("semente").expansoes.mean()
        n_inst = (base_raw.heuristica == c).sum()
        fonte = "base.csv"
    else:
        n = int(c.replace("memory", ""))
        sub = rob_orig[rob_orig.n_pivos == n]
        p1 = sub.groupby("semente").exp_orig_mem.mean()
        n_inst = len(sub); fonte = "robustez.csv"
    sp = np.mean([manh_s[s] / p1[s] for s in p1.index])
    rows.append(dict(config=ROTULOS[c], fonte=fonte, n_instancias=n_inst,
                     exp=p1.mean(), std=p1.std(ddof=1), speedup=sp,
                     rel_exp=REP_EXP[c], rel_spd=REP_SPD[c]))
rep = pd.DataFrame(rows)
rep["confere"] = (np.isclose(rep.exp, rep.rel_exp, atol=0.01) &
                  np.isclose(rep.speedup, rep.rel_spd, atol=0.01))
print(rep.round(2).to_string(index=False))
print(f"\n>>> reproduz {int(rep.confere.sum())}/{len(rep)} linhas exatamente")
rep.to_csv(TABELAS / "a3_reproducao_tabela4.csv", index=False)

# ------------------------------------------- 2. tamanho do erro de população
print("\n=== 2. O erro: duas populações diferentes ===")
m_todas = manh_s.mean()
m_sobrev = rob_orig[rob_orig.n_pivos == 100].groupby("semente").exp_orig_manh.mean().mean()
f_sobrev = rob_orig[rob_orig.n_pivos == 100].groupby("semente").exp_orig_form.mean().mean()
print(f"  Manhattan, todas as instâncias      : {m_todas:8.2f}  (n=116.700)")
print(f"  Manhattan, só as sobreviventes      : {m_sobrev:8.2f}  (n=23.906)")
print(f"  Fórmula,   só as sobreviventes      : {f_sobrev:8.2f}")
print(f"  As sobreviventes são {m_todas/m_sobrev:.2f}x mais fáceis para o mesmo algoritmo.")
print(f"\n  speedup memória-100 reportado (populações distintas): {m_todas/145.20:6.2f}x")
print(f"  speedup memória-100 na MESMA população              : {m_sobrev/145.20:6.2f}x")

# ------------------------------------- 3. comparação correta, mesma população
print("\n=== 3. Comparação correta: todas as instâncias, pareadas (base.csv) ===")
w = base_larga()
deg = celulas_degeneradas()

def sem_deg(w, cfg):
    if not cfg.startswith("memory"): return w
    n = int(cfg.replace("memory", ""))
    mau = {(m, s) for (m, s, k) in deg if k == n}
    return w[~pd.MultiIndex.from_arrays([w.mapa, w.semente]).isin(mau)]

rows = []
for c in CONFIGS:
    sub = sem_deg(w, c).copy()
    sub["r"] = sub.manhattan / sub[c].clip(lower=1)
    por_mapa, glob = escada_geometrica(sub, "r")
    lo, hi = bootstrap_bca_geom(por_mapa.values) if c != "manhattan" else (1.0, 1.0)
    tudo = w.copy(); tudo["r"] = tudo.manhattan / tudo[c].clip(lower=1)
    _, glob_cd = escada_geometrica(tudo, "r")
    rows.append(dict(config=ROTULOS[c],
                     exp_media_agrupada=sub[c].mean(),
                     speedup_aritmetico=w.manhattan.mean() / sub[c].mean(),
                     speedup_geometrico=glob, ic95_lo=lo, ic95_hi=hi,
                     geom_com_degeneradas=glob_cd, relatorio=REP_SPD[c]))
t = pd.DataFrame(rows)
t["erro_relatorio_x"] = t.relatorio / t.speedup_geometrico
print(t.round(2).to_string(index=False))
t.to_csv(TABELAS / "a3_speedups_corrigidos.csv", index=False)

print("\n=== 4. Speedup geométrico por mapa ===")
pm = {}
for c in CONFIGS[1:]:
    sub = sem_deg(w, c).copy(); sub["r"] = sub.manhattan / sub[c].clip(lower=1)
    pm[ROTULOS[c]], _ = escada_geometrica(sub, "r")
pm = pd.DataFrame(pm)
pm["categoria"] = [categoria(m) for m in pm.index]
print(pm.round(2).sort_values("Memória-100", ascending=False).to_string())
pm.to_csv(TABELAS / "a3_speedup_por_mapa.csv")
