"""A0 — A heurística de memória É reprocessada após a degradação.

O relatório afirma o contrário (main.tex:534, :695) e constrói sobre isso a narrativa
de mecanismo de main.tex:685. Este script quantifica o reprocessamento e mede o que o
experimento teria medido se as distâncias estivessem de fato congeladas.

Registro metodológico: o teste de otimalidade de caminho NÃO decide a questão.
Verifiquei que path_deg_mem == path_deg_manh em 100% das 431.016 linhas, mas isso é
esperado nos dois casos: bloquear células só aumenta distâncias, então
|d_orig(p,s) - d_orig(p,g)| <= d_orig(s,g) <= d_deg(s,g), e uma distância obsoleta
continua admissível. Só o código, ou a medição direta feita aqui, decidem.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *

r = pd.read_csv(MEDICOES / "reprocessamento.csv")
e = pd.read_csv(MEDICOES / "reprocessamento_expansoes.csv")

# Só sementes COMPLETAS entram no agregado. O experimento pode estar em curso
# (a extensão L5 mede as sementes 123/456/789/1011 e grava em append), e agregar
# uma semente pela metade produziria uma média desbalanceada entre mapas —
# um número errado, sem nenhum aviso.
COMPLETA = 17 * 5 * 3 * 4          # mapas x padrões x níveis x configurações de pivô
cont = r.groupby("semente").size()
completas = sorted(cont[cont == COMPLETA].index)
parciais = {int(k): int(v) for k, v in cont[cont != COMPLETA].items()}
if parciais:
    print(f"[aviso] sementes incompletas ignoradas: {parciais} "
          f"(cada semente completa tem {COMPLETA} linhas)")
if not completas:
    raise SystemExit("nenhuma semente completa em reprocessamento.csv")
r = r[r.semente.isin(completas)]
e = e[e.semente.isin(completas)]
print(f"sementes usadas: {completas}   mapas: {r.mapa.nunique()}   linhas: {len(r)}")

print("\n=== 1. As distâncias pré-computadas mudam? ===")
print(f"  posições dos pivôs mantidas idênticas em {100*r.pivos_iguais.mean():.1f}% das medições")
t = r.groupby(["tipo_degradacao_", "nivel"]).frac_diferentes.agg(["mean", "min", "max"]) \
    if "tipo_degradacao_" in r else r.groupby(["padrao", "nivel"]).frac_diferentes.agg(
        ["mean", "min", "max"])
print((100 * t).round(2).to_string())
print(f"\n  >>> fração de células de distância que mudam: "
      f"{100*r.frac_diferentes.min():.1f}% a {100*r.frac_diferentes.max():.1f}% "
      f"(mediana {100*r.frac_diferentes.median():.1f}%)")
print(f"  >>> células que se tornam inalcançáveis a partir do pivô: mediana "
      f"{100*(r.viraram_inalcancaveis/r.celulas_comparadas).median():.1f}%")
t.to_csv(TABELAS / "a0_reprocessamento.csv")

print("\n=== 2. Quanto vale o reprocessamento? δ com distâncias frescas vs congeladas ===")
g = e.groupby(["padrao", "nivel"])[["delta_fresco", "delta_congelado"]].apply(
    lambda d: pd.Series({"fresco": media_geometrica(d.delta_fresco),
                         "congelado": media_geometrica(d.delta_congelado)}))
g["ganho_do_reprocessamento"] = g.congelado / g.fresco
print(g.round(3).to_string())
print("\n  ganho > 1: recalcular a BFS AJUDA.  ganho < 1: recalcular PIORA.")
piora = g[g.ganho_do_reprocessamento < 1]
print(f"  padrões/níveis em que recalcular PIORA: {len(piora)} de {len(g)}")
g.to_csv(TABELAS / "a0_fresco_vs_congelado.csv")

print("\n  por número de pivôs (30% de bloqueio):")
g2 = e[e.nivel == 0.3].groupby(["padrao", "n_pivos"])[["delta_fresco", "delta_congelado"]].apply(
    lambda d: pd.Series({"fresco": media_geometrica(d.delta_fresco),
                         "congelado": media_geometrica(d.delta_congelado)}))
print(g2.round(2).unstack().to_string())

print("\n=== 3. A tese sobrevive? ===")
print("  A memória recebe um BFS completo de graça a cada padrão x nível x configuração;")
print("  a fórmula e Manhattan não recebem nada. Mesmo assim (A1/A2):")
tab = pd.read_csv(TABELAS / "a1_delta_por_padrao.csv", index_col=0)
tab = tab[[c for c in CONFIGS if c in tab.columns]]
print(tab.round(2).to_string())
venc = (tab.idxmin(axis=1) == "formula").sum()
print(f"\n  >>> a fórmula é a menos degradada em {venc} dos {len(tab)} padrões,")
print("      apesar de ser a única das duas que não é reprocessada.")
