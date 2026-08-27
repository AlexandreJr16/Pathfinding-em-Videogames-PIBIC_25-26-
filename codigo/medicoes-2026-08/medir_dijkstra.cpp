// Baseline h=0: teto de expansões, para normalizar entre mapas de escalas diferentes.
// Não depende de semente (A* com h=0 é determinístico), então roda 1x por (mapa, instância).
#include "comum.h"

int main() {
  ofstream out("../medicoes/dijkstra.csv");
  out << "mapa,id_problema,exp_dijkstra,caminho_otimo\n";
  for (auto &[nome, base] : MAPAS) {
    loadMap(base + ".map");
    auto scenario = loadScenario(base + ".map.scen");
    auto t1 = chrono::high_resolution_clock::now();
    for (size_t i = 0; i < scenario.size(); ++i) {
      auto r = aStar(scenario[i].start, scenario[i].goal, heuristicaZero);
      out << nome << "," << i << "," << r.expansions << "," << (int)r.path.size() - 1 << "\n";
    }
    auto t2 = chrono::high_resolution_clock::now();
    cerr << nome << ": " << scenario.size() << " instancias em "
         << chrono::duration<double>(t2 - t1).count() << " s" << endl;
    out.flush();
  }
  cerr << ">>> dijkstra.csv pronto" << endl;
  return 0;
}
