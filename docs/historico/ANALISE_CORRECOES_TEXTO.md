# Correções a fazer no `main.tex`

Referências de linha são do `main.tex` em
`/home/alejr/RelatorioFinal_Modelo_AlexandrePereira_PIBIC_2025_2026/`.
Cada item traz o que o texto diz hoje, o que os dados dizem e uma redação sugerida.
Ordem: do mais grave para o menos.

---

## Antes de começar: duas armadilhas de leitura

**1. Existem DUAS monotonias, e elas têm destinos opostos.** Os nomes são parecidos e
trocá-las na redação inverte o sentido do texto:

| | o que é | onde aparece | destino |
|---|---|---|---|
| **monotonia dos speedups estáticos** | 4,70 < 5,94 < 7,32 < 7,87 (razão vs Manhattan, por nº de pivôs) | C4 | **restaurada** pela correção — e é ela que apaga o parágrafo dos "50 pivôs anômalos" de `main.tex:619` |
| **monotonia dos fatores de degradação** | δ₁₀ > δ₂₀ > δ₅₀ > δ₁₀₀, nos cinco padrões | C3c | **confirmada** — o parágrafo de `main.tex:685` fica como está |

Regra prática: se a frase fala de *quanto a heurística economiza no mapa intacto*, é a
primeira. Se fala de *quanto ela piora quando o mapa muda*, é a segunda.

**2. No C5, o p do teste binomial é alto de propósito.** p = 0,241 significa que a taxa de
colapsos observada **não se distingue** da prevista pelo modelo geométrico — é o modelo
passando no teste, não falhando. A leitura errada ("p > 0,05, logo não é significativo")
é fácil de fazer e vai aparecer em arguição. A resposta pronta: *"a hipótese nula aqui é o
próprio mecanismo proposto; um p baixo é que refutaria a explicação geométrica."* Se
preferir evitar a discussão, o argumento se sustenta sem o teste — 7 colapsos previstos,
7 observados, exatamente nas mesmas 7 células, e zero nos 15 mapas 100% conexos.

---

## C1 — §4.3 e Fig. 6: "sem reprocessamento das heurísticas" é falso para a memória
**Onde:** `main.tex:534` (Padrões de Degradação) e `main.tex:695` (legenda da Fig. 6).
**Hoje:** "os bloqueios são aplicados cumulativamente [...] **sem reprocessamento das
heurísticas após as modificações**."

**O que o código faz:** `main.cpp:227` troca o grid pelo degradado e `main.cpp:244` chama
`computarDistPivosFixos(pivosPorN[n])`, que executa `bfsPivo` (`heuristics.cpp`) sobre o
grid **já degradado**. Só as *posições* dos pivôs ficam congeladas. Medição direta
(`medicoes/reprocessamento.csv`, 17 mapas, semente 42): **93,4% das distâncias
pré-computadas mudam** entre o mapa original e o degradado (mediana; intervalo interquartil
81,9%–98,0%, e em 97% das medições a mudança passa de metade das células). A média por
padrão e nível vai de 59,5% (radial a 10%) a 99,3% (linear a 30%), e **87,5% das células
tornam-se inalcançáveis a partir do pivô** (mediana). As 6 medições em que nada muda são
todas de `brc201d`, onde os pivôs colapsados do C5 ficaram num bolsão que a degradação nunca
alcançou — corroboração independente daquele mecanismo.

> Estes números são da semente 42 (17 mapas, medição completa). A extensão às outras quatro
> sementes não foi executada, por prazo — ver L5. A conclusão qualitativa, que é a que entra
> no texto — **o reprocessamento é total** — não depende de semente, porque decorre do
> próprio código (`main.cpp:227,244`), não da amostra.

**Redação sugerida (§4.3):** "Os bloqueios são aplicados cumulativamente nos níveis de 10%,
20% e 30% das células livres. As posições dos pivôs são mantidas fixas, mas as distâncias
a partir deles são recalculadas sobre o mapa modificado; as heurísticas de Manhattan e de
fórmula não requerem reprocessamento algum. A comparação de robustez, portanto, concede à
heurística de memória uma atualização completa de suas tabelas — e o resultado da
Seção 5.4 deve ser lido como um limite *superior* para a robustez dessa estratégia."

