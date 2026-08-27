# DADOS.md — o que tem em cada arquivo

Índice dos dados da análise. **Tudo que é dado está em `.csv`.** Este arquivo explica, para
cada CSV, o que ele contém, qual é o número que importa e onde ele toca o relatório.

Estrutura:

```
analise/
  tabelas/*.csv     <- 34 tabelas, uma ou mais por análise (A0..A12)   <- os DADOS
  figuras/*.pdf     <- 2 figuras candidatas ao relatório (+ .png)
  medicoes/*.csv    <- medições novas em C++ (insumo das tabelas)
  scripts/*.py      <- reproduzem tabelas/ e figuras/ a partir de medicoes/ + CSVs originais
  RESUMO.md         <- os achados, com a frase pronta em português por análise
  LIMITACOES.md     <- o que NÃO se pode afirmar, e por quê (L1..L10)
  CORRECOES_TEXTO.md<- trechos do main.tex a corrigir, com linha e redação sugerida (C1..C11)
```

Reproduzir tudo do zero: `.venv/bin/python scripts/run_all.py` (roda em ~3 min).

**Convenção de agregação usada em todas as tabelas** (é o conserto metodológico central):
razão pareada por instância → média **geométrica** por mapa → média geométrica entre os
17 mapas. **A unidade de replicação é o mapa (n = 17), não a instância (n = 116.050)** —
instâncias do mesmo mapa não são independentes. Semente global dos scripts: `20260820`.

---

## A0 — A memória é reprocessada sob degradação

O relatório afirma em §4.3 e §5.4 que as heurísticas não são reprocessadas. **O código
reprocessa**: `main.cpp:227` troca o grid pelo degradado e `main.cpp:244` recalcula todas as
distâncias dos pivôs por BFS. Só as *posições* dos pivôs ficam congeladas.

| arquivo | o que tem |
|---|---|
| `a0_reprocessamento.csv` | fração das distâncias pré-computadas que **mudam** após a degradação, por padrão × nível. Colunas `mean/min/max` sobre os 17 mapas. |
| `a0_fresco_vs_congelado.csv` | δ (fator de degradação) com distâncias recalculadas (`fresco`) vs. congeladas (`congelado`), e a razão entre os dois. |

**Números:** 93,4% das distâncias mudam (mediana; IQR 81,9%–98,0%; >50% em 97% das medições).
87,5% das células ficam inalcançáveis a partir do pivô. Posições dos pivôs congeladas em 100%
das medições. O ganho do reprocessamento **muda de sinal por padrão**: Linear 0,36–0,44
(recalcular *piora* 2,3–2,8×), Stochastic 2,3–2,7 (ajuda).

**Por que importa:** a tese sobrevive e fica mais forte — a fórmula é a menos degradada em
5 dos 5 padrões *apesar* de a memória receber um BFS completo de graça a cada configuração.
Mas a narrativa de mecanismo do §5.4 ("distâncias que descrevem um mapa que já não existe")
está errada e precisa ser reescrita.

**Ressalva:** o teste de otimalidade de caminho **não** decide isso. Bloquear células só
aumenta distâncias, então uma distância obsoleta continua admissível. Só o código decide —
por isso a medição direta em `medicoes/reprocessamento*.csv`.

---

## A1 — A tese central (interação estratégia × padrão)

Resposta: `log δ`, pareada por instância, num modelo `log δ ~ estrategia * padrao * nivel`.

| arquivo | o que tem |
|---|---|
| `a1_anova_completa.csv` | ANOVA tipo II sobre todas as instâncias sobreviventes. F, p, η²ₚ, η² total. |
| `a1_anova_estrato.csv` | a mesma ANOVA **dentro do estrato de dificuldade comum** — controla o viés de seleção do A10. |
| `a1_delta_por_padrao.csv` | δ médio por padrão × estratégia (a matriz 5 × 6 que resume tudo). |
| `a1b_delta30_corrigido.csv` | δ a 30% de bloqueio, recalculado com a regra correta. |
| `a1b_delta30_relatorio.csv` | o mesmo, no formato média ± dp, para comparar com o que está no relatório hoje. |

