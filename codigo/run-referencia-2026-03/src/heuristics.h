#pragma once
#include "map.h"
#include "synthesis/HeuristicNode.h"
#include <functional>

// Heurística baseada em fórmula sintetizada
extern std::shared_ptr<HeuristicNode> currentFormula;

// Utilizo isso para memory-based
extern vector<pair<int, int>> pivos;
extern vector<vector<vector<int>>> distPivos;
extern map<int, vector<pair<int,int>>> pivosMap;

// Gerar números aleatórios
int randomNumbers(int num);

/*
 * Metodologia de Seleção de Pivôs: Farthest-First Traversal (Max-Min Distance)
 * Artigo Seminal: "Computing Point-to-Point Shortest Paths from External Memory" (Andrew V. Goldberg e Renato F. Werneck, 2005) - Algoritmo ALT.
 *
 * Como funciona: O 1º pivô é escolhido aleatoriamente. O 2º pivô é o ponto mais distante do 1º.
 * O 3º pivô é o ponto cuja menor distância para os pivôs já existentes seja a maior possível (maximiza a distância mínima).
 * Isso garante uma dispersão espacial geométrica ótima e minimiza áreas do mapa sem representação na heurística de memória,
 * elevando a performance da Desigualdade Triangular.
 */
vector<pair<int, int>> generatePivots(int n);

// BFS dos pivos até todos os pontos
vector<vector<int>> bfsPivo(pair<int, int> pivo);

// Pre-computa a distancia de todos os pontos a todos os pivôs
void computarDistPivos(int n);

// Heuristica baseada em memória
int heuristicaMemoryBased(pair<int, int> s, pair<int, int> goal);

// Heuristica Manhattan
int heuristicaManhattan(pair<int, int> start, pair<int, int> goal);

// Heurística Formula
int heuristicaFormula(pair<int, int> s, pair<int, int> goal);

// Heurística Zero (Dijkstra)
int heuristicaZero(pair<int, int> s, pair<int, int> goal);

//Carrega pivos salvos antes
void computarDistPivosFixos(vector<pair<int,int>> pivosFixos);