**Consequência positiva:** a tese fica mais forte, não mais fraca. A fórmula supera a
memória em todos os cinco padrões (ver C3) **mesmo dando à memória um BFS completo de graça**.

---

## C2 — §5.4: o mecanismo narrado está invertido
**Onde:** `main.tex:685`.
**Hoje:** "a memória --- guiada por **distâncias que descrevem um mapa que já não existe**
--- inunda a sala inteira".

**Problema:** as distâncias descrevem exatamente o mapa que existe (C1). A explicação
correta é outra e está medida: ao recalcular a BFS num mapa fragmentado, parte dos pivôs
fica **inalcançável** a partir da origem ou do destino; `heuristicaMemoryBased`
(`heuristics.cpp`) pula esses pivôs (`if (dS != -1 && dG != -1)`), e a estimativa colapsa
em direção a zero. Quanto mais o mapa fragmenta, menos pivôs contribuem.

**Evidência:** em `medicoes/reprocessamento_expansoes.csv` o efeito **troca de sinal** por
padrão. Em den501d, 30% de bloqueio: sob padrão linear, distâncias *congeladas* dariam
δ = 1,55 contra δ = 3,00 das recalculadas (a atualização **piora**); sob estocástico, o
inverso (δ = 7,51 congelado contra 3,13 recalculado).

---

## C3 — §5.4 e resumo: fatores de degradação (média aritmética de razões)
**Onde:** `main.tex:130` (resumo), `main.tex:681`, `main.tex:683`.
**Hoje:** δ_max de 2,54 (fórmula), 3,26 (memória-100), 4,25 (Manhattan), 6,33 (memória-10).

Os quatro números **reproduzem exatamente**, mas vêm de média aritmética de razões sobre
instâncias agrupadas, sem normalizar por mapa (E1, E2). Corrigidos para média geométrica,
com a duplicata de `arena` removida e peso igual por mapa:

| estratégia | δ_max reportado | δ_max corrigido | pior padrão |
|---|---|---|---|
| Fórmula | 2,54 | **1,77** | Estocástico |
| Memória-100 | 3,26 | **2,30** | Linear |
| Manhattan | 4,25 | **2,51** | Estocástico |
| Memória-10 | 6,33 | **3,43** | Orgânico |

**A ordem se preserva** — a conclusão qualitativa do trabalho sobrevive. Mas:

**C3b — `main.tex:683` está contradito.** O texto afirma que "nos padrões radial e esparso
[...] a memória com 100 pivôs é a mais robusta (1,18 e 1,44), seguida de perto pela fórmula
(1,56 e 1,49)". Com a agregação corrigida, **a fórmula é a mais robusta nos cinco padrões**
(radial 1,09 contra 1,11; esparso 1,19 contra 1,26). Trocar por: "a fórmula é a estratégia
menos degradada em todos os cinco padrões, com vantagem estreita sobre a memória de 100
pivôs nos padrões espacialmente concentrados (radial e esparso) e ampla nos demais."

**C3c — `main.tex:685` CONFIRMA.** A monotonia δ₁₀ > δ₂₀ > δ₅₀ > δ₁₀₀ vale em todos os
cinco padrões também na agregação corrigida. Manter.

---

## C4 — Tabela 4 (§5.1): as linhas de memória vêm de outra população
**Onde:** `main.tex:598-619`.

`analise.py:120-134` monta as linhas de memória a partir de `resultados_robustez.csv`,
enquanto Manhattan e Fórmula vêm de `resultados_base.csv`. A robustez contém apenas as
**23.906 instâncias (20,5%)** que sobreviveram ao filtro de conectividade em 30% de
bloqueio — sistematicamente os pares mais curtos. Sobre esses mesmos pares, o **próprio
Manhattan expande 2.169,46 nós, não 7.472,95**. O speedup de 51,98× divide o Manhattan de
uma população pelo memória de outra.

Recalculado sobre as mesmas instâncias, pareado por par origem-destino, com média
geométrica e peso igual por mapa (IC 95% BCa sobre os 17 mapas):

