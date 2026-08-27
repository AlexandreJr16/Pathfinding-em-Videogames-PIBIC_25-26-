"""
gerar_figuras.py
────────────────────────────────────────────────────────────────────────────────
Gera as três figuras do artigo com estilo tipográfico e visual unificado.

CSVs esperados (mesma pasta que este script):
  - resultados_ratio.csv    → colunas: mapa, semente, ratio
  - resultados_sintese.csv  → colunas: mapa, tempo_sintese_ms, fitness_final, formula_string
  - resultados_robustez.csv → colunas: mapa, tipo_degradacao, n_pivos,
                                        porcentagem_bloqueio, semente, id_problema,
                                        exp_deg_manh, exp_orig_manh,
                                        exp_deg_form, exp_orig_form,
                                        exp_deg_mem,  exp_orig_mem

Saída (pasta img/):
  fig1_ratio_por_categoria.pdf
  fig2_sintese_por_mapa.pdf
  fig3_degradacao_por_padrao.pdf
"""

import os
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D
import seaborn as sns

# ══════════════════════════════════════════════════════════════════════════════
# 1. SISTEMA DE ESTILO GLOBAL
# ══════════════════════════════════════════════════════════════════════════════

CM = 1 / 2.54
COL_W  = 8.5  * CM   # coluna simples
COL_2W = 17.5 * CM   # coluna dupla (Fig. 3)

# Paleta Profissional: Manhattan (Azul), Fórmula (Laranja/Vermelho), Memória (Gradient de Verdes)
CORES = {
    "manhattan": "#1E88E5",    # Azul vibrante
    "formula":   "#D32F2F",    # Vermelho/Laranja
    "mem_10":    "#1B5E20",    # Verde Escuro
    "mem_20":    "#388E3C",    # Verde Médio-Escuro
    "mem_50":    "#66BB6A",    # Verde Médio-Claro
    "mem_100":   "#A5D6A7",    # Verde Pálido
}

TRACOS = {
    "manhattan": "-",
    "formula":   "--",
    "mem_10":    "-",
    "mem_20":    ":",
    "mem_50":    "-.",
    "mem_100":   "--",
}

MARCADORES = {
    "manhattan": "o",
    "formula":   "s",
    "mem_10":    "^",
    "mem_20":    "D",
    "mem_50":    "v",
    "mem_100":   "p",
}

ROTULOS = {
    "manhattan": "Manhattan",
    "formula":   "Fórmula",
    "mem_10":    "Memória (10 pivôs)",
    "mem_20":    "Memória (20 pivôs)",
    "mem_50":    "Memória (50 pivôs)",
    "mem_100":   "Memória (100 pivôs)",
}

ORDEM_HEUR = ["manhattan", "formula", "mem_10", "mem_20", "mem_50", "mem_100"]

def configurar_estilo_global():
    sns.set_theme(style="whitegrid", context="paper", font_scale=0.95)
    mpl.rcParams.update({
        "font.family":           "serif",
        "font.serif":            ["Liberation Serif", "DejaVu Serif", "Times New Roman"],
        "font.size":             9,
        "axes.labelsize":        9.5,
        "axes.titlesize":        9.5,
        "xtick.labelsize":       8.5,
        "ytick.labelsize":       8.5,
        "legend.fontsize":       8,
        "axes.edgecolor":        "#444444",
        "axes.linewidth":        0.8,
        "axes.spines.top":       False,
        "axes.spines.right":     False,
        "xtick.direction":       "out",
        "ytick.direction":       "out",
        "xtick.major.size":      3.0,
        "ytick.major.size":      3.0,
        "xtick.major.width":     0.8,
        "ytick.major.width":     0.8,
        "lines.linewidth":       1.5,
        "lines.markersize":      5.0,
        "lines.markeredgewidth": 0.5,
        "grid.linewidth":        0.4,
        "grid.alpha":            0.35,
        "grid.linestyle":        ":",
        "grid.color":            "#888888",
        "legend.framealpha":     0.95,
        "legend.edgecolor":      "#cccccc",
        "legend.borderpad":      0.5,
        "legend.labelspacing":   0.35,
        "savefig.dpi":           300,
        "savefig.bbox":          "tight",
        "savefig.pad_inches":    0.03,
    })



