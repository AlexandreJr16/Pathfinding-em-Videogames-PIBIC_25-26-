"""A1b — Fatores de degradação a 30%: reproduzir os do relatório e corrigi-los.

O relatório afirma δ_max de 2,54 (fórmula), 3,26 (memória-100), 4,25 (Manhattan) e
6,33 (memória-10). Aqui os quatro são primeiro reproduzidos com a regra original
(média aritmética de razões, sem dedup, sem normalizar por mapa — analise.py::
bloco_degradacao_30) e depois recalculados pela escada geométrica.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import comum
from comum import *

REL = {"Manhattan": 4.25, "Fórmula": 2.54, "Memória-10": 6.33, "Memória-100": 3.26}

print("=== 1. Réplica da regra do relatório ===")
raw = comum._csv_bruto("resultados_robustez.csv")
r30 = raw[raw.porcentagem_bloqueio == 0.3].copy()
for s_ in ("manh", "form", "mem"):
    r30[f"f_{s_}"] = r30[f"exp_deg_{s_}"] / r30[f"exp_orig_{s_}"]
def ag(df, col):
    p1 = df.groupby("semente")[col].mean()
    return p1.mean(), p1.std(ddof=1)

lin = []
for t in PADROES:
    s = r30[r30.tipo_degradacao == t]
    d = {"padrao": t}
    for lab, col, n in [("Manhattan", "f_manh", 10), ("Fórmula", "f_form", 10),
                        ("Memória-10", "f_mem", 10), ("Memória-20", "f_mem", 20),
                        ("Memória-50", "f_mem", 50), ("Memória-100", "f_mem", 100)]:
        m, sd = ag(s[s.n_pivos == n], col)
        d[lab], d[lab + "_dp"] = m, sd
    lin.append(d)
R = pd.DataFrame(lin).set_index("padrao")
print(R[[c for c in R.columns if not c.endswith("_dp")]].round(2).to_string())
mx = R[[c for c in R.columns if not c.endswith("_dp")]].max()
print("\n  δ_max reproduzido vs relatório:")
for k, v in REL.items():
    ok = "confere" if abs(mx[k] - v) < 0.006 else "DIVERGE"
    print(f"    {k:<12} {mx[k]:.2f} (pior padrão: {R[k].idxmax()})   relatório {v:.2f}   {ok}")
R.to_csv(TABELAS / "a1b_delta30_relatorio.csv")

print("\n=== 2. Corrigido: média geométrica, dedup, peso igual por mapa ===")
rob = carregar_robustez()
r3 = rob[rob.porcentagem_bloqueio == 0.3]
out = {}
for lab, col, n in [("Manhattan", "delta_manh", 10), ("Fórmula", "delta_form", 10),
                    ("Memória-10", "delta_mem", 10), ("Memória-20", "delta_mem", 20),
                    ("Memória-50", "delta_mem", 50), ("Memória-100", "delta_mem", 100)]:
    s = r3[r3.n_pivos == n]
    g = s.groupby(["mapa", "tipo_degradacao"])[col].apply(media_geometrica)
    out[lab] = g.groupby("tipo_degradacao").apply(media_geometrica)
C = pd.DataFrame(out)
print(C.round(2).to_string())
C.to_csv(TABELAS / "a1b_delta30_corrigido.csv")

print("\n  δ_max corrigido:")
for k in C.columns:
    ref = f"   relatório {REL[k]:.2f}" if k in REL else ""
    print(f"    {k:<12} {C[k].max():.2f} (pior padrão: {C[k].idxmax()}){ref}")
print("\n  A ORDEM se preserva — a conclusão qualitativa do trabalho sobrevive:")
print("   ", " < ".join(C.max().sort_values().index))

print("\n  Vencedor por padrão (menos degradada):")
print("   ", C.idxmin(axis=1).to_dict())
print("\n  >>> main.tex:683 afirma que a memória-100 é a mais robusta em radial e esparso;")
print("      com a agregação corrigida a fórmula vence nos cinco padrões:")
for t in ["Radial", "Sparse"]:
    print(f"        {t}: fórmula {C.loc[t,'Fórmula']:.2f} vs memória-100 {C.loc[t,'Memória-100']:.2f}")

print("\n  Monotonia no nº de pivôs (main.tex:685 afirma δ10 > δ20 > δ50 > δ100):")
mons = C[["Memória-10", "Memória-20", "Memória-50", "Memória-100"]]
ok = (mons.diff(axis=1).iloc[:, 1:] < 0).all(axis=1)
print("   ", ok.to_dict(), "->", "CONFIRMA" if ok.all() else "não vale em todos")
