"""Estilo das figuras: vetor, meia coluna A4 em ABNT, legível em preto e branco."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

plt.rcParams.update({
    "font.family": "serif", "font.size": 8, "axes.labelsize": 8,
    "axes.titlesize": 8.5, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.linewidth": 0.6, "lines.linewidth": 1.1,
    "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "figure.dpi": 260, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "pdf.fonttype": 42, "axes.spines.top": False, "axes.spines.right": False,
})
# Preto e branco: distinguir por traço e marcador, nunca só por cor.
TRACOS = ["-", "--", "-.", ":", (0, (3, 1, 1, 1)), (0, (5, 1))]
MARCAS = ["o", "s", "^", "D", "v", "P"]
CINZAS = ["0.0", "0.30", "0.0", "0.30", "0.55", "0.55"]

def salvar(fig, nome, figuras_dir):
    for ext in ("pdf", "png"):
        fig.savefig(figuras_dir / f"{nome}.{ext}")
    plt.close(fig)
    print(f"    figura: {nome}.pdf + .png")

def diagrama_cd(ax, postos, cd, rotulos, titulo):
    """Diagrama de diferença crítica (Demšar 2006). Menor posto = melhor."""
    k = len(postos)
    ordem = np.argsort(postos)
    postos, rotulos = np.asarray(postos)[ordem], np.asarray(rotulos)[ordem]
    lo, hi = np.floor(postos.min()) - 0.2, np.ceil(postos.max()) + 0.2
    ax.set_xlim(lo, hi); ax.set_ylim(-(k / 2) * 0.32 - 0.45, 0.92); ax.axis("off")
    ax.plot([lo, hi], [0, 0], "k-", lw=0.9)
    for t in np.arange(np.ceil(lo), np.floor(hi) + 1):
        ax.plot([t, t], [0, 0.10], "k-", lw=0.7)
        ax.text(t, 0.16, f"{t:.0f}", ha="center", va="bottom", fontsize=7)
    for i, (r, lab) in enumerate(zip(postos, rotulos)):
        esq = i < k / 2
        y = -(i + 1) * 0.32 - 0.26 if esq else -(k - i) * 0.32 - 0.26
        xt = lo - 0.05 if esq else hi + 0.05
        ax.plot([r, r], [-0.02, y], "k-", lw=0.7)
        ax.plot([r, xt], [y, y], "k-", lw=0.7)
        ax.text(xt + (-0.05 if esq else 0.05), y, f"{lab} ({r:.2f})",
                ha="right" if esq else "left", va="center", fontsize=7)
    # barras de não-significância: grupos contíguos com amplitude <= CD
    nivel, usados = 0, []
    for i in range(k):
        j = i
        while j + 1 < k and postos[j + 1] - postos[i] <= cd:
            j += 1
        if j > i and not any(a <= i and j <= b for a, b in usados):
            usados.append((i, j))
            ax.plot([postos[i] - 0.03, postos[j] + 0.03],
                    [-0.08 - nivel * 0.10] * 2, "k-", lw=1.8, solid_capstyle="butt")
            nivel += 1
    ax.plot([lo + 0.05, lo + 0.05 + cd], [0.55, 0.55], "k-", lw=1.0)
    for xx in (lo + 0.05, lo + 0.05 + cd):
        ax.plot([xx, xx], [0.50, 0.60], "k-", lw=1.0)
    ax.text(lo + 0.05 + cd / 2, 0.63, f"DC = {cd:.2f}", ha="center", va="bottom", fontsize=7)
    ax.set_title(titulo, pad=6, loc="left", x=0.0)
