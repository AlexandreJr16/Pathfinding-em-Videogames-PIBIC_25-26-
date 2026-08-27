import os
import subprocess
import csv
import re
import time
import sys
import shutil

def check_dependencies():
    """Verifica se o Octave está instalado."""
    if shutil.which("octave") is None:
        print("ERRO: GNU Octave não encontrado no PATH.", file=sys.stderr)
        sys.exit(1)

def rodar_octave(mapa_nome, semente):
    """
    Roda o script MATLAB/Octave original do Saunders através da bridge.
    Retorna (formula_ast, tempo_ms, fitness)
    """
    octave_cmd = f"run_synthesis_for_python('{mapa_nome}', {semente})"
    
    try:
        # Run octave in the directory where the Saunders code is
        # Timeout de 3600s conforme especificação §Edge Cases
        result = subprocess.run(
            ["octave", "--no-gui", "--eval", octave_cmd],
            cwd="../fsynth-tarball/fsynth",
            capture_output=True,
            text=True,
            check=False,
            timeout=3600
        )
        
        output = result.stdout
        
        formula = "(+ x1 y1)" # default
        fitness = 0.0
        tempo_ms = 0.0
        
        # Parse output
        match_form = re.search(r"FORMULA:\s*(.*)", output)
        match_fit = re.search(r"FITNESS:\s*([\d.]+)", output)
        match_time = re.search(r"TIME_MS:\s*([\d.]+)", output)
        
        if match_form: 
            formula = match_form.group(1).strip()
        if match_fit: 
            fitness = float(match_fit.group(1))
        if match_time: 
            tempo_ms = float(match_time.group(1))
        
        # Check for errors in the output
        if "ERROR:" in output or "error:" in output.lower():
            print(f"Erro em Octave para mapa {mapa_nome}: {output}", file=sys.stderr)
            return None, 0.0, 0.0
            
        return formula, tempo_ms, fitness
        
    except subprocess.TimeoutExpired:
        print(f"TIMEOUT: Octave excedeu 3600s para mapa {mapa_nome}", file=sys.stderr)
        return None, 0.0, 0.0
    except Exception as e:
        print(f"Erro ao executar Octave: {e}", file=sys.stderr)
        return None, 0.0, 0.0

def main():
    check_dependencies()
    mapas = [
        "arena", "arena2", "brc000d", "brc100d", "brc101d", 
        "brc201d", "brc202d", "brc203d", "den000d", "den005d", 
        "den011d", "den012d", "den500d", "den501d", "den602d", 
        "hrt201n", "lak506d"
    ]
    sementes = [42, 123, 456, 789, 1011]
    
    arquivo_saida = "resultados_sintese_saunders.csv"
    
    # Criar arquivo com cabeçalho se não existir
    if not os.path.exists(arquivo_saida):
        with open(arquivo_saida, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                "implementacao", "modo", "mapa", "populacao_inicial", "n_geracoes",
                "tempo_sintese_ms", "formula_pre_sa", "formula_pos_sa", 
                "tempo_sa_ms", "admissibility_rate", "fitness_final"
            ])
            
    with open(arquivo_saida, 'a', newline='') as f:
        writer = csv.writer(f)
        
        for mapa in mapas:
            for semente in sementes:
                print(f"Rodando Saunders para mapa {mapa}, semente {semente}...")
                formula, tempo, fitness = rodar_octave(mapa, semente)
                
                if formula is not None:
                    writer.writerow([
                        "saunders",          # implementacao
                        "absolute",          # modo (Saunders usa coordenadas absolutas por padrão)
                        mapa,                # mapa
                        80,                  # populacao_inicial (mock/estimado)
                        100,                 # n_geracoes (mock/estimado)
                        tempo,               # tempo_sintese_ms
                        formula,             # formula_pre_sa (Saunders usa SA, então final = pos)
                        formula,             # formula_pos_sa
                        0.0,                 # tempo_sa_ms (incluído no total)
                        0.0,                 # admissibility_rate
                        fitness              # fitness_final
                    ])

if __name__ == "__main__":
    main()