**Números:** interação estratégia × padrão F(20; 7544) = 119,48, **η²ₚ = 0,241**. Sobrevive à
estratificação por dificuldade (η²ₚ = 0,123). Teste de permutação (rótulos embaralhados dentro
da instância, 200 réplicas): F observado é **82× o máximo dos 200 nulos** → p ≤ 0,005 sem
pressupostos. A fórmula é posto 1 nos 5 padrões; Manhattan vai de posto 2 a 4.

---

## A2 — Ranking honesto (Friedman + Nemenyi) → **Figura 1**

| arquivo | o que tem |
|---|---|
| `a2_escore_estatico.csv` | escore por mapa (17 linhas × 6 configs) no mapa **original**. |
| `a2_escore_degradado.csv` | idem, sob degradação. |
| `a2_postos.csv` | posto médio de cada config nos dois cenários, e a variação. **É o resumo da figura.** |

**Números:** Friedman estático χ²(5) = 70,98 (p = 6,4·10⁻¹⁴); degradado χ²(5) = 67,42
(p = 3,5·10⁻¹³); distância crítica de Nemenyi **CD = 1,83**. Memória-100 vai de posto 1,06 a
2,82; a Fórmula de 4,47 a **1,35**; Manhattan de 5,94 a 2,47. Cliff's δ da inversão:
+0,917 → −0,813.

**A figura é a inversão de hierarquia** — dois diagramas CD lado a lado. É a prova visual da
tese central. `figuras/fig1_diagrama_cd.pdf`.

---

## A3 — Os speedups corrigidos (o conserto da Tabela 4)

| arquivo | o que tem |
|---|---|
| `a3_reproducao_tabela4.csv` | **reprodução dos 12 valores da Tabela 4 com a regra antiga**, mais a coluna `fonte` (de qual população cada linha veio) e `confere` (bate ou não). |
| `a3_speedups_corrigidos.csv` | speedup geométrico com IC BCa sobre os 17 mapas, com e sem as células degeneradas, e o erro do relatório em ×. |
| `a3_speedup_por_mapa.csv` | o dado bruto por mapa, antes de agregar. |

**O achado:** os 12 valores reproduzem **exatamente** (coluna `confere` = True nas 6 linhas).
A causa do erro é que as linhas de memória vêm do subconjunto de **23.906** instâncias
sobreviventes — 20,5% do total, e 21.361 no caso de 50 pivôs, por causa da exclusão de
`brc000d` — enquanto Manhattan e fórmula usam as **116.700**. São populações diferentes.
**Nessas mesmas 23.906 instâncias o próprio Manhattan expande 2.169,46, não 7.472,95** — um
fator de 3,4× que infla todos os speedups de memória.

| config | relatório | corrigido | IC 95% |
|---|---|---|---|
| Fórmula | 3,10× | **2,80×** | [2,32; 3,30] |
| Memória-10 | 17,25× | **4,70×** | [3,30; 5,43] |
| Memória-20 | 30,78× | **5,94×** | [3,94; 6,95] |
| Memória-50 | 33,50× | **7,32×** | [4,64; 8,69] |
| Memória-100 | 51,98× | **7,87×** | [4,92; 9,39] |

**Efeito colateral importante:** a hierarquia vira **monotônica** em número de pivôs. Isso
apaga o parágrafo do `main.tex:619` sobre a "não-monotonicidade em 50 pivôs" — que era um
artefato, não um fenômeno.

---

## A4 — Distribuições e cauda → **Figura 2**

| arquivo | o que tem |
|---|---|
| `a4_distribuicao_normalizada.csv` | mediana, IQR, p90, p95, p99, máx das expansões **normalizadas pelo Dijkstra**, por config. |
| `a4_distribuicao_absoluta.csv` | o mesmo em expansões absolutas. |
| `a4_cauda_vs_colapso.csv` | p99 com e sem as células de colapso do A11 — mostra que a cauda **é** o colapso. |

