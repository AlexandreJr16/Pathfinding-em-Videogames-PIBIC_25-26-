/**
 * @file SimulatedAnnealing.cpp
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 * 
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma 
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024). [Título do Artigo/Tese].
 */

#include "SimulatedAnnealing.h"
#include <iostream>

SimulatedAnnealing::SimulatedAnnealing(HeuristicGrammar& g, GeneticOperators& o) 
    : grammar(g), operators(o), gen(std::random_device{}()) {}

std::shared_ptr<HeuristicNode> SimulatedAnnealing::optimize(
    std::shared_ptr<HeuristicNode> initialFormula,
    std::function<double(std::shared_ptr<HeuristicNode>)> evaluateFunc,
    int iterations
) {
    auto currentFormula = initialFormula->clone();
    double currentFitness = evaluateFunc(currentFormula) - (lambda * currentFormula->size());
    
    auto bestFormula = currentFormula->clone();
    double bestFitness = currentFitness;
    
    double T = initialTemperature;
    std::uniform_real_distribution<double> dist(0.0, 1.0);

    for (int i = 0; i < iterations; ++i) {
        // 1. Gerar vizinho via mutação
        auto neighbor = operators.mutate(currentFormula);
        double neighborFitness = evaluateFunc(neighbor) - (lambda * neighbor->size());
        
        // 2. Calcular delta (energia)
        double delta = neighborFitness - currentFitness;
        
        // 3. Critério de Aceitação de Boltzmann
        if (delta > 0 || dist(gen) < std::exp(delta / T)) {
            currentFormula = neighbor;
            currentFitness = neighborFitness;
            
            // Atualizar o campeão absoluto
            if (currentFitness > bestFitness) {
                bestFitness = currentFitness;
                bestFormula = currentFormula->clone();
            }
        }
        
        // 4. Resfriamento
        T *= coolingRate;
        
        // Opcional: Logar progresso se a melhora for significativa
        // std::cout << "Iter " << i << " T: " << T << " Best Fitness: " << bestFitness << std::endl;
    }
    
    return bestFormula;
}
