# Heurística — Critical Code & Methodology Review

I found **3 bugs** (one serious), **4 methodological imprecisions**, and **4 design concerns**. Here's everything, ranked by severity.

---

## 🔴 BUGS

### BUG 1: Coordinate Swap in ADMISSIBILITY Mode (SERIOUS)

**Where**: [main.cpp:199-201](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L199-L201) and [main.cpp:246-248](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L246-L248)

**The problem**: The admissibility check evaluates the formula with **swapped coordinates** compared to how A\* actually uses it.

During A\*, the formula is called like this:
```cpp
// main.cpp:189-191 — inside lambda_fitness
auto h_local = [&](pair<int, int> s, pair<int, int> g) {
    return (int)formula->evaluate({s.first, s.second},   // Point.x = row, Point.y = col
                                  {g.first, g.second});
};
```

But the admissibility check does this:
```cpp
// main.cpp:199-201 — same function, a few lines later
double h_val = formula->evaluate(
    {fitnessProblems[i].start.second, fitnessProblems[i].start.first},  // Point.x = COL, Point.y = ROW ← SWAPPED!
    {fitnessProblems[i].goal.second, fitnessProblems[i].goal.first});
```

Since `start` is `pair<int,int>{row, col}`, `.second = col` and `.first = row`. So the admissibility check passes `{col, row}` while A\* passes `{row, col}`.

**Impact**: For formulas using `DELTAX`/`DELTAY`, the meaning of Δx and Δy is swapped between the admissibility check and actual A\* execution:
- A\* sees: `DELTAX = |Δrow|`, `DELTAY = |Δcol|`
- Admissibility check sees: `DELTAX = |Δcol|`, `DELTAY = |Δrow|`

For **symmetric formulas** like `deltaX + deltaY` this doesn't matter. But for **asymmetric formulas** like `2*deltaX + deltaY` or `max(deltaX, sqr(deltaY))`, the admissibility check evaluates a different function than what A\* actually runs. This means:
- A formula could be flagged as inadmissible when it's actually admissible (or vice versa)
- The `admissibility_rate` in `resultados_sintese.csv` is unreliable for asymmetric formulas
- The ADMISSIBILITY mode's fitness penalty is based on incorrect data

**The same bug appears twice**: once inside `lambda_fitness` (line 199) and once in the post-SA check (line 246).

**Fix**:
```diff
 // Both occurrences should be:
-double h_val = formula->evaluate(
-    {fitnessProblems[i].start.second, fitnessProblems[i].start.first},
-    {fitnessProblems[i].goal.second, fitnessProblems[i].goal.first});
+double h_val = formula->evaluate(
+    {fitnessProblems[i].start.first, fitnessProblems[i].start.second},
+    {fitnessProblems[i].goal.first, fitnessProblems[i].goal.second});
```

---

### BUG 2: HYBRID Mode Never Generates Pivot Terminals

