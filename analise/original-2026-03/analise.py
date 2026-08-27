"""
analise.py — Análise completa dos experimentos ETC 2026
────────────────────────────────────────────────────────
Gera todas as métricas necessárias para o artigo a partir dos quatro CSVs:
  - resultados_base.csv
  - resultados_robustez.csv
  - resultados_ratio.csv
  - resultados_sintese.csv

Todas as métricas com múltiplas sementes reportam média ± desvio padrão.
A unidade de agregação é sempre (mapa × semente) antes de agregar para o global.
"""

import pandas as pd
import numpy as np

SEP = "─" * 90

# ── CARREGAMENTO ──────────────────────────────────────────────────────────────

def carregar():
    try:
        base     = pd.read_csv("resultados_base.csv")
        robustez = pd.read_csv("resultados_robustez.csv")
        ratio    = pd.read_csv("resultados_ratio.csv")
        sintese  = pd.read_csv("resultados_sintese.csv")
    except FileNotFoundError as e:
        print(f"Erro ao carregar: {e}")
        raise
    return base, robustez, ratio, sintese


# ── UTILITÁRIOS ───────────────────────────────────────────────────────────────

def pm(media, std, casas=2):
    """Formata 'média ± std'."""
    fmt = f"{{:.{casas}f}}"
    return f"{fmt.format(media)} ± {fmt.format(std)}"


def agregar_sementes(df, group_cols, value_col):
    """
    Agrega em dois passos:
      1. Média por (group_cols + semente) — colapsa instâncias dentro de cada semente
      2. Média e std sobre as sementes — reporta variabilidade entre sementes
    """
    passo1 = df.groupby(group_cols + ["semente"])[value_col].mean().reset_index()
    if group_cols:
        passo2 = passo1.groupby(group_cols)[value_col].agg(["mean", "std"]).reset_index()
        passo2.columns = list(group_cols) + ["media", "std"]
    else:
        passo2 = pd.DataFrame({
            "media": [passo1[value_col].mean()],
            "std":   [passo1[value_col].std(ddof=1) if len(passo1) > 1 else 0.0]
        })
    return passo2


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — DESEMPENHO ESTÁTICO
# Manhattan e Fórmula: resultados_base.csv
# Memória: colunas exp_orig_mem / tempo_orig_mem_ms de resultados_robustez.csv
# Para a Tabela 1 do artigo
# ══════════════════════════════════════════════════════════════════════════════

