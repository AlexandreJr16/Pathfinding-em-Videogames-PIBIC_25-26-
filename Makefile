# ============================================================================
#  PIBIC 2025-2026 — Síntese automática de heurísticas para busca de caminhos
#  Alexandre Pereira de Souza Junior — UFAM/IComp
#
#  Sempre compile e execute A PARTIR DA RAIZ do repositório: os binários
#  procuram os mapas em `maps/`, com caminho relativo ao diretório atual.
# ============================================================================

CXX      = g++
# -march=native: instruções específicas do Ryzen 5 5500 (Zen 3), como no experimento original.
# -ffast-math : otimização agressiva de ponto flutuante (ver docs/05-problemas-conhecidos.md, P6).
CXXFLAGS = -O3 -march=native -ffast-math -fopenmp -std=c++17
BIN      = bin

REF  = codigo/run-referencia-2026-03
NOVO = codigo/refatoracao-2026-06

FONTES_COMUNS = src/map.cpp src/heuristics.cpp src/astar.cpp \
                src/synthesis/HeuristicGrammar.cpp src/synthesis/GeneticOperators.cpp \
                src/synthesis/GeneticAlgorithm.cpp

.PHONY: all referencia refatoracao testes limpar ajuda

ajuda:
	@echo "Alvos disponíveis (rode sempre da raiz do repositório):"
	@echo "  make referencia   Compila o código de MARÇO/2026 -> $(BIN)/pathfinding-referencia"
	@echo "                    É o código que gerou TODOS os dados do relatório final."
	@echo "  make refatoracao  Compila o código de JUNHO/2026 -> $(BIN)/pathfinding-refatorado"
	@echo "                    Versão posterior ao relatório; NÃO reproduz os números publicados."
	@echo "  make testes       Compila e roda os testes unitários da versão de junho."
	@echo "  make all          referencia + refatoracao"
	@echo "  make limpar       Remove $(BIN)/"
	@echo ""
	@echo "  Executar:  ./$(BIN)/pathfinding-referencia          (grava os 4 resultados_*.csv na raiz)"
	@echo "  Atenção:   a execução completa levou ~20 h nos 17 mapas."

all: referencia refatoracao

$(BIN):
	mkdir -p $(BIN)

# --- Código da run de referência (março/2026) -------------------------------
# Sem Simulated Annealing e sem os modos --mode; esquema de CSV sem as colunas
# `implementacao` e `modo`. É esta versão que produziu resultados_*.csv.
referencia: | $(BIN)
	$(CXX) $(CXXFLAGS) -o $(BIN)/pathfinding-referencia \
		$(REF)/src/main.cpp $(addprefix $(REF)/,$(FONTES_COMUNS)) \
		$(REF)/src/synthesis/SimulatedAnnealing.cpp

# --- Código refatorado (junho/2026) ----------------------------------------
refatoracao: | $(BIN)
	$(CXX) $(CXXFLAGS) -o $(BIN)/pathfinding-refatorado \
		$(NOVO)/src/main.cpp $(addprefix $(NOVO)/,$(FONTES_COMUNS)) \
		$(NOVO)/src/synthesis/SimulatedAnnealing.cpp

testes: | $(BIN)
	$(CXX) $(CXXFLAGS) -o $(BIN)/testes \
		$(addprefix $(NOVO)/,$(FONTES_COMUNS)) \
		$(NOVO)/src/synthesis/SimulatedAnnealing.cpp \
		$(NOVO)/tests/test_main.cpp $(NOVO)/tests/test_heuristics.cpp
	./$(BIN)/testes

limpar:
	rm -rf $(BIN)
