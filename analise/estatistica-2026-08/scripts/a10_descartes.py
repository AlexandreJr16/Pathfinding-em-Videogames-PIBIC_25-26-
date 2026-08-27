"""A10 — Contabilizar os pares descartados por perda de conectividade (E7).

main.cpp:217-224 seleciona os pares no estado de 30% de bloqueio e usa esse mesmo
conjunto nos três níveis; por isso o descarte não é separável por nível. O conjunto
sobrevivente é específico de cada padrão e NÃO é aninhado.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *

rob = carregar_robustez()
base = carregar_base()
manh = base[base.heuristica == "manhattan"]

# denominador: pares do cenário por (mapa, semente)
denom = manh.groupby(["mapa", "semente"]).size().rename("total")
print(f"pares avaliados no cenário estático: {denom.sum()}")

sob = (rob[(rob.n_pivos == 10) & (rob.porcentagem_bloqueio == 0.1)]
       .groupby(["mapa", "semente", "tipo_degradacao"]).size().rename("sobreviventes"))
tab = sob.reset_index().merge(denom.reset_index(), on=["mapa", "semente"])
tab["taxa"] = tab.sobreviventes / tab.total

print("\n=== Taxa de sobrevivência por padrão (todos os mapas e sementes) ===")
por_padrao = tab.groupby("tipo_degradacao").agg(
    sobreviventes=("sobreviventes", "sum"), total=("total", "sum"))
por_padrao["taxa_global"] = por_padrao.sobreviventes / por_padrao.total
por_padrao["descartados"] = por_padrao.total - por_padrao.sobreviventes
por_padrao["taxa_media_por_mapa"] = tab.groupby("tipo_degradacao").taxa.mean()
por_padrao["dp_entre_mapas"] = tab.groupby("tipo_degradacao").taxa.std()
print((por_padrao * [1, 1, 100, 1, 100, 100]).round(2).to_string())
por_padrao.to_csv(TABELAS / "a10_sobrevivencia_por_padrao.csv")

print("\n=== Taxa de sobrevivência por mapa × padrão (%) ===")
piv = (tab.groupby(["mapa", "tipo_degradacao"]).taxa.mean().unstack() * 100)
piv["|S|"] = celulas_transitaveis().set_index("mapa").S
print(piv.round(1).sort_values("Linear").to_string())
piv.to_csv(TABELAS / "a10_sobrevivencia_por_mapa.csv")

# --------------------------------------------- aninhamento entre padrões
print("\n=== Os conjuntos sobreviventes são aninhados? ===")
conj = {t: set(map(tuple, rob[(rob.tipo_degradacao == t) & (rob.n_pivos == 10) &
                              (rob.porcentagem_bloqueio == 0.1)]
                   [["mapa", "semente", "id_problema"]].values))
        for t in PADROES}
uni = set().union(*conj.values())
inter = set.intersection(*conj.values())
print(f"  união dos 5 padrões    : {len(uni)}")
print(f"  interseção dos 5 padrões: {len(inter)}  <- base de uma comparação pareada entre padrões")
cont = pd.Series([sum(k in c for c in conj.values()) for k in uni]).value_counts().sort_index()
print("  instâncias presentes em k padrões:")
for k, v in cont.items(): print(f"    k={k}: {v}")

# --------------------------------------------- viés de dificuldade
print("\n=== O filtro seleciona pares fáceis? (comprimento ótimo do caminho) ===")
todos = manh.set_index(["mapa", "semente", "id_problema"]).caminho_tamanho
linhas = []
for t in PADROES:
    idx = pd.MultiIndex.from_tuples(sorted(conj[t]))
    s = todos.reindex(idx).dropna()
    linhas.append(dict(padrao=t, n=len(s), mediana=s.median(), media=s.mean(), p90=s.quantile(.9)))
linhas.append(dict(padrao="TODOS os pares", n=len(todos), mediana=todos.median(),
                   media=todos.mean(), p90=todos.quantile(.9)))
d = pd.DataFrame(linhas)
d["razao_vs_todos"] = d.media / d.media.iloc[-1]
print(d.round(2).to_string(index=False))
d.to_csv(TABELAS / "a10_vies_dificuldade.csv", index=False)

# expansões de Manhattan nas duas populações (o mesmo algoritmo, populações distintas)
w = base_larga_cache().set_index(["mapa", "semente", "id_problema"])
print("\n  Manhattan (expansões médias):")
print(f"    todos os pares          : {w.manhattan.mean():8.1f}")
for t in PADROES:
    s = w.reindex(pd.MultiIndex.from_tuples(sorted(conj[t]))).dropna()
    print(f"    sobreviventes {t:<11}: {s.manhattan.mean():8.1f}  "
          f"({w.manhattan.mean()/s.manhattan.mean():.2f}x mais fáceis)")
