"""A1 — Teste da tese central: a hierarquia do cenário estático não se preserva
sob degradação. Em linguagem estatística: interação estratégia × padrão.

Desenho, dado o A10:
  - `estrategia` é fator INTRA-instância (as 6 configurações rodam no mesmo par):
    comparação limpa.
  - `padrao` é fator ENTRE-instâncias e está confundido pela sobrevivência
    diferencial (0,75% a 10,73%, com dificuldade média variando 275x entre padrões).
    Mitigação: reajustar dentro de estratos de dificuldade comparáveis.
Resposta: log δ = log(exp_deg / exp_orig), pareado por instância.
"""
import sys, numpy as np, pandas as pd
sys.path.insert(0, str(__import__("pathlib").Path(__file__).parent))
from comum import *
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

rng = np.random.default_rng(SEED)
rob = carregar_robustez()

# ---------------------------------------------------------- formato longo
partes = []
mm = rob[rob.n_pivos == 10]                     # manh/form estão replicados nas 4 configs
for nome, col in [("manhattan", "delta_manh"), ("formula", "delta_form")]:
    p = mm[["mapa","semente","id_problema","tipo_degradacao","porcentagem_bloqueio",
            "path_orig_manh"]].copy()
    p["estrategia"], p["delta"] = nome, mm[col].values
    partes.append(p)
for n in (10, 20, 50, 100):
    s = rob[rob.n_pivos == n]
    p = s[["mapa","semente","id_problema","tipo_degradacao","porcentagem_bloqueio",
           "path_orig_manh"]].copy()
    p["estrategia"], p["delta"] = f"memory{n}", s.delta_mem.values
    partes.append(p)
lg = pd.concat(partes, ignore_index=True)
lg = lg[np.isfinite(lg.delta) & (lg.delta > 0)]
lg["log_delta"] = np.log(lg.delta)
lg = lg.rename(columns={"tipo_degradacao": "padrao", "porcentagem_bloqueio": "nivel"})
print(f"observações: {len(lg)}   ({lg.estrategia.nunique()} estratégias)")

def ajusta(df, rotulo):
    cel = (df.groupby(["mapa","semente","estrategia","padrao","nivel"])
             .log_delta.mean().reset_index())
    m = smf.ols("log_delta ~ C(estrategia)*C(padrao)*C(nivel) + C(mapa)", data=cel).fit()
    av = anova_lm(m, typ=2)
    ssr = av.loc["Residual", "sum_sq"]
    av["eta2_parcial"] = av.sum_sq / (av.sum_sq + ssr)
    av["eta2_total"] = av.sum_sq / av.sum_sq.sum()
    print(f"\n--- {rotulo}  (n_células={len(cel)}, R²={m.rsquared:.3f}) ---")
    print(av[["sum_sq","df","F","PR(>F)","eta2_parcial","eta2_total"]]
          .rename(columns={"PR(>F)":"p"}).round(4).to_string())
    return cel, av

print("\n=== 1. Modelo completo (todas as instâncias sobreviventes) ===")
cel, av = ajusta(lg, "todas as instâncias")
av.to_csv(TABELAS / "a1_anova_completa.csv")

# modelo misto como verificação do efeito aleatório por mapa
mm_ = smf.mixedlm("log_delta ~ C(estrategia)*C(padrao)*C(nivel)", data=cel,
                  groups=cel["mapa"]).fit(reml=False)
print(f"\nMixedLM (1|mapa): var(mapa)={mm_.cov_re.iloc[0,0]:.4f}  "
      f"var(resid)={mm_.scale:.4f}  ICC={mm_.cov_re.iloc[0,0]/(mm_.cov_re.iloc[0,0]+mm_.scale):.3f}")