**Número:** Memória-50 tem a 2ª melhor **mediana** (0,025) e p99 **= 1,000** — ou seja, no
pior 1% dos casos ela expande o mapa inteiro, como o Dijkstra. Isso é **39,4× a mediana**.
Removendo as células de colapso, o p99 cai para 0,167.

**O argumento:** num jogo, o que estoura o orçamento de quadro é a pior busca, não a média.
Uma heurística com ótima mediana e p99 no teto é pior na prática do que a média sugere.
`figuras/fig2_ecdf.pdf`.

---

## A5 — Testes pareados com tamanho de efeito

`a5_testes_pareados.csv` — 4 pares (Manhattan×Fórmula, Manhattan×Memória-100,
Fórmula×Memória-10, Fórmula×Memória-100). Wilcoxon com correção de Holm, Cliff's δ, razão
geométrica com IC.

**A coluna que interessa é o contraste `p_instancia` vs `p_mapa`:** no nível da instância
(n = 116.050) qualquer diferença dá p ≈ 0; no nível do mapa (n = 17) só sobrevive o que é
real. δ de Cliff de 0,33 (médio) a 0,87 (grande). **Esse contraste é, ele próprio, a
demonstração de por que média ± dp sobre 5 sementes não era suficiente.**

---

## A6 — Subotimalidade fina

| arquivo | o que tem |
|---|---|
| `a6_taxas_desvio.csv` | fração de caminhos ótimos e acima de 1,05 / 1,10 / 1,50. |
| `a6_por_mapa.csv` | recalculado **por mapa antes de agrupar** (é isso que move o 12,19% do relatório). |
| `a6_por_categoria.csv` | por categoria de mapa. |
| `a6_por_comprimento.csv` | por faixa de comprimento do caminho ótimo — testa se o desvio cresce em caminhos que exigem contorno. |
| `a6_subotimalidade_degradada.csv` | **dado inédito**: subotimalidade da fórmula **no mapa degradado**, por padrão × nível. |

**Números:** só **18,48%** dos caminhos são ótimos; **44,94%** excedem 1,10.
Spearman(comprimento, ρ) = **+0,494** — o desvio cresce com o comprimento, confirmando a
hipótese de contorno. Sob degradação a subotimalidade sobe de 37,79% para **49,32%**, e 100%
dos desvios são superestimativas.

---

## A7 — Memória e fronteira de Pareto

| arquivo | o que tem |
|---|---|
| `a7_memoria_por_mapa.csv` | consumo teórico (4 B/int) e **real** (`vector<vector<vector<int>>>`) em MB, por mapa × config. |
| `a7_custo_preparacao.csv` | tempo de pré-computação dos pivôs vs. tempo de síntese do AG, por mapa. |
| `a7_pareto.csv` | as 6 configs em 5 eixos (expansões, memória, subotimalidade, robustez, preparação) e quais são não-dominadas. |

**Números:** `bfsPivo` aloca a grade inteira por pivô → **4,1× o teórico** (até 8,2×), chegando
a **109 MB** em `den602d` com 100 pivôs. A pré-computação dos pivôs custa 12–103 ms; a síntese
do AG custa 4–2.025 s → **777× a 12.197× mais cara**. **As 6 configurações são todas
não-dominadas** — não há uma escolha universalmente melhor, e isso é o resultado.

---

## A8 — As fórmulas sintetizadas (a tangente qualitativa)

| arquivo | o que tem |
|---|---|
| `a8_formulas.csv` | uma linha por mapa: tamanho e profundidade da AST, contagem de cada operador, simetria em Δx/Δy, constantes, aptidão, **penalidade λ‖T‖ e seu percentual da aptidão**. |
| `a8_correlacoes.csv` | tamanho/profundidade/aptidão vs. speedup e subotimalidade medidos. |
| `a8_gap_generalizacao.csv` | `speedup_treino` (a aptidão, medida em 25% do cenário) vs. `speedup_medido` → **medida direta de overfitting**. |

