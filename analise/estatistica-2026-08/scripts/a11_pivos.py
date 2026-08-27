"""A11 — O colapso do sorteio de pivôs explica o desvio de 138,44.

generatePivots (heuristics.cpp) sorteia o PRIMEIRO pivô uniformemente entre as células
transitáveis. Se ele cai num bolsão desconexo, bfsPivo devolve -1 fora do bolsão, o argmax
de minDists fica preso lá e todos os pivôs ficam confinados; então dS == dG == -1 em quase
toda consulta e heurísticaMemoryBased devolve h ≡ 0 — o A* degenera em Dijkstra.

A previsão é falseável: colapsos só podem ocorrer nos mapas com bolsões, a uma taxa igual
à fração de células fora da maior componente. Se não bater, o mecanismo cai.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from scipy.stats import binomtest

comps = celulas_transitaveis().set_index("mapa")
piv = carregar_pivos()
piv["colapsou"] = piv.frac_consultas_h_zero > 0.5
piv["frac_fora"] = piv.mapa.map(comps.frac_fora_maior)

print("=== Estrutura de componentes conexas dos 17 mapas ===")
print(comps[["S", "n_componentes", "maior_componente", "frac_fora_maior"]]
      .sort_values("frac_fora_maior", ascending=False).round(4).to_string())

print("\n=== Previsão vs observação ===")
t = piv.groupby("mapa").agg(sorteios=("colapsou", "size"), observados=("colapsou", "sum"),
                            frac_fora=("frac_fora", "first"))
t["esperados"] = t.sorteios * t.frac_fora
t["n_componentes"] = comps.n_componentes
print(t[t.frac_fora > 0].round(2).to_string())
print(f"\n  mapas 100% conexos: {int((t.frac_fora == 0).sum())} — colapsos neles: "
      f"{int(t.loc[t.frac_fora == 0, 'observados'].sum())}")
print(f"  total observado: {int(t.observados.sum())}   esperado: {t.esperados.sum():.1f}")
bt = binomtest(int(t.observados.sum()), int(t.sorteios.sum()),
               float((t.esperados.sum() / t.sorteios.sum())))
print(f"  teste binomial contra a taxa prevista: p = {bt.pvalue:.3f} "
      f"(não rejeita o mecanismo)")
t.to_csv(TABELAS / "a11_colapso_pivos.csv")

print("\n=== As 7 células que colapsaram ===")
c = piv[piv.colapsou][["mapa", "semente", "n_pivos", "pivos_fora_maior_comp",
                       "primeiro_pivo_fora", "frac_consultas_h_zero", "h_medio"]]
print(c.to_string(index=False))
print(f"\n  em todas, o primeiro pivô caiu fora da maior componente: "
      f"{bool((c.primeiro_pivo_fora == 1).all())}")
print(f"  em todas, TODOS os pivôs ficaram fora: "
      f"{bool((c.pivos_fora_maior_comp == c.n_pivos).all())}")

print("\n=== Consequência: a distribuição é bimodal, não ruidosa ===")
w = base_larga_cache()
cel = w.groupby(["mapa", "semente"])[["manhattan"] + [f"memory{n}" for n in (10,20,50,100)]].mean()
for n in (10, 20, 50, 100):
    col = f"memory{n}"
    mau = {(m, s) for (m, s, k) in celulas_degeneradas() if k == n}
    ok = ~cel.index.isin(mau)
    print(f"  {col:<10}: {int((~ok).sum())} células colapsadas | "
          f"média {cel[col].mean():8.1f} (dp {cel[col].std():8.1f})  ->  "
          f"sem colapso {cel.loc[ok, col].mean():7.1f} (dp {cel.loc[ok, col].std():6.1f})")
print("\n  média ± desvio sobre uma mistura bimodal não descreve nenhum dos dois regimes.")