def salvar(fig, caminho):
    fig.savefig(caminho)
    print(f"  Salvo: {caminho}")


# ══════════════════════════════════════════════════════════════════════════════
# 2. FIGURA 1 — Razão de qualidade de caminho (ρ) por categoria de mapa
#    CSV: resultados_ratio.csv  |  colunas: mapa, semente, ratio
# ══════════════════════════════════════════════════════════════════════════════

def _categoria(nome):
    n = nome.lower()
    if "arena" in n:               return "Arenas"
    if "den"   in n:               return "Dungeons"
    if "brc"   in n:               return "Áreas\nabertas"
    if "lak"   in n or "hrt" in n: return "Natureza"
    return "Outros"


def gerar_fig1_ratio(csv="resultados_ratio.csv"):
    df = pd.read_csv(csv)
    df["categoria"] = df["mapa"].apply(_categoria)

    ordem_todas = ["Arenas", "Áreas\nabertas", "Natureza", "Dungeons", "Outros"]
    ordem = [c for c in ordem_todas if c in df["categoria"].values]
    
    # Prepara rótulos com N
    labels_n = []
    dados = []
    for cat in ordem:
        subset = df[df["categoria"] == cat]["ratio"].dropna().values
        dados.append(subset)
        labels_n.append(f"{cat}\n(N={len(subset):,})".replace(",", "."))

    fig, ax = plt.subplots(figsize=(COL_W, 6.8 * CM))

    bp = ax.boxplot(
        dados,
        vert=True,
        patch_artist=True,
        widths=0.48,
        showfliers=False,
        medianprops=dict(color="#111111", linewidth=2.0, solid_capstyle="round"),
        whiskerprops=dict(linewidth=1.0, color="#444444"),
        capprops=dict(linewidth=1.0, color="#444444"),
        boxprops=dict(linewidth=1.0, color="#333333"),
    )
    
    # Cores dos boxes
    for patch in bp["boxes"]:
        patch.set_facecolor(CORES["formula"])
        patch.set_alpha(0.55)

    # Linha de ótimo
    ax.axhline(1.0, color="#444444", linestyle="--", linewidth=0.8, zorder=0)
    
    # Anotação "ótimo" (movida para não sobrepor Dungeons)
    ax.text(
        0.55, 1.002,
        "ótimo (ρ = 1)",
        va="bottom", ha="left",
        fontsize=7.8, color="#444444", style="italic",
    )

    ax.set_xticklabels(labels_n)
    ax.set_ylabel("Razão de qualidade de caminho (ρ)")
    
    # Ajustes finais
    sns.despine(ax=ax, left=False, bottom=False)
    ax.yaxis.grid(True, linestyle=":", alpha=0.4, color="#888888")
    ax.set_axisbelow(True)

    plt.tight_layout()
    salvar(fig, "img/fig1_ratio_por_categoria.pdf")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 3. FIGURA 2 — Tempo de síntese evolutiva por mapa
#    CSV: resultados_sintese.csv  |  colunas: mapa, tempo_sintese_ms
# ══════════════════════════════════════════════════════════════════════════════

