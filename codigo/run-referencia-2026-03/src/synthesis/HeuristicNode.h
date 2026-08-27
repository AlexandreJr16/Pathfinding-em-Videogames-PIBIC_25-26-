/**
 * @file HeuristicNode.h
 * @brief Estruturas de Árvore Sintática (AST) para Heurísticas.
 */

#ifndef HEURISTIC_NODE_H
#define HEURISTIC_NODE_H

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <cmath>
#include <algorithm>

/**
 * @struct Point
 * @brief Representa uma coordenada (x, y) no mapa.
 */
struct Point {
    int x;
    int y;
};

/**
 * @class HeuristicNode
 * @brief Classe base abstrata para nós da árvore de fórmulas heurísticas.
 */
class HeuristicNode {
public:
    virtual ~HeuristicNode() = default;
    
    virtual double evaluate(const Point& s, const Point& g) const = 0;
    virtual std::string toString() const = 0;
    
    size_t size() const { return _cachedSize; }
    size_t depth() const { return _cachedDepth; }
    
    /**
     * @brief Cria uma cópia profunda (deep copy) da subárvore.
     */
    virtual std::shared_ptr<HeuristicNode> clone() const = 0;

    /**
     * @brief Retorna um ponteiro para o n-ésimo nó da subárvore (ordem pré-fixada).
     */
    virtual std::shared_ptr<HeuristicNode> getNode(size_t index, size_t& currentIndex) = 0;

    /**
     * @brief Substitui o n-ésimo nó por um novo nó.
     */
    virtual bool replaceNode(size_t index, std::shared_ptr<HeuristicNode> newNode, size_t& currentIndex) = 0;

protected:
    size_t _cachedSize = 1;
    size_t _cachedDepth = 1;
};

// --- TERMINAIS ---

class TerminalNode : public HeuristicNode, public std::enable_shared_from_this<TerminalNode> {
public:
    enum Type { DELTAX, DELTAY, X1, Y1, X2, Y2, CONSTANT };
    
    TerminalNode(Type t, double val = 0.0) : type(t), constantValue(val) {
        _cachedSize = 1;
        _cachedDepth = 1;
    }
    
    double evaluate(const Point& s, const Point& g) const override {
        switch (type) {
            case DELTAX: return std::abs(s.x - g.x);
            case DELTAY: return std::abs(s.y - g.y);
            case X1: return s.x;
            case Y1: return s.y;
            case X2: return g.x;
            case Y2: return g.y;
            case CONSTANT: return constantValue;
            default: return 0.0;
        }
    }
    
    std::string toString() const override {
        switch (type) {
            case DELTAX: return "deltaX";
            case DELTAY: return "deltaY";
            case X1: return "x1";
            case Y1: return "y1";
            case X2: return "x2";
            case Y2: return "y2";
            case CONSTANT: {
                char buffer[32];
                snprintf(buffer, sizeof(buffer), "%.1f", constantValue);
                return std::string(buffer);
            }
            default: return "unknown";
        }
    }
    
    std::shared_ptr<HeuristicNode> clone() const override {
        return std::make_shared<TerminalNode>(type, constantValue);
    }

    std::shared_ptr<HeuristicNode> getNode(size_t index, size_t& currentIndex) override {
        if (currentIndex == index) return shared_from_this();
        return nullptr;
    }

    bool replaceNode(size_t index, std::shared_ptr<HeuristicNode> newNode, size_t& currentIndex) override {
        return false; // Substituição deve ser tratada no pai
    }

private:
    Type type;
    double constantValue;
};

// --- OPERADORES UNÁRIOS ---

class UnaryNode : public HeuristicNode, public std::enable_shared_from_this<UnaryNode> {
public:
    enum Type { SQRT, ABS, NEG, SQR };
    
    UnaryNode(Type t, std::shared_ptr<HeuristicNode> child) : type(t), operand(child) {
        _cachedSize = 1 + operand->size();
        _cachedDepth = 1 + operand->depth();
    }
    
    double evaluate(const Point& s, const Point& g) const override {
        double val = operand->evaluate(s, g);
        switch (type) {
            case SQRT: return std::sqrt(std::abs(val));
            case ABS: return std::abs(val);
            case NEG: return -val;
            case SQR: return val * val;
            default: return 0.0;
        }
    }
    
