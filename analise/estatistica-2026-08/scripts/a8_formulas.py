"""A8 — Análise das 17 fórmulas sintetizadas (a tangente qualitativa).

O relatório mostra UMA das 17 fórmulas. As outras dezesseis estão inexploradas.
Parser da notação prefixa com a semântica de src/synthesis/HeuristicNode.h:
  deltaX = |s.x-g.x|, deltaY = |s.y-g.y|; size = nº de nós; depth = profundidade.
Alvo central: quantificar a regularização. main.tex:412 afirma que o fator 0,0005
"favorece fórmulas mais compactas, prevenindo overfitting"; GeneticAlgorithm.h:71
comenta a mesma constante como "Penalidade por tamanho baixíssima para permitir
fórmulas complexas". Os dois não podem estar certos.
"""
import sys, re, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
from scipy.stats import spearmanr

UNARIOS = {"sqr", "sqrt", "abs", "neg"}
BINARIOS = {"+", "-", "*", "/", "max", "min"}

def tokenize(s):
    return re.findall(r"\(|\)|[^\s()]+", s)

def parse(tokens, i=0):
    """Devolve (nó, próximo índice). Nó = (op, filhos) ou ('term', valor)."""
    t = tokens[i]
    if t == "(":
        op = tokens[i + 1]; i += 2; filhos = []
        while tokens[i] != ")":
            f, i = parse(tokens, i); filhos.append(f)
        return (op, filhos), i + 1
    return ("term", t), i + 1

def caminha(no, prof=1):
    """(tamanho, profundidade, contagem de operadores, terminais)"""
    op, x = no
    if op == "term":
        return 1, prof, {}, [x]
    tam, pmax, ops, terms = 1, prof, {op: 1}, []
    for f in x:
        t, p, o, tm = caminha(f, prof + 1)
        tam += t; pmax = max(pmax, p); terms += tm
        for k, v in o.items(): ops[k] = ops.get(k, 0) + v
    return tam, pmax, ops, terms

def troca_xy(no):
    """Espelha deltaX<->deltaY, para testar simetria da expressão."""
    op, x = no
    if op == "term":
        return ("term", {"deltaX": "deltaY", "deltaY": "deltaX"}.get(x, x))
    return (op, [troca_xy(f) for f in x])

def canon(no):
    """Forma canônica: operadores comutativos ordenam os filhos."""
    op, x = no
    if op == "term": return ("term", x)
    f = [canon(c) for c in x]
    if op in {"+", "*", "max", "min"}: f = sorted(f, key=repr)
    return (op, f)

s = carregar_sintese()
dup = s[s.duplicated("mapa", keep=False)]
s = s.drop_duplicates("mapa").set_index("mapa")

lin = []
for m, row in s.iterrows():
    no, _ = parse(tokenize(row.formula_string))
    tam, prof, ops, terms = caminha(no)
    cst = [float(t) for t in terms if re.fullmatch(r"-?\d+\.?\d*", t)]
    lin.append(dict(mapa=m, tamanho=tam, profundidade=prof,
                    n_operadores=sum(ops.values()), n_terminais=len(terms),
                    usa_deltaX="deltaX" in terms, usa_deltaY="deltaY" in terms,
                    n_deltaX=terms.count("deltaX"), n_deltaY=terms.count("deltaY"),
                    n_constantes=len(cst), max_constante=max(cst) if cst else np.nan,
                    simetrica=canon(no) == canon(troca_xy(no)),
                    tem_max_min=bool(ops.get("max", 0) + ops.get("min", 0)),
                    tem_div=bool(ops.get("/", 0)), tem_sqrt=bool(ops.get("sqrt", 0)),
                    fitness=row.fitness_final, tempo_ms=row.tempo_sintese_ms,
                    **{f"op_{k}": v for k, v in ops.items()}))
f = pd.DataFrame(lin).set_index("mapa").fillna({c: 0 for c in
        [c for c in pd.DataFrame(lin).columns if c.startswith("op_")]})
f["categoria"] = [categoria(m) for m in f.index]
f["penalidade"] = 0.0005 * f.tamanho
f["speedup_treino"] = f.fitness + f.penalidade          # fitness = speedup - λ·‖T‖
f["penalidade_pct"] = 100 * f.penalidade / f.speedup_treino

