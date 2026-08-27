#pragma once
#include "src/astar.h"
#include "src/heuristics.h"
#include <bits/stdc++.h>
using namespace std;

// Mesma lista e mesma ordem de src/main.cpp:48-65
static const vector<pair<string,string>> MAPAS = {
  {"arena","maps/arena"},   {"arena2","maps/arena2"},   {"brc000d","maps/brc000d"},
  {"brc100d","maps/brc100d"},{"brc101d","maps/brc101d"},{"brc201d","maps/brc201d"},
  {"brc202d","maps/brc202d"},{"brc203d","maps/brc203d"},{"den000d","maps/den000d"},
  {"den005d","maps/den005d"},{"den011d","maps/den011d"},{"den012d","maps/den012d"},
  {"den500d","maps/den500d"},{"den501d","maps/den501d"},{"den602d","maps/den602d"},
  {"hrt201n","maps/hrt201n"},{"lak506d","maps/lak506d"}};

static const vector<int> SEMENTES = {42,123,456,789,1011};
static const vector<int> NUMPIVOS = {10,20,50,100};

struct ScenProblem { pair<int,int> start, goal; double distOtima; };

// Cópia literal de src/main.cpp:22-35
static vector<ScenProblem> loadScenario(const string &scenPath) {
  vector<ScenProblem> problems; ifstream file(scenPath);
  if (!file.is_open()) return problems;
  string l; int sX,sY,gX,gY; double dO;
  file >> l >> l;
  while (file >> l >> l >> l >> l >> sX >> sY >> gX >> gY >> dO)
    problems.push_back({{sY,sX},{gY,gX},dO});
  return problems;
}

// Rotula componentes conexas 4-vizinhas do grid atual. -1 = bloqueada.
static vector<vector<int>> rotulaComponentes(vector<int>& tamanhos) {
  vector<vector<int>> comp(height, vector<int>(width,-1));
  tamanhos.clear();
  for (int i=0;i<height;i++) for (int j=0;j<width;j++) {
    if (!grid[i][j] || comp[i][j]!=-1) continue;
    int id=tamanhos.size(), n=0; queue<pair<int,int>> q;
    comp[i][j]=id; q.push({i,j});
    while(!q.empty()){ auto[x,y]=q.front(); q.pop(); n++;
      for(int k=0;k<4;k++){ int a=x+px[k], b=y+py[k];
        if(a>=0&&a<height&&b>=0&&b<width&&grid[a][b]&&comp[a][b]==-1){comp[a][b]=id;q.push({a,b});}}}
    tamanhos.push_back(n);
  }
  return comp;
}