# ---------------------------------------------- 2. estrato de dificuldade comum
print("\n=== 2. Reajuste em estrato de dificuldade comum (mitiga o viés do A10) ===")
q = lg.groupby("padrao").path_orig_manh.quantile([.1,.5,.9]).unstack()
print("comprimento ótimo do caminho, por padrão:"); print(q.round(1).to_string())
lo = lg.groupby("padrao").path_orig_manh.quantile(.10).max()
hi = lg.groupby("padrao").path_orig_manh.quantile(.90).min()
print(f"\nfaixa de suporte comum aos 5 padrões: [{lo:.0f}, {hi:.0f}] células")
est = lg[(lg.path_orig_manh >= lo) & (lg.path_orig_manh <= hi)]
print("instâncias por padrão no estrato:")
print((est[est.estrategia=="manhattan"].groupby("padrao").size()).to_string())
if est.groupby("padrao").size().min() > 30:
    cel_e, av_e = ajusta(est, f"estrato comum [{lo:.0f},{hi:.0f}]")
    av_e.to_csv(TABELAS / "a1_anova_estrato.csv")

# --------------------------------------- 3. teste de permutação da interação
print("\n=== 3. Teste de permutação da interação estratégia × padrão ===")
print("    (embaralha o rótulo de estratégia DENTRO de cada instância; válido")
print("     porque estratégia é fator intra-instância — mesmo par, mesmas 6 buscas)")

# matriz (instância x 6 estratégias): permutar = embaralhar cada linha
piv = lg.pivot_table(index=["mapa","semente","id_problema","padrao","nivel"],
                     columns="estrategia", values="log_delta")[CONFIGS].dropna()
M = piv.to_numpy()
idx = piv.index.to_frame(index=False)
# código de célula (mapa,semente,padrao,nivel) para agregar rápido
cod, _ = pd.factorize(pd.Series(list(zip(idx.mapa, idx.semente, idx.padrao, idx.nivel))))
ncel = cod.max() + 1
cnt = np.bincount(cod, minlength=ncel)
meta = idx.groupby(cod).first()

def F_de(M):
    """Média por célula para cada estratégia -> OLS -> F da interação."""
    somas = np.stack([np.bincount(cod, weights=M[:, j], minlength=ncel)
                      for j in range(M.shape[1])], axis=1) / cnt[:, None]
    c = pd.DataFrame(somas, columns=CONFIGS).assign(
        mapa=meta.mapa.values, semente=meta.semente.values,
        padrao=meta.padrao.values, nivel=meta.nivel.values)
    c = c.melt(id_vars=["mapa","semente","padrao","nivel"],
               var_name="estrategia", value_name="log_delta")
    m = smf.ols("log_delta ~ C(estrategia)*C(padrao)*C(nivel) + C(mapa)", data=c).fit()
    return anova_lm(m, typ=2).loc["C(estrategia):C(padrao)", "F"]

F_obs = F_de(M)
NPERM = 200
nulos = np.empty(NPERM)
for b in range(NPERM):
    ordem = rng.random(M.shape).argsort(axis=1)          # permuta cada linha
    nulos[b] = F_de(np.take_along_axis(M, ordem, axis=1))
p_perm = (1 + (nulos >= F_obs).sum()) / (1 + NPERM)
print(f"  F observado = {F_obs:.2f}   |   nulo: mediana {np.median(nulos):.2f}, "
      f"máx {nulos.max():.2f}   |   p = {p_perm:.4f} ({NPERM} permutações, seed {SEED})")

# ------------------------------------------------- 4. hierarquia por padrão
print("\n=== 4. δ mediano por estratégia e padrão (30% de bloqueio) ===")
d30 = lg[lg.nivel == 0.3]
tab = (d30.groupby(["padrao","estrategia"]).log_delta.mean().apply(np.exp)
       .unstack()[CONFIGS])
print(tab.round(2).to_string())
tab.to_csv(TABELAS / "a1_delta_por_padrao.csv")
print("\n--- postos dentro de cada padrão (1 = menos degradada) ---")
postos = tab.rank(axis=1)
print(postos.astype(int).to_string())
print("\nA interação NÃO é troca de vencedor — a fórmula é a menos degradada nos 5")
print("padrões. É a reordenação das DEMAIS estratégias, e a amplitude do efeito:")
for c in CONFIGS:
    print(f"  {ROTULOS[c]:<12}: posto varia de {int(postos[c].min())} a "
          f"{int(postos[c].max())};  δ de {tab[c].min():.2f} a {tab[c].max():.2f} "
          f"({tab[c].max()/tab[c].min():.1f}x conforme o padrão)")