    std::string toString() const override {
        std::string op;
        switch (type) {
            case SQRT: op = "sqrt"; break;
            case ABS: op = "abs"; break;
            case NEG: op = "neg"; break;
            case SQR: op = "sqr"; break;
            default: op = "unknown"; break;
        }
        return "(" + op + " " + operand->toString() + ")";
    }
    
    std::shared_ptr<HeuristicNode> clone() const override {
        return std::make_shared<UnaryNode>(type, operand->clone());
    }

    std::shared_ptr<HeuristicNode> getNode(size_t index, size_t& currentIndex) override {
        if (currentIndex == index) return shared_from_this();
        currentIndex++;
        return operand->getNode(index, currentIndex);
    }

    bool replaceNode(size_t index, std::shared_ptr<HeuristicNode> newNode, size_t& currentIndex) override {
        size_t nextIndex = currentIndex + 1;
        if (nextIndex == index) {
            operand = newNode;
            _cachedSize = 1 + operand->size();
            _cachedDepth = 1 + operand->depth();
            return true;
        }
        currentIndex++;
        if (operand->replaceNode(index, newNode, currentIndex)) {
            _cachedSize = 1 + operand->size();
            _cachedDepth = 1 + operand->depth();
            return true;
        }
        return false;
    }

private:
    Type type;
    std::shared_ptr<HeuristicNode> operand;
};

// --- OPERADORES BINÁRIOS ---

class BinaryNode : public HeuristicNode, public std::enable_shared_from_this<BinaryNode> {
public:
    enum Type { ADD, SUB, MUL, DIV, MAX, MIN };
    
    BinaryNode(Type t, std::shared_ptr<HeuristicNode> l, std::shared_ptr<HeuristicNode> r) 
        : type(t), left(l), right(r) {
        _cachedSize = 1 + left->size() + right->size();
        _cachedDepth = 1 + std::max(left->depth(), right->depth());
    }
    
    double evaluate(const Point& s, const Point& g) const override {
        double lVal = left->evaluate(s, g);
        double rVal = right->evaluate(s, g);
        switch (type) {
            case ADD: return lVal + rVal;
            case SUB: return lVal - rVal;
            case MUL: return lVal * rVal;
            case DIV: return (rVal != 0) ? lVal / rVal : 0.0;
            case MAX: return std::max(lVal, rVal);
            case MIN: return std::min(lVal, rVal);
            default: return 0.0;
        }
    }
    
    std::string toString() const override {
        std::string op;
        switch (type) {
            case ADD: op = "+"; break;
            case SUB: op = "-"; break;
            case MUL: op = "*"; break;
            case DIV: op = "/"; break;
            case MAX: op = "max"; break;
            case MIN: op = "min"; break;
            default: op = "unknown"; break;
        }
        return "(" + op + " " + left->toString() + " " + right->toString() + ")";
    }
    
    std::shared_ptr<HeuristicNode> clone() const override {
        return std::make_shared<BinaryNode>(type, left->clone(), right->clone());
    }

    std::shared_ptr<HeuristicNode> getNode(size_t index, size_t& currentIndex) override {
        if (currentIndex == index) return shared_from_this();
        
        currentIndex++;
        auto res = left->getNode(index, currentIndex);
        if (res) return res;
        
        currentIndex++;
        return right->getNode(index, currentIndex);
    }

    bool replaceNode(size_t index, std::shared_ptr<HeuristicNode> newNode, size_t& currentIndex) override {
        if (currentIndex + 1 == index) {
            left = newNode;
            _cachedSize = 1 + left->size() + right->size();
            _cachedDepth = 1 + std::max(left->depth(), right->depth());
            return true;
        }
        currentIndex++;
        if (left->replaceNode(index, newNode, currentIndex)) {
            _cachedSize = 1 + left->size() + right->size();
            _cachedDepth = 1 + std::max(left->depth(), right->depth());
            return true;
        }

        if (currentIndex + 1 == index) {
            right = newNode;
            _cachedSize = 1 + left->size() + right->size();
            _cachedDepth = 1 + std::max(left->depth(), right->depth());
            return true;
        }
        currentIndex++;
        if (right->replaceNode(index, newNode, currentIndex)) {
            _cachedSize = 1 + left->size() + right->size();
            _cachedDepth = 1 + std::max(left->depth(), right->depth());
            return true;
        }
        return false;
    }

private:
    Type type;
    std::shared_ptr<HeuristicNode> left;
    std::shared_ptr<HeuristicNode> right;
};

#endif // HEURISTIC_NODE_H
