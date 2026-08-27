/**
 * @file HeuristicGrammar.cpp
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 *
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024).
 */

#include "HeuristicGrammar.h"

HeuristicGrammar::HeuristicGrammar(Mode m, unsigned int seed)
    : mode(m), gen(seed) {}

std::shared_ptr<HeuristicNode>
HeuristicGrammar::generateRandomHCT(size_t size) {
  if (size <= 1) {
    // Terminal
    if (std::uniform_int_distribution<int>(0, 10)(gen) > 8) {
      return std::make_shared<TerminalNode>(TerminalNode::CONSTANT,
                                            getRandomConstant());
    } else {
      auto type = getRandomTerminal();
      if (type == TerminalNode::PIVOT_DIST_S ||
          type == TerminalNode::PIVOT_DIST_G) {
        std::uniform_int_distribution<int> pDist(0, 2); // 3 pivôs
        return std::make_shared<TerminalNode>(type, 0.0, pDist(gen));
      }
      return std::make_shared<TerminalNode>(type);
    }
  } else if (size == 2) {
    // Unário + Terminal
    return std::make_shared<UnaryNode>(getRandomUnary(), generateRandomHCT(1));
  } else {
    // Unário + binário
    std::uniform_int_distribution<int> dist(1, 2);
    if (dist(gen) == 1) {
      // Unário
      return std::make_shared<UnaryNode>(getRandomUnary(),
                                         generateRandomHCT(size - 1));
    } else {
      // Binário
      size_t remaining = size - 1;
      std::uniform_int_distribution<size_t> splitDist(1, remaining - 1);
      size_t leftSize = splitDist(gen);
      size_t rightSize = remaining - leftSize;

      return std::make_shared<BinaryNode>(getRandomBinary(),
                                          generateRandomHCT(leftSize),
                                          generateRandomHCT(rightSize));
    }
  }
}

TerminalNode::Type HeuristicGrammar::getRandomTerminal() {
  if (mode == Mode::ABSOLUTE) {
    std::uniform_int_distribution<int> dist(2, 5); // X1, Y1, X2, Y2
    return static_cast<TerminalNode::Type>(dist(gen));
  } else if (mode == Mode::HYBRID) {
    // 50% chance delta terminals, 50% chance pivot terminals
    std::uniform_int_distribution<int> choice(0, 3);
    int c = choice(gen);
    if (c <= 1) {
      return static_cast<TerminalNode::Type>(c); // DELTAX or DELTAY
    } else {
      return (c == 2) ? TerminalNode::PIVOT_DIST_S : TerminalNode::PIVOT_DIST_G;
    }
  } else {
    // DELTA, ADMISSIBILITY base
    std::uniform_int_distribution<int> dist(0, 1); // DELTAX, DELTAY
    return static_cast<TerminalNode::Type>(dist(gen));
  }
}

UnaryNode::Type HeuristicGrammar::getRandomUnary() {
  std::uniform_int_distribution<int> dist(0, 3);
  return static_cast<UnaryNode::Type>(dist(gen));
}

BinaryNode::Type HeuristicGrammar::getRandomBinary() {
  std::uniform_int_distribution<int> dist(0, 5);
  return static_cast<BinaryNode::Type>(dist(gen));
}

double HeuristicGrammar::getRandomConstant() {
  std::uniform_real_distribution<double> dist(1.0, 10.0);
  return std::round(dist(gen) * 10.0) / 10.0; // One decimal place as in MATLAB
}
