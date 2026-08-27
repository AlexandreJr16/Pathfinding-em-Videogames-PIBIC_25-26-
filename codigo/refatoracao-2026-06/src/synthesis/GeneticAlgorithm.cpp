/**
 * @file GeneticAlgorithm.cpp
 * @brief Algoritmo Genético para Evolução de Heurísticas (Saunders 2024).
 */

#include "GeneticAlgorithm.h"
#include <algorithm>
#include <random>
#ifdef _OPENMP
#endif

GeneticAlgorithm::GeneticAlgorithm(HeuristicGrammar &g, GeneticOperators &o, unsigned int seed)
    : grammar(g), operators(o), gen(seed) {}

void GeneticAlgorithm::initPopulation(size_t size) {
  popSize = size;
  population.clear();
  std::uniform_int_distribution<size_t> sizeDist(5, 20);

  for (size_t i = 0; i < popSize; ++i) {
    population.emplace_back(grammar.generateRandomHCT(sizeDist(gen)));
  }
}

void GeneticAlgorithm::evolve(
    std::function<double(std::shared_ptr<HeuristicNode>)> evaluateFunc) {

#pragma omp parallel for schedule(dynamic)
  for (int i = 0; i < (int)population.size(); ++i) {
    double speedup = evaluateFunc(population[i].formula);
    // Regularização de Saunders (2024): fitness = speedup - lambda * size
    population[i].fitness = speedup - (lambda * population[i].formula->size());
  }

  // 2. Seleção (Elitismo)
  selection();

  // 3. Reprodução (Crossover + Mutação)
  reproduction();
}

void GeneticAlgorithm::selection() {
  // Ordenar do melhor para o pior (decrescente)
  std::sort(population.begin(), population.end(),
            [](const Individual &a, const Individual &b) {
              return a.fitness > b.fitness;
            });

  // Manter apenas os elites
  size_t numElites = static_cast<size_t>(std::ceil(elitePercentage * popSize));
  if (population.size() > numElites) {
    population.erase(population.begin() + numElites, population.end());
  }
}

void GeneticAlgorithm::reproduction() {
  size_t numElites = population.size();
  size_t offspringNeeded = popSize - numElites;

  std::uniform_int_distribution<size_t> eliteDist(0, numElites - 1);

  std::vector<Individual> offspring;
  for (size_t i = 0; i < offspringNeeded; ++i) {
    // Escolher dois pais elites aleatoriamente
    auto &p1 = population[eliteDist(gen)];
    auto &p2 = population[eliteDist(gen)];

    // Crossover
    auto childFormula = operators.crossover(p1.formula, p2.formula);

    // Mutação (conforme Saunders: cada filho sofre mutação)
    childFormula = operators.mutate(childFormula);

    offspring.emplace_back(childFormula);
  }

  // Adicionar filhos à população de elites
  population.insert(population.end(), offspring.begin(), offspring.end());
}

std::shared_ptr<HeuristicNode> GeneticAlgorithm::getBest() const {
  if (population.empty())
    return nullptr;
  // Como a população está sempre ordenada após evolve(), o primeiro é o melhor
  return population[0].formula;
}

double GeneticAlgorithm::getBestFitness() const {
  if (population.empty())
    return -1.0e18;
  return population[0].fitness;
}