| configuração | razão reportada | razão corrigida | IC 95% |
|---|---|---|---|
| Fórmula | 3,10× | **2,80×** | [2,32; 3,30] |
| Memória-10 | 17,25× | **4,70×** | [3,30; 5,43] |
| Memória-20 | 30,78× | **5,94×** | [3,94; 6,95] |
| Memória-50 | 33,50× | **7,32×** | [4,64; 8,69] |
| Memória-100 | 51,98× | **7,87×** | [4,92; 9,39] |

**Efeito colateral:** a hierarquia passa a ser monotônica no número de pivôs
(4,70 < 5,94 < 7,32 < 7,87). **O "comportamento não monotônico" de `main.tex:619` some** —
era artefato da mistura de populações e das células degeneradas (C5). O parágrafo inteiro
que explica a não monotonia deve sair.

---

## C5 — §5.1 e nota da Tabela 4: o desvio de 138,44 tem causa geométrica identificada
**Onde:** `main.tex:615` (nota) e `main.tex:619`.
**Hoje:** exclui-se apenas `(brc000d, 50 pivôs)`; o texto atribui o desvio a "instabilidade
do sorteio [...] **e não necessariamente um efeito geométrico sistemático**".

**É exatamente um efeito geométrico sistemático, e previsível.** `generatePivots`
(`heuristics.cpp`) sorteia o **primeiro** pivô uniformemente entre as células transitáveis.
Se ele cai num bolsão desconexo, `bfsPivo` devolve −1 fora do bolsão, o argmax de
`minDists` fica preso lá, todos os pivôs ficam no bolsão e, para quase toda consulta,
`dS == dG == -1` → **h ≡ 0 → o A\* degenera em Dijkstra**.

Verificação (`medicoes/pivos_precomp.csv`): **7 colapsos observados, 7 previstos, as mesmas
7 células.** Em todas, o primeiro pivô caiu fora da maior componente e h ≡ 0 em 99,3% a
100% das consultas. Nenhum colapso em mapa 100% conexo.

| mapa | componentes | fora da maior | colapsos observados | esperado |
|---|---|---|---|---|
| brc201d | 167 | 17,9% | 5 de 20 | 3,6 |
| brc000d | 2 | 5,4% | 2 de 20 | 1,1 |
| outros 15 | 1 | 0% | 0 | 0 |

**A nota da Tabela 4 está incompleta:** além de `(brc000d, 50)`, colapsaram
`(brc201d, 10)` nas sementes 123 e 456 e `(brc201d, 50)` nas sementes 42, 456 e 789 — todas
mantidas na agregação. São elas que produzem o desvio de 138,44.

**Recomendação de código (trabalho futuro):** sortear o primeiro pivô na maior componente
conexa, ou reiniciar o sorteio se `max(minDists) == 0`. Correção de uma linha.

---

## C6 — §3.4: a regularização não faz o que o texto afirma
**Onde:** `main.tex:412` e `main.tex:429`.
**Hoje:** "o fator 0,0005 aplica uma penalidade de regularização que **favorece fórmulas
mais compactas**, prevenindo *overfitting*".

**O comentário do próprio código diz o contrário** (`GeneticAlgorithm.h:71`):
`lambda = 0.0005; // Penalidade por tamanho baixíssima para permitir fórmulas complexas`.

**Quantificação:** λ·‖T‖ vale no máximo **1,56%** do fitness (mediana 0,52%). Para chegar a
10% do fitness, λ teria de ser **19× maior**. As ASTs campeãs têm mediana de **39 nós** e
máximo de **78** (brc203d), com profundidade até 26. E
**Spearman(tamanho, fitness) = +0,487 (p = 0,047)**: fórmulas maiores têm fitness *maior* —
a seleção premia tamanho, não o contrário.

**Redação sugerida:** "O termo 0,0005·‖T‖ é uma penalidade de regularização deliberadamente
branda. Na prática ela representa no máximo 1,6% do valor de aptidão (mediana 0,5%) e não
restringe o crescimento das expressões: as fórmulas campeãs têm mediana de 39 nós e chegam
a 78, e o tamanho correlaciona-se **positivamente** com a aptidão (ρ = +0,49; p = 0,047).
A contenção do *overfitting*, portanto, não é obtida por regularização neste experimento."

