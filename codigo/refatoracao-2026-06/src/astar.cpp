#include "astar.h"

// Algoritmo A*
SearchResult aStar(pair<int, int> start, pair<int, int> goal,
                   std::function<int(pair<int, int>, pair<int, int>)> h_func) {
  SearchResult res;
  res.expansions = 0;

  // Lista aberta
  priority_queue<pair<int, tipoNo>, vector<pair<int, tipoNo>>, comparadorTipoNo>
      aberta;
  // Lista fechada
  vector<vector<bool>> fechado(height, vector<bool>(width, false));
  // Auxiliar para caminho
  vector<vector<pair<int, int>>> pai(height,
                                     vector<pair<int, int>>(width, {-1, -1}));

  // Melhor distância
  vector<vector<int>> melhorG(height, vector<int>(width, INT_MAX));

  pair<int, int> aux;
  tipoNo inicio, vizinho;
  int h, actualX, actualY, novoG;

  // Inicializaçao
  inicio.coord = start;
  inicio.pai = {-1, -1};
  inicio.g = 0;
  melhorG[start.first][start.second] = 0;
  h = h_func(start, goal);
  aberta.push({inicio.g + h, inicio});

  while (!aberta.empty()) {
    auto [f, atual] = aberta.top();
    aberta.pop();

    if (atual.g != melhorG[atual.coord.first][atual.coord.second])
      continue;

    fechado[atual.coord.first][atual.coord.second] = true;
    res.expansions++;

    // Reconstrução
    if (atual.coord == goal) {
      aux = goal;
      while (aux != start) {
        res.path.push_back(aux);
        aux = pai[aux.first][aux.second];
      }
      res.path.push_back(start);
      reverse(res.path.begin(), res.path.end());
      return res;
    }

    for (int i = 0; i < 4; i++) {
      actualX = atual.coord.first + px[i];
      actualY = atual.coord.second + py[i];

      // Verificações
      if ((actualX < 0 || actualX >= height || actualY < 0 ||
           actualY >= width) ||
          !grid[actualX][actualY] || fechado[actualX][actualY])
        continue;

      // Verifica se tá em um caminho melhor
      novoG = atual.g + 1;

      // Verifica se o novo caminho é melhor que o melhor caminho até então
      if (novoG < melhorG[actualX][actualY]) {
        melhorG[actualX][actualY] = novoG;
        pai[actualX][actualY] = atual.coord;
        vizinho.coord = {actualX, actualY};
        vizinho.pai = atual.coord;
        vizinho.g = novoG;
        h = h_func({actualX, actualY}, goal);
        aberta.push({novoG + h, vizinho});
      }
    }
  }
  return res;
}
