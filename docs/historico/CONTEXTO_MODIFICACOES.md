# Contexto de Modificações e Evolução do Projeto (Pós-Resumo Estendido)

Este documento detalha as alterações técnicas, arquiteturais e metodológicas implementadas no sistema de síntese de heurísticas desde a conclusão do resumo estendido para a SBC. O objetivo é fornecer uma base de comparação entre a versão inicial do projeto e o framework atual de experimentação.

## 1. Arquitetura e Performance (HPC)

### Processamento Multi-thread (OpenMP)
- **Implementação:** Foi introduzido o paralelismo de dados na avaliação da população do Algoritmo Genético (GA). Utilizando a diretiva `#pragma omp parallel for`, a carga de processamento dos testes A* foi distribuída entre as threads disponíveis do hardware (ex: 12 threads no Ryzen 5500).
- **Thread-Safety:** A função `aStar` foi refatorada para ser puramente funcional. Variáveis globais (`extern`) como `estadosExpandidos` e `currentFormula` foram removidas.
- **Estrutura de Retorno:** O algoritmo de busca agora retorna uma struct `SearchResult`, contendo o vetor de caminho e o contador de expansões de forma isolada por execução.

### Otimizações de Redundância
- **Memoização de Baseline:** Implementou-se o pré-cálculo das expansões da Heurística de Manhattan para os problemas de treino. O valor é calculado uma única vez antes do início das gerações do GA e armazenado em memória.
- **Caching Estrutural (AST):** Os nós da árvore sintática (`HeuristicNode`) agora possuem atributos `_cachedSize` e `_cachedDepth`, calculados no momento da construção ou mutação. Isso alterou a complexidade de obtenção do tamanho da fórmula de $O(N)$ para $O(1)$.

## 2. Síntese de Heurísticas e Gramática

### Restrição do Espaço de Busca
- **Terminais Relativos:** A gramática de geração de fórmulas foi alterada para restringir os nós terminais apenas a `DELTAX`, `DELTAY` e `CONSTANT`.
- **Remoção de Coordenadas Absolutas:** Os terminais `X1, Y1, X2, Y2` foram removidos da gramática. O objetivo técnico é priorizar a compacidade da fórmula e a invariância à translação, focando em distâncias relativas entre estados.

### Regularização
- **Parâmetros de Saunders (2024):** Os hiperparâmetros de penalidade por tamanho (`lambda`), taxa de elitismo e tamanho da população foram alinhados estritamente com os valores reportados no trabalho de referência para garantir paridade metodológica.

## 3. Metodologia Experimental e Coleta de Dados

### Granularidade dos Dados (Raw Data)
- **Log Caso-a-Caso:** O sistema de coleta de dados foi alterado para gravar o resultado de cada problema individual no `resultados_robustez.csv` e `resultados_base.csv`, em vez de apenas médias agregadas.
- **Campos Registrados:** Incluem-se agora expansões e tamanhos de caminho para os estados "Original" e "Degradado" de cada instância, permitindo análises estatísticas posteriores (mediana, desvio padrão, distribuição).

### Escalabilidade de Mapas
- **Estrutura de Lote (Batch Run):** O `main.cpp` foi refatorado para iterar sobre um vetor de configurações de mapas (`MapConfig`). Isso permite que múltiplos mapas e cenários `.scen` sejam processados em uma única execução do binário.

### Modelos de Degradação
- **Adição de Degradação Estocástica:** Além dos modelos Radial, Linear, Sparse e Organic, foi incluída a função `degradaMapaSaunders`. Este modelo bloqueia N células aleatórias que eram originalmente navegáveis, mimetizando o processo de modificação estocástica descrito na literatura de 2024.

## 4. Ambiente de Compilação

- **Flags de Hardware:** O `Makefile` foi atualizado para utilizar `-O3 -march=native -ffast-math -fopenmp`. Estas flags instruem o compilador a utilizar instruções específicas da arquitetura (ex: AVX2) e otimizações agressivas de ponto flutuante.

---
**Nota:** Este documento descreve as ferramentas e o ambiente. A interpretação dos impactos destas mudanças na performance das heurísticas e na sua robustez sob degradação cabe à análise científica posterior dos dados coletados.
