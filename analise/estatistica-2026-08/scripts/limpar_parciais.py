#!/usr/bin/env python3
"""Remove de medicoes/reprocessamento.csv os (mapa, semente) medidos pela metade.

Um processo morto no meio de um mapa deixa menos que as 60 linhas esperadas
(5 padrões x 3 níveis x 4 configurações). Este script apaga essas linhas para que
verifica_reprocessamento possa refazer o mapa do zero, sem duplicar.
"""
import sys
from collections import Counter
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "medicoes" / "reprocessamento.csv"
linhas = p.read_text().splitlines()
cab, corpo = linhas[0], linhas[1:]
chave = lambda l: tuple(l.split(",")[:2])
c = Counter(chave(l) for l in corpo)
parciais = {k for k, n in c.items() if n != 60}
if not parciais:
    print(f"nada a limpar: {len(c)} pares (mapa,semente), todos com 60 linhas"); sys.exit()
mantidas = [l for l in corpo if chave(l) not in parciais]
tmp = p.with_suffix(".tmp"); tmp.write_text("\n".join([cab] + mantidas) + "\n"); tmp.replace(p)
for k in sorted(parciais):
    print(f"  removido {k[0]} s{k[1]}: {c[k]}/60 linhas")
print(f"{len(corpo)-len(mantidas)} linhas removidas; refaça com scripts/rodar_l5.sh")