def gerar_fig2_sintese(csv="resultados_sintese.csv"):
    df  = pd.read_csv(csv).drop_duplicates(subset=["mapa"])
    df["tempo_s"] = df["tempo_sintese_ms"] / 1000.0
    agg = df.groupby("mapa")["tempo_s"].mean().sort_values()

    fig, ax = plt.subplots(figsize=(COL_W, 9.8 * CM))

    # Gradiente de intensidade azul profissional proporcional ao log do tempo
    log_vals = np.log10(np.clip(agg.values, 1e-1, None))
    t_norm   = (log_vals - log_vals.min()) / (log_vals.max() - log_vals.min() + 1e-9)
    r, g, b  = mpl.colors.to_rgb(CORES["manhattan"])
    # Alpha de 0.3 a 0.9 para dar profundidade sem parecer "erro" (vermelho)
    cores    = [(r, g, b, 0.35 + 0.60 * t) for t in t_norm]

    ax.barh(
        agg.index, agg.values,
        color=cores,
        edgecolor="#333333",
        linewidth=0.6,
        height=0.68,
    )

    ax.set_xscale("log")
    ax.set_xlabel("Tempo de síntese (s)")
    ax.xaxis.grid(True, which="both", linestyle=":", alpha=0.3, color="#888888")
    ax.set_axisbelow(True)

    # Limite de 1 minuto (mais discreto)
    ax.axvline(60, color="#666666", linestyle="--", linewidth=0.7, zorder=0)
    ax.text(
        65, len(agg) - 0.7,
        "1 min",
        va="top", ha="left",
        fontsize=7.5, color="#666666", style="italic",
    )

    sns.despine(ax=ax, left=True, bottom=False)
    ax.tick_params(axis="y", length=0, pad=5)

    plt.tight_layout()
    salvar(fig, "img/fig2_sintese_por_mapa.pdf")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# 4. FIGURA 3 — Fator de degradação por padrão de bloqueio (5 painéis)
#    CSV: resultados_robustez.csv
#
#    Valores de tipo_degradacao no CSV: "Linear", "Organic", "Radial",
#                                        "Sparse", "Stochastic"
#    Fórmulas de fator:
#      fator_manh = exp_deg_manh / exp_orig_manh
#      fator_form = exp_deg_form / exp_orig_form
#      fator_mem  = exp_deg_mem  / exp_orig_mem
# ══════════════════════════════════════════════════════════════════════════════

# Chave CSV → rótulo PT-BR
PADROES = {
    "Linear":     "Linear",
    "Organic":    "Orgânico",
    "Radial":     "Radial",
    "Sparse":     "Esparso",
    "Stochastic": "Estocástico",
}

PIVOS_LIST = [10, 20, 50, 100]


def _fator_medio(df_sub, col_deg, col_orig):
    """Média de col_deg / col_orig; NaN se df_sub vazio."""
    if df_sub.empty:
        return np.nan
    return (df_sub[col_deg] / df_sub[col_orig]).mean()


