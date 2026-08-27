import pandas as pd
import os
import subprocess
import datetime
import shutil
import sys

def get_env_info():
    """Captura informações de ambiente para o relatório."""
    try:
        octave_version = subprocess.check_output(["octave", "--version"]).decode().split("\n")[0]
    except:
        octave_version = "N/A"
    
    cxxflags = os.environ.get("CXXFLAGS", "N/A (Rodar com CXXFLAGS='...' make compare para capturar)")
    return octave_version, cxxflags

def load_data():
    saunders_file = "resultados_sintese_saunders.csv"
    ours_file = "resultados_sintese.csv"
    
    if not os.path.exists(saunders_file) or not os.path.exists(ours_file):
        print("Erro: Arquivos de dados não encontrados. Rode 'make saunders' e 'make all-modes' primeiro.")
        return None, None
        
    df_saunders = pd.read_csv(saunders_file)
    df_ours = pd.read_csv(ours_file)
    
    return df_saunders, df_ours

def archive_results():
    """Arquiva os resultados em uma pasta datada (T019)."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archive_dir = os.path.join("WPerformance", "archives", f"{timestamp}_comparison")
    os.makedirs(archive_dir, exist_ok=True)
    
    files_to_archive = [
        "resultados_sintese_saunders.csv",
        "resultados_sintese.csv",
        "resultados_base.csv",
        "resultados_robustez.csv",
        "resultados_ratio.csv"
    ]
    
    for f in files_to_archive:
        if os.path.exists(f):
            shutil.copy(f, archive_dir)
    
    print(f"\n[ARCHIVE] Resultados arquivados em: {archive_dir}")
    return archive_dir

def main():
    octave_ver, cxxflags = get_env_info()
    
    print("=" * 100)
    print(f"{'COMPARAÇÃO DIRETA DE IMPLEMENTAÇÕES (SAUNDERS vs OURS)':^100}")
    print("=" * 100)
    print(f"Ambiente: Octave: {octave_ver}")
    print(f"          CXXFLAGS: {cxxflags}")
    print("-" * 100)
    
    df_saunders, df_ours = load_data()
    if df_saunders is None or df_ours is None:
        return
        
    # Filtrar apenas os modos relevantes do nosso CSV
    df_ours_delta = df_ours[df_ours['modo'] == 'delta'].copy()
    
    # Agrupar por mapa para calcular médias (Seed Aggregation T018)
    saunders_agg = df_saunders.groupby('mapa').agg({
        'tempo_sintese_ms': 'mean',
        'fitness_final': 'mean',
        'admissibility_rate': 'mean'
    }).reset_index()
    
    ours_agg = df_ours_delta.groupby('mapa').agg({
        'tempo_sintese_ms': 'mean',
        'fitness_final': 'mean',
        'admissibility_rate': 'mean'
    }).reset_index()
    
    # Merge para comparação lado a lado
    merged = pd.merge(saunders_agg, ours_agg, on='mapa', suffixes=('_saunders', '_ours'))
    
    header = f"{'Mapa':<15} | {'Tempo Saunders':<15} | {'Tempo Ours':<15} | {'Fit Saunders':<12} | {'Fit Ours':<12} | {'Winner'}"
    print(header)
    print("-" * 100)
    
    vitorias_saunders = 0
    vitorias_ours = 0
    
    for _, row in merged.iterrows():
        mapa = row['mapa']
        ts = row['tempo_sintese_ms_saunders']
        to = row['tempo_sintese_ms_ours']
        fs = row['fitness_final_saunders']
        fo = row['fitness_final_ours']
        as_s = row['admissibility_rate_saunders']
        as_o = row['admissibility_rate_ours']
        
        # Admissibility Warning (T018)
        warn_s = " (!)" if as_s > 0 else ""
        warn_o = " (!)" if as_o > 0 else ""
        
        # Winner calculation
        winner = "Ours" if fo > fs else "Saunders"
        if winner == "Ours": vitorias_ours += 1
        else: vitorias_saunders += 1
            
        line = f"{mapa:<15} | {ts:<15.2f} | {to:<15.2f} | {fs:<12.4f}{warn_s} | {fo:<12.4f}{warn_o} | {winner}"
        print(line)
        
    print("-" * 100)
    print(f"Vitórias Saunders: {vitorias_saunders}")
    print(f"Vitórias Ours    : {vitorias_ours}")
    print("(!) Indica fórmula com inadmissibilidade detectada.")
    
    if vitorias_ours > vitorias_saunders:
        print("\nCONCLUSÃO: A implementação nativa (Ours) resultou em menos expansões médias no A*.")
    else:
        print("\nCONCLUSÃO: A implementação original (Saunders) resultou em menos expansões médias no A*.")

    # Archival step
    archive_results()

if __name__ == "__main__":
    main()
