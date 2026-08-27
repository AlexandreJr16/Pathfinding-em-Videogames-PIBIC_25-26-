#pragma once
// Serialização de estado do AG para retomada após parada ou queda.
//
// Round-trip exato: getRandomConstant() gera round(x*10)/10 (uma casa decimal) e
// toString() imprime com %.1f; mutação e crossover apenas movem ou substituem
// subárvores, nunca alteram constantes aritmeticamente. Logo, texto -> AST -> texto
// é bit-exato, e a população restaurada é idêntica à salva.
#include "src/synthesis/GeneticAlgorithm.h"
#include <bits/stdc++.h>

// ------------------------------------------------- parser da notação prefixa
inline std::vector<std::string> tokenizar(const std::string &s) {
  std::vector<std::string> t; std::string cur;
  for (char c : s) {
    if (c == '(' || c == ')') { if (!cur.empty()) { t.push_back(cur); cur.clear(); } t.push_back(std::string(1, c)); }
    else if (isspace((unsigned char)c)) { if (!cur.empty()) { t.push_back(cur); cur.clear(); } }
    else cur += c;
  }
  if (!cur.empty()) t.push_back(cur);
  return t;
}

inline std::shared_ptr<HeuristicNode> parseNo(const std::vector<std::string> &t, size_t &i) {
  static const std::map<std::string, UnaryNode::Type> UN = {
      {"sqrt", UnaryNode::SQRT}, {"abs", UnaryNode::ABS},
      {"neg", UnaryNode::NEG},   {"sqr", UnaryNode::SQR}};
  static const std::map<std::string, BinaryNode::Type> BIN = {
      {"+", BinaryNode::ADD}, {"-", BinaryNode::SUB}, {"*", BinaryNode::MUL},
      {"/", BinaryNode::DIV}, {"max", BinaryNode::MAX}, {"min", BinaryNode::MIN}};
  static const std::map<std::string, TerminalNode::Type> TERM = {
      {"deltaX", TerminalNode::DELTAX}, {"deltaY", TerminalNode::DELTAY},
      {"x1", TerminalNode::X1}, {"y1", TerminalNode::Y1},
      {"x2", TerminalNode::X2}, {"y2", TerminalNode::Y2}};

  if (i >= t.size()) throw std::runtime_error("checkpoint: fórmula truncada");
  if (t[i] == "(") {
    ++i;
    std::string op = t[i++];
    auto u = UN.find(op);
    if (u != UN.end()) {
      auto c = parseNo(t, i);
      if (t[i] != ")") throw std::runtime_error("checkpoint: falta ) após " + op);
      ++i;
      return std::make_shared<UnaryNode>(u->second, c);
    }
    auto b = BIN.find(op);
    if (b == BIN.end()) throw std::runtime_error("checkpoint: operador desconhecido " + op);
    auto l = parseNo(t, i), r = parseNo(t, i);
    if (t[i] != ")") throw std::runtime_error("checkpoint: falta ) após " + op);
    ++i;
    return std::make_shared<BinaryNode>(b->second, l, r);
  }
  std::string tok = t[i++];
  auto k = TERM.find(tok);
  if (k != TERM.end()) return std::make_shared<TerminalNode>(k->second);
  return std::make_shared<TerminalNode>(TerminalNode::CONSTANT, std::stod(tok));
}

inline std::shared_ptr<HeuristicNode> parseFormula(const std::string &s) {
  auto t = tokenizar(s); size_t i = 0;
  auto n = parseNo(t, i);
  if (i != t.size()) throw std::runtime_error("checkpoint: sobrou texto na fórmula");
  return n;
}

// ------------------------------------------------------------- estado salvo
struct Estado {
  std::string mapa; int semente = 0, geracao = 0;
  size_t popSize = 0; double msAcumulado = 0;
  std::string rngGrammar, rngOperators, rngGA;
  std::vector<std::pair<double, std::string>> populacao;  // fitness, fórmula
};

// Grava por arquivo temporário + rename: o rename é atômico, então nunca existe
// um checkpoint pela metade, mesmo se a máquina desligar no meio da escrita.
inline void gravarAtomico(const std::string &caminho, const std::string &conteudo) {
  std::string tmp = caminho + ".tmp";
  { std::ofstream f(tmp); f << conteudo; f.flush();
    if (!f) throw std::runtime_error("falha ao escrever " + tmp); }
  if (std::rename(tmp.c_str(), caminho.c_str()) != 0)
    throw std::runtime_error("falha ao renomear " + tmp);
}

inline void salvarEstado(const std::string &caminho, const Estado &e) {
  std::ostringstream o;
  o << "ckpt-v1\n" << e.mapa << " " << e.semente << " " << e.geracao << " "
    << e.popSize << " " << std::setprecision(17) << e.msAcumulado << "\n"
    << e.rngGrammar << "\n" << e.rngOperators << "\n" << e.rngGA << "\n"
    << e.populacao.size() << "\n";
  for (auto &[fit, f] : e.populacao)
    o << std::setprecision(17) << fit << " " << f << "\n";
  gravarAtomico(caminho, o.str());
}

inline bool carregarEstado(const std::string &caminho, Estado &e) {
  std::ifstream f(caminho);
  if (!f.is_open()) return false;
  std::string versao; std::getline(f, versao);
  if (versao != "ckpt-v1") return false;
  f >> e.mapa >> e.semente >> e.geracao >> e.popSize >> e.msAcumulado;
  f.ignore();
  std::getline(f, e.rngGrammar);
  std::getline(f, e.rngOperators);
  std::getline(f, e.rngGA);
  size_t n; f >> n; f.ignore();
  e.populacao.clear();
  for (size_t i = 0; i < n; i++) {
    std::string linha; std::getline(f, linha);
    size_t sp = linha.find(' ');
    if (sp == std::string::npos) return false;
    e.populacao.push_back({std::stod(linha.substr(0, sp)), linha.substr(sp + 1)});
  }
  return e.populacao.size() == n;
}
