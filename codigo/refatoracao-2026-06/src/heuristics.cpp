#include "heuristics.h"

// Utilizo isso para memory-based
vector<pair<int, int>> pivos;
vector<vector<vector<int>>> distPivos;

// Gerar números aleatórios
int randomNumbers(int num) { return rand() % num; }

// Gera pivôs usando Farthest-First Traversal (Max-Min)
vector<pair<int, int>> generatePivots(int n) {
  vector<pair<int, int>> pivotList;
  if (n <= 0)
    return pivotList;

  pair<int, int> pivot;
  // 1. O primeiro pivô é sempre aleatório
  int tries = 0;
  while (tries < height * width * 2) {
    pivot.first = randomNumbers(height);
    pivot.second = randomNumbers(width);
    if (grid[pivot.first][pivot.second]) {
      pivotList.push_back(pivot);
      break;
    }
    tries++;
  }

  if (pivotList.empty() || n == 1)
    return pivotList;

  // 2. Guarda a menor distância de cada bloco no mapa para qualquer pivô
  // escolhido inicialmente, é a distância apenas do 1º pivô
  vector<vector<int>> minDists = bfsPivo(pivotList[0]);

  // 3. Escolhe iterativamente os próximos n-1 pivôs
  while (pivotList.size() < n) {
    int maxDist = -1;
    pair<int, int> nextPivot = {-1, -1};

    // Procura o ponto válido que tem a MAIOR distância mínima (está mais longe
    // de todos os pivôs atuais)
    for (int i = 0; i < height; i++) {
      for (int j = 0; j < width; j++) {
        if (grid[i][j] && minDists[i][j] > maxDist) {
          maxDist = minDists[i][j];
          nextPivot = {i, j};
        }
      }
    }

    // Se encontrou um candidato válido no mesmo subgrafo
    if (nextPivot.first != -1 && maxDist > 0) {
      pivotList.push_back(nextPivot);

      // Roda uma BFS a partir do novo pivô escolhido
      vector<vector<int>> newDists = bfsPivo(nextPivot);

      // Atualiza a tabela global de menores distâncias para um pivô
      for (int i = 0; i < height; i++) {
        for (int j = 0; j < width; j++) {
          if (grid[i][j]) {
            if (minDists[i][j] == -1) {
              minDists[i][j] = newDists[i][j];
            } else if (newDists[i][j] != -1) {
              minDists[i][j] = min(minDists[i][j], newDists[i][j]);
            }
          }
        }
      }
    } else {
      // Sorteia o restante aleatoriamente para evitar loop infinito
      int tries_fallback = 0;
      while (tries_fallback < height * width * 2) {
        pivot.first = randomNumbers(height);
        pivot.second = randomNumbers(width);
        if (grid[pivot.first][pivot.second]) {
          pivotList.push_back(pivot);
          break;
        }
        tries_fallback++;
      }
      if (tries_fallback >= height * width * 2)
        break; // Não consegue mais pivôs
    }
  }

  return pivotList;
}

// Carrega pivos fixos
void computarDistPivosFixos(vector<pair<int, int>> pivosFixos) {
  pivos = pivosFixos;
  distPivos.clear();
  for (auto &pivo : pivos) {
    distPivos.push_back(bfsPivo(pivo));
  }
}

// BFS dos pivos até todos os pontos
vector<vector<int>> bfsPivo(pair<int, int> pivo) {
  vector<vector<int>> dists(height, vector<int>(width, -1));
  vector<bool> visitado(width * height, false);
  queue<pair<int, int>> q;
  int actualX, actualY;

  visitado[pivo.first * width + pivo.second] = true;
  q.push(pivo);
  dists[pivo.first][pivo.second] = 0;

  while (!q.empty()) {
    pair<int, int> v = q.front();
    // isso soa como k-pop
    q.pop();

    for (int i = 0; i < 4; i++) {
      actualX = v.first + px[i];
      actualY = v.second + py[i];
      int locVizinho = actualX * width + actualY;
      if (actualX >= 0 && actualX < height && actualY >= 0 && actualY < width &&
          grid[actualX][actualY] && !visitado[locVizinho]) {
        visitado[locVizinho] = true;
        dists[actualX][actualY] = dists[v.first][v.second] + 1;
        q.push({actualX, actualY});
      }
    }
  }
  return dists;
}

// Pre-computa a distancia de todos os pontos a todos os pivôs
void computarDistPivos(int n) {
  pivos = generatePivots(n);
  distPivos.clear();
  for (auto &pivo : pivos) {
    distPivos.push_back(bfsPivo(pivo));
  }
}

// Heuristica baseada em memória
int heuristicaMemoryBased(pair<int, int> s, pair<int, int> goal) {
  int dist = 0;
  for (unsigned i = 0; i < pivos.size(); i++) {
    int dS = distPivos[i][s.first][s.second];
    int dG = distPivos[i][goal.first][goal.second];

    // Só aplica a desigualdade triangular se ambos os pontos alcançarem o pivô
    if (dS != -1 && dG != -1) {
      dist = max(abs(dS - dG), dist);
    }
  }
  return dist;
}

// Heurística Manhattan
int heuristicaManhattan(pair<int, int> start, pair<int, int> goal) {

  // Manhattan
  return abs(start.first - goal.first) + abs(start.second - goal.second);
}

// Heurística baseada em fórmula sintetizada
std::shared_ptr<HeuristicNode> currentFormula = nullptr;

// Heuristica de fórmula utilizando AST traduzida de Saunders (2024)
int heuristicaFormula(pair<int, int> s, pair<int, int> goal) {
  if (currentFormula) {
    Point start = {s.first, s.second};
    Point target = {goal.first, goal.second};
    return std::max(0, (int)std::lround(currentFormula->evaluate(start, target)));
  }

  int dx = abs(s.first - goal.first);
  int dy = abs(s.second - goal.second);
  return 75 * max(dx, dy);
}

// Usado só pra testes no inicio (Deixar de recordação)
int heuristicaZero(pair<int, int> s, pair<int, int> goal) { return 0; }
