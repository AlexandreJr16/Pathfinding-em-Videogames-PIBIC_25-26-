# Programas de medição — agosto/2026

Cinco programas C++ escritos para a reanálise estatística, para medir o que a execução de março
**não instrumentou**.

| Programa | Mede | Análise |
|---|---|---|
| `medir_dijkstra` | expansões do A\* com `h = 0`, para normalizar expansões entre mapas | L8 |
| `medir_pivos` | memória e tempo de pré-computação dos pivôs; diagnostica o colapso de pivô | A7, A11 |
| `verifica_reprocessamento` | quanto das distâncias pré-computadas muda sob degradação | A0 |
| `sintese_repetida` | re-síntese com semente explícita, em lote | A9 |
| `sintese_worker` | uma síntese isolada, com checkpoint; é o processo que `sintese_pool.py` dispara em paralelo | A9 |

```fish
cd codigo/medicoes-2026-08
make            # compila os cinco
./medir_dijkstra
```

Rode **a partir deste diretório**: `maps` é um link simbólico para `../../maps`.

## Sobre o `src/` daqui

É uma **cópia do código de março** com uma alteração deliberada: as sementes do algoritmo
genético viraram parâmetro explícito, em vez de virem de `std::random_device`. Sem isso a
análise A9 — "a síntese reencontra a mesma fórmula?" — seria impossível de fazer.

Os arquivos alterados em relação a `codigo/run-referencia-2026-03/src/` são quatro, todos em
`synthesis/`: `GeneticAlgorithm.{h,cpp}`, `GeneticOperators.h`, `HeuristicGrammar.h`.

```fish
diff -r ../run-referencia-2026-03/src src    # mostra exatamente o que mudou
```

Ver `docs/04-problemas-conhecidos.md`, P5.