print("=== As 17 fórmulas ===")
print(f[["tamanho", "profundidade", "n_deltaX", "n_deltaY", "n_constantes",
         "simetrica", "fitness", "categoria"]].sort_values("tamanho").to_string())
f.to_csv(TABELAS / "a8_formulas.csv")

print(f"\ntamanho da AST: mediana {f.tamanho.median():.0f}, "
      f"min {f.tamanho.min()} ({f.tamanho.idxmin()}), max {f.tamanho.max()} ({f.tamanho.idxmax()})")
print(f"profundidade  : mediana {f.profundidade.median():.0f}, máx {f.profundidade.max()}")
print(f"simétricas em Δx/Δy: {int(f.simetrica.sum())}/17    "
      f"usam ambos os deltas: {int((f.usa_deltaX & f.usa_deltaY).sum())}/17")

print("\n=== A regularização funciona? ===")
print(f[["tamanho", "fitness", "penalidade", "speedup_treino", "penalidade_pct"]]
      .sort_values("tamanho").round(4).to_string())
print(f"\n  λ = 0,0005; penalidade máxima observada = {f.penalidade.max():.4f} "
      f"({f.penalidade_pct.max():.2f}% do fitness)")
print(f"  penalidade mediana = {f.penalidade_pct.median():.3f}% do fitness")
print(f"  para a penalidade igualar 10% do fitness, λ teria de ser "
      f"{0.0005 * (0.10 / (f.penalidade_pct.median()/100)):.4f} "
      f"({(0.10 / (f.penalidade_pct.median()/100)):.0f}x maior)")
rho, p = spearmanr(f.tamanho, f.fitness)
print(f"  Spearman(tamanho, fitness) = {rho:+.3f} (p={p:.3f}) — se a regularização")
print("    mordesse, fórmulas grandes seriam penalizadas e a correlação seria negativa.")

print("\n=== Famílias ===")
def familia(r):
    if r.tamanho <= 7: return "quadrática compacta"
    if r.tem_max_min and r.tem_div: return "grande com max/min e divisão"
    if r.tem_max_min: return "grande com max/min"
    return "grande sem max/min"
f["familia"] = f.apply(familia, axis=1)
print(f.groupby("familia").agg(n=("tamanho", "size"), tam_mediano=("tamanho", "median"),
                               fitness_medio=("fitness", "mean")).round(2).to_string())

print("\n=== Gap de generalização: fitness (treino) vs speedup medido (teste) ===")
sp = pd.read_csv(TABELAS / "a3_speedup_por_mapa.csv", index_col=0)["Fórmula"]
g = pd.DataFrame({"speedup_treino": f.speedup_treino, "speedup_medido": sp,
                  "tamanho": f.tamanho})
g["gap"] = g.speedup_treino / g.speedup_medido
print(g.sort_values("gap", ascending=False).round(3).to_string())
print(f"\n  o AG maximiza o speedup no conjunto de treino (25% do cenário, main.cpp:109-117)")
print(f"  gap mediano treino/teste: {g.gap.median():.2f}x  "
      f"(faixa {g.gap.min():.2f}-{g.gap.max():.2f}x)")
rho2, p2 = spearmanr(g.tamanho, g.gap)
print(f"  Spearman(tamanho da AST, gap) = {rho2:+.3f} (p={p2:.3f})")
g.to_csv(TABELAS / "a8_gap_generalizacao.csv")

print("\n=== Correlações com desempenho medido ===")
rat = pd.read_csv(TABELAS / "a6_por_mapa.csv", index_col=0)
cor = pd.DataFrame({"tamanho": f.tamanho, "profundidade": f.profundidade,
                    "fitness": f.fitness, "tempo_sintese": f.tempo_ms,
                    "S": celulas_transitaveis().set_index("mapa").S,
                    "speedup": sp, "subotimalidade": rat.media - 1})
print(cor.corr(method="spearman").round(3).to_string())
cor.to_csv(TABELAS / "a8_correlacoes.csv")

print("\n=== A9: duplicata de arena ===")
print(dup[["mapa", "tempo_sintese_ms", "fitness_final", "formula_string"]].to_string(index=False))
