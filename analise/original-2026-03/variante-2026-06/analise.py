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

SEP = "─" * 120

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
    if pd.isna(media): return "N/A"
    fmt = f"{{:.{casas}f}}"
    return f"{fmt.format(media)} ± {fmt.format(std)}"

def agregar_sementes(df, group_cols, value_col):
    """
    Agrega em dois passos:
      1. Média por (group_cols + semente) — colapsa instâncias dentro de cada semente
      2. Média e std sobre as sementes — reporta variabilidade entre sementes
    """
    if df.empty:
        if group_cols:
            return pd.DataFrame(columns=list(group_cols) + ["media", "std"])
        return pd.DataFrame({"media": [np.nan], "std": [np.nan]})
        
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

def extrair_modos(df):
    if "modo" in df.columns:
        return sorted([m for m in df["modo"].unique() if pd.notna(m)])
    return []

# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 1 — DESEMPENHO ESTÁTICO
# ══════════════════════════════════════════════════════════════════════════════
def bloco_estatico(base, robustez):
    print(f"\n{'BLOCO 1 — DESEMPENHO ESTÁTICO (Tabela 1)':^120}")
    print(SEP)
    
    manh_s = (base[base["heuristica"] == "manhattan"]
              .groupby("semente")["expansoes"].mean())
    manh_global = manh_s.mean() if not manh_s.empty else np.nan

    print(f"{'Heurística (Modo)':<30} {'Expansões (média ± std)':>26} {'Tempo ms (média ± std)':>26} {'Speedup expansões':>18}")
    print(f"{'':─<30} {'':─<26} {'':─<26} {'':─<18}")

    resultados = []

    # Manhattan
    sub = base[base["heuristica"] == "manhattan"]
    if not sub.empty:
        exp = agregar_sementes(sub, [], "expansoes")
        tmp = agregar_sementes(sub, [], "tempo_ms")
        print(f"{'Manhattan':<30} {pm(exp['media'].iloc[0], exp['std'].iloc[0]):>26} "
              f"{pm(tmp['media'].iloc[0], tmp['std'].iloc[0]):>26} {'1.00 ± 0.00':>18}")
        resultados.append({"heuristica": "Manhattan", "modo": "N/A", "exp_media": exp['media'].iloc[0], "exp_std": exp['std'].iloc[0]})

    # Fórmula
    sub_form = base[base["heuristica"] == "formula"]
    if not sub_form.empty:
        modos = extrair_modos(sub_form) or ["N/A"]
        for m in modos:
            sf = sub_form[sub_form["modo"] == m] if m != "N/A" else sub_form
            if sf.empty: continue
            exp = agregar_sementes(sf, [], "expansoes")
            tmp = agregar_sementes(sf, [], "tempo_ms")
            
            sp_por_semente = [manh_s.get(s, np.nan) / sf[sf["semente"] == s]["expansoes"].mean()
                              for s in sf["semente"].unique() if s in manh_s.index]
            sp_media = np.nanmean(sp_por_semente) if sp_por_semente else np.nan
            sp_std   = np.nanstd(sp_por_semente, ddof=1) if len(sp_por_semente) > 1 else 0.0
            
            label = f"Fórmula ({m})"
            print(f"{label:<30} {pm(exp['media'].iloc[0], exp['std'].iloc[0]):>26} "
                  f"{pm(tmp['media'].iloc[0], tmp['std'].iloc[0]):>26} "
                  f"{pm(sp_media, sp_std):>18}")
            resultados.append({"heuristica": "Fórmula", "modo": m, "exp_media": exp['media'].iloc[0], "exp_std": exp['std'].iloc[0]})

    # Memória
    if "n_pivos" in robustez.columns:
        rob_orig = robustez.drop_duplicates(
            subset=["mapa", "semente", "id_problema", "n_pivos"]
        ).copy()
        rob_orig = rob_orig[~((rob_orig["mapa"] == "brc000d") & (rob_orig["n_pivos"] == 50))]

        for n in [10, 20, 50, 100]:
            label = f"Memória ({n} pivôs)"
            sub   = rob_orig[rob_orig["n_pivos"] == n]
            if sub.empty: continue
            exp   = agregar_sementes(sub, [], "exp_orig_mem")
            tmp   = agregar_sementes(sub, [], "tempo_orig_mem_ms")
            sp_por_semente = [manh_s.get(s, np.nan) / sub[sub["semente"] == s]["exp_orig_mem"].mean()
                              for s in sub["semente"].unique() if s in manh_s.index]
            sp_media = np.nanmean(sp_por_semente) if sp_por_semente else np.nan
            sp_std   = np.nanstd(sp_por_semente, ddof=1) if len(sp_por_semente) > 1 else 0.0
            print(f"{label:<30} {pm(exp['media'].iloc[0], exp['std'].iloc[0]):>26} "
                  f"{pm(tmp['media'].iloc[0], tmp['std'].iloc[0]):>26} "
                  f"{pm(sp_media, sp_std):>18}")
            resultados.append({"heuristica": label, "modo": "N/A", "exp_media": exp['media'].iloc[0], "exp_std": exp['std'].iloc[0]})

    return pd.DataFrame(resultados)


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 2 — FATOR DE DEGRADAÇÃO EM 30%
# ══════════════════════════════════════════════════════════════════════════════
def bloco_degradacao_30(robustez):
    print(f"\n\n{'BLOCO 2 — FATOR DE DEGRADAÇÃO EM 30%':^120}")
    print(SEP)

    rob30 = robustez[robustez["porcentagem_bloqueio"] == 0.3].copy()
    if rob30.empty:
        print("Sem dados para 30% de bloqueio.")
        return pd.DataFrame()

    rob30["fator_manh"] = rob30["exp_deg_manh"] / rob30["exp_orig_manh"]
    rob30["fator_form"] = rob30["exp_deg_form"] / rob30["exp_orig_form"]
    rob30["fator_mem"]  = rob30["exp_deg_mem"]  / rob30["exp_orig_mem"]

    tipos = ["Linear", "Organic", "Radial", "Sparse", "Stochastic"]
    nomes = {"Linear": "Linear", "Organic": "Orgânico", "Radial": "Radial",
             "Sparse": "Esparso", "Stochastic": "Estocástico"}
    pivos_mem = [10, 20, 50, 100]

    modos = extrair_modos(rob30) or ["N/A"]

    for m in modos:
        print(f"\n  Modo: {m}")
        print(f"  {'Tipo':<12} {'Manhattan':>20} {'Fórmula':>20}", end="")
        for n in pivos_mem:
            print(f" {'Mem-'+str(n):>18}", end="")
        print()
        
        rob30_m = rob30[rob30.get("modo", "") == m] if m != "N/A" else rob30
        
        for tipo in tipos:
            sub = rob30_m[rob30_m["tipo_degradacao"] == tipo]
            if sub.empty: continue
            
            s_pivos = sub[sub["n_pivos"] == pivos_mem[0]]
            if s_pivos.empty: continue
            
            fa = agregar_sementes(s_pivos, [], "fator_manh")
            ff = agregar_sementes(s_pivos, [], "fator_form")
            
            print(f"  {nomes.get(tipo, tipo):<12} {pm(fa['media'].iloc[0], fa['std'].iloc[0]):>20} "
                  f"{pm(ff['media'].iloc[0], ff['std'].iloc[0]):>20}", end="")
            for n in pivos_mem:
                fm = agregar_sementes(sub[sub["n_pivos"] == n], [], "fator_mem")
                if fm.empty:
                    print(f" {'N/A':>18}", end="")
                else:
                    print(f" {pm(fm['media'].iloc[0], fm['std'].iloc[0]):>18}", end="")
            print()

    return rob30


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 3 — CURVA DE DEGRADAÇÃO (10%, 20%, 30%)
# ══════════════════════════════════════════════════════════════════════════════
def bloco_curva_degradacao(robustez):
    print(f"\n\n{'BLOCO 3 — CURVA DE DEGRADAÇÃO POR NÍVEL':^120}")
    print(SEP)

    rob = robustez.copy()
    if rob.empty: return
    rob["fator_manh"] = rob["exp_deg_manh"] / rob["exp_orig_manh"]
    rob["fator_form"] = rob["exp_deg_form"] / rob["exp_orig_form"]
    rob["fator_mem"]  = rob["exp_deg_mem"]  / rob["exp_orig_mem"]

    tipos = ["Linear", "Organic", "Radial", "Sparse", "Stochastic"]
    modos = extrair_modos(rob) or ["N/A"]

    for m in modos:
        print(f"\n  Modo: {m}")
        rob_m = rob[rob.get("modo", "") == m] if m != "N/A" else rob
        for tipo in tipos:
            sub_tipo = rob_m[rob_m["tipo_degradacao"] == tipo]
            if sub_tipo.empty: continue
            
            print(f"  Tipo: {tipo}")
            print(f"  {'Bloq.':<8} {'Manhattan':>20} {'Fórmula':>20} "
                  f"{'Mem-10':>18} {'Mem-50':>18} {'Mem-100':>18}")
            
            for p in [0.1, 0.2, 0.3]:
                sub = sub_tipo[sub_tipo["porcentagem_bloqueio"] == p]
                if sub.empty: continue
                
                s10 = sub[sub["n_pivos"] == 10]
                if s10.empty: continue
                fa   = agregar_sementes(s10, [], "fator_manh")
                ff   = agregar_sementes(s10, [], "fator_form")
                f10  = agregar_sementes(s10, [], "fator_mem")
                f50  = agregar_sementes(sub[sub["n_pivos"] == 50],  [], "fator_mem")
                f100 = agregar_sementes(sub[sub["n_pivos"] == 100], [], "fator_mem")
                
                val_fa = pm(fa['media'].iloc[0], fa['std'].iloc[0]) if not fa.empty else "N/A"
                val_ff = pm(ff['media'].iloc[0], ff['std'].iloc[0]) if not ff.empty else "N/A"
                val_f10 = pm(f10['media'].iloc[0], f10['std'].iloc[0]) if not f10.empty else "N/A"
                val_f50 = pm(f50['media'].iloc[0], f50['std'].iloc[0]) if not f50.empty else "N/A"
                val_f100 = pm(f100['media'].iloc[0], f100['std'].iloc[0]) if not f100.empty else "N/A"

                print(f"  {int(p*100):>3}%   "
                      f"{val_fa:>20} {val_ff:>20} "
                      f"{val_f10:>18} {val_f50:>18} {val_f100:>18}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 4 — QUALIDADE DO CAMINHO (ratio vs Dijkstra)
# ══════════════════════════════════════════════════════════════════════════════
def bloco_ratio(ratio):
    print(f"\n\n{'BLOCO 4 — QUALIDADE DO CAMINHO (ratio fórmula / ótimo Dijkstra)':^120}")
    print(SEP)

    if ratio.empty: return ratio
    modos = extrair_modos(ratio) or ["N/A"]

    for m in modos:
        rm = ratio[ratio.get("modo", "") == m] if m != "N/A" else ratio
        if rm.empty: continue
        
        agg = agregar_sementes(rm, [], "ratio")
        if agg.empty: continue
        subopt     = (agg["media"].iloc[0] - 1.0) * 100
        subopt_std = agg["std"].iloc[0] * 100

        print(f"\n  Modo: {m}")
        print(f"  Ratio médio global : {pm(agg['media'].iloc[0], agg['std'].iloc[0], casas=4)}")
        print(f"  Sub-otimalidade    : {pm(subopt, subopt_std, casas=4)} %")
        
        por_mapa = agregar_sementes(rm, ["mapa"], "ratio")
        print(f"  {'Mapa':<12} {'Ratio':>20} {'Sub-otimalidade (%)':>22}")
        for _, row in por_mapa.sort_values("media", ascending=False).iterrows():
            subopt_m = (row["media"] - 1.0) * 100
            subopt_s = row["std"] * 100
            print(f"  {row['mapa']:<12} {pm(row['media'], row['std'], casas=4):>20} "
                  f"{pm(subopt_m, subopt_s, casas=4):>22}")

    return ratio


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 5 — SÍNTESE DA FÓRMULA
# ══════════════════════════════════════════════════════════════════════════════
def bloco_sintese(sintese):
    print(f"\n\n{'BLOCO 5 — SÍNTESE DA FÓRMULA':^120}")
    print(SEP)

    if sintese.empty: return

    modos = extrair_modos(sintese) or ["N/A"]
    
    for m in modos:
        sm = sintese[sintese.get("modo", "") == m] if m != "N/A" else sintese
        if sm.empty: continue
        
        sm_uniq = sm.drop_duplicates(subset=["mapa"]).copy()
        
        print(f"\n  Modo: {m}")
        has_sa = "tempo_sa_ms" in sm.columns
        
        if has_sa:
            print(f"  {'Mapa':<12} {'SA (ms)':>10} {'Admiss %':>10} {'Fórmula Pós SA':<40} {'Fórmula Pré SA'}")
            print(f"  {'':─<12} {'':─<10} {'':─<10} {'':─<40} {'':─<40}")
        else:
            print(f"  {'Mapa':<12} {'Sintese (ms)':>15} {'Fitness':>10} {'Fórmula'}")
            print(f"  {'':─<12} {'':─<15} {'':─<10} {'':─<70}")

        for _, row in sm_uniq.iterrows():
            if has_sa:
                form_pos = str(row.get("formula_pos_sa", ""))[:38]
                form_pre = str(row.get("formula_pre_sa", ""))[:38]
                print(f"  {row['mapa']:<12} {row.get('tempo_sa_ms', 0):>10.1f} "
                      f"{row.get('admissibility_rate', 0)*100:>9.1f}%  {form_pos:<40} {form_pre}")
            else:
                formula = str(row.get("formula_string", ""))[:65]
                print(f"  {row['mapa']:<12} {row.get('tempo_sintese_ms', 0):>15.1f} "
                      f"{row.get('fitness_final', 0):>10.4f}  {formula}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 6 — MEMÓRIA DE ARMAZENAMENTO (estimativa)
# ══════════════════════════════════════════════════════════════════════════════
def bloco_memoria(base, pivos_list=(10, 20, 50, 100)):
    print(f"\n\n{'BLOCO 6 — ESTIMATIVA DE ARMAZENAMENTO':^120}")
    print(SEP)

    manh = base[base["heuristica"] == "manhattan"]
    if manh.empty: return

    manh_max = manh.groupby(["mapa", "semente"])["expansoes"].max().groupby("mapa").mean()

    print(f"\n  {'Mapa':<12}", end="")
    for n in pivos_list: print(f" {'Mem-'+str(n)+' (KB)':>14}", end="")
    print()
    
    for mapa, max_exp in manh_max.sort_values(ascending=False).items():
        print(f"  {mapa:<12}", end="")
        for n in pivos_list:
            kb = (max_exp * n * 4) / 1024
            print(f" {kb:>13.1f}K", end="")
        print()


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 8 — COMPARAÇÃO TERMINAIS (absolute vs delta)
# ══════════════════════════════════════════════════════════════════════════════
def bloco_comparacao_terminais(base, robustez, ratio):
    print(f"\n\n{'BLOCO 8 — COMPARAÇÃO TERMINAIS (absolute vs delta)':^120}")
    print(SEP)
    
    modos_alvo = ["absolute", "delta"]
    
    print("\n  ── Média Global de Expansões (Formula) ──")
    for m in modos_alvo:
        sub = base[(base["heuristica"] == "formula") & (base.get("modo", "") == m)]
        if not sub.empty:
            exp = agregar_sementes(sub, [], "expansoes")
            print(f"  Modo {m:<10} : {pm(exp['media'].iloc[0], exp['std'].iloc[0])}")

    print("\n  ── Qualidade do Caminho (Ratio) ──")
    for m in modos_alvo:
        sub = ratio[ratio.get("modo", "") == m]
        if not sub.empty:
            agg = agregar_sementes(sub, [], "ratio")
            print(f"  Modo {m:<10} : {pm(agg['media'].iloc[0], agg['std'].iloc[0], casas=4)}")

    print("\n  ── Fator de Degradação (30%) ──")
    if not robustez.empty:
        rob30 = robustez[robustez.get("porcentagem_bloqueio", 0) == 0.3].copy()
        if not rob30.empty:
            rob30["fator_form"] = rob30["exp_deg_form"] / rob30["exp_orig_form"]
            for m in modos_alvo:
                sub = rob30[rob30.get("modo", "") == m]
                if not sub.empty:
                    ff = agregar_sementes(sub, [], "fator_form")
                    print(f"  Modo {m:<10} : {pm(ff['media'].iloc[0], ff['std'].iloc[0])}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 9 — ADMISSIBILIDADE
# ══════════════════════════════════════════════════════════════════════════════
def bloco_admissibilidade(ratio, sintese):
    print(f"\n\n{'BLOCO 9 — ADMISSIBILIDADE (admissibility vs delta)':^120}")
    print(SEP)
    
    print("\n  ── Taxa de Admissibilidade Global ──")
    for m in ["admissibility", "delta"]:
        sub = sintese[sintese.get("modo", "") == m]
        if not sub.empty and "admissibility_rate" in sub.columns:
            taxa = sub["admissibility_rate"].mean() * 100
            print(f"  Modo {m:<15} : {taxa:.2f}%")

    print("\n  ── Qualidade do Caminho (Ratio) ──")
    for m in ["admissibility", "delta"]:
        sub = ratio[ratio.get("modo", "") == m]
        if not sub.empty:
            agg = agregar_sementes(sub, [], "ratio")
            print(f"  Modo {m:<15} : {pm(agg['media'].iloc[0], agg['std'].iloc[0], casas=4)}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 10 — HÍBRIDO
# ══════════════════════════════════════════════════════════════════════════════
def bloco_hibrido(base, robustez, ratio):
    print(f"\n\n{'BLOCO 10 — HÍBRIDO (hybrid vs delta vs absolute)':^120}")
    print(SEP)
    
    modos_alvo = ["hybrid", "delta", "absolute"]
    
    print("\n  ── Expansões (Fórmula) ──")
    for m in modos_alvo:
        sub = base[(base["heuristica"] == "formula") & (base.get("modo", "") == m)]
        if not sub.empty:
            exp = agregar_sementes(sub, [], "expansoes")
            print(f"  Modo {m:<10} : {pm(exp['media'].iloc[0], exp['std'].iloc[0])}")


# ══════════════════════════════════════════════════════════════════════════════
# BLOCO 11 — RESUMO GERAL
# ══════════════════════════════════════════════════════════════════════════════
def bloco_resumo_geral(base, robustez, ratio, sintese):
    print(f"\n\n{'BLOCO 11 — RESUMO GERAL DOS MODOS':^120}")
    print(SEP)
    
    modos = extrair_modos(base)
    if not modos: 
        print("  (Nenhum modo especificado na base de dados)")
        return
    
    print(f"\n  {'Modo':<15} {'Expansões':>20} {'Ratio':>15} {'Degrad. (30%)':>15} {'Admiss %':>15}")
    print(f"  {'':─<15} {'':─<20} {'':─<15} {'':─<15} {'':─<15}")
    
    rob30 = robustez[robustez.get("porcentagem_bloqueio", 0) == 0.3].copy() if not robustez.empty else pd.DataFrame()
    if not rob30.empty:
        rob30["fator_form"] = rob30["exp_deg_form"] / rob30["exp_orig_form"]

    for m in modos:
        # Expansoes
        sub_b = base[(base["heuristica"] == "formula") & (base.get("modo", "") == m)]
        v_exp = "N/A"
        if not sub_b.empty:
            exp = agregar_sementes(sub_b, [], "expansoes")
            v_exp = f"{exp['media'].iloc[0]:.0f}"
            
        # Ratio
        sub_r = ratio[ratio.get("modo", "") == m]
        v_rat = "N/A"
        if not sub_r.empty:
            agg = agregar_sementes(sub_r, [], "ratio")
            v_rat = f"{agg['media'].iloc[0]:.4f}"
            
        # Degradacao
        sub_rob = rob30[rob30.get("modo", "") == m] if not rob30.empty else pd.DataFrame()
        v_deg = "N/A"
        if not sub_rob.empty:
            ff = agregar_sementes(sub_rob, [], "fator_form")
            v_deg = f"{ff['media'].iloc[0]:.2f}"
            
        # Admiss
        sub_s = sintese[sintese.get("modo", "") == m]
        v_adm = "N/A"
        if not sub_s.empty and "admissibility_rate" in sub_s.columns:
            v_adm = f"{sub_s['admissibility_rate'].mean()*100:.1f}%"
            
        print(f"  {m:<15} {v_exp:>20} {v_rat:>15} {v_deg:>15} {v_adm:>15}")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 120)
    print(f"{'ANÁLISE EXPERIMENTAL — ETC 2026':^120}")
    print("=" * 120)

    base, robustez, ratio, sintese = carregar()

    print(f"\n  Sementes presentes : {sorted(base['semente'].unique()) if 'semente' in base.columns else 'N/A'}")
    print(f"  Mapas              : {base['mapa'].nunique() if 'mapa' in base.columns else 'N/A'}")
    print(f"  Modos identificados: {', '.join(extrair_modos(base)) or 'N/A'}")

    # Blocos Originais Adaptados
    bloco_estatico(base, robustez)
    bloco_degradacao_30(robustez)
    bloco_curva_degradacao(robustez)
    bloco_ratio(ratio)
    bloco_sintese(sintese)
    bloco_memoria(base)

    # Novos Blocos
    bloco_comparacao_terminais(base, robustez, ratio)
    bloco_admissibilidade(ratio, sintese)
    bloco_hibrido(base, robustez, ratio)
    bloco_resumo_geral(base, robustez, ratio, sintese)

    print(f"\n{'=' * 120}")
    print(f"{'Análise concluída.':^120}")
    print(f"{'=' * 120}\n")
