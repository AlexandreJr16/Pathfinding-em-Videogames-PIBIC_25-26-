// A0: o relatório (main.tex:534, :695) afirma "sem reprocessamento das heurísticas".
// src/main.cpp:227 faz grid = gridsPorPct[pct] e :244 chama computarDistPivosFixos(),
// que roda bfsPivo() sobre o grid JÁ DEGRADADO. Este programa decide a questão e,
// de quebra, mede o que o experimento teria medido com distâncias de fato congeladas.
#include "comum.h"

struct DegType { string name; function<void(int)> func; };

int main(int argc, char** argv) {
  string alvo = argc > 1 ? argv[1] : "den501d";
  int semente = argc > 2 ? atoi(argv[2]) : 42;

  ofstream out("../medicoes/reprocessamento.csv", ios::app);
  { ifstream c("../medicoes/reprocessamento.csv"); if (c.peek()!=ifstream::traits_type::eof()) out.seekp(0,ios::end); else
  out << "mapa,semente,padrao,nivel,n_pivos,pivos_iguais,celulas_comparadas,"
         "celulas_diferentes,frac_diferentes,viraram_inalcancaveis,dist_max_aumento\n"; }
  ofstream out2("../medicoes/reprocessamento_expansoes.csv", ios::app);
  { ifstream c("../medicoes/reprocessamento_expansoes.csv"); if (c.peek()==ifstream::traits_type::eof())
    out2 << "mapa,semente,padrao,nivel,n_pivos,n_instancias,"
            "exp_orig,exp_deg_fresco,exp_deg_congelado,delta_fresco,delta_congelado\n"; }
  out << fixed << setprecision(6); out2 << fixed << setprecision(4);

  // Idempotência: se este (mapa, semente) já está no CSV, não refaz nem duplica.
  // O programa grava em modo append, então reinvocar sem esta checagem somaria
  // linhas repetidas em vez de retomar.
  {
    // Conta as linhas em vez de só checar existência: uma medição interrompida
    // pela metade deixaria o par (mapa,semente) incompleto para sempre se
    // bastasse "existe alguma linha".
    const int POR_CELULA = 5 * 3 * 4;   // padrões x níveis x configurações de pivô
    std::ifstream j("../medicoes/reprocessamento.csv");
    std::string l, chave = alvo + "," + std::to_string(semente) + ",";
    int n = 0;
    while (std::getline(j, l))
      if (l.rfind(chave, 0) == 0) n++;
    if (n >= POR_CELULA) {
      std::cerr << "[" << alvo << " s" << semente << " já medido — pulando]\n";
      return 0;
    }
    if (n > 0) {
      std::cerr << "[" << alvo << " s" << semente << " tem " << n << "/" << POR_CELULA
                << " linhas — apague-as antes de remedir]\n";
      return 3;
    }
  }

  for (auto &[nome, base] : MAPAS) {
    if (nome != alvo) continue;
    loadMap(base + ".map");
    auto scenario = loadScenario(base + ".map.scen");

    // 1. Pivôs e distâncias no mapa ORIGINAL, na mesma ordem de main.cpp
    srand(semente);
    map<int, vector<pair<int,int>>> pivosPorN;
    map<int, vector<vector<vector<int>>>> distOriginal;
    vector<int> expOrig(scenario.size());
    map<int, vector<int>> expOrigMem;
    for (int n : NUMPIVOS) {
      computarDistPivos(n);
      pivosPorN[n] = pivos;
      distOriginal[n] = distPivos;
      vector<int> e(scenario.size());
      for (size_t i = 0; i < scenario.size(); ++i)
        e[i] = aStar(scenario[i].start, scenario[i].goal, heuristicaMemoryBased).expansions;
      expOrigMem[n] = e;
    }
    auto gridOriginal = grid;

    vector<DegType> degs = {
      {"Radial",[](int n){degradaMapa(n);}}, {"Linear",[](int n){degradaMapaLinear(n);}},
      {"Sparse",[](int n){degradaMapaSparse(n);}}, {"Organic",[](int n){degradaMapaOrganic(n);}},
      {"Stochastic",[](int n){degradaMapaSaunders(n);}}};

    for (auto &deg : degs) {
      grid = gridOriginal; srand(semente);          // igual a main.cpp:205-206
      map<double, vector<vector<bool>>> gridsPorPct; int last = 0;
      for (double pct : {0.1, 0.2, 0.3}) {
        int target = (int)(originalTraversableCells * pct);
        deg.func(target - last); gridsPorPct[pct] = grid; last = target;
      }
      // pares válidos no estado de 30%, igual a main.cpp:217-224
      grid = gridsPorPct[0.3];
      vector<int> validos;
      for (size_t i = 0; i < scenario.size(); ++i)
        if (verificaPontosConectados(scenario[i].start, scenario[i].goal)) validos.push_back(i);

      for (double pct : {0.1, 0.2, 0.3}) {
        grid = gridsPorPct[pct];
        for (int n : NUMPIVOS) {
          computarDistPivosFixos(pivosPorN[n]);      // igual a main.cpp:244
          auto &orig = distOriginal[n];

          long long comp = 0, dif = 0, inalc = 0; int maxAum = 0;
          bool mesmosPivos = (pivos == pivosPorN[n]);
          for (size_t p = 0; p < pivos.size(); ++p)
            for (int i = 0; i < height; i++) for (int j = 0; j < width; j++) {
              int a = orig[p][i][j], b = distPivos[p][i][j];
              if (a == -1) continue;                 // não era alcançável nem antes
              comp++;
              if (a != b) { dif++; if (b == -1) inalc++; else maxAum = max(maxAum, b - a); }
            }
          out << nome << "," << semente << "," << deg.name << "," << pct << "," << n << ","
              << mesmosPivos << "," << comp << "," << dif << ","
              << (comp ? (double)dif/comp : 0) << "," << inalc << "," << maxAum << "\n";

          // Quanto o reprocessamento vale: A* com distâncias frescas vs congeladas
          auto distFresco = distPivos;   // já calculadas acima, uma única vez
          double sO=0, sF=0, sC=0;
          for (int i : validos) {
            distPivos = distFresco;        // o que o código de fato faz
            int ef = aStar(scenario[i].start, scenario[i].goal, heuristicaMemoryBased).expansions;
            distPivos = distOriginal[n];   // o que o texto afirma que foi feito
            int ec = aStar(scenario[i].start, scenario[i].goal, heuristicaMemoryBased).expansions;
            sO += expOrigMem[n][i]; sF += ef; sC += ec;
          }
          distPivos = distFresco;
          int k = validos.size();
          out2 << nome << "," << semente << "," << deg.name << "," << pct << "," << n << ","
               << k << "," << sO/k << "," << sF/k << "," << sC/k << ","
               << sF/sO << "," << sC/sO << "\n";
          out.flush(); out2.flush();
          cerr << nome << " " << deg.name << " " << pct << " n=" << n
               << " difs=" << dif << "/" << comp << " delta_fresco=" << sF/sO
               << " delta_congelado=" << sC/sO << endl;
        }
      }
    }
  }
  return 0;
}
