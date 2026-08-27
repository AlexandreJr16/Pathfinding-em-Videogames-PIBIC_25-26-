// E10/A9: o AG original puxa entropia de std::random_device em initPopulation() e
// reproduction(), então cada fórmula reportada é uma amostra de tamanho 1.
// Aqui a MESMA entropia vira semente explícita, e só ela varia entre rodadas:
// grammar(42), operators(grammar,42) e srand(42) (conjunto de treino) ficam fixos,
// exatamente como no original. Isso isola a variabilidade que de fato afetou os
// resultados reportados, sem confundi-la com variação do conjunto de treino.
// Replica src/main.cpp:101-145.
#include "comum.h"
#include "src/synthesis/GeneticAlgorithm.h"
#include "src/synthesis/GeneticOperators.h"
#include "src/synthesis/HeuristicGrammar.h"

int main() {
  ofstream out("../medicoes/sintese_repetida.csv", ios::app);
  { ifstream chk("../medicoes/sintese_repetida.csv");
    if (chk.peek() == ifstream::traits_type::eof())
      out << "mapa,run_seed,populacao_inicial,n_geracoes,tempo_sintese_ms,"
             "formula_string,fitness_final,ast_size,ast_depth\n"; }

  for (int runSeed : {1, 2, 3, 4, 5}) {          // rodada completa antes da próxima
    for (auto &[nome, base] : MAPAS) {
      loadMap(base + ".map");
      auto scenario = loadScenario(base + ".map.scen");
      if (scenario.empty()) continue;

      auto t0 = chrono::high_resolution_clock::now();
      HeuristicGrammar grammar(42);              // fixo, como no original
      GeneticOperators operators(grammar, 42);   // fixo, como no original
      GeneticAlgorithm ga(grammar, operators, runSeed);   // <- única variação
      ga.initPopulation(80);

      vector<ScenProblem> fitnessProblems;
      int trainingSize = min((int)scenario.size(), max(150, (int)scenario.size() / 4));
      int strataSize = scenario.size() / trainingSize;
      srand(42);                                 // fixo: mesmo conjunto de treino
      for (int i = 0; i < trainingSize; i++) {
        int st = i * strataSize, en = min((int)scenario.size(), (i + 1) * strataSize);
        fitnessProblems.push_back(scenario[st + (rand() % (en - st))]);
      }
      vector<int> trainManh(fitnessProblems.size());
      for (size_t i = 0; i < fitnessProblems.size(); ++i)
        trainManh[i] = max(1, aStar(fitnessProblems[i].start, fitnessProblems[i].goal,
                                    heuristicaManhattan).expansions);

      for (int g = 0; g < 100; g++) {
        ga.evolve([&](std::shared_ptr<HeuristicNode> f) {
          long long tm = 0, tf = 0;
          for (size_t i = 0; i < fitnessProblems.size(); ++i) {
            auto h = [&](pair<int,int> s, pair<int,int> gg) {
              return (int)f->evaluate({s.first, s.second}, {gg.first, gg.second}); };
            tm += trainManh[i];
            tf += max(1, aStar(fitnessProblems[i].start, fitnessProblems[i].goal, h).expansions);
          }
          return (double)tm / (double)tf;
        });
      }
      auto best = ga.getBest();
      double ms = chrono::duration<double, milli>(
          chrono::high_resolution_clock::now() - t0).count();
      out << nome << "," << runSeed << ",80,100," << ms << ",\"" << best->toString()
          << "\"," << ga.getBestFitness() << "," << best->size() << "," << best->depth() << "\n";
      out.flush();
      cerr << "[run " << runSeed << "] " << nome << " fitness=" << ga.getBestFitness()
           << " size=" << best->size() << " (" << ms/1000 << " s)" << endl;
    }
    cerr << ">>> rodada " << runSeed << " completa" << endl;
  }
  return 0;
}
