#include "map.h"

int height, width;
vector<vector<bool>> grid;
int originalTraversableCells = 0;

// Coordenadas para buscar vizinhos
int px[4] = {0, 0, 1, -1};
int py[4] = {-1, 1, 0, 0};

bool verificaPontosConectados(pair<int, int> start, pair<int, int> goal) {
  if (start.first < 0 || start.first >= height || start.second < 0 || start.second >= width ||
      goal.first < 0 || goal.first >= height || goal.second < 0 || goal.second >= width) return false;
  
  if (!grid[start.first][start.second] || !grid[goal.first][goal.second]) return false;

  vector<bool> visitado(width * height, false);
  queue<pair<int, int>> q;

  int actualX, actualY;

  visitado[start.first * width + start.second] = true;
  q.push(start);

  while (!q.empty()) {
    pair<int, int> v = q.front();
    q.pop();

    for (int i = 0; i < 4; i++) {
      actualX = v.first + px[i];
      actualY = v.second + py[i];
      int locVizinho = actualX * width + actualY;

      if (actualX >= 0 && actualX < height && actualY >= 0 && actualY < width &&
          grid[actualX][actualY] && !visitado[locVizinho]) {
        if (actualX == goal.first && actualY == goal.second) return true;
        visitado[locVizinho] = true;
        q.push({actualX, actualY});
      }
    }
  }

  return visitado[goal.first * width + goal.second];
}

// Carrega o mapa
void loadMap(const string &filename) {
  ifstream file(filename);
  string token;

  // Faz a leituras das informaç~ões do mapa
  file >> token >> token;
  file >> token >> height;
  file >> token >> width;
  file >> token;

  grid.assign(height, vector<bool>(width));
  string line;
  getline(file, line);
  originalTraversableCells = 0;

  // le o mapa
  for (int i = 0; i < height; i++) {
    getline(file, line);
    for (int j = 0; j < width; j++) {
      grid[i][j] = (line[j] == '.');
      if (grid[i][j]) originalTraversableCells++;
    }
  }
}

// Helper para pegar raio dinâmico (aprox 5% da menor dimensão)
int getDynamicSize() {
    return max(2, min(height, width) / 20);
}

int radialObstacle(int raio, double aspecto) {
  int xa = rand() % height;
  int ya = rand() % width;
  int blocked = 0;

  if (grid[xa][ya]) {
    for (int y = -raio; y <= raio; y++) {
      for (int x = -raio * aspecto; x <= raio * aspecto; x++) {
        int ix = x + xa;
        int iy = y + ya;
        float dist = sqrt(pow(x / aspecto, 2) + pow(y, 2));
        if (dist <= raio && ix >= 0 && iy >= 0 && ix < height && iy < width) {
          if (grid[ix][iy]) {
              grid[ix][iy] = false;
              blocked++;
          }
        }
      }
    }
  }
  return blocked;
}

void degradaMapa(int targetBlocked) {
  int currentBlocked = 0;
  int tries = 0;
  int raio = getDynamicSize();
  while (currentBlocked < targetBlocked && tries < height * width) {
    currentBlocked += radialObstacle(raio, 1.0);
    tries++;
  }
}

int linearObstacle(int length) {
  int xa = rand() % height;
  int ya = rand() % width;
  int blocked = 0;

  if (grid[xa][ya]) {
    int dir = rand() % 4;
    int currX = xa;
    int currY = ya;

    for (int i = 0; i < length; i++) {
      if (currX >= 0 && currX < height && currY >= 0 && currY < width) {
        if (grid[currX][currY]) {
            grid[currX][currY] = false;
            blocked++;
        }
      }
      currX += px[dir];
      currY += py[dir];
    }
  }
  return blocked;
}

void degradaMapaLinear(int targetBlocked) {
  int currentBlocked = 0;
  int tries = 0;
  int length = max(10, min(height, width) / 2); // 50% da dimensão
  while (currentBlocked < targetBlocked && tries < height * width) {
    currentBlocked += linearObstacle(length);
    tries++;
  }
}

int sparseObstacle(int raio, double density) {
  int xa = rand() % height;
  int ya = rand() % width;
  int blocked = 0;

  if (grid[xa][ya]) {
    for (int y = -raio; y <= raio; y++) {
      for (int x = -raio; x <= raio; x++) {
        int ix = xa + x;
        int iy = ya + y;
        float dist = sqrt(x * x + y * y);
        if (dist <= raio && ix >= 0 && iy >= 0 && ix < height && iy < width) {
          double chance = (rand() % 1000) / 1000.0;
          if (chance < density && grid[ix][iy]) {
            grid[ix][iy] = false;
            blocked++;
          }
        }
      }
    }
  }
  return blocked;
}

void degradaMapaSparse(int targetBlocked) {
  int currentBlocked = 0;
  int tries = 0;
  int raio = max(5, min(height, width) / 10);
  while (currentBlocked < targetBlocked && tries < height * width) {
    currentBlocked += sparseObstacle(raio, 0.4);
    tries++;
  }
}

int organicObstacle(int numCells) {
  int xa = rand() % height;
  int ya = rand() % width;
  int blocked = 0;

  if (grid[xa][ya]) {
    int currX = xa;
    int currY = ya;
    int maxIterations = numCells * 5;

    for (int i = 0; i < maxIterations && blocked < numCells; i++) {
      if (currX >= 0 && currX < height && currY >= 0 && currY < width) {
        if (grid[currX][currY]) {
          grid[currX][currY] = false;
          blocked++;
        }
      }
      int dir = rand() % 4;
      currX += px[dir];
      currY += py[dir];
      if (currX < 0 || currX >= height || currY < 0 || currY >= width) {
        currX = xa; currY = ya;
      }
    }
  }
  return blocked;
}

void degradaMapaOrganic(int targetBlocked) {
  int currentBlocked = 0;
  int tries = 0;
  int numCells = max(20, (height * width) / 250); // 2x maior
  while (currentBlocked < targetBlocked && tries < height * width) {
    currentBlocked += organicObstacle(numCells);
    tries++;
  }
}

void degradaMapaSaunders(int targetBlocked) {
  int currentBlocked = 0;
  int tries = 0;
  while (currentBlocked < targetBlocked && tries < height * width * 10) {
    int x = rand() % height;
    int y = rand() % width;
    if (grid[x][y]) {
      grid[x][y] = false;
      currentBlocked++;
    }
    tries++;
  }
}
