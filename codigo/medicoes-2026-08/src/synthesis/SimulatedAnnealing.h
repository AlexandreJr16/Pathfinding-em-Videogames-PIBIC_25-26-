/**
 * @file SimulatedAnnealing.h
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 * 
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma 
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024). [Título do Artigo/Tese].
 */

#ifndef SIMULATED_ANNEALING_H
#define SIMULATED_ANNEALING_H

#include "HeuristicNode.h"
#include "HeuristicGrammar.h"
#include "GeneticOperators.h"
#include <functional>
#include <cmath>
#include <random>

/**
 * @class SimulatedAnnealing
 * @brief Implementa a otimização por Simulated Annealing para fórmulas.
 */
class SimulatedAnnealing {
public:
    SimulatedAnnealing(HeuristicGrammar& grammar, GeneticOperators& operators);

    /**
     * @brief Executa o processo de annealing para encontrar uma heurística melhor.
     * @param initialFormula Fórmula de partida.
     * @param evaluateFunc Função que retorna o fitness (speedup).
     * @param iterations Número de iterações do processo.
     * @return A melhor fórmula encontrada durante o processo.
     */
    std::shared_ptr<HeuristicNode> optimize(
        std::shared_ptr<HeuristicNode> initialFormula,
        std::function<double(std::shared_ptr<HeuristicNode>)> evaluateFunc,
        int iterations
    );

private:
    HeuristicGrammar& grammar;
    GeneticOperators& operators;
    std::mt19937 gen;
    
    // Parâmetros de Annealing
    double initialTemperature = 1.0;
    double coolingRate = 0.95;
    double lambda = 0.001; // Penalidade por tamanho
};

#endif // SIMULATED_ANNEALING_H
