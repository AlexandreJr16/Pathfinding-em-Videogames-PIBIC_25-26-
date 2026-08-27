// E9 + A11: tempo de pré-computação dos pivôs e diagnóstico de colapso.
// Reproduz exatamente o consumo de rand() de src/main.cpp:147-191:
//   srand(semente) -> baselines (não consomem rand) -> computarDistPivos(n) para n em ordem.
#include "comum.h"

int main() {
  ofstream out("../medicoes/pivos_precomp.csv");
  out << "mapa,semente,n_pivos,tempo_precomp_ms,n_pivos_gerados,"
         "pivos_fora_maior_comp,primeiro_pivo_fora,frac_consultas_h_zero,h_medio\n";
  out << fixed << setprecision(6);

  for (auto &[nome, base] : MAPAS) {
    loadMap(base + ".map");
    auto scenario = loadScenario(base + ".map.scen");
    vector<int> tam; auto comp = rotulaComponentes(tam);
    int maior = max_element(tam.begin(), tam.end()) - tam.begin();
    cerr << nome << " |S|=" << originalTraversableCells << " comps=" << tam.size()
         << " maior=" << tam[maior] << " consultas=" << scenario.size() << endl;

    for (int semente : SEMENTES) {
      srand(semente);                       // igual a main.cpp:149
      for (int n : NUMPIVOS) {              // ordem preservada: 10,20,50,100
        auto t1 = chrono::high_resolution_clock::now();
        computarDistPivos(n);               // Farthest-First + |P| BFS
        auto t2 = chrono::high_resolution_clock::now();
        double ms = chrono::duration<double, milli>(t2 - t1).count();

        int fora = 0;
        for (auto &p : pivos) if (comp[p.first][p.second] != maior) fora++;
        int primFora = pivos.empty() ? -1 : (comp[pivos[0].first][pivos[0].second] != maior);

        long long zeros = 0, soma = 0;
        for (auto &pr : scenario) {
          int h = heuristicaMemoryBased(pr.start, pr.goal);
          if (h == 0) zeros++;
          soma += h;
        }
        out << nome << "," << semente << "," << n << "," << ms << "," << pivos.size()
            << "," << fora << "," << primFora << ","
            << (double)zeros / scenario.size() << ","
            << (double)soma / scenario.size() << "\n";
        out.flush();
      }
    }
  }
  cerr << ">>> pivos_precomp.csv pronto" << endl;
  return 0;
}