def gerar_fig3_degradacao(
    csv="resultados_robustez.csv",
    porc_max=0.3,
):
    df = pd.read_csv(csv)
    df = df[df["porcentagem_bloqueio"] <= porc_max].copy()

    niveis     = sorted(df["porcentagem_bloqueio"].unique())
    xticks_pct = [int(round(p * 100)) for p in niveis]

    # ── Layout: 3 linhas × 4 colunas (2-1-2) ──────────────────
    fig = plt.figure(figsize=(COL_2W, 14.8 * CM))
    gs = gridspec.GridSpec(3, 4, figure=fig,
                           left=0.08, right=0.98,
                           top=0.93, bottom=0.22,
                           wspace=0.18, hspace=0.40)

    ax_list = [
        fig.add_subplot(gs[0, 0:2]),
        fig.add_subplot(gs[0, 2:4]),
        fig.add_subplot(gs[1, 1:3]), # Painel centralizado
        fig.add_subplot(gs[2, 0:2]),
        fig.add_subplot(gs[2, 2:4])
    ]
    
    # Sincroniza eixos X e Y
    for ax in ax_list[1:]:
        ax.sharex(ax_list[0])
        ax.sharey(ax_list[0])

    for ax, (tipo_csv, tipo_label) in zip(ax_list, PADROES.items()):
        df_t = df[df["tipo_degradacao"] == tipo_csv]

        # Manhattan e Fórmula
        yvals_manh = []
        yvals_form = []
        for p in niveis:
            sub = df_t[
                (df_t["porcentagem_bloqueio"] == p) &
                (df_t["n_pivos"] == PIVOS_LIST[0])
            ]
            yvals_manh.append(_fator_medio(sub, "exp_deg_manh", "exp_orig_manh"))
            yvals_form.append(_fator_medio(sub, "exp_deg_form", "exp_orig_form"))

        ax.plot(
            xticks_pct, yvals_manh,
            color=CORES["manhattan"], linestyle=TRACOS["manhattan"],
            marker=MARCADORES["manhattan"],
            markeredgecolor="white", markeredgewidth=0.6,
            label=ROTULOS["manhattan"], zorder=4,
        )
        ax.plot(
            xticks_pct, yvals_form,
            color=CORES["formula"], linestyle=TRACOS["formula"],
            marker=MARCADORES["formula"],
            markeredgecolor="white", markeredgewidth=0.6,
            label=ROTULOS["formula"], zorder=4,
        )

        # Memória — uma linha por contagem de pivôs
        for n in PIVOS_LIST:
            chave = f"mem_{n}"
            yvals = []
            for p in niveis:
                sub = df_t[
                    (df_t["porcentagem_bloqueio"] == p) &
                    (df_t["n_pivos"] == n)
                ]
                yvals.append(_fator_medio(sub, "exp_deg_mem", "exp_orig_mem"))

            ax.plot(
                xticks_pct, yvals,
                color=CORES[chave], linestyle=TRACOS[chave],
                marker=MARCADORES[chave],
                markeredgecolor="white", markeredgewidth=0.6,
                label=ROTULOS[chave], zorder=3,
            )

        ax.axhline(1.0, color="#444444", linewidth=0.7, linestyle="--", zorder=0)
        ax.set_title(tipo_label, fontsize=10, fontweight="bold", pad=5)
        ax.set_xticks(xticks_pct)
        ax.set_xticklabels([f"{p}%" for p in xticks_pct])
        
        # Fixar eixo Y em (1, 2, 3, 4, 5, 6)
        ax.set_yticks([1, 2, 3, 4, 5, 6])
        ax.set_ylim(0.8, 6.5) # Margem pequena para os marcadores
        
        ax.yaxis.grid(True, linestyle=":", alpha=0.35, color="#888888")
        ax.set_axisbelow(True)
        sns.despine(ax=ax)

    # Oculta ytick labels redundantes
    # Em 2-1-2, o painel central (índice 2) e os da direita (1, 4) podem ser limpos se compartilhado
    # Mas para clareza, vamos manter apenas os da esquerda (0, 3) e o central (2) com labels se necessário
    # Decidimos: labels Y em todos os da esquerda (0, 3). No central (2) também pois está isolado.
    for i in [1, 4]:
        ax_list[i].tick_params(labelleft=False)

    # Rótulos de eixo globais
    fig.text(0.50, 0.15, "Bloqueios (%)", ha="center", fontsize=10)
    fig.text(
        0.02, 0.58,
        "Fator de degradação de expansões (δ)",
        va="center", ha="center", rotation="vertical", fontsize=10,
    )

    # Legenda redesenhada (3 colunas, 2 linhas) na parte inferior
    handles = [
        Line2D(
            [0], [0],
            color=CORES[ch],
            linestyle=TRACOS[ch],
            marker=MARCADORES[ch],
            markersize=5.5,
            markeredgecolor="white",
            markeredgewidth=0.6,
            label=ROTULOS[ch],
        )
        for ch in ORDEM_HEUR
    ]

    fig.legend(
        handles=handles,
        loc="lower center",
        ncol=3,
        frameon=True,
        framealpha=1.0,
        edgecolor="#cccccc",
        fontsize=8.5,
        handlelength=2.8,
        labelspacing=0.5,
        borderpad=0.8,
        bbox_to_anchor=(0.5, 0.01)
    )

    salvar(fig, "img/fig3_degradacao_por_padrao.pdf")
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    os.makedirs("img", exist_ok=True)
    configurar_estilo_global()
    print("Gerando figuras...\n")

    print("→ Figura 1 — Razão de qualidade de caminho (ρ) por categoria")
    gerar_fig1_ratio()

    print("→ Figura 2 — Tempo de síntese por mapa")
    gerar_fig2_sintese()

    print("→ Figura 3 — Fator de degradação por padrão de bloqueio")
    gerar_fig3_degradacao()

    print("\nConcluído. Arquivos em img/")
