/**
 * @file GeneticOperators.h
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 *
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024).
 * */

#ifndef GENETIC_OPERATORS_H
#define GENETIC_OPERATORS_H

#include "HeuristicGrammar.h"
#include "HeuristicNode.h"

/**
 * @class GeneticOperators
 * @brief Implementa os operadores de Programação Genética (GP).
 */
class GeneticOperators {
public:
  GeneticOperators(HeuristicGrammar &grammar,
                   unsigned int seed = std::random_device{}());

  /**
   * @brief Realiza a mutação de um indivíduo.
   * @param individual Ponteiro para a fórmula a ser mutada.
   * @return Uma nova fórmula mutada.
   */
  std::shared_ptr<HeuristicNode>
  mutate(std::shared_ptr<HeuristicNode> individual);

  /**
   * @brief Realiza o crossover entre dois pais.
   * @param parent1 Primeiro pai.
   * @param parent2 Segundo pai.
   * @return Um novo filho resultante da combinação.
   */
  std::shared_ptr<HeuristicNode>
  crossover(std::shared_ptr<HeuristicNode> parent1,
            std::shared_ptr<HeuristicNode> parent2);

private:
  HeuristicGrammar &grammar;
  std::mt19937 gen;
};

#endif // GENETIC_OPERATORS_H
