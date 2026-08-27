# RESUMO — análise estatística do PIBIC

4 CSVs originais + 3 medições novas (`medicoes/`). `arena` deduplicado em tudo (execução
repetida em modo append: 3.900 linhas em `base`, 12.900 em `robustez`). Semente 20260820.
Redação das correções em `CORRECOES_TEXTO.md`; o não-computável em `LIMITACOES.md`.

**A regra que muda quase todos os números:** razões agregam por média **geométrica**;
expansões normalizam por mapa antes de agrupar; e a unidade de replicação para generalizar
é o **mapa (n = 17)**, não a instância (n = 116.050). É isso, e não um ± sobre 5 sementes,
que conserta o E3. Uma checagem que só a média geométrica passa, e que serve de defesa em
arguição: 2,799 (Manhattan÷Fórmula) × 2,811 (Fórmula÷Memória-100) = 7,866, exatamente a
razão Manhattan÷Memória-100 medida em separado. Médias aritméticas de razões não fecham
assim — é a manifestação concreta do viés que Fleming & Wallace (CACM, 1986) descrevem.

## Placar

| | achado em uma linha | veredito | relatório |
|---|---|---|---|
| **A0** | a memória **é** reprocessada sob degradação; 93,4% das distâncias mudam | **contradiz** §4.3, §5.4 | sim, texto |
| **A3** | o 51,98× compara memória de uma população com Manhattan de outra → **7,87×** | **corrige** Tab. 4 | sim, tabela |
| **A11** | o desvio de 138,44 é colapso de pivô em bolsão desconexo: 7 previstos, 7 observados | **contradiz** §5.1 | sim, 2 frases |
| **A1** | interação estratégia × padrão: η²ₚ = 0,241, p ≤ 0,005 (permutação) | confirma a tese | sim, 1 frase |
| **A2** | inversão de hierarquia: Memória-100 1,06→2,82; Fórmula 4,47→1,35 | confirma, agora com prova | **Figura 1** |
| **A4** | Memória-50 tem a 2ª melhor mediana e p99 no teto do Dijkstra (39× a mediana) | revela | **Figura 2** |
| **A5** | 4 pares, Holm, δ de Cliff de 0,33 (médio) a 0,87 (grande) | resolve E3–E5 | meia frase |
| **A6** | só **18,5%** dos caminhos são ótimos; 44,9% excedem 1,10 | confirma + acrescenta | sim, 1 frase |
| **A7** | 109 MB num só mapa; síntese custa 777×–12.197× a pré-computação dos pivôs | resolve E8, E9 | tabela + 1 frase |
| **A8** | a regularização é inerte: λ‖T‖ ≤ 1,6% da aptidão, e tamanho **aumenta** a aptidão | **contradiz** §3.4 | sim, 2 frases |
| **A12** | a fórmula viola admissibilidade em **99,9%** dos pares — e isso não prevê subotimalidade | **contradiz** §5.3 | sim, 1 frase |
| **A9** | re-sintetizando com semente fixa, **12 de 13** mapas dão fórmula diferente | **corrige** estatuto da Tab. 3 | sim, 1 frase |
| **A10** | 89%–99% dos pares são descartados, sem contabilização | resolve E7 | limitação |

---

## Os três achados que mudam o que o texto pode afirmar

### A0 — O relatório diz que a memória não é reprocessada; o código a reprocessa por inteiro
`main.cpp:227` troca o grid pelo degradado e `main.cpp:244` chama `computarDistPivosFixos`,
que roda `bfsPivo` sobre o grid já degradado. Medido nos 17 mapas: **93,4% das distâncias pré-computadas mudam** (mediana; intervalo interquartil
81,9%–98,0%, e em 97,0% das medições a mudança passa de metade das células), e **87,5% das
células ficam inalcançáveis a partir do pivô**. Só as *posições* dos pivôs ficam congeladas (100% das medições). As 6 medições em que nada
muda são todas de `brc201d`, onde os pivôs colapsados do A11 ficaram num bolsão que a
degradação nunca alcançou — corroboração independente daquele mecanismo.

> "As posições dos pivôs permanecem fixas sob degradação, mas as distâncias a partir deles
> são recalculadas sobre o mapa modificado; a comparação de robustez concede à heurística de
> memória uma atualização completa de suas tabelas, e seus fatores de degradação devem ser
> lidos como um limite superior."