**O achado que contradiz o §3.4:** o relatório (`main.tex:412`) diz que a regularização
"favorece fórmulas mais compactas". O próprio código diz o contrário —
`GeneticAlgorithm.h:71`: `lambda = 0.0005 // Penalidade por tamanho baixíssima para permitir
fórmulas complexas`. Medido: **λ‖T‖ ≤ 1,56% da aptidão** (λ precisaria ser 19× maior para
entrar na seleção), AST mediana de 39 nós e máxima de 78, e
**Spearman(tamanho, aptidão) = +0,487 (p = 0,047)** — tamanho **aumenta** a aptidão.
A regularização é inerte.

---

## A9 — Reprodutibilidade da síntese

`a9_sintese_repetida.csv` — por mapa: nº de re-sínteses, fórmulas distintas, faixa de aptidão
e de tamanho da AST, e `bate_com_original`.

**Número:** re-sintetizando com a semente do AG fixada e explícita, **12 dos 13 mapas testados
produzem uma fórmula campeã diferente** da reportada. O único que reconverge é `arena`, o
menor e mais fácil. A aptidão muda pouco (mediana 2,1%, máx 9,0%) mas a fórmula muda quase
sempre.

**Leitura:** as fórmulas da Tabela 3 são **uma amostra de um espaço de soluções
aproximadamente equivalentes**, não um ótimo reprodutível. Isso **não invalida** nenhuma
expansão medida — o A* é determinístico dada a fórmula. Muda o *estatuto* da tabela.

**Cobertura:** 14 sínteses, 13 dos 17 mapas (faltam `den500d`, `den501d`, `den602d`,
`hrt201n`), semente 1 em todos + semente 2 em `arena`. Encerrado por prazo. Ver **L4** —
reportar sempre como "12 de 13 mapas testados", nunca "todos os mapas".

---

## A10 — Contabilizar os descartes

| arquivo | o que tem |
|---|---|
| `a10_sobrevivencia_por_padrao.csv` | sobreviventes, taxa global, taxa média por mapa e dispersão entre mapas. |
| `a10_sobrevivencia_por_mapa.csv` | a matriz 17 × 5 completa. |
| `a10_vies_dificuldade.csv` | distribuição do comprimento ótimo dos sobreviventes **contra** a de todos os pares — mede o quanto o filtro seleciona pares fáceis. |

**Números:** Linear **869 (0,75%)**, Sparse 4.996 (4,31%), Organic 5.444 (4,69%), Radial
11.086 (9,55%), Stochastic 12.448 (10,73%). **Interseção dos 5 padrões: 71 instâncias.**
Sob bloqueio linear o caminho ótimo mediano dos sobreviventes cai de 328 para **5** células.

**Por que o descarte não é separável por nível:** `main.cpp:217-224` seleciona os pares pela
conectividade **no estado de 30%** e usa esse mesmo conjunto nos três níveis. Por isso as
contagens não caem com o nível.

**Consequência:** a comparação **entre estratégias** segue válida (pareada na mesma linha do
CSV). A comparação **entre padrões** está confundida e precisa de ressalva — ver **L2**.

---

## A11 — Os pivôs degenerados (a explicação do desvio de 138,44)

`a11_colapso_pivos.csv` — por mapa: nº de componentes conexas, fração de células fora da
maior componente, colapsos **esperados** e **observados**.

**O mecanismo:** `generatePivots` sorteia o **primeiro** pivô uniformemente sobre as células
transitáveis. Se ele cai num bolsão desconexo, `bfsPivo` devolve −1 fora do bolsão, o argmax
da travessia Farthest-First fica preso lá, **todos** os pivôs ficam no bolsão, e para quase
toda consulta h ≡ 0 → **o A\* vira Dijkstra**.

