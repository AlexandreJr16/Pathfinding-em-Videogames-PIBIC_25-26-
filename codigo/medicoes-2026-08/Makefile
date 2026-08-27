# ============================================================================
#  Programas auxiliares de medição — agosto/2026
#
#  Escritos para a reanálise estatística, para produzir números que a execução
#  original de março NÃO instrumentou (ver docs/04-achados-estatisticos.md):
#
#    medir_dijkstra          expansões do A* com h=0, baseline para normalizar
#                            expansões entre mapas de escalas diferentes  (L8)
#    medir_pivos             custo de memória e tempo de pré-computação dos
#                            pivôs, e diagnóstico do colapso de pivô   (A7, A11)
#    verifica_reprocessamento  quanto das distâncias pré-computadas muda quando
#                            o mapa é degradado                             (A0)
#    sintese_repetida        re-síntese com semente explícita, para medir a
#                            (ir)reprodutibilidade do AG                (A9, E10)
#    sintese_worker          uma síntese isolada, com checkpoint; é o processo
#                            que o pool em analise/.../scripts/sintese_pool.py
#                            dispara em paralelo
#
#  `src/` aqui é uma CÓPIA do código de março (codigo/run-referencia-2026-03/src)
#  com uma alteração deliberada: as sementes do AG viraram parâmetro explícito,
#  em vez de virem de std::random_device. É essa alteração que torna o A9
#  possível. Ver docs/00-PROVENIENCIA.md.
#
#  Rode a partir DESTE diretório: `maps` é um link simbólico para ../../maps.
# ============================================================================
CXX  = g++
BASE = src/map.cpp src/heuristics.cpp src/astar.cpp
SINT = src/synthesis/HeuristicGrammar.cpp src/synthesis/GeneticOperators.cpp \
       src/synthesis/GeneticAlgorithm.cpp

all: medir_dijkstra medir_pivos verifica_reprocessamento sintese_repetida sintese_worker

medir_dijkstra medir_pivos verifica_reprocessamento: %: %.cpp $(BASE)
	$(CXX) -O2 -std=c++17 -o $@ $^

# Mesmas flags do experimento original, para que os tempos sejam comparáveis.
sintese_repetida sintese_worker: %: %.cpp $(BASE) $(SINT)
	$(CXX) -O3 -march=native -ffast-math -fopenmp -std=c++17 -o $@ $^

clean:
	rm -f medir_dijkstra medir_pivos verifica_reprocessamento sintese_repetida sintese_worker
