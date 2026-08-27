"""A9 — Reprodutibilidade da síntese (E10).

Duas evidências:
 (a) `arena` aparece duas vezes nos CSVs: execução repetida do pipeline em modo
     append (main.cpp:73-86 abre tudo com ios::app). Mesma fórmula, mesmo fitness,
     tempos diferentes.
 (b) 5 sínteses semeadas por mapa (medicoes/sintese_repetida.csv), em que só a
     entropia do AG varia — grammar(42), operators(42) e o conjunto de treino
     ficam fixos, como no original. Isola exatamente a variabilidade que afetou
     os resultados reportados.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
import comum
from comum import *

print("=== (a) A duplicata de arena ===")
s = carregar_sintese()
d = s[s.duplicated("mapa", keep=False)]
print(d.to_string(index=False))
print(f"\n  fórmulas idênticas: {d.formula_string.nunique() == 1}")
print(f"  fitness idênticos : {d.fitness_final.nunique() == 1}")
print(f"  tempos diferentes : {d.tempo_sintese_ms.nunique() > 1} "
      f"({d.tempo_sintese_ms.min():.0f} e {d.tempo_sintese_ms.max():.0f} ms)")
w = base_larga()  # sem cache: precisa contar as duplicatas
raw = comum._csv_bruto("resultados_base.csv")
a = raw[(raw.mapa == "arena") & (raw.heuristica == "manhattan")]
dupes = a.duplicated(subset=["semente", "id_problema"], keep=False)
ig = (a[dupes].sort_values(["semente", "id_problema"]).groupby(["semente", "id_problema"])
      .expansoes.nunique() == 1).mean()
print(f"  as duas execuções de arena dão expansões idênticas em {100*ig:.1f}% dos pares")
print("  => o A* é determinístico dada a fórmula; a duplicata testa só a síntese.")

print("\n=== (b) 5 sínteses semeadas por mapa ===")
p = MEDICOES / "sintese_repetida.csv"
if not p.exists() or len(pd.read_csv(p)) == 0:
    print("  (ainda em execução — sem dados)"); sys.exit()
r = pd.read_csv(p)
print(f"  execuções concluídas: {len(r)} de 85 ({r.mapa.nunique()} mapas, "
      f"{r.run_seed.nunique()} sementes)")
orig = s.drop_duplicates("mapa").set_index("mapa")
comp = []
for m, g in r.groupby("mapa"):
    o = orig.loc[m]
    comp.append(dict(mapa=m, n=len(g),
                     formulas_distintas=g.formula_string.nunique(),
                     fitness_min=g.fitness_final.min(), fitness_max=g.fitness_final.max(),
                     fitness_cv=g.fitness_final.std() / g.fitness_final.mean()
                                if len(g) > 1 else np.nan,
                     tam_min=g.ast_size.min(), tam_max=g.ast_size.max(),
                     fitness_original=o.fitness_final,
                     bate_com_original=(g.formula_string == o.formula_string).any()))
c = pd.DataFrame(comp).set_index("mapa")
print(c.round(4).to_string())
c.to_csv(TABELAS / "a9_sintese_repetida.csv")
if len(c):
    print(f"\n  mapas em que alguma rodada reencontrou a fórmula reportada: "
          f"{int(c.bate_com_original.sum())}/{len(c)}")
    if c.n.max() > 1:
        print(f"  CV do fitness entre sementes: mediana {c.fitness_cv.median():.3f}, "
              f"máx {c.fitness_cv.max():.3f}")
        print(f"  amplitude do tamanho da AST: mediana "
              f"{(c.tam_max - c.tam_min).median():.0f} nós")
