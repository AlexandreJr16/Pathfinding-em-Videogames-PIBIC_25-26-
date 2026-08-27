import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D

# ── CONFIGURAÇÃO SBC ──────────────────────────────────────────────────────────
# Configurações para garantir legibilidade em publicações (SBC/IEEE style)
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.labelsize": 11,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.figsize": (7, 4.5),
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "font.family": "serif",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--"
})

CSV_ROBUSTEZ = "resultados_robustez.csv"
CSV_BASE = "resultados_base.csv"

# Mapeamento de nomes de heurísticas para labels legíveis
HEUR_LABELS = {
    "manhattan": "Manhattan",
    "formula": "Fórmula",
    10: "Memória (10 pivôs)",
    20: "Memória (20 pivôs)",
    50: "Memória (50 pivôs)",
    100: "Memória (100 pivôs)"
}

# Estilos de linha e marcadores para SBC (distinguíveis em P&B)
ESTILOS = {
    "manhattan": {"color": "#000000", "ls": "-",  "marker": "o"},
    "formula":   {"color": "#d62728", "ls": "--", "marker": "s"},
    10:          {"color": "#2ca02c", "ls": ":",  "marker": "^"},
    20:          {"color": "#1f77b4", "ls": "-.", "marker": "D"},
    50:          {"color": "#ff7f0e", "ls": "--", "marker": "v"},
    100:         {"color": "#9467bd", "ls": "-",  "marker": "P"},
}

def carregar_dados():
    try:
        rob = pd.read_csv(CSV_ROBUSTEZ)
        base = pd.read_csv(CSV_BASE)
        return rob, base
    except FileNotFoundError as e:
        print(f"Erro ao carregar CSVs: {e}")
        exit(1)

def plot_rho_degradacao(df_rob):
    print("Gerando gráfico de sub-otimalidade (rho)...")
    df = df_rob.copy()
    
    # 2.1 e 2.2: Cálculo dos ratios por linha
    # rho = path_length / optimal_path_length (aqui, optimal_path_length é o path com Manhattan)
    df["rho_formula"] = df["path_deg_form"] / df["path_deg_manh"]
    df["rho_mem"]     = df["path_deg_mem"]  / df["path_deg_manh"]
    
    # 2.3: Agregação por bloqueio
    # Primeiro agregamos por (bloqueio, semente) e depois por bloqueio
    def agregar_metricas(sub_df, col_name):
        # Passo 1: Média por semente para colapsar instâncias
        s_agg = sub_df.groupby(["porcentagem_bloqueio", "semente"])[col_name].mean().reset_index()
        # Passo 2: Média e erro padrão sobre as sementes
        final_agg = s_agg.groupby("porcentagem_bloqueio")[col_name].agg(["mean", "sem"]).reset_index()
        return final_agg

    # Dados para Manhattan (rho é sempre 1.0 por definição aqui)
    bloqueios = sorted(df["porcentagem_bloqueio"].unique())
    manh_data = pd.DataFrame({"porcentagem_bloqueio": bloqueios, "mean": [1.0]*len(bloqueios), "sem": [0.0]*len(bloqueios)})
    
    # Dados para Fórmula
    form_agg = agregar_metricas(df, "rho_formula")
    
    # Dados para Memória (4 contagens)
    mem_aggs = {}
    for n in [10, 20, 50, 100]:
        sub_mem = df[df["n_pivos"] == n]
        mem_aggs[n] = agregar_metricas(sub_mem, "rho_mem")

    # 2.4: Plotagem
    fig, ax = plt.subplots()
    
    def plot_with_error(agg_df, label, style_key):
        st = ESTILOS[style_key]
        x = agg_df["porcentagem_bloqueio"] * 100
        y = agg_df["mean"]
        err = agg_df["sem"]
        
        ax.errorbar(x, y, yerr=err, label=HEUR_LABELS[label],
                    color=st["color"], linestyle=st["ls"], marker=st["marker"],
                    capsize=3, markersize=6, linewidth=1.5)

    plot_with_error(manh_data, "manhattan", "manhattan")
    plot_with_error(form_agg, "formula", "formula")
    for n in [10, 20, 50, 100]:
        plot_with_error(mem_aggs[n], n, n)

    ax.set_xlabel("Nível de Bloqueio (%)")
    ax.set_ylabel(r"Sub-otimalidade Média ($\rho$)")
    ax.set_title("Evolução da Qualidade do Caminho sob Degradação")
    ax.legend(ncol=2, frameon=True, edgecolor="#cccccc")
    
    # Ajustes de eixos
    ax.set_xticks([0, 10, 20, 30])
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d%%"))
    ax.set_xlim(-2, 32)
    
    plt.tight_layout()
    saida = "sbc_rho_degradacao.pdf"
    plt.savefig(saida)
    print(f"Salvo: {saida}")