def bloco_estatico(base, robustez):
    print(f"\n{'BLOCO 1 — DESEMPENHO ESTÁTICO (Tabela 1)':^90}")
    print(SEP)
    print(f"\n  Manhattan e Fórmula: resultados_base.csv")
    print(f"  Memória: colunas exp_orig_mem / tempo_orig_mem_ms de resultados_robustez.csv\n")

    manh_s = (base[base["heuristica"] == "manhattan"]
              .groupby("semente")["expansoes"].mean())
    manh_global = manh_s.mean()

    print(f"{'Heurística':<22} {'Expansões (média ± std)':>26} {'Tempo ms (média ± std)':>26} {'Speedup expansões':>18}")
    print(f"{'':─<22} {'':─<26} {'':─<26} {'':─<18}")

    resultados = []

    # Manhattan e Fórmula — base.csv
    for heur, label in [("manhattan", "Manhattan"), ("formula", "Fórmula")]:
        sub = base[base["heuristica"] == heur]
        exp = agregar_sementes(sub, [], "expansoes")
        tmp = agregar_sementes(sub, [], "tempo_ms")
        sp_por_semente = [manh_s[s] / sub[sub["semente"] == s]["expansoes"].mean()
                          for s in sub["semente"].unique() if s in manh_s.index]
        sp_media = np.mean(sp_por_semente)
        sp_std   = np.std(sp_por_semente, ddof=1) if len(sp_por_semente) > 1 else 0.0
        print(f"{label:<22} {pm(exp['media'].iloc[0], exp['std'].iloc[0]):>26} "
              f"{pm(tmp['media'].iloc[0], tmp['std'].iloc[0]):>26} "
              f"{pm(sp_media, sp_std):>18}")
        resultados.append({"heuristica": label,
                           "exp_media": exp["media"].iloc[0], "exp_std": exp["std"].iloc[0],
                           "tempo_media": tmp["media"].iloc[0], "tempo_std": tmp["std"].iloc[0],
                           "speedup_media": sp_media, "speedup_std": sp_std})

    # Memória — colunas orig do robustez (execução no mapa original, antes da degradação)
    # drop_duplicates: uma linha por (mapa, semente, id_problema, n_pivos)
    rob_orig = robustez.drop_duplicates(
        subset=["mapa", "semente", "id_problema", "n_pivos"]
    ).copy()

    # Exclusão pontual: brc000d com 50 pivôs apresenta valores aberrantes nas
    # sementes 123 e 789 (~14k e ~12k expansões vs ~180 nas demais), causados
    # por sorteio desfavorável de pivôs pelo Farthest-First nesse mapa/semente.
    # As outras contagens de pivôs para brc000d são normais e mantidas.
    rob_orig = rob_orig[~((rob_orig["mapa"] == "brc000d") & (rob_orig["n_pivos"] == 50))]
    print(f"  [Aviso] brc000d/50 pivôs excluído da agregação estática (outlier de sorteio de pivôs).\n")

    for n in [10, 20, 50, 100]:
        label = f"Memória ({n} pivôs)"
        sub   = rob_orig[rob_orig["n_pivos"] == n]
        exp   = agregar_sementes(sub, [], "exp_orig_mem")
        tmp   = agregar_sementes(sub, [], "tempo_orig_mem_ms")
        sp_por_semente = [manh_s[s] / sub[sub["semente"] == s]["exp_orig_mem"].mean()
                          for s in sub["semente"].unique() if s in manh_s.index]
        sp_media = np.mean(sp_por_semente)
        sp_std   = np.std(sp_por_semente, ddof=1) if len(sp_por_semente) > 1 else 0.0
        print(f"{label:<22} {pm(exp['media'].iloc[0], exp['std'].iloc[0]):>26} "
              f"{pm(tmp['media'].iloc[0], tmp['std'].iloc[0]):>26} "
              f"{pm(sp_media, sp_std):>18}")
        resultados.append({"heuristica": label,
                           "exp_media": exp["media"].iloc[0], "exp_std": exp["std"].iloc[0],
                           "tempo_media": tmp["media"].iloc[0], "tempo_std": tmp["std"].iloc[0],
                           "speedup_media": sp_media, "speedup_std": sp_std})

    print(f"\n  Speedup = razão de expansões médias (Manhattan / heurística).")
    print(f"  Média global Manhattan: {manh_global:.2f} expansões.")
    return pd.DataFrame(resultados)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — FATOR DE DEGRADAÇÃO EM 30%
# ══════════════════════════════════════════════════════════════════════════════

