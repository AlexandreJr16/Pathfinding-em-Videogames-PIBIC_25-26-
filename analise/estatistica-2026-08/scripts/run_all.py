#!/usr/bin/env python3
"""Reproduz toda a análise do zero, a partir dos 4 CSVs originais + medicoes/.

    rm -rf tabelas figuras medicoes/*.pkl
    .venv/bin/python scripts/run_all.py

As medições em C++ (medicoes/dijkstra.csv, pivos_precomp.csv, reprocessamento*.csv,
sintese_repetida.csv) são pré-requisito e se refazem com:
    cd ../../codigo/medicoes-2026-08 && make && ./medir_dijkstra && ./medir_pivos
    for m in <17 mapas>; do ./verifica_reprocessamento $m 42; done
    ./sintese_repetida        # ~13-20 h
"""
import subprocess, sys, time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
PY_ = RAIZ / ".venv" / "bin" / "python"

# A ordem importa (dependências entre tabelas):
#   a7  <- a2_escore_*.csv, a6_por_mapa.csv
#   a8  <- a3_speedup_por_mapa.csv, a6_por_mapa.csv
#   a0  <- a1_delta_por_padrao.csv   (por isso a1 vem antes de a0)
ETAPAS = ["a11_pivos", "a10_descartes", "a3_estatico", "a2_ranking",
          "a4_a5_distribuicoes", "a6_subotimalidade", "a12_admissibilidade", "a7_memoria_pareto",
          "a8_formulas", "a9_reprodutibilidade", "a1_tese", "a1b_delta30", "a0_reprocessamento"]

def main():
    (RAIZ / "tabelas").mkdir(exist_ok=True)
    (RAIZ / "figuras").mkdir(exist_ok=True)
    falhas = []
    for e in ETAPAS:
        t = time.time()
        print(f"\n{'='*70}\n>>> {e}\n{'='*70}", flush=True)
        r = subprocess.run([str(PY_), str(AQUI / f"{e}.py")], cwd=RAIZ)
        print(f"<<< {e}: {'ok' if r.returncode == 0 else 'FALHOU'} ({time.time()-t:.0f}s)")
        if r.returncode: falhas.append(e)
    print(f"\n{'='*70}")
    print(f"tabelas: {len(list((RAIZ/'tabelas').glob('*.csv')))}   "
          f"figuras: {len(list((RAIZ/'figuras').glob('*.pdf')))}")
    if falhas:
        print("FALHARAM:", ", ".join(falhas)); sys.exit(1)
    print("tudo reproduzido.")

if __name__ == "__main__":
    main()
