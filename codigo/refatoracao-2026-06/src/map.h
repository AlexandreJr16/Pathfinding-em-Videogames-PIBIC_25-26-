#pragma once
#include <bits/stdc++.h>

using namespace std;

extern int height, width;
extern vector<vector<bool>> grid;
extern int originalTraversableCells;

// Coordenadas para buscar vizinhos
extern int px[4];
extern int py[4];

bool verificaPontosConectados(pair<int, int> start, pair<int, int> goal);

// Carrega o mapa
void loadMap(const string &filename);

int radialObstacle(int raio, double aspecto);
void degradaMapa(int targetBlocked);

int linearObstacle(int length);
void degradaMapaLinear(int targetBlocked);

int sparseObstacle(int raio, double density);
void degradaMapaSparse(int targetBlocked);

int organicObstacle(int numCells);
void degradaMapaOrganic(int targetBlocked);

void degradaMapaSaunders(int targetBlocked);
