#pragma once
#include "heuristics.h"
#include <functional>

typedef struct tipoNo {
  pair<int, int> coord;
  pair<int, int> pai;
  int g;
} tipoNo;

struct comparadorTipoNo {
  bool operator()(const pair<int, tipoNo> &a, const pair<int, tipoNo> b) {
    // O desempate do Saunders
    if (a.first == b.first)
      return a.second.g < b.second.g;
    return a.first > b.first;
  }
};

struct SearchResult {
  vector<pair<int, int>> path;
  int expansions;
};

SearchResult aStar(pair<int, int> start, pair<int, int> goal,
                   std::function<int(pair<int, int>, pair<int, int>)> h_func);
