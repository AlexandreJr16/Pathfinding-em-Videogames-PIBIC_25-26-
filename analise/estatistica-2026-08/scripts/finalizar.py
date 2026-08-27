#!/usr/bin/env python3
"""Fecha a análise quando os jobs de fundo terminarem.

Espera o pool de síntese (A9) e a extensão L5 acabarem, reconsolida os CSVs,
re-roda o pipeline inteiro e regenera as páginas HTML. Pode ser chamado a
qualquer momento: se os jobs ainda estiverem rodando, ele espera; se já
acabaram, apenas refaz tudo com os dados finais.

    .venv/bin/python scripts/finalizar.py            # espera e finaliza
    .venv/bin/python scripts/finalizar.py --agora    # não espera, usa o que houver
"""
import argparse, subprocess, sys, time
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PY_ = RAIZ / ".venv" / "bin" / "python"

def rodando(padrao):
    return subprocess.run(["pgrep", "-f", padrao], capture_output=True).returncode == 0

def esperar():
    while rodando("sintese_pool.py") or rodando("rodar_l5.sh"):
        pend = [n for n, p in (("A9", "sintese_pool.py"), ("L5", "rodar_l5.sh")) if rodando(p)]
        print(f"  aguardando {', '.join(pend)}… ({time.strftime('%H:%M')})", flush=True)
        time.sleep(300)

def main():
    a = argparse.ArgumentParser(); a.add_argument("--agora", action="store_true")
    if not a.parse_args().agora:
        esperar()
    print(">>> consolidando sínteses")
    subprocess.run([PY_, RAIZ / "scripts" / "sintese_pool.py", "--merge"], cwd=RAIZ)
    print(">>> re-rodando o pipeline com os dados finais")
    r = subprocess.run([PY_, RAIZ / "scripts" / "run_all.py"], cwd=RAIZ)
    if r.returncode:
        print("pipeline falhou — nada foi regenerado"); sys.exit(1)
    for g in ("gerar_artefato.py", "gerar_artefato_correcoes.py"):
        subprocess.run([PY_, RAIZ / "scripts" / g], cwd=RAIZ)
    # espelha os entregáveis no repositório do relatório
    dest = Path("/home/alejr/RelatorioFinal_Modelo_AlexandrePereira_PIBIC_2025_2026/analise_estatistica")
    if dest.exists():
        for f in ("RESUMO.md", "LIMITACOES.md", "CORRECOES_TEXTO.md"):
            (dest / f).write_bytes((RAIZ / f).read_bytes())
        subprocess.run(["cp", "-r", str(RAIZ / "tabelas"), str(RAIZ / "figuras"), str(dest)])
        print(f">>> espelhado em {dest}")
    print("\n>>> ANÁLISE FECHADA. As páginas HTML foram regeneradas em disco;")
    print("    para republicar os links, peça numa próxima sessão do Claude Code.")

if __name__ == "__main__":
    main()
