/**
 * @file GeneticOperators.cpp
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 * 
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma 
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024). [Título do Artigo/Tese].
 */

#include "GeneticOperators.h"

GeneticOperators::GeneticOperators(HeuristicGrammar& g, unsigned int seed) 
    : grammar(g), gen(seed) {}

std::shared_ptr<HeuristicNode> GeneticOperators::mutate(std::shared_ptr<HeuristicNode> individual) {
    auto offspring = individual->clone();
    size_t treeSize = offspring->size();
    
    if (treeSize <= 1) return grammar.generateRandomHCT(1);

    std::uniform_int_distribution<size_t> dist(1, treeSize - 1);
    size_t targetIdx = dist(gen);

    size_t currentIdx = 0;
    std::uniform_int_distribution<size_t> sizeDist(1, 5);
    auto newBranch = grammar.generateRandomHCT(sizeDist(gen));
    
    if (!offspring->replaceNode(targetIdx, newBranch, currentIdx)) {
        return newBranch; // Se falhou em substituir (ex: alvo era a raiz), retorna o novo galho
    }

    return offspring;
}

std::shared_ptr<HeuristicNode> GeneticOperators::crossover(std::shared_ptr<HeuristicNode> parent1, 
                                                         std::shared_ptr<HeuristicNode> parent2) {
    auto offspring = parent1->clone();
    size_t size1 = offspring->size();
    size_t size2 = parent2->size();

    std::uniform_int_distribution<size_t> dist1(0, size1 - 1);
    std::uniform_int_distribution<size_t> dist2(0, size2 - 1);

    size_t target1 = dist1(gen);
    size_t target2 = dist2(gen);

    size_t currentIdx2 = 0;
    auto branchFrom2 = parent2->getNode(target2, currentIdx2)->clone();

    if (target1 == 0) return branchFrom2; // Troca a árvore inteira

    size_t currentIdx1 = 0;
    if (!offspring->replaceNode(target1, branchFrom2, currentIdx1)) {
        return parent2->clone();
    }

    return offspring;
}