---

## C7 — §5.2 e §6: custo de preparação — agora medido, e a comparação aponta para o outro lado

> **Este é o único item que corrige uma _conclusão_, não um número ou uma descrição.** Ele
> muda a recomendação prática para desenvolvedores, que é a entrega de um trabalho de
> natureza aplicada — e é o que um parecerista da área de jogos verifica primeiro.
**Onde:** `main.tex:656` ("este experimento [...] não instrumentou o tempo de pré-computação
dos pivôs, de modo que essa comparação permanece qualitativa") e `main.tex:703`
("o custo de memória [...] não medido empiricamente neste experimento").

Ambos os buracos foram fechados (`medicoes/pivos_precomp.csv`, `tabelas/a7_*.csv`):

- **Pré-computação dos pivôs:** 12,0 ms (10 pivôs) a **103,4 ms** (100 pivôs), média entre
  mapas e sementes; máximo 207,7 ms.
- **Síntese evolutiva:** 4 s a 2.025 s. **A síntese custa de 777× a 12.197× a
  pré-computação de 100 pivôs.**
- **Memória:** o texto caracteriza O(|P|·|S|), mas `bfsPivo` aloca
  `vector<vector<int>> dists(height, vector<int>(width, -1))` — a **grade inteira**, não só
  as células transitáveis. Real = |P|·altura·largura·4 B: **4,1× o teórico** (mediana; até
  8,2× em mapas esparsos), chegando a **109 MB num único mapa** (den602d, 100 pivôs) e
  835 MB para os 17 mapas contra 171 MB teóricos.

**A frase de `main.tex:656` precisa inverter.** O texto conclui que o custo dos pivôs, pago
a cada mapa carregado, "torna a heurística de memória mais custosa em cenários com [...]
geração procedural de mapas". A estrutura do argumento está certa, mas a magnitude o
derruba: carregar um mapa novo custa ~100 ms de BFS, enquanto sintetizar uma fórmula para
um mapa novo custa até 34 minutos. **Em geração procedural, a fórmula é a estratégia
inviável, não a memória** — o que a memória paga é armazenamento, não tempo.

---

## C8 — §5.3: a média de 12,19% precisa da distribuição ao lado
**Onde:** `main.tex:667`.
**Veredito: CONFIRMA os números, mas eles escondem o resultado.**
Reproduzido: ρ médio agrupado = 1,1226 (12,26%; o 12,19% do texto vem de incluir a duplicata
de `arena`, cujos 650 pares têm ρ = 1). Por mapa: 11,18% [IC 95% BCa 8,49%–13,33%].
Máximo ρ = 4,1928 em `den012d` — **confirma** o 4,19.

O que falta e é mais acionável para um desenvolvedor:

| | fração das instâncias |
|---|---|
| caminho ótimo (ρ = 1) | **18,48%** |
| ρ > 1,05 | 62,97% |
| ρ > 1,10 | **44,94%** |
| ρ > 1,50 | 1,58% |

**Medianas por categoria:** o texto diz 1,05 / 1,06 / 1,09 / 1,11 (arenas / áreas abertas /
natureza / dungeons). Recalculado sem a duplicata: **1,078 / 1,062 / 1,088 / 1,112**. Só o
valor das arenas muda de forma perceptível (1,05 → 1,08).

**A hipótese do texto sobre contorno CONFIRMA-SE:** a fração de caminhos ótimos cai de
97,2% (caminhos de 1–25 células) para 1,1% (acima de 400), com
Spearman(comprimento, ρ) = **+0,494** (p < 10⁻³⁰⁰, n = 116.005).

---

## C9 — Falta declarar os descartes (E7)
**Onde:** `main.tex:534` e §5.4 inteira. Hoje o texto não menciona que pares foram
descartados.

`main.cpp:217-224` seleciona os pares pela conectividade **no estado de 30%** e usa esse
conjunto nos três níveis. Sobre 116.050 pares:

| padrão | sobreviventes | taxa | caminho ótimo mediano | Manhattan (expansões médias) |
|---|---|---|---|---|
| Linear | 869 | **0,75%** | 5 | 10 |
| Sparse | 4.996 | 4,31% | 44 | 396 |
| Organic | 5.444 | 4,69% | 37 | 310 |
| Radial | 11.086 | 9,55% | 70 | 1.877 |
| Stochastic | 12.448 | 10,73% | 111 | 2.825 |
| *(todos os pares)* | *116.050* | *100%* | *328* | *7.515* |

A interseção dos cinco padrões tem **71 instâncias**. Os conjuntos não são aninhados.

**Isto precisa entrar no texto como limitação declarada**, com a ressalva de que a
comparação *entre estratégias* permanece válida (é pareada dentro da mesma instância) e
que a comparação *entre padrões* é a que fica comprometida.

---

## C10 — §7: uma pergunta de trabalho futuro já está respondida
**Onde:** `main.tex:709` — "investigar a correlação entre a complexidade da árvore sintática
das fórmulas e a subotimalidade dos caminhos em *dungeons*".

**Resposta: não há correlação.** Spearman(tamanho da AST, subotimalidade média por mapa)
= **−0,014** sobre os 17 mapas. O tamanho da AST correlaciona-se com o *speedup*
(ρ = +0,53) e com a aptidão (ρ = +0,49), mas não com a qualidade do caminho. Remover o item
da lista de trabalhos futuros e reportar o resultado.

---

## C11 — §5.3: a explicação dada para o `arena` é factualmente falsa
**Onde:** `main.tex:667`.
**Hoje:** "a fórmula sintetizada converge para $(\Delta x)^2 + (\Delta y)^2$ [...] que nesse
ambiente **sem obstáculos internos nunca chega a superestimar o custo real**."

**Ela superestima quase sempre.** Medindo h(s,g) contra a distância ótima d\*(s,g) do Dijkstra
em todos os pares do cenário: no `arena` a fórmula viola admissibilidade em **99,2%** dos
pares, com fator de superestimação **mediano de 19×**. É aritmética elementar — num grid
4-conectado sem obstáculos d\* = Δx + Δy, e Δx² + Δy² excede esse valor para qualquer
distância acima de 2 (para Δx=3, Δy=4: h = 25 contra d\* = 7).

E não é só o `arena`: **os 17 mapas violam admissibilidade em mais de 99% dos pares**, com
superestimação mediana de 270× e máximo de 6.711×. O controle confirma o método — Manhattan
viola em 0,0000% dos pares, como manda a construção.

**O que explica de fato o ρ = 1,0 do `arena`** é outra coisa, e é mais interessante: a
correlação entre violar admissibilidade e produzir caminho subótimo é **nula**
(ρ de Spearman = −0,003; p = 0,99 sobre os 17 mapas). Uma heurística inflada mas monótona na
distância faz o A\* se comportar como busca gulosa; num mapa sem obstáculos internos, o
caminho guloso *é* o ótimo. A violação é condição necessária para a subotimalidade, não
suficiente — o que a determina é a geometria, não a magnitude do erro da estimativa.

**Redação sugerida:** "No `arena`, a fórmula converge para $(\Delta x)^2 + (\Delta y)^2$, que
superestima o custo real em 99,2% dos pares (fator mediano de 19×) e ainda assim devolve o
caminho ótimo em todas as instâncias: num ambiente sem obstáculos internos, a ordem de
expansão induzida por uma estimativa inflada mas monótona na distância coincide com a do
caminho ótimo. Medida sobre os 17 mapas, a violação de admissibilidade é praticamente
universal (acima de 99% dos pares em todos eles, com superestimação mediana de 270×), mas
não se correlaciona com a subotimalidade observada ($\rho = -0{,}003$); o que a determina é
a geometria do mapa, não a magnitude do erro da heurística."

**Isto liga a Seção 3 aos dados**, que era o pedido de fortalecer o lado teórico: a
caracterização formal diz que as fórmulas "não garantem admissibilidade"; a medição mostra
que elas a violam essencialmente sempre, e que a consequência prática é desacoplada da
violação.