def bloco_degradacao_30(robustez):
    print(f"\n\n{'BLOCO 2 — FATOR DE DEGRADAÇÃO EM 30% (valores para o texto)':^90}")
    print(SEP)

    rob30 = robustez[robustez["porcentagem_bloqueio"] == 0.3].copy()
    rob30["fator_manh"] = rob30["exp_deg_manh"] / rob30["exp_orig_manh"]
    rob30["fator_form"] = rob30["exp_deg_form"] / rob30["exp_orig_form"]
    rob30["fator_mem"]  = rob30["exp_deg_mem"]  / rob30["exp_orig_mem"]

    tipos = ["Linear", "Organic", "Radial", "Sparse", "Stochastic"]
    nomes = {"Linear": "Linear", "Organic": "Orgânico", "Radial": "Radial",
             "Sparse": "Esparso", "Stochastic": "Estocástico"}
    pivos_mem = [10, 20, 50, 100]

    print(f"\n  {'Tipo':<12} {'Manhattan':>20} {'Fórmula':>20}", end="")
    for n in pivos_mem:
        print(f" {'Mem-'+str(n)+' pivôs':>20}", end="")
    print()
    print(f"  {'':─<12} {'':─<20} {'':─<20}", end="")
    for _ in pivos_mem:
        print(f" {'':─<20}", end="")
    print()

    resultado_tipos = []
    for tipo in tipos:
        sub = rob30[rob30["tipo_degradacao"] == tipo]
        fa = agregar_sementes(sub[sub["n_pivos"] == pivos_mem[0]], [], "fator_manh")
        ff = agregar_sementes(sub[sub["n_pivos"] == pivos_mem[0]], [], "fator_form")
        linha = {"tipo": nomes[tipo],
                 "manh_media": fa["media"].iloc[0], "manh_std": fa["std"].iloc[0],
                 "form_media": ff["media"].iloc[0], "form_std": ff["std"].iloc[0]}
        print(f"  {nomes[tipo]:<12} {pm(fa['media'].iloc[0], fa['std'].iloc[0]):>20} "
              f"{pm(ff['media'].iloc[0], ff['std'].iloc[0]):>20}", end="")
        for n in pivos_mem:
            fm = agregar_sementes(sub[sub["n_pivos"] == n], [], "fator_mem")
            linha[f"mem{n}_media"] = fm["media"].iloc[0]
            linha[f"mem{n}_std"]   = fm["std"].iloc[0]
            print(f" {pm(fm['media'].iloc[0], fm['std'].iloc[0]):>20}", end="")
        print()
        resultado_tipos.append(linha)

    return pd.DataFrame(resultado_tipos)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — CURVA DE DEGRADAÇÃO (10%, 20%, 30%)
# ══════════════════════════════════════════════════════════════════════════════

