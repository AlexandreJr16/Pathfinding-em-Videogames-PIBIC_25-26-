"""
gerarGraficos_v3.py
────────────────────────────────────────────────────────────────────────────────
Correção metodológica: o fator de degradação é calculado apenas sobre pares
origem-destino válidos em TODOS os níveis de bloqueio de um mesmo grupo
(mapa × tipo_degradacao × n_pivos). Isso garante que a média em 10%, 20% e 30%
reflita o mesmo conjunto de instâncias, eliminando o viés de seleção causado
pelo descarte silencioso de pares inacessíveis.

Saída: figura1_degradacao_v3.pdf
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

# ── CONFIGURAÇÃO ──────────────────────────────────────────────────────────────
CSV_PATH    = "resultados_robustez.csv"
PORC_MAXIMA = 0.3
PIVOS_LIST  = [10, 20, 50, 100]

MAP_TIPOS = {
    "Linear":     "Linear",
    "Organic":    "Orgânico",
    "Radial":     "Radial",
    "Sparse":     "Esparso",
    "Stochastic": "Estocástico",
}

COR_MANH  = "#2196F3"
COR_FORM  = "#FF5722"
CORES_MEM = {10: "#1B5E20", 20: "#388E3C", 50: "#81C784", 100: "#C8E6C9"}
BORDA_MEM = "#1B5E20"

ESTILOS = {
    "manhattan": ("solid",   "o"),
    "formula":   ("dashed",  "s"),
    10:          ("solid",   "^"),
    20:          ("dotted",  "D"),
    50:          ("dashdot", "v"),
    100:         ("dashed",  "P"),
}
# ─────────────────────────────────────────────────────────────────────────────


def filtrar_pares_validos(df):
    """
    Para cada grupo (mapa, tipo_degradacao, n_pivos), mantém apenas os
    id_problema presentes em TODOS os níveis de porcentagem_bloqueio.
    Isso garante comparação sobre o mesmo conjunto de instâncias.
    """
    porcs = sorted(df["porcentagem_bloqueio"].unique())
    grupos = ["mapa", "tipo_degradacao", "n_pivos"]

    partes = []
    for chave, grupo in df.groupby(grupos):
        # conjunto de id_problema por nível de bloqueio
        conjuntos = [
            set(grupo[grupo["porcentagem_bloqueio"] == p]["id_problema"])
            for p in porcs
        ]
        # interseção: pares presentes em todos os níveis
        intersecao = conjuntos[0]
        for c in conjuntos[1:]:
            intersecao &= c

        if len(intersecao) == 0:
            # nenhum par sobrevive em todos os níveis — descarta o grupo
            continue

        filtrado = grupo[grupo["id_problema"].isin(intersecao)]
        partes.append(filtrado)

    if not partes:
        raise ValueError("Nenhum par válido após filtragem. Verifique os dados.")

    return pd.concat(partes, ignore_index=True)


def calcular_fatores(df):
    df = df.copy()
    df["fator_manh"] = df["exp_deg_manh"] / df["exp_orig_manh"]
    df["fator_form"] = df["exp_deg_form"] / df["exp_orig_form"]
    df["fator_mem"]  = df["exp_deg_mem"]  / df["exp_orig_mem"]
    return df


def agregar(df, col_fator):
    return (
        df.groupby(["tipo_degradacao", "porcentagem_bloqueio"])[col_fator]
          .mean()
          .reset_index()
          .rename(columns={col_fator: "fator"})
    )


def carregar(path, porc_maxima):
    df = pd.read_csv(path)
    df = df[df["porcentagem_bloqueio"] <= porc_maxima].copy()
    return df


def preparar_series(df_filtrado):
    # Manhattan e Fórmula: qualquer n_pivos serve (são independentes);
    # usamos n_pivos==10 como âncora para não duplicar linhas.
    base = df_filtrado[df_filtrado["n_pivos"] == 10].copy()
    base = calcular_fatores(base)

    manh_agg = agregar(base, "fator_manh")
    form_agg = agregar(base, "fator_form")

    mem_agg_list = []
    for n in PIVOS_LIST:
        sub = df_filtrado[df_filtrado["n_pivos"] == n].copy()
        sub = calcular_fatores(sub)
        agg = agregar(sub, "fator_mem")
        agg["n_pivos_label"] = n
        mem_agg_list.append(agg)

    mem_agg = pd.concat(mem_agg_list, ignore_index=True)
    return manh_agg, form_agg, mem_agg


def construir_figura(manh_agg, form_agg, mem_agg):
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(13, 11))

    # GridSpec único de 3 linhas × 4 colunas
    # Top: gs[0, 0:2], gs[0, 2:4] (2 subplots)
    # Mid: gs[1, 1:3]             (1 subplot, centrado)
    # Bot: gs[2, 0:2], gs[2, 2:4] (2 subplots)
    gs = gridspec.GridSpec(3, 4, figure=fig,
                           left=0.07, right=0.98,
                           top=0.95, bottom=0.10,
                           wspace=0.15, hspace=0.35)

    ax_list = [
        fig.add_subplot(gs[0, 0:2]),
        fig.add_subplot(gs[0, 2:4]),
        fig.add_subplot(gs[1, 1:3]),
        fig.add_subplot(gs[2, 0:2]),
        fig.add_subplot(gs[2, 2:4])
    ]
    # Sincroniza eixos Y entre todos
    for ax in ax_list[1:]:
        ax.sharey(ax_list[0])

    xticks_vals = sorted(manh_agg["porcentagem_bloqueio"].unique())

    for ax, (tipo_orig, tipo_disp) in zip(ax_list, MAP_TIPOS.items()):

        # Manhattan
        sub = manh_agg[manh_agg["tipo_degradacao"] == tipo_orig].sort_values("porcentagem_bloqueio")
        ax.plot(sub["porcentagem_bloqueio"] * 100, sub["fator"],
                color=COR_MANH, linestyle=ESTILOS["manhattan"][0],
                marker=ESTILOS["manhattan"][1], markersize=6, linewidth=2.0,
                label="Manhattan")

        # Fórmula
        sub = form_agg[form_agg["tipo_degradacao"] == tipo_orig].sort_values("porcentagem_bloqueio")
        ax.plot(sub["porcentagem_bloqueio"] * 100, sub["fator"],
                color=COR_FORM, linestyle=ESTILOS["formula"][0],
                marker=ESTILOS["formula"][1], markersize=6, linewidth=2.0,
                label="Fórmula")

        # Memória (4 contagens)
        for n in PIVOS_LIST:
            sub = (mem_agg[(mem_agg["tipo_degradacao"] == tipo_orig) &
                           (mem_agg["n_pivos_label"] == n)]
                   .sort_values("porcentagem_bloqueio"))
            ax.plot(sub["porcentagem_bloqueio"] * 100, sub["fator"],
                    color=CORES_MEM[n], linestyle=ESTILOS[n][0],
                    marker=ESTILOS[n][1], markersize=6, linewidth=2.0,
                    markeredgecolor=BORDA_MEM, markeredgewidth=0.7,
                    label=f"Memória ({n} pivôs)")

        ax.axhline(1.0, color="gray", linewidth=0.8, linestyle=":")
        ax.set_title(tipo_disp, fontsize=13, pad=5)
        ax.set_xlabel("Bloqueios (%)", fontsize=11)
        ax.set_xticks([int(p * 100) for p in xticks_vals])
        ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d%%"))
        ax.tick_params(axis="both", labelsize=11)
        ax.grid(True, axis="y", alpha=0.3)
        ax.set_xlim(left=5)

    # Rótulo Y na coluna esquerda de cada linha
    ax_list[0].set_ylabel("Fator de degradação (expansões)", fontsize=11)
    ax_list[2].set_ylabel("Fator de degradação (expansões)", fontsize=11)
    ax_list[3].set_ylabel("Fator de degradação (expansões)", fontsize=11)

    # Ocultar ytick labels nos subplots que não são o primeiro de cada linha
    for i in [1, 4]:
        ax_list[i].tick_params(labelleft=False)

    legend_elements = [
        Line2D([0], [0], color=COR_MANH, linestyle=ESTILOS["manhattan"][0],
               marker=ESTILOS["manhattan"][1], markersize=6, label="Manhattan"),
        Line2D([0], [0], color=COR_FORM, linestyle=ESTILOS["formula"][0],
               marker=ESTILOS["formula"][1], markersize=6, label="Fórmula"),
    ] + [
        Line2D([0], [0], color=CORES_MEM[n], linestyle=ESTILOS[n][0],
               marker=ESTILOS[n][1], markersize=6,
               markeredgecolor=BORDA_MEM, markeredgewidth=0.7,
               label=f"Memória ({n} pivôs)")
        for n in PIVOS_LIST
    ]

    fig.legend(handles=legend_elements, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, 0.00), fontsize=11,
               frameon=True, edgecolor="#cccccc")

    fig.suptitle(
        "Fator de degradação de expansões por tipo de bloqueio",
        fontsize=13, y=0.98,
    )
    return fig


# ── DIAGNÓSTICO: imprime quantos pares são descartados por grupo ──────────────
def diagnostico(df_original, df_filtrado):
    total_orig    = len(df_original)
    total_filtrado = len(df_filtrado)
    descartados   = total_orig - total_filtrado
    pct           = 100 * descartados / total_orig if total_orig > 0 else 0
    print(f"\n[DIAGNÓSTICO] Linhas originais : {total_orig:>8}")
    print(f"              Após filtragem   : {total_filtrado:>8}")
    print(f"              Descartadas      : {descartados:>8}  ({pct:.1f}%)")

    # por tipo de degradação
    print("\n  Descartadas por tipo_degradacao:")
    for tipo in df_original["tipo_degradacao"].unique():
        o = len(df_original[df_original["tipo_degradacao"] == tipo])
        f = len(df_filtrado[df_filtrado["tipo_degradacao"] == tipo])
        print(f"    {tipo:<12}: {o - f:>6} descartadas de {o:>6}  ({100*(o-f)/o:.1f}%)")
    print()


if __name__ == "__main__":
    df_raw      = carregar(CSV_PATH, PORC_MAXIMA)
    df_filtrado = filtrar_pares_validos(df_raw)
    diagnostico(df_raw, df_filtrado)

    manh_agg, form_agg, mem_agg = preparar_series(df_filtrado)
    fig = construir_figura(manh_agg, form_agg, mem_agg)

    saida = "figura1_degradacao_v3.pdf"
    fig.savefig(saida, bbox_inches="tight", dpi=300)
    print(f"Salvo: {saida}")