**Contradiz** `main.tex:534` e `:695` ("sem reprocessamento das heurísticas") e o mecanismo
de `:685` ("distâncias que descrevem um mapa que já não existe"). A causa real está medida:
pivôs inalcançáveis são **pulados** por `heuristicaMemoryBased` e a estimativa colapsa para
zero. **Não destrói a tese — reforça:** a fórmula é a menos degradada nos **5 de 5** padrões
sendo a única sem reprocessamento. E o efeito troca de sinal: sob padrão **linear**,
recalcular a BFS **piora** δ em 2,3–2,8× (os pivôs ficam do lado errado da barreira); sob
**estocástico**, melhora em 2,3–2,7×.

### A3 — O speedup de 51,98× compara duas populações de instâncias
`analise.py:120-134` monta as linhas de memória da Tabela 4 a partir de
`resultados_robustez.csv`; Manhattan e Fórmula vêm de `resultados_base.csv`. A robustez só
tem as **23.906 instâncias (20,5%)** que sobreviveram ao filtro de conectividade em 30% — os
pares mais curtos. Sobre esses mesmos pares, **o próprio Manhattan expande 2.169,46 nós, não
7.472,95**. As 12 células da tabela reproduzem exatamente sob essa regra, o que fecha o
diagnóstico. Corrigido (mesmas instâncias, pareado, média geométrica, IC 95% BCa/17 mapas):

| | Fórmula | Mem-10 | Mem-20 | Mem-50 | Mem-100 |
|---|---|---|---|---|---|
| relatório | 3,10× | 17,25× | 30,78× | 33,50× | 51,98× |
| **corrigido** | **2,80×** | **4,70×** | **5,94×** | **7,32×** | **7,87×** |
| IC 95% | [2,32; 3,30] | [3,30; 5,43] | [3,94; 6,95] | [4,64; 8,69] | [4,92; 9,39] |

> "As heurísticas de memória reduzem as expansões em 7,87× em relação a Manhattan com 100
> pivôs (IC 95% [4,92; 9,39] sobre os 17 mapas), contra 2,80× [2,32; 3,30] da fórmula."

**Corrige** `main.tex:130`, `:606-611` e `:619` — o fator está inflado 6,6×. **E elimina uma
anomalia:** a hierarquia passa a ser monotônica (4,70 < 5,94 < 7,32 < 7,87), então o
parágrafo sobre "comportamento não monotônico" dos 50 pivôs deve sair inteiro.

### A11 — O desvio de 138,44 tem causa geométrica exata e previsível
`generatePivots` sorteia o **primeiro** pivô uniformemente entre as células transitáveis. Se
ele cai num bolsão desconexo, todos os pivôs ficam presos lá, `dS == dG == -1` em quase toda
consulta, **h ≡ 0 e o A\* degenera em Dijkstra**. Previsto a partir das componentes conexas:
**7 colapsos esperados, 7 observados, as mesmas 7 células** — todas com o primeiro pivô fora
da maior componente e h ≡ 0 em 99,3%–100% das consultas. Nenhum colapso nos 15 mapas 100%
conexos. `brc201d`: 167 componentes, 17,9% fora da maior, 5 colapsos em 20 sorteios
(esperado 3,6). `brc000d`: 2 componentes, 5,4%, 2 em 20 (esperado 1,1).

> "O desvio de 138,44 não reflete ruído amostral: `brc201d` tem 167 componentes conexas, com
> 17,9% das células fora da maior, e o sorteio uniforme do primeiro pivô cai nesse conjunto
> com probabilidade proporcional — em 7 dos 340 sorteios, todos os pivôs ficaram confinados
> a um bolsão e a heurística colapsou para h ≡ 0."

