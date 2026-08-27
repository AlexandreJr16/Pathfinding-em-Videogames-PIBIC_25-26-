/**
 * @file HeuristicGrammar.h
 * @brief Tradução assistida por IA do código original de Saunders (2024)
 * 
 * @note Este módulo foi traduzido de MATLAB para C++ como parte de uma 
 * estratégia de otimização para síntese de heurísticas.
 * Original: Saunders, P. (2024). [Título do Artigo/Tese].
 */

#ifndef HEURISTIC_GRAMMAR_H
#define HEURISTIC_GRAMMAR_H

#include "HeuristicNode.h"
#include <random>
#include <sstream>

/**
 * @class HeuristicGrammar
 * @brief Classe responsável pela geração aleatória de fórmulas heurísticas.
 */
class HeuristicGrammar {
public:
    HeuristicGrammar(unsigned int seed = std::random_device{}());
    
    /**
     * @brief Gera uma árvore de fórmula heurística aleatória com o tamanho especificado.
     * @param size Tamanho desejado da árvore (número de nós).
     * @return Ponteiro compartilhado para a raiz da árvore gerada.
     */
    std::shared_ptr<HeuristicNode> generateRandomHCT(size_t size);

    // Checkpoint: o estado do mt19937 é serializável por operator<< / operator>>
    std::string rngState() const { std::ostringstream o; o << gen; return o.str(); }
    void setRngState(const std::string& s) { std::istringstream i(s); i >> gen; }

private:
    std::mt19937 gen;
    
    TerminalNode::Type getRandomTerminal();
    UnaryNode::Type getRandomUnary();
    BinaryNode::Type getRandomBinary();
    double getRandomConstant();
};

#endif // HEURISTIC_GRAMMAR_H
