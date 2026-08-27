/**
 * @file HeuristicGrammar.cpp
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 * 
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma 
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024). [Título do Artigo/Tese].
 */

#include "HeuristicGrammar.h"

HeuristicGrammar::HeuristicGrammar(unsigned int seed) : gen(seed) {}

std::shared_ptr<HeuristicNode> HeuristicGrammar::generateRandomHCT(size_t size) {
    if (size <= 1) {
        // Base case: Terminal
        if (std::uniform_int_distribution<int>(0, 10)(gen) > 8) {
            return std::make_shared<TerminalNode>(TerminalNode::CONSTANT, getRandomConstant());
        } else {
            return std::make_shared<TerminalNode>(getRandomTerminal());
        }
    } else if (size == 2) {
        // Case 2: Unary + Terminal
        return std::make_shared<UnaryNode>(getRandomUnary(), generateRandomHCT(1));
    } else {
        // Case > 2: Unary or Binary
        std::uniform_int_distribution<int> dist(1, 2);
        if (dist(gen) == 1) {
            // Unary
            return std::make_shared<UnaryNode>(getRandomUnary(), generateRandomHCT(size - 1));
        } else {
            // Binary
            // Size must be split between left and right, minus the binary node itself
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
    // Restringe a DELTAX (0) e DELTAY (1) para garantir robustez e generalização
    // Removendo X1, Y1, X2, Y2 (2, 3, 4, 5) que causavam overfitting ao mapa
    std::uniform_int_distribution<int> dist(0, 1);
    return static_cast<TerminalNode::Type>(dist(gen));
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
