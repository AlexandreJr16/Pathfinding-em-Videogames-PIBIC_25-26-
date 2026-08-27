#include "astar.h"
#include "heuristics.h"
#include "synthesis/GeneticAlgorithm.h"
#include "synthesis/GeneticOperators.h"
#include "synthesis/HeuristicGrammar.h"
#include <bits/stdc++.h>

using namespace std;

struct MapConfig {
  string name;
  string mapPath;
  string scenPath;
};

struct ScenProblem {
  pair<int, int> start;
  pair<int, int> goal;
  double distOtima;
};

vector<ScenProblem> loadScenario(const string &scenPath) {
  vector<ScenProblem> problems;
  ifstream file(scenPath);
  if (!file.is_open())
    return problems;
  string l;
  int sX, sY, gX, gY;
  double dO;
  file >> l >> l; // Skip header
  while (file >> l >> l >> l >> l >> sX >> sY >> gX >> gY >> dO) {
    problems.push_back({{sY, sX}, {gY, gX}, dO});
  }
  return problems;
}

void writeCSVHeader(ofstream &file, const string &filename, const string &header) {
    ifstream checkFile(filename);
    bool isEmpty = checkFile.peek() == ifstream::traits_type::eof();
    checkFile.close();
    if (isEmpty) {
        file << header << "\n";
    }
}