def bloco_curva_degradacao(robustez):
    print(f"\n\n{'BLOCO 3 — CURVA DE DEGRADAÇÃO POR NÍVEL (verificação da Figura 1)':^90}")
    print(SEP)

    rob = robustez.copy()
    rob["fator_manh"] = rob["exp_deg_manh"] / rob["exp_orig_manh"]
    rob["fator_form"] = rob["exp_deg_form"] / rob["exp_orig_form"]
    rob["fator_mem"]  = rob["exp_deg_mem"]  / rob["exp_orig_mem"]

    tipos = ["Linear", "Organic", "Radial", "Sparse", "Stochastic"]
    nomes = {"Linear": "Linear", "Organic": "Orgânico", "Radial": "Radial",
             "Sparse": "Esparso", "Stochastic": "Estocástico"}

    for tipo in tipos:
        print(f"\n  {nomes[tipo]}")
        print(f"  {'Bloqueio':<10} {'Manhattan':>20} {'Fórmula':>20} "
              f"{'Mem-10':>16} {'Mem-50':>16} {'Mem-100':>16}")
        print(f"  {'':─<10} {'':─<20} {'':─<20} {'':─<16} {'':─<16} {'':─<16}")

        sub_tipo = rob[rob["tipo_degradacao"] == tipo]
        for p in [0.1, 0.2, 0.3]:
            sub  = sub_tipo[sub_tipo["porcentagem_bloqueio"] == p]
            fa   = agregar_sementes(sub[sub["n_pivos"] == 10],  [], "fator_manh")
            ff   = agregar_sementes(sub[sub["n_pivos"] == 10],  [], "fator_form")
            f10  = agregar_sementes(sub[sub["n_pivos"] == 10],  [], "fator_mem")
            f50  = agregar_sementes(sub[sub["n_pivos"] == 50],  [], "fator_mem")
            f100 = agregar_sementes(sub[sub["n_pivos"] == 100], [], "fator_mem")
            print(f"  {int(p*100):>3}%       "
                  f"{pm(fa['media'].iloc[0],   fa['std'].iloc[0]):>20} "
                  f"{pm(ff['media'].iloc[0],   ff['std'].iloc[0]):>20} "
                  f"{pm(f10['media'].iloc[0],  f10['std'].iloc[0]):>16} "
                  f"{pm(f50['media'].iloc[0],  f50['std'].iloc[0]):>16} "
                  f"{pm(f100['media'].iloc[0], f100['std'].iloc[0]):>16}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — QUALIDADE DO CAMINHO (ratio vs Dijkstra)
# ══════════════════════════════════════════════════════════════════════════════

def bloco_ratio(ratio):
    print(f"\n\n{'BLOCO 4 — QUALIDADE DO CAMINHO (ratio fórmula / ótimo Dijkstra)':^90}")
    print(SEP)

    agg = agregar_sementes(ratio, [], "ratio")
    subopt     = (agg["media"].iloc[0] - 1.0) * 100
    subopt_std = agg["std"].iloc[0] * 100

    print(f"\n  Ratio médio global : {pm(agg['media'].iloc[0], agg['std'].iloc[0], casas=4)}")
    print(f"  Sub-otimalidade    : {pm(subopt, subopt_std, casas=4)} %")
    print(f"  (ratio = 1,0000 indica caminho ótimo)")

    print(f"\n  Ratio por mapa (média ± std sobre sementes):")
    print(f"  {'Mapa':<12} {'Ratio':>20} {'Sub-otimalidade (%)':>22}")
    print(f"  {'':─<12} {'':─<20} {'':─<22}")

    por_mapa = agregar_sementes(ratio, ["mapa"], "ratio")
    for _, row in por_mapa.sort_values("media", ascending=False).iterrows():
        subopt_m = (row["media"] - 1.0) * 100
        subopt_s = row["std"] * 100
        print(f"  {row['mapa']:<12} {pm(row['media'], row['std'], casas=4):>20} "
              f"{pm(subopt_m, subopt_s, casas=4):>22}")

    return agg


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — SÍNTESE DA FÓRMULA
# ══════════════════════════════════════════════════════════════════════════════

def bloco_sintese(sintese):
    print(f"\n\n{'BLOCO 5 — SÍNTESE DA FÓRMULA (custo de pré-processamento)':^90}")
    print(SEP)

    # Remove duplicata de arena (duas linhas idênticas no CSV)
    sintese_uniq = sintese.drop_duplicates(subset=["mapa"]).copy()

    print(f"\n  {'Mapa':<12} {'Tempo síntese (ms)':>20} {'Fitness final':>16} {'Fórmula'}")
    print(f"  {'':─<12} {'':─<20} {'':─<16} {'':─<40}")

    for _, row in sintese_uniq.sort_values("tempo_sintese_ms", ascending=False).iterrows():
        formula = str(row["formula_string"])[:45]
        print(f"  {row['mapa']:<12} {row['tempo_sintese_ms']:>20.1f} "
              f"{row['fitness_final']:>16.4f}   {formula}")

    print(f"\n  Tempo médio de síntese : {sintese_uniq['tempo_sintese_ms'].mean():.1f} ms")
    print(f"  Tempo total de síntese : {sintese_uniq['tempo_sintese_ms'].sum():.1f} ms "
          f"({sintese_uniq['tempo_sintese_ms'].sum()/1000:.1f} s)")
    print(f"  Fitness médio final    : {sintese_uniq['fitness_final'].mean():.4f} ± "
          f"{sintese_uniq['fitness_final'].std():.4f}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — MEMÓRIA DE ARMAZENAMENTO (estimativa)
# ══════════════════════════════════════════════════════════════════════════════

def bloco_memoria(base, pivos_list=(10, 20, 50, 100)):
    print(f"\n\n{'BLOCO 6 — ESTIMATIVA DE ARMAZENAMENTO (heurística de memória)':^90}")
    print(SEP)
    print(f"\n  Fórmula: células_ativas × n_pivôs × 4 bytes (float)")
    print(f"\n  {'Mapa':<12}", end="")
    for n in pivos_list:
        print(f" {'Mem-'+str(n)+' (KB)':>14}", end="")
    print()
    print(f"  {'':─<12}", end="")
    for _ in pivos_list:
        print(f" {'':─<14}", end="")
    print()

    manh = (base[base["heuristica"] == "manhattan"]
            .groupby(["mapa", "semente"])["expansoes"].max()
            .groupby("mapa").mean())

    for mapa, max_exp in manh.sort_values(ascending=False).items():
        print(f"  {mapa:<12}", end="")
        for n in pivos_list:
            kb = (max_exp * n * 4) / 1024
            print(f" {kb:>13.1f}K", end="")
        print()

    print(f"\n  Nota: estimativa baseada no máximo de expansões observado por mapa.")
    print(f"  Para valores exatos, use as dimensões do arquivo .map correspondente.")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 7 — RESUMO PARA O ARTIGO
# ══════════════════════════════════════════════════════════════════════════════

def bloco_resumo(df_estatico, df_deg30, df_ratio):
    print(f"\n\n{'BLOCO 7 — NÚMEROS PARA O TEXTO DO ARTIGO':^90}")
    print(SEP)

    print("\n  ── Tabela 1 (desempenho estático) ──")
    for _, row in df_estatico.iterrows():
        print(f"  {row['heuristica']:<22}: "
              f"expansões = {row['exp_media']:.2f} ± {row['exp_std']:.2f}, "
              f"tempo = {row['tempo_media']:.3f} ± {row['tempo_std']:.3f} ms, "
              f"speedup = {row['speedup_media']:.2f}×")

    print("\n  ── Fator de degradação em 30% (Figura 1 / texto Seção 3) ──")
    for _, row in df_deg30.iterrows():
        print(f"  {row['tipo']:<12}: "
              f"Manh = {row['manh_media']:.2f} ± {row['manh_std']:.2f}, "
              f"Form = {row['form_media']:.2f} ± {row['form_std']:.2f}, "
              f"Mem-10 = {row['mem10_media']:.2f} ± {row['mem10_std']:.2f}, "
              f"Mem-50 = {row['mem50_media']:.2f} ± {row['mem50_std']:.2f}, "
              f"Mem-100 = {row['mem100_media']:.2f} ± {row['mem100_std']:.2f}")

    print("\n  ── Qualidade do caminho ──")
    subopt = (df_ratio["media"].iloc[0] - 1.0) * 100
    print(f"  Ratio médio: {df_ratio['media'].iloc[0]:.4f} "
          f"(sub-otimalidade de {subopt:.2f}%)")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 90)
    print(f"{'ANÁLISE EXPERIMENTAL — ETC 2026':^90}")
    print("=" * 90)

    base, robustez, ratio, sintese = carregar()

    print(f"\n  Sementes presentes : {sorted(base['semente'].unique())}")
    print(f"  Mapas              : {base['mapa'].nunique()} ({sorted(base['mapa'].unique())})")
    print(f"  Linhas base        : {len(base):,}")
    print(f"  Linhas robustez    : {len(robustez):,}")
    print(f"  Linhas ratio       : {len(ratio):,}")

    df_estatico = bloco_estatico(base, robustez)
    df_deg30    = bloco_degradacao_30(robustez)
    bloco_curva_degradacao(robustez)
    df_ratio    = bloco_ratio(ratio)
    bloco_sintese(sintese)
    bloco_memoria(base)
    bloco_resumo(df_estatico, df_deg30, df_ratio)

    print(f"\n{'=' * 90}")
    print(f"{'Análise concluída.':^90}")
    print(f"{'=' * 90}\n")
