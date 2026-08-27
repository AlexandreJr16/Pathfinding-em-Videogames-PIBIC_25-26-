/**
 * @file GeneticAlgorithm.h
 * @brief Implementação de GA para síntese de heurísticas.
 */

#ifndef GENETIC_ALGORITHM_H
#define GENETIC_ALGORITHM_H

#include "HeuristicNode.h"
#include "HeuristicGrammar.h"
#include "GeneticOperators.h"
#include <vector>
#include <functional>

/**
 * @struct Individual
 * @brief Representa um indivíduo na população do GA.
 */
struct Individual {
    std::shared_ptr<HeuristicNode> formula;
    double fitness;
    
    Individual(std::shared_ptr<HeuristicNode> f) : formula(f), fitness(-1.0e18) {}
};

/**
 * @class GeneticAlgorithm
 * @brief Gerencia a evolução da população de heurísticas.
 */
class GeneticAlgorithm {
public:
    /**
     * @brief Construtor configurando hiperparâmetros de Saunders (2024).
     */
    GeneticAlgorithm(HeuristicGrammar& grammar, GeneticOperators& operators);

    /**
     * @brief Inicializa a população com fórmulas aleatórias.
     */
    void initPopulation(size_t popSize);

    /**
     * @brief Executa uma geração completa da evolução.
     * @param evaluateFunc Função que recebe uma fórmula e retorna o seu fitness (speedup).
     */
    void evolve(std::function<double(std::shared_ptr<HeuristicNode>)> evaluateFunc);

    /**
     * @brief Retorna a melhor fórmula encontrada até agora.
     */
    std::shared_ptr<HeuristicNode> getBest() const;

    /**
     * @brief Retorna o fitness da melhor fórmula.
     */
    double getBestFitness() const;

    /**
     * @brief Retorna a população atual.
     */
    const std::vector<Individual>& getPopulation() const { return population; }

private:
    HeuristicGrammar& grammar;
    GeneticOperators& operators;
    std::vector<Individual> population;
    
    // Hiperparâmetros baseados em Saunders (2024)
    size_t popSize = 80;
    double elitePercentage = 0.1;
    double lambda = 0.0005; // Penalidade por tamanho baixíssima para permitir fórmulas complexas

    void selection();
    void reproduction();
};

#endif // GENETIC_ALGORITHM_H