int main() {
  // Lista Completa de Mapas para o Experimento em Lote
  vector<MapConfig> mapas = {
      {"arena", "maps/arena.map", "maps/arena.map.scen"},
      {"arena2", "maps/arena2.map", "maps/arena2.map.scen"},
      {"brc000d", "maps/brc000d.map", "maps/brc000d.map.scen"},
      {"brc100d", "maps/brc100d.map", "maps/brc100d.map.scen"},
      {"brc101d", "maps/brc101d.map", "maps/brc101d.map.scen"},
      {"brc201d", "maps/brc201d.map", "maps/brc201d.map.scen"},
      {"brc202d", "maps/brc202d.map", "maps/brc202d.map.scen"},
      {"brc203d", "maps/brc203d.map", "maps/brc203d.map.scen"},
      {"den000d", "maps/den000d.map", "maps/den000d.map.scen"},
      {"den005d", "maps/den005d.map", "maps/den005d.map.scen"},
      {"den011d", "maps/den011d.map", "maps/den011d.map.scen"},
      {"den012d", "maps/den012d.map", "maps/den012d.map.scen"},
      {"den500d", "maps/den500d.map", "maps/den500d.map.scen"},
      {"den501d", "maps/den501d.map", "maps/den501d.map.scen"},
      {"den602d", "maps/den602d.map", "maps/den602d.map.scen"},
      {"hrt201n", "maps/hrt201n.map", "maps/hrt201n.map.scen"},
      {"lak506d", "maps/lak506d.map", "maps/lak506d.map.scen"}};

  // Configurações Metodológicas
  vector<int> sementes = {42, 123, 456, 789, 1011};
  vector<int> numPivos = {10, 20, 50, 100};
  vector<double> porcentagensPadrao = {0.1, 0.2, 0.3};

  // Tabelas de Saída (Modo Append habilitado)
  ofstream csvBase("resultados_base.csv", ios::app);
  writeCSVHeader(csvBase, "resultados_base.csv", "mapa,semente,id_problema,heuristica,n_pivos,expansoes,tempo_ms,caminho_tamanho");

  ofstream csvRobustez("resultados_robustez.csv", ios::app);
  writeCSVHeader(csvRobustez, "resultados_robustez.csv", "mapa,semente,id_problema,tipo_degradacao,n_pivos,porcentagem_bloqueio,"
                 "exp_orig_manh,exp_deg_manh,exp_orig_form,exp_deg_form,exp_orig_mem,exp_deg_mem,"
                 "path_orig_manh,path_deg_manh,path_orig_form,path_deg_form,path_orig_mem,path_deg_mem,"
                 "tempo_orig_manh_ms,tempo_deg_manh_ms,tempo_orig_form_ms,tempo_deg_form_ms,tempo_orig_mem_ms,tempo_deg_mem_ms");

  ofstream csvRatio("resultados_ratio.csv", ios::app);
  writeCSVHeader(csvRatio, "resultados_ratio.csv", "mapa,semente,id_problema,caminho_otimo,caminho_formula,ratio");

  ofstream csvSintese("resultados_sintese.csv", ios::app);
  writeCSVHeader(csvSintese, "resultados_sintese.csv", "mapa,populacao_inicial,n_geracoes,tempo_sintese_ms,formula_string,fitness_final");

  auto tExperimentoInicio = chrono::high_resolution_clock::now();
  long long totalLinhasRobustez = 0;
  map<string, map<int, int>> sobreviventes;

  for (const auto &config : mapas) {
    cout << "\n>>> INICIANDO MAPA: " << config.name << " <<<" << endl;
    loadMap(config.mapPath);
    auto scenario = loadScenario(config.scenPath);
    if (scenario.empty()) {
      cerr << "Erro: Cenário não encontrado para " << config.name << endl;
      continue;
    }

    // 1. SÍNTESE DE HEURÍSTICA (Uma vez por mapa)
    auto tSinteseInicio = chrono::high_resolution_clock::now();
    HeuristicGrammar grammar(42); // Semente fixa para síntese
    GeneticOperators operators(grammar, 42);
    GeneticAlgorithm ga(grammar, operators);
    ga.initPopulation(80);

    vector<ScenProblem> fitnessProblems;
    int trainingSize = min((int)scenario.size(), max(150, (int)scenario.size() / 4));
    int strataSize = scenario.size() / trainingSize;
    srand(42);
    for (int i = 0; i < trainingSize; i++) {
      int start = i * strataSize;
      int end = min((int)scenario.size(), (i + 1) * strataSize);
      int idx = start + (rand() % (end - start));
      fitnessProblems.push_back(scenario[idx]);
    }

    vector<int> trainingManhattanExp(fitnessProblems.size());
    for (size_t i = 0; i < fitnessProblems.size(); ++i) {
      auto res = aStar(fitnessProblems[i].start, fitnessProblems[i].goal, heuristicaManhattan);
      trainingManhattanExp[i] = max(1, res.expansions);
    }

    cout << "  > Evoluindo heurística..." << endl;
    for (int g = 0; g < 100; g++) {
      ga.evolve([&](std::shared_ptr<HeuristicNode> formula) {
        long long totalExpManh = 0, totalExpForm = 0;
        for (size_t i = 0; i < fitnessProblems.size(); ++i) {
          auto h_local = [&](pair<int, int> s, pair<int, int> g) {
            return (int)formula->evaluate({s.first, s.second}, {g.first, g.second});
          };
          auto res = aStar(fitnessProblems[i].start, fitnessProblems[i].goal, h_local);
          totalExpManh += trainingManhattanExp[i];
          totalExpForm += max(1, res.expansions);
        }
        return (double)totalExpManh / (double)totalExpForm;
      });
    }
    currentFormula = ga.getBest();
    auto tSinteseFim = chrono::high_resolution_clock::now();
    double tempoSinteseMs = chrono::duration<double, milli>(tSinteseFim - tSinteseInicio).count();
    
    csvSintese << config.name << ",80,100," << tempoSinteseMs << ",\"" << currentFormula->toString() << "\"," << ga.getBestFitness() << endl;
    cout << "  > Heurística Campeã: " << currentFormula->toString() << " (Fitness: " << ga.getBestFitness() << ")" << endl;

    for (int semente : sementes) {
      cout << "  > SEMENTE: " << semente << endl;
      srand(semente);
      
      struct PerfData { int exp; double time; int path; };
      vector<PerfData> baseManh(scenario.size()), baseForm(scenario.size());
      map<int, vector<PerfData>> baseMem;
      map<int, vector<pair<int, int>>> pivosPorN;

      // 2. BASELINE (Mapa Original)
      cout << "    - Executando baselines..." << endl;
      for (size_t i = 0; i < scenario.size(); ++i) {
        // Manhattan
        auto t1 = chrono::high_resolution_clock::now();
        auto resM = aStar(scenario[i].start, scenario[i].goal, heuristicaManhattan);
        auto t2 = chrono::high_resolution_clock::now();
        baseManh[i] = {resM.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)resM.path.size() - 1};
        csvBase << config.name << "," << semente << "," << i << ",manhattan,0," << baseManh[i].exp << "," << baseManh[i].time << "," << baseManh[i].path << endl;

        // Formula
        t1 = chrono::high_resolution_clock::now();
        auto resF = aStar(scenario[i].start, scenario[i].goal, heuristicaFormula);
        t2 = chrono::high_resolution_clock::now();
        baseForm[i] = {resF.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)resF.path.size() - 1};
        csvBase << config.name << "," << semente << "," << i << ",formula,0," << baseForm[i].exp << "," << baseForm[i].time << "," << baseForm[i].path << endl;

        // Ratio (Dijkstra)
        auto resD = aStar(scenario[i].start, scenario[i].goal, heuristicaZero);
        double ratio = (resD.path.size() <= 1) ? 1.0 : (double)(resF.path.size() - 1) / (double)(resD.path.size() - 1);
        csvRatio << config.name << "," << semente << "," << i << "," << (int)resD.path.size() - 1 << "," << (int)resF.path.size() - 1 << "," << ratio << endl;
      }

      for (int n : numPivos) {
        computarDistPivos(n);
        pivosPorN[n] = pivos;
        vector<PerfData> currentMem(scenario.size());
        for (size_t i = 0; i < scenario.size(); ++i) {
          auto t1 = chrono::high_resolution_clock::now();
          auto res = aStar(scenario[i].start, scenario[i].goal, heuristicaMemoryBased);
          auto t2 = chrono::high_resolution_clock::now();
          currentMem[i] = {res.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)res.path.size() - 1};
          csvBase << config.name << "," << semente << "," << i << ",memory," << n << "," << currentMem[i].exp << "," << currentMem[i].time << "," << currentMem[i].path << endl;
        }
        baseMem[n] = currentMem;
      }

      // 3. ROBUSTEZ (Degradações)
      cout << "    - Testando robustez..." << endl;
      vector<vector<bool>> gridOriginal = grid;
      struct DegType { string name; function<void(int)> func; };
      vector<DegType> degs = {
          {"Radial", [](int n) { degradaMapa(n); }},
          {"Linear", [](int n) { degradaMapaLinear(n); }},
          {"Sparse", [](int n) { degradaMapaSparse(n); }},
          {"Organic", [](int n) { degradaMapaOrganic(n); }},
          {"Stochastic", [](int n) { degradaMapaSaunders(n); }}};

      for (auto &deg : degs) {
        grid = gridOriginal;
        srand(semente); // Mesma semente para degradação cumulativa
        
        map<double, vector<vector<bool>>> gridsPorPct;
        int lastTarget = 0;
        for (double pct : porcentagensPadrao) {
          int target = static_cast<int>(originalTraversableCells * pct);
          deg.func(target - lastTarget);
          gridsPorPct[pct] = grid;
          lastTarget = target;
        }

        // Seleção de pares no estado 30%
        grid = gridsPorPct[0.3];
        vector<int> problemasValidos;
        for (size_t i = 0; i < scenario.size(); ++i) {
          if (baseManh[i].path >= 0 && verificaPontosConectados(scenario[i].start, scenario[i].goal)) {
            problemasValidos.push_back(i);
          }
        }

        for (double pct : porcentagensPadrao) {
          grid = gridsPorPct[pct];
          
          // Pre-executa Manh e Form para esta pct
          vector<PerfData> degManh(scenario.size()), degForm(scenario.size());
          for (int i : problemasValidos) {
            auto t1 = chrono::high_resolution_clock::now();
            auto resM = aStar(scenario[i].start, scenario[i].goal, heuristicaManhattan);
            auto t2 = chrono::high_resolution_clock::now();
            degManh[i] = {resM.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)resM.path.size() - 1};

            t1 = chrono::high_resolution_clock::now();
            auto resF = aStar(scenario[i].start, scenario[i].goal, heuristicaFormula);
            t2 = chrono::high_resolution_clock::now();
            degForm[i] = {resF.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)resF.path.size() - 1};
          }

          for (int n : numPivos) {
            computarDistPivosFixos(pivosPorN[n]);
            for (int i : problemasValidos) {
              auto t1 = chrono::high_resolution_clock::now();
              auto resMem = aStar(scenario[i].start, scenario[i].goal, heuristicaMemoryBased);
              auto t2 = chrono::high_resolution_clock::now();
              PerfData dMem = {resMem.expansions, chrono::duration<double, milli>(t2 - t1).count(), (int)resMem.path.size() - 1};

              csvRobustez << config.name << "," << semente << "," << i << "," << deg.name << "," << n << "," << pct << ","
                          << baseManh[i].exp << "," << degManh[i].exp << ","
                          << baseForm[i].exp << "," << degForm[i].exp << ","
                          << baseMem[n][i].exp << "," << dMem.exp << ","
                          << baseManh[i].path << "," << degManh[i].path << ","
                          << baseForm[i].path << "," << degForm[i].path << ","
                          << baseMem[n][i].path << "," << dMem.path << ","
                          << baseManh[i].time << "," << degManh[i].time << ","
                          << baseForm[i].time << "," << degForm[i].time << ","
                          << baseMem[n][i].time << "," << dMem.time << endl;
              totalLinhasRobustez++;
            }
          }
        }
        if (deg.name == "Radial") sobreviventes[config.name][semente] = problemasValidos.size();
      }
      grid = gridOriginal;
      csvBase.flush(); csvRobustez.flush(); csvRatio.flush(); csvSintese.flush();
    }
  }

  auto tExperimentoFim = chrono::high_resolution_clock::now();
  double tempoTotalMs = chrono::duration<double, milli>(tExperimentoFim - tExperimentoInicio).count();

  csvBase.close(); csvRobustez.close(); csvRatio.close(); csvSintese.close();
  cout << "\n>>> Experimento Metodológico Completo Concluído." << endl;
  cout << "  > Tempo Total: " << tempoTotalMs / 1000.0 << " s" << endl;
  cout << "  > Total de Linhas no CSV de Robustez: " << totalLinhasRobustez << endl;
  cout << "  > Sobreviventes por Mapa/Semente (Filtro 30%):" << endl;
  for (auto const& [mapName, seedMap] : sobreviventes) {
      cout << "    - " << mapName << ": ";
      for (auto const& [seed, count] : seedMap) {
          cout << "[S" << seed << ": " << count << "] ";
      }
      cout << endl;
  }
  return 0;
}
