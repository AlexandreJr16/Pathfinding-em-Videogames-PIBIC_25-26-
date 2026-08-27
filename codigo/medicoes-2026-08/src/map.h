#pragma once
#include <bits/stdc++.h>

using namespace std;

extern int height, width;
extern vector<vector<bool>> grid;
extern int originalTraversableCells;

// Coordenadas para buscar vizinhos
extern int px[4];
extern int py[4];

bool verificaPontosConectados(pair<int, int> start, pair<int,int> goal);

// Carrega o mapa
void loadMap(const string &filename);

/*
 * Nome: radialObstacle
 * Cenário: Simula explosões de artilharia, meteoros ou construção de bases (bloqueio de área densa).
 * Implementação: Sorteia um centro e bloqueia um maciço contínuo em formato circular. 
 */
int radialObstacle(int raio, double aspecto);
void degradaMapa(int targetBlocked);

/*
 * Nome: linearObstacle
 * Cenário: Simula muros em jogos RTS, fechamento de vias, pontes caídas ou trincheiras longas.
 */
int linearObstacle(int length);
void degradaMapaLinear(int targetBlocked);

/*
 * Nome: sparseObstacle
 * Cenário: Simula campos minados, escombros esparsos após batalhas ou terrenos rugosos (pântano denso).
 */
int sparseObstacle(int raio, double density);
void degradaMapaSparse(int targetBlocked);

/*
 * Nome: organicObstacle
 * Cenário: Simula o espalhamento de fluidos (água, lava), incêndios florestais ou infestações (Zerg Creep).
 */
int organicObstacle(int numCells);
void degradaMapaOrganic(int targetBlocked);

// Saunders (2024) Stochastic Modification
void degradaMapaSaunders(int targetBlocked);