**A previsão é falseável e passou:** 7 colapsos previstos a partir da estrutura de componentes
conexas, **7 observados, nas mesmas células**, todos com o primeiro pivô fora da maior
componente e h ≡ 0 em 99,3%–100% das consultas. **Zero** nos 15 mapas totalmente conexos.
Binomial p = 0,241 (consistente com o acaso *dado* o mecanismo). Sem essas 5 células, o desvio
de Memória-50 cai de **3.452,4 para 165,8**.

**O que isso corrige:** o relatório atribui a anomalia a "instabilidade do sorteio... e não
necessariamente um efeito geométrico sistemático" (`main.tex:619`). É exatamente um efeito
geométrico sistemático, e previsível. Além disso a nota de rodapé do `main.tex:615` exclui só
`(brc000d, 50 pivôs)` e mantém em silêncio `brc201d@10` e `brc201d@50`, onde a memória fica
*pior* que Manhattan. **Média ± dp sobre uma mistura bimodal não significa nada.**

**Conserto:** uma linha — sortear o primeiro pivô dentro da maior componente conexa.

---

## A12 — Admissibilidade, medida

`a12_admissibilidade.csv` — por mapa: fração de pares em que h(s,g) > d\*(s,g) para a fórmula,
**a mesma fração para Manhattan como controle**, inflação mediana/p99/máxima, e a
subotimalidade medida.

**Números:** a fórmula viola admissibilidade em **99,9%** dos pares (17/17 mapas acima de
99%), com inflação mediana de **269,6×** e máxima de **6.711×**. **O controle Manhattan dá
0,0000%** — o que valida o método de medição.

**O achado contra-intuitivo:** Spearman(inadmissibilidade, subotimalidade) = **−0,003
(p = 0,99)**. Violar admissibilidade **não prevê** caminho ruim. O `arena` é o caso extremo:
99,2% de violações, inflação mediana de 19×, e **100% dos caminhos ótimos**.

**Contradiz** `main.tex:667`, que afirma que a fórmula do `arena` "nunca chega a superestimar
o custo real". É o item que liga a Seção 3 (teoria) aos dados.

---

## `medicoes/` — as medições novas em C++

Não são re-execuções do experimento: são medições que **nunca tinham sido feitas**.

| arquivo | o que é |
|---|---|
| `dijkstra.csv` | expansões do Dijkstra por instância. É o **teto adimensional** que permite normalizar expansões entre mapas de escalas diferentes. Sem ele não dá para comparar mapas. |
| `pivos_precomp.csv` | tempo de pré-computação dos pivôs (17 mapas × 5 sementes × 4 configs). Fecha o lado não medido da comparação de custo e alimenta o Pareto do A7. |
| `reprocessamento.csv` | teste direto do A0: `distPivos` recalculado após degradação vs. BFS do mapa original. 20 células, 60 linhas cada, todas completas. |
| `reprocessamento_expansoes.csv` | δ com distâncias frescas vs. congeladas. |
| `sintese_repetida.csv` | as 14 re-sínteses semeadas do A9. |
| `sintese/*.csv` | uma linha por síntese concluída (insumo do consolidado acima). |
| `sintese/_incompletos_backup/` | checkpoints e locks de sínteses interrompidas por prazo. **Não entram em nenhuma tabela.** Guardados, não apagados. |
| `*.log` | saída bruta de cada medição, para auditoria. |

---

## O que **não** foi re-executado, por decisão

- **Experimentos base e de robustez.** As contagens de expansão são determinísticas e corretas
  *como medição*; o defeito é de **agregação**, e se conserta em pós-processamento. Re-rodar
  não mudaria nenhum número.
- **`tempo_ms`.** Medição única por instância, sem warm-up nem isolamento, com
  `-march=native -ffast-math`, em máquina compartilhada. Sem protocolo de benchmark o re-run
  não melhora nada. Conserto correto: **liderar com expansões** e declarar a limitação (L3).
- **Re-sortear os pivôs degenerados.** Seria cherry-picking. Mantê-los e explicá-los **é** o
  resultado (A11); a agregação reporta com e sem.

Ver `LIMITACOES.md` para a lista completa do que não se pode afirmar e por quê.
