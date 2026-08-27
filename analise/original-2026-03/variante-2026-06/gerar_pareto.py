import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np
import os

# --- 1. DADOS E CONFIGURAÇÕES ---
N_medio = 50000  # Vértices (Dragon Age Origins)

heuristicas_raw = [
    {
        "nome": "Manhattan",
        "expansoes": 7472.95,
        "expansoes_std": 0,
        "memoria_mb": 0.001,
        "cor": "#2196F3",
        "marcador": "o"
    },
    {
        "nome": "Fórmula (GP)",
        "expansoes": 2412.69,
        "expansoes_std": 0,
        "memoria_mb": 0.005,
        "cor": "#FF5722",
        "marcador": "s"
    },
    {
        "nome": "10 pivôs",
        "pivos": 10,
        "expansoes": 441.53,
        "expansoes_std": 62.65,
        "memoria_mb": None,
        "cor": "#4CAF50",
        "marcador": "^"
    },
    {
        "nome": "20 pivôs",
        "pivos": 20,
        "expansoes": 251.46,
        "expansoes_std": 55.06,
        "memoria_mb": None,
        "cor": "#4CAF50",
        "marcador": "v"
    },
    {
        "nome": "50 pivôs",
        "pivos": 50,
        "expansoes": 280.71,
        "expansoes_std": 138.44,
        "memoria_mb": None,
        "cor": "#4CAF50",
        "marcador": "D"
    },
    {
        "nome": "100 pivôs",
        "pivos": 100,
        "expansoes": 145.20,
        "expansoes_std": 16.46,
        "memoria_mb": None,
        "cor": "#4CAF50",
        "marcador": "P"
    }
]

# --- 2. CÁLCULO DE MEMÓRIA ---
print("Valores de memória calculados:")
for h in heuristicas_raw:
    if h["memoria_mb"] is None:
        h["memoria_mb"] = (h["pivos"] * N_medio * 4) / (1024 * 1024)
    print(f"- {h['nome']}: {h['memoria_mb']:.4f} MB")

# --- 3. ESTILO ACADÊMICO ---
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    "font.family": "serif",
    "font.serif": ["Times New Roman", "DejaVu Serif"],
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "text.usetex": False  # Definido como False para evitar dependência de LaTeX no sistema
})

# Tamanho da figura: 8.5cm x 7cm (em polegadas)
# 1 cm = 0.3937 polegadas
fig, ax = plt.subplots(figsize=(8.5 * 0.3937, 7 * 0.3937))

# --- 4. CÁLCULO DA FRONTEIRA DE PARETO ---
# Ordenar por memória (X)
heuristicas_sorted = sorted(heuristicas_raw, key=lambda x: x["memoria_mb"])

pareto_points = []
min_expansoes = float('inf')

for h in heuristicas_sorted:
    if h["expansoes"] < min_expansoes:
        pareto_points.append(h)
        min_expansoes = h["expansoes"]

# Pontos para a linha da fronteira (escada/step)
pareto_x = [h["memoria_mb"] for h in pareto_points]
pareto_y = [h["expansoes"] for h in pareto_points]

# --- 5. PLOTAGEM ---
# Plotar todos os pontos
for h in heuristicas_raw:
    ax.errorbar(
        h["memoria_mb"], h["expansoes"], 
        yerr=h["expansoes_std"],
        fmt=h["marcador"], color=h["cor"],
        label=h["nome"], markersize=5, 
        markeredgecolor='white', markeredgewidth=0.5,
        capsize=3, elinewidth=0.8
    )

# Desenhar a fronteira de Pareto (linha de escada para visualizar dominância)
# Usamos drawstyle='steps-post' para representar que a performance se mantém 
# até o próximo ponto de memória
ax.step(pareto_x, pareto_y, where='post', color='#555555', linestyle='--', 
        linewidth=1, alpha=0.8, zorder=1)

# Preencher a área abaixo da fronteira
ax.fill_between(pareto_x, pareto_y, step="post", color='#555555', alpha=0.08)

# --- 6. ANOTAÇÕES ---
# Sweet spot: Fórmula (GP)
gp_data = next(h for h in heuristicas_raw if h["nome"] == "Fórmula (GP)")
ax.annotate(
    "sweet spot", 
    xy=(gp_data["memoria_mb"], gp_data["expansoes"]),
    xytext=(gp_data["memoria_mb"] * 4, gp_data["expansoes"] * 0.4),
    arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=-.3", linewidth=0.8),
    fontstyle='italic', fontsize=8, ha='center'
)

# --- 7. FORMATAÇÃO FINAL ---
ax.set_xscale('log')
ax.set_xlabel("Uso de Memória (MB)", labelpad=12)
ax.set_ylabel("Expansões Médias de Nós", labelpad=12)

# Margens internas: Forçar limites para criar "gap" nas bordas
ax.set_xlim(0.0005, 50)
ax.set_ylim(-500, 9000)

# Configuração de ticks logarítmicos (Minor Ticks)
ax.xaxis.set_minor_locator(ticker.LogLocator(base=10.0, subs='auto', numticks=12))
ax.xaxis.set_minor_formatter(ticker.NullFormatter()) # Não mostrar texto nos minor ticks
ax.tick_params(axis='x', which='minor', length=2, color='#cccccc')

# Grid e Bordas
ax.grid(axis='y', linewidth=0.5, alpha=0.3, linestyle='-')
ax.grid(axis='x', visible=False)
sns.despine()

# Legenda - sem título e posicionada para maximizar área
ax.legend(
    frameon=False, 
    loc='upper center', 
    bbox_to_anchor=(0.5, -0.22),
    ncol=3,
    columnspacing=0.8,
    handletextpad=0.2
)

# Margens ajustadas para um visual mais esparso
plt.tight_layout(pad=1.2)
fig.subplots_adjust(bottom=0.25)

# --- 8. EXPORTAÇÃO ---
plt.savefig("pareto_heuristicas.pdf", format="pdf", bbox_inches="tight")
plt.savefig("pareto_heuristicas.png", format="png", dpi=300, bbox_inches="tight")

print("\nGráficos gerados com sucesso:")
print("- pareto_heuristicas.pdf")
print("- pareto_heuristicas.png")

# plt.show()  # Disabled for non-interactive environment