**Contradiz** `main.tex:619` ("instabilidade do sorteio [...] e **não necessariamente um
efeito geométrico sistemático**"). **E corrige a nota da Tabela 4**, que exclui só
`(brc000d, 50)` e mantém caladas `(brc201d, 10)` nas sementes 123 e 456 e `(brc201d, 50)`
nas sementes 42, 456 e 789 — onde a memória fica **pior que Manhattan** (13.290 contra 7.163
expansões). Correção de código: sortear o primeiro pivô na maior componente (uma linha).

---

## As demais

**A1 — tese central.** `log δ ~ estrategia*padrao*nivel + C(mapa)` sobre células
(mapa × semente × estratégia × padrão × nível): interação **F(20; 7.544) = 119,48;
η²ₚ = 0,241**. Principais: estratégia 0,494; nível 0,309; padrão 0,264. Permutação com o
rótulo de estratégia embaralhado **dentro da instância** (válido: é fator intra-instância):
F observado **82× o máximo de 200 permutações nulas**, p ≤ 0,005 — limite de resolução, não
de evidência. No estrato de dificuldade comum aos 5 padrões a interação **sobrevive**
(η²ₚ = 0,123), o que mostra que não é artefato do viés do A10.
> "A estratégia explica 49,4% da variância parcial do fator de degradação e o padrão, 26,4%;
> a interação é significativa (η²ₚ = 0,241; p < 0,001), confirmando que a ordem de mérito
> depende do regime de modificação do mapa."

Precisão importante: a interação **não é troca de vencedor** — a fórmula é a menos degradada
nos 5 padrões. É a reordenação das demais: Manhattan vai do posto 2 (linear, δ = 1,16, à
frente de todas as memórias) ao posto 4 (estocástico, δ = 2,47, atrás de memória-50 e -100).

**A2 — ranking (Demšar) — FIGURA 1.** Friedman: estático χ² = 70,98 (p = 6,4·10⁻¹⁴),
degradado χ² = 67,42 (p = 3,5·10⁻¹³); distância crítica de Nemenyi = **1,83**.
Postos estático→degradado: Memória-100 **1,06→2,82**; Memória-50 2,47→3,53;
Memória-20 2,94→4,94; Memória-10 4,12→**5,88**; Fórmula 4,47→**1,35**; Manhattan
**5,94**→2,47. Fórmula vs Memória-100: Cliff δ **+0,917 → −0,813** (ambos "grande").
> "A hierarquia se inverte: a memória com 100 pivôs sai do primeiro posto no cenário
> estático (1,06) para o terceiro sob degradação (2,82), enquanto a fórmula sai do quinto
> (4,47) para o primeiro (1,35) — variação superior à distância crítica (1,83) nos dois
> sentidos."

**A4 — cauda — FIGURA 2.** Expansões ÷ teto do Dijkstra (medido agora), mediana / p99 /
razão: Manhattan 0,323 / 0,873 / **2,7**; Fórmula 0,071 / 0,518 / 7,3; Memória-10
0,039 / **1,000** / **26,0**; Memória-20 0,030 / 0,261 / 8,7; Memória-50
0,025 / **1,000** / **39,4**; Memória-100 0,023 / 0,128 / 5,5. O p99 no teto vem
**inteiramente do A11** — sem as células colapsadas cai para 0,339 e 0,167.
> "Em jogo, o que estoura o orçamento de quadro não é a busca média, é a pior busca do
> segundo: a configuração de 50 pivôs tem a segunda melhor mediana de todas (0,025 do teto do
> Dijkstra) e ainda assim um percentil 99 no teto — 39 vezes a própria mediana."

**A5 — pareados.** Wilcoxon + Holm + δ de Cliff, nos dois níveis. Manhattan×Fórmula
δ = +0,550, razão 2,80× [2,32; 3,30]; Manhattan×Memória-100 δ = +0,868, 7,87× [4,92; 9,39];
Fórmula×Memória-10 δ = +0,333 (médio), 1,68× [1,41; 1,98]; Fórmula×Memória-100 δ = +0,665,
2,81× [2,22; 3,38]. Com 116.050 pares todo p é abaixo do menor float representável — o que
separa é a magnitude.

**A6 — subotimalidade.** ρ médio 1,1226 (**confirma** 12,19%; a diferença é a duplicata de
`arena`); por mapa 11,18% [8,49%; 13,33%]. Máximo ρ = 4,1928 em `den012d` (**confirma** 4,19).
O que a média esconde: **18,5% de caminhos ótimos**, 62,97% acima de 1,05, **44,94% acima de
1,10**. A hipótese do contorno **confirma-se**: caminhos ótimos caem de 97,2% (1–25 células)
para 1,1% (>400), Spearman = **+0,494**. **Inédito:** no mapa degradado a subotimalidade sobe
de 37,8% para **49,3%** das instâncias.

**A7 — memória, preparação e Pareto.** `bfsPivo` aloca a **grade inteira**, não só as células
transitáveis: real = |P|·h·w·4 B, **4,1× o teórico** (até 8,2× em mapas esparsos), **109 MB
num único mapa** (den602d, 100 pivôs). Pré-computação dos pivôs (E9, nunca instrumentada):
**12,0 ms a 103,4 ms**; síntese 4 s a 2.025 s → **a síntese custa 777×–12.197× a
pré-computação de 100 pivôs**. Pareto sobre expansões × memória × subotimalidade × robustez:
**as 6 configurações são não-dominadas** — prova de dominância para o "não há estratégia
universalmente superior" de `main.tex:705`. **Corrige** `:656`: em geração procedural a
estratégia inviável é a fórmula, não a memória.

**A8 — as 17 fórmulas.** ASTs com **mediana de 39 nós**, máximo **78** (brc203d),
profundidade até 26; 1 de 17 é simétrica em Δx/Δy. A penalidade λ‖T‖ vale no máximo **1,56%**
da aptidão (mediana 0,52%); para chegar a 10%, λ teria de ser **19× maior**. E
**Spearman(tamanho, aptidão) = +0,487 (p = 0,047)** — tamanho *aumenta* a aptidão. Gap de
generalização (treino ÷ medido): mediana 1,13×, até 1,56×.
**Contradiz** `main.tex:412`; o comentário do próprio código diz o oposto
(`GeneticAlgorithm.h:71`: *"Penalidade por tamanho baixíssima para permitir fórmulas
complexas"*). **Responde um trabalho futuro** de `:709`: a correlação entre complexidade da
AST e subotimalidade **não existe** (ρ = −0,014).

**A12 — admissibilidade, medida.** O relatório caracteriza a admissibilidade das três
classes de forma teórica mas nunca a mede. Comparando h(s,g) com a distância ótima d\*(s,g)
do Dijkstra em todos os pares: a fórmula viola admissibilidade em **mais de 99% dos pares nos
17 mapas**, com superestimação **mediana de 270×** e máximo de 6.711×. Controle: Manhattan
viola em **0,0000%**, como manda a construção. **O achado:** a correlação entre violar
admissibilidade e produzir caminho subótimo é **nula** (ρ = −0,003; p = 0,99). No `arena`, h
superestima em 99,2% dos pares (fator mediano 19×) e ainda assim 100% dos caminhos são ótimos.
> "A violação de admissibilidade é praticamente universal — acima de 99% dos pares em todos os
> 17 mapas, com superestimação mediana de 270× — mas não se correlaciona com a subotimalidade
> observada (ρ = −0,003): o que a determina é a geometria do mapa, não a magnitude do erro da
> estimativa."

**Contradiz** `main.tex:667`, que afirma que a fórmula do `arena` "nunca chega a superestimar
o custo real". **É o item que liga a Seção 3 aos dados**, que era o pedido de fortalecer o
lado teórico.

**A9 — reprodutibilidade.** `GeneticAlgorithm.cpp:19,68` semeia população inicial e seleção
de pais com `std::random_device`. A duplicata de `arena` (fórmula e aptidão idênticas,
expansões idênticas em 100% dos pares) **não é evidência de estabilidade do AG** — é
evidência de que o A* é determinístico dada a fórmula. Re-sintetizando com a semente do AG
fixada e explícita, em **13 dos 17 mapas** (n interrompido por prazo; ver L4): em **12 dos 13
a fórmula campeã é diferente** da reportada. O único mapa que reconverge é `arena`, o menor e
mais fácil. A aptidão muda pouco (mediana **2,1%**, máx **9,0%** em `den000d`) mas a fórmula
muda quase sempre, e o tamanho da AST muda junto (mediana 41 nós, de 11 a 87).
> "Fixando a semente do algoritmo genético e re-sintetizando, 12 dos 13 mapas testados
> produzem uma fórmula campeã diferente da reportada, com variação de aptidão de apenas 2,1%
> (mediana). As fórmulas da Tabela 3 são, portanto, **uma amostra de um espaço de soluções
> aproximadamente equivalentes**, e não um ótimo reprodutível."

Isso **não invalida** nenhum número medido — as expansões reportadas são as daquelas fórmulas,
e o A* é determinístico. Muda o **estatuto** da Tabela 3: ela documenta uma execução, não um
resultado reproduzível. Correção de uma linha em `GeneticAlgorithm.cpp` resolve (C10).

**A10 — descartes.** `main.cpp:217-224` seleciona os pares no estado de 30% e usa esse
conjunto nos três níveis (por isso o descarte não é separável por nível). Sobreviventes /
caminho ótimo mediano / expansões de Manhattan: Linear **869 (0,75%)** / 5 / 10; Sparse
4.996 (4,31%) / 44 / 396; Organic 5.444 (4,69%) / 37 / 310; Radial 11.086 (9,55%) / 70 /
1.877; Stochastic 12.448 (10,73%) / 111 / 2.825 — contra 116.050 / 328 / 7.515 no conjunto
completo. Interseção dos 5 padrões: **71 instâncias**; os conjuntos não são aninhados.
> "Entre 89% e 99% dos pares perdem conectividade a 30% de bloqueio e são descartados; os
> sobreviventes são sistematicamente os mais curtos — sob bloqueio linear, o caminho ótimo
> mediano cai de 328 para 5 células."

A comparação **entre estratégias** segue válida (pareada na mesma linha do CSV); a comparação
**entre padrões** fica comprometida e precisa de ressalva (`LIMITACOES.md`, L2).

---

**Fora do relatório:** Pareto completo, tabelas por mapa, testes no nível de instância,
correlações da AST, curvas δ por nível — em `tabelas/` e `figuras/`, para o repositório.
Critério aplicado: **se o aluno não sabe explicar o número numa arguição, ele não entra.**