**Where**: [HeuristicGrammar.cpp:59-63](file:///home/alejr/Documentos/heuristica/heuristicas/src/synthesis/HeuristicGrammar.cpp#L59-L63)

**The problem**: The grammar's `getRandomTerminal()` treats HYBRID the same as DELTA:

```cpp
} else {
    // DELTA, ADMISSIBILITY, HYBRID base
    std::uniform_int_distribution<int> dist(0, 1); // DELTAX, DELTAY only!
    return static_cast<TerminalNode::Type>(dist(gen));
}
```

`PIVOT_DIST_S` is enum value 7 and `PIVOT_DIST_G` is enum value 8. The distribution `(0, 1)` only generates `DELTAX (0)` or `DELTAY (1)`. **Pivot terminals are never generated.**

Meanwhile, [main.cpp:150](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L150) pre-computes 3 pivots for HYBRID mode:
```cpp
if (currentMode == Mode::HYBRID) {
    computarDistPivos(3); // This computation is wasted
}
```

And [HeuristicGrammar.cpp:26-28](file:///home/alejr/Documentos/heuristica/heuristicas/src/synthesis/HeuristicGrammar.cpp#L26-L28) has dead code ready to handle pivot terminals:
```cpp
if (type == TerminalNode::PIVOT_DIST_S || type == TerminalNode::PIVOT_DIST_G) {
    std::uniform_int_distribution<int> pDist(0, 2); // 3 pivots — never reached!
    return std::make_shared<TerminalNode>(type, 0.0, pDist(gen));
}
```

**Impact**: HYBRID mode produces formulas **identical to DELTA mode**. The pivot precomputation is wasted. Any HYBRID results in your data are actually DELTA results with extra overhead.

**Fix**: Add HYBRID-specific terminal selection:
```diff
 TerminalNode::Type HeuristicGrammar::getRandomTerminal() {
   if (mode == Mode::ABSOLUTE) {
     std::uniform_int_distribution<int> dist(2, 5);
     return static_cast<TerminalNode::Type>(dist(gen));
+  } else if (mode == Mode::HYBRID) {
+    // 50% chance delta terminals, 50% chance pivot terminals
+    std::uniform_int_distribution<int> choice(0, 3);
+    int c = choice(gen);
+    if (c <= 1) {
+      return static_cast<TerminalNode::Type>(c); // DELTAX or DELTAY
+    } else {
+      return (c == 2) ? TerminalNode::PIVOT_DIST_S : TerminalNode::PIVOT_DIST_G;
+    }
   } else {
     std::uniform_int_distribution<int> dist(0, 1);
     return static_cast<TerminalNode::Type>(dist(gen));
   }
 }
```

---

### BUG 3: Potential `size_t` Underflow in Ratio Calculation

**Where**: [main.cpp:306-309](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L306-L309)

```cpp
double ratio = (resD.path.size() <= 1)
    ? 1.0
    : (double)(resF.path.size() - 1) / (double)(resD.path.size() - 1);
```

If the formula fails to find a path (A\* returns empty result), `resF.path.size() = 0`. Since `path.size()` returns `size_t` (unsigned), `0 - 1 = 18446744073709551615` (SIZE_MAX). Cast to double ≈ 1.8 × 10¹⁹. The ratio becomes astronomically wrong.

**Impact**: Low in practice (A\* should always find a path on connected maps), but if any scenario has a disconnected start-goal pair, one garbage row poisons the entire map's ratio statistics.

**Fix**:
```diff
-double ratio = (resD.path.size() <= 1)
-    ? 1.0
-    : (double)(resF.path.size() - 1) / (double)(resD.path.size() - 1);
+int pathOptimal = (resD.path.empty()) ? 0 : (int)resD.path.size() - 1;
+int pathFormula = (resF.path.empty()) ? 0 : (int)resF.path.size() - 1;
+double ratio = (pathOptimal <= 0) ? 1.0 : (double)pathFormula / (double)pathOptimal;
```

---

## 🟡 METHODOLOGICAL IMPRECISIONS

### ISSUE 4: No Negative Heuristic Clamping

**Where**: [heuristics.cpp:170](file:///home/alejr/Documentos/heuristica/heuristicas/src/heuristics.cpp#L170)

```cpp
return static_cast<int>(currentFormula->evaluate(start, target));
```

The formula can produce **negative values** (via the `NEG` operator, or `SUB` where right > left). A negative heuristic means `f = g + h < g`, which makes A\* explore nodes that should be deprioritized. This doesn't break correctness (A\* still finds *a* path), but:
- Negative h makes the node appear closer than it is → more expansions
- It can make A\* behave worse than Dijkstra (h=0) in local areas
- The fitness function won't penalize this directly — it measures total expansions which include this wasted work

**Fix**: Clamp to non-negative:
```diff
-return static_cast<int>(currentFormula->evaluate(start, target));
+return std::max(0, static_cast<int>(currentFormula->evaluate(start, target)));
```

> [!NOTE]
> This is a design choice. Some GP literature allows negative heuristics intentionally. But for A\* pathfinding, `h ≥ 0` is standard and there's no information gain from negative values.

---

### ISSUE 5: Non-Deterministic GA (Broken Reproducibility)

**Where**: [GeneticAlgorithm.cpp:18](file:///home/alejr/Documentos/heuristica/heuristicas/src/synthesis/GeneticAlgorithm.cpp#L18) and [GeneticAlgorithm.cpp:61](file:///home/alejr/Documentos/heuristica/heuristicas/src/synthesis/GeneticAlgorithm.cpp#L61)

```cpp
// In initPopulation():
std::mt19937 gen(std::random_device{}());  // Random seed every time!

// In reproduction():
std::mt19937 gen(std::random_device{}());  // Random seed every time!
```

Both `initPopulation()` and `reproduction()` create a **new RNG with a random seed** on every call. This means:
- Running the same experiment twice produces different populations
- Running the same experiment twice produces different parent selections in every generation
- The grammar (seed 42) and operators (seed 42) are deterministic, but the GA's own decisions are not
- **Your results are not fully reproducible**

The `HeuristicGrammar` and `GeneticOperators` use seeded RNGs (seed 42), but the GA creates fresh `random_device` RNGs for population init and reproduction, undermining the determinism of the entire pipeline.

**Fix**: Pass a seed to the GA constructor and use a member-level RNG:
```diff
 class GeneticAlgorithm {
+    std::mt19937 gen;
 public:
-    GeneticAlgorithm(HeuristicGrammar& grammar, GeneticOperators& operators);
+    GeneticAlgorithm(HeuristicGrammar& grammar, GeneticOperators& operators, unsigned int seed = 42);
 };

-GeneticAlgorithm::GeneticAlgorithm(HeuristicGrammar& g, GeneticOperators& o)
-    : grammar(g), operators(o) {}
+GeneticAlgorithm::GeneticAlgorithm(HeuristicGrammar& g, GeneticOperators& o, unsigned int seed)
+    : grammar(g), operators(o), gen(seed) {}
```

---

### ISSUE 6: Mixing `rand()` and `std::mt19937`

**Where**: [main.cpp:163](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L163), [heuristics.cpp:23](file:///home/alejr/Documentos/heuristica/heuristicas/src/heuristics.cpp#L23), all `map.cpp` degradation functions

The codebase mixes two RNG systems:
- **`srand()`/`rand()`**: Used in `main.cpp` (training set sampling, seed setting), `heuristics.cpp` (pivot generation), and all `map.cpp` degradation functions
- **`std::mt19937`**: Used in the synthesis subsystem (grammar, operators, SA)

Problems:
- `rand()` shares global state — the order of operations matters, and any change to call sequences can silently alter results
- `rand()` has poor statistical properties (often only 15-bit period on some implementations)
- Fragile reproducibility: inserting a debugging `rand()` call anywhere changes all downstream random numbers

**Recommendation**: Migrate everything to `std::mt19937` with explicit seeds. This is a bigger refactor but eliminates a class of subtle irreproducibility bugs.

---

### ISSUE 7: Integer Truncation Loses Precision

**Where**: [heuristics.cpp:170](file:///home/alejr/Documentos/heuristica/heuristicas/src/heuristics.cpp#L170)

```cpp
return static_cast<int>(currentFormula->evaluate(start, target));
```

`static_cast<int>` truncates toward zero. For a formula that returns `4.9`, the heuristic becomes `4` — losing 18% of the information. This systematically underestimates, which:
- Increases node expansions (weaker guidance)
- Benefits admissibility (underestimation is safe)
- May create "staircase" artifacts in the fitness landscape

**Recommendation**: Use `std::round()` or `std::lround()` instead:
```diff
-return static_cast<int>(currentFormula->evaluate(start, target));
+return std::max(0, (int)std::lround(currentFormula->evaluate(start, target)));
```

This combines with Issue 4's non-negative clamping for a complete fix.

---

## 🟢 DESIGN CONCERNS (Not Bugs, But Worth Noting)

### CONCERN 8: SA Compares Incompatible Fitness Values

**Where**: [main.cpp:227-234](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L227-L234)

```cpp
double fitness_pre = ga.getBestFitness();           // GA fitness = speedup - 0.0005 × size
double fitness_pos = lambda_fitness(optimizedFormula); // Raw speedup (no regularization!)

if (fitness_pos < fitness_pre) {  // Comparing apples to oranges!
    optimizedFormula = currentFormula;
```

`ga.getBestFitness()` returns `speedup - 0.0005 × size` (GA's regularized fitness), but `lambda_fitness(optimizedFormula)` returns raw speedup (or `speedup - 0.01 × admissibility_rate`). These are **different metrics** being compared.

If the SA produces a simpler formula with equal speedup, `fitness_pos` (raw speedup) will be higher than `fitness_pre` (speedup minus regularization), so SA wins — this is actually OK behavior but it's incidental, not intentional. If you later change the GA's λ, this comparison silently changes semantics.

**Recommendation**: Compare using the same metric:
```diff
-double fitness_pre = ga.getBestFitness();
+double fitness_pre = lambda_fitness(ga.getBest());
```

---

### CONCERN 9: No Timeout on A\* During Fitness Evaluation

**Where**: [main.cpp:193-194](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L193-L194)

Each fitness evaluation runs A\* on ~150 training problems. If a formula produces a terrible heuristic (e.g., constant negative value), A\* may expand the entire grid per problem. For a 500×500 map, that's ~250K expansions × 150 problems × 80 individuals = **3 billion expansions per generation**. At ~10M expansions/sec, that's ~5 minutes per generation.

Currently there's no timeout or expansion limit per A\* call during fitness evaluation. A single bad individual can stall the entire generation.

**Recommendation**: Add an expansion cap:
```cpp
// In aStar():
if (res.expansions > MAX_EXPANSIONS_BUDGET) {
    res.path.clear();
    return res; // Abandon search
}
```

---

### CONCERN 10: Training Set Uses Only One Seed

**Where**: [main.cpp:163](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L163)

```cpp
srand(42); // Always seed 42 for training set selection
```

The formula is synthesized once per map using a fixed training set (seed 42), then tested across 5 seeds. But the training set itself never varies. This means:
- You can't measure variance in the *synthesis* process
- If seed 42 happens to produce a non-representative training sample for a map, the formula will be biased
- The 5 seeds only vary the *benchmark* (pivot selection, degradation), not the *synthesis*

**Recommendation**: For more robust results, consider synthesizing one formula per seed (5 formulas per map) and reporting the variance. This would capture the stochastic nature of GP synthesis itself.

---

### CONCERN 11: `computarDistPivos` Called Multiple Times Per Seed

**Where**: [main.cpp:316-318](file:///home/alejr/Documentos/heuristica/heuristicas/src/main.cpp#L316-L318)

```cpp
for (int n : numPivos) {
    computarDistPivos(n);  // Generates NEW pivots for each n
    pivosPorN[n] = pivos;
```

For each seed, `computarDistPivos` is called 4 times (for 10, 20, 50, 100 pivots). Each call generates a **completely independent set** of pivots via Farthest-First. This means the 10-pivot set is NOT a subset of the 20-pivot set.

This is defensible (each pivot count is independently optimized), but it means you can't directly attribute the improvement from 10→20→50→100 pivots to "adding more pivots." You're comparing entirely different pivot placements.

**Alternative approach** (not necessarily better, just different): Generate 100 pivots once via Farthest-First, then use the first 10, 20, 50, 100 as nested subsets. This would isolate the effect of *adding* pivots vs. *changing* pivot placement.

---

## Summary Table

| # | Type | Severity | Issue | Affects Results? |
|---|---|---|---|---|
| 1 | 🔴 Bug | **HIGH** | Coordinate swap in ADMISSIBILITY check | Yes — admissibility_rate is wrong for asymmetric formulas |
| 2 | 🔴 Bug | **HIGH** | HYBRID never generates pivot terminals | Yes — HYBRID ≡ DELTA in practice |
| 3 | 🔴 Bug | LOW | `size_t` underflow in ratio for empty paths | Potentially, if any scenario is disconnected |
| 4 | 🟡 Method | MEDIUM | No negative heuristic clamping | Increases unnecessary expansions |
| 5 | 🟡 Method | MEDIUM | Non-deterministic GA reproduction | Results not fully reproducible |
| 6 | 🟡 Method | LOW | Mixed `rand()` / `mt19937` | Fragile reproducibility |
| 7 | 🟡 Method | LOW | Integer truncation (floor vs round) | Systematic underestimation |
| 8 | 🟢 Design | LOW | SA vs GA fitness comparison uses different metrics | Incidentally OK but semantically wrong |
| 9 | 🟢 Design | LOW | No A\* timeout in fitness eval | Can stall on bad individuals |
| 10 | 🟢 Design | LOW | Single synthesis seed | Can't measure synthesis variance |
| 11 | 🟢 Design | INFO | Independent pivot sets per count | Alternative: nested subsets |

> [!IMPORTANT]
> **Issues 1 and 2 are the most impactful.** Issue 1 means your ADMISSIBILITY mode results may be inaccurate (the admissibility rate reported in the CSV is computed on a different function than what A\* actually uses). Issue 2 means HYBRID mode is completely broken — it's just DELTA mode with wasted pivot computation.
>
> The good news: **DELTA mode** (your primary mode) and **ABSOLUTE mode** are unaffected by these bugs. Manhattan and Memory-based heuristics are also clean.