def plot_heatmap_expansoes(df_base, df_rob):
    print("Gerando heatmap de expansões...")
    
    # 3.1: Coleta de dados base (Manhattan e Fórmula)
    # df_base tem colunas: mapa, semente, id_problema, heuristica, n_pivos, expansoes
    base_agg = df_base.groupby(["mapa", "heuristica"])["expansoes"].mean().unstack()
    
    # 3.2: Coleta de dados de Memória (do robustez, 0% de bloqueio)
    # Filtramos n_pivos==10, 20, 50, 100
    mem_orig = df_rob.drop_duplicates(subset=["mapa", "semente", "id_problema", "n_pivos"])
    mem_agg = mem_orig.groupby(["mapa", "n_pivos"])["exp_orig_mem"].mean().unstack()
    mem_agg.columns = [f"mem_{c}" for c in mem_agg.columns]
    
    # Combinar tudo
    combined = pd.concat([base_agg[["manhattan", "formula"]], mem_agg], axis=1)
    
    # Normalizar por Manhattan
    # 3.2: E_ratio = E_heur / E_manh
    for col in combined.columns:
        if col != "manhattan":
            combined[col] = combined[col] / combined["manhattan"]
    combined["manhattan"] = 1.0  # Por definição
    
    # 3.3 e 3.4: Reordenar colunas e linhas
    cols_order = ["manhattan", "formula", "mem_10", "mem_20", "mem_50", "mem_100"]
    combined = combined[cols_order]
    
    # Ordenar mapas por tipo (prefixo)
    def map_sort_key(name):
        prefixes = ["arena", "brc", "den", "hrt", "lak"]
        for i, p in enumerate(prefixes):
            if name.startswith(p):
                return (i, name)
        return (len(prefixes), name)
    
    combined = combined.reindex(sorted(combined.index, key=map_sort_key))
    
    # 3.5: Plotagem com Seaborn
    plt.figure(figsize=(8, 10))
    sns.set_theme(style="white")
    
    # Usando escala logarítmica para cores se houver muita variação, ou linear se for pequena
    # Como brc000d pode ser outlier, vamos usar uma escala divergente ou truncada para visualização
    # mas mantendo os números reais na anotação.
    ax = sns.heatmap(combined, annot=True, fmt=".2f", cmap="YlOrRd", 
                     cbar_kws={'label': 'Fator de Expansões ($E_{heur} / E_{manh}$)'},
                     linewidths=.5, annot_kws={"size": 9})
    
    plt.title("Desempenho por Mapa: Expansões Normalizadas", pad=20)
    plt.xlabel("Heurística")
    plt.ylabel("Mapa")
    
    # Renomear colunas no eixo X
    ax.set_xticklabels([HEUR_LABELS.get(int(c.split('_')[1]) if '_' in c else c, c) 
                        for c in combined.columns], rotation=45, ha="right")

    plt.tight_layout()
    saida = "sbc_heatmap_expansoes.pdf"
    plt.savefig(saida)
    print(f"Salvo: {saida}")

if __name__ == "__main__":
    rob, base = carregar_dados()
    print(f"Dados carregados: {len(rob)} linhas de robustez, {len(base)} linhas base.")
    
    # Adicionando ponto zero (0%) a partir dos dados 'orig' do robustez
    zero_pct = rob[rob["porcentagem_bloqueio"] == 0.1].copy()
    zero_pct["porcentagem_bloqueio"] = 0.0
    zero_pct["path_deg_manh"] = zero_pct["path_orig_manh"]
    zero_pct["path_deg_form"] = zero_pct["path_orig_form"]
    zero_pct["path_deg_mem"]  = zero_pct["path_orig_mem"]
    rob_completo = pd.concat([zero_pct, rob], ignore_index=True)
    
    plot_rho_degradacao(rob_completo)
    plot_heatmap_expansoes(base, rob)
