# Briefing — Análise estatística do PIBIC (pathfinding com heurísticas sintetizadas)

> Documento de contexto para execução da análise no Claude Code, na máquina local.
> Escrito para não perder nada do que foi discutido com a orientadora.
> **Leia inteiro antes de rodar qualquer coisa.**

---

## 1. O trabalho

Relatório final PIBIC/PAIC 2025-2026, UFAM/IComp. Aluno Alexandre Pereira de Souza Junior,
orientadora Dra. Rosiane de Freitas Rodrigues. Projeto PIB-E/0151/2025, financiamento CNPq.

**Título:** Estratégias para síntese automática de heurísticas baseadas em fórmulas e em
memória na busca de caminhos em videogames.

**O que foi feito:** comparação experimental de três classes de heurística para o algoritmo A*
em 17 mapas do conjunto *Dragon Age Origins* (Moving AI Lab), grades 4-conectadas com custo
unitário:

1. **Manhattan** — `|Δx| + |Δy|`, admissível, sem pré-processamento, linha de base.
2. **Memória com pivôs** — distâncias exatas pré-computadas por BFS a partir de pivôs
   selecionados por *Farthest-First*; estimativa por desigualdade triangular,
   `h(s,g) = max_i |d(p_i,s) − d(p_i,g)|`. Admissível. Configurações com 10, 20, 50 e 100 pivôs.
3. **Fórmula sintetizada por algoritmo genético** — expressão simbólica sobre `deltaX`/`deltaY`,
   evoluída como AST (80 indivíduos, 100 gerações, elitismo 10%). **Não garante admissibilidade.**

Além do cenário estático, os mapas são submetidos a **cinco padrões de degradação estrutural**
(linear, orgânico, radial, esparso, estocástico) em **três níveis de bloqueio (10%, 20%, 30%)**,
**sem reprocessamento das heurísticas** — a ideia é medir robustez a mudanças do mapa.

**Prazo:** entrega até 30/08/2026. **Limite:** 20 páginas, 2 MB, PDF, ABNT.

---

## 2. O que a orientadora disse (isto é o que a análise precisa responder)

Em reunião de revisão, ela avaliou o relatório e, sobre a parte de dados, disse textualmente
(anotações do aluno):

- A seção deve se chamar **"Resultados e Discussão"**, não só "Resultados" —
  *"só resultados é um trabalho porco, deve ter discussão"*.
- Chamou a análise atual de **"uma análise ruim"** e pediu explicitamente para usar IA
  *"para ver o que falta de trabalho estatístico e de ciência de dados com base nos dados que eu tenho"*,
  com o objetivo de dar ao trabalho **"um viés estatístico completo"**.
- Sobre a natureza da pesquisa: *"seu trabalho é de natureza aplicada, quantitativa e descritiva,
  o que é um trabalho básico. Um bom trabalho deve ter suas tangentes qualitativas, que é mostrar
  uma razão"* — ou seja, **o quantitativo estabelece _quanto_; falta estabelecer _por quê_**.
- O lado teórico (um artigo submetido ao ETC, com caracterização formal de admissibilidade,
  consistência, complexidade e expressividade das três classes) **tem que entrar no relatório e
  ser tão forte quanto os dados**.

**Tradução para a análise:** não basta produzir mais números. Cada resultado estatístico precisa
sustentar uma afirmação que hoje está no texto sem prova, ou revelar algo que o texto ainda não diz.

---

## 3. O que está errado na análise atual (diagnóstico já feito)

O relatório hoje reporta **apenas média ± desvio-padrão sobre 5 sementes**. Problemas concretos:

| # | Problema | Onde aparece |
|---|---|---|
| **E1** | Média **aritmética** de razões de *speedup*. O próprio texto (Seção 5.5) registra que "as duas formas de cálculo podem divergir quando a variância é alta" e **não decide qual usar**. | Tabela 4 |
| **E2** | Agregação de expansões através de 17 mapas de escalas muito diferentes — dominada pelos mapas grandes. | Tabela 4 |
| **E3** | O `±` reportado mede variabilidade **entre sementes** (n=5), não incerteza da estimativa. Poder estatístico ~nulo. | todas as tabelas |
| **E4** | **Nenhum teste de hipótese** em todo o trabalho. | — |
| **E5** | **Nenhum tamanho de efeito.** | — |
| **E6** | Só médias; nenhuma distribuição, percentil ou cauda. | — |
| **E7** | Pares desconectados sob 30% de bloqueio são descartados **sem contabilização** — risco de viés de seleção, provavelmente desigual entre padrões. | Seção 5.5 |
| **E8** | Custo de memória dos pivôs **não medido**, apesar de "memória" ser um dos três eixos da conclusão. | Seções 6.2 e 7 |
| **E9** | Tempo de pré-computação dos pivôs **não instrumentado** — a comparação de custo de preparação só tem um lado medido (o da síntese). | Seção 6.2 |
| **E10** | Síntese do AG **não reprodutível** (inicialização usa entropia do sistema). Cada fórmula reportada é amostra de tamanho 1. | Seção 5.5 |

**Números que o relatório afirma hoje e que precisam ser reconferidos:**
speedup de até **51,98×** (memória 100 pivôs vs Manhattan); fórmula **3,10×** vs Manhattan;
subotimalidade média da fórmula **12,19%**; fator de degradação máximo — fórmula **2,54**,
memória 100 pivôs **3,26**, Manhattan **4,25**, memória 10 pivôs **6,33**;
desvio-padrão anômalo de **138,44** na configuração de 50 pivôs.

---

## 4. Os dados

Todos em CSV, na pasta do projeto.

### `resultados_base.csv` — 700.200 linhas, ~30 MB
```
mapa, semente, id_problema, heuristica, n_pivos, expansoes, tempo_ms, caminho_tamanho
```
- `heuristica` ∈ {`manhattan`, `formula`, `memory`}; `n_pivos` ∈ {0, 10, 20, 50, 100}
- 6 configurações × 116.700 instâncias = 700.200 linhas
- **Desenho pareado**: as 6 configurações rodam sobre exatamente os mesmos pares
  origem-destino. Isso não está sendo aproveitado hoje e é a maior oportunidade estatística.

### `resultados_ratio.csv` — 116.700 linhas, ~3,5 MB
```
mapa, semente, id_problema, caminho_otimo, caminho_formula, ratio
```
- `ratio = caminho_formula / caminho_otimo`. Só existe para a fórmula (as outras são admissíveis).

### `resultados_sintese.csv` — 18 linhas
```
mapa, populacao_inicial, n_geracoes, tempo_sintese_ms, formula_string, fitness_final
```
- 17 mapas únicos, **18 linhas** — `arena` aparece **duas vezes**, com tempos diferentes
  (4140,47 ms e 3938,43 ms) e **fórmula idêntica**. Verificar se são duas execuções independentes;
  se forem, é a única evidência de reprodutibilidade que existe. Ver análise **A9**.
- `formula_string` em notação prefixa: `(+ (sqr deltaY) (sqr deltaX))`.
  Operadores observados: `+ - * / max min sqr sqrt abs neg`.

### `resultados_robustez.csv` — ~51 MB, **schema desconhecido**
Não foi inspecionado ainda. **Primeira tarefa: imprimir cabeçalho, dtypes, número de linhas,
valores únicos de cada coluna categórica, e conferir se contém `padrao`, `nivel_bloqueio`,
`expansoes` e algum identificador de instância.** Reporte o schema real antes de prosseguir —
o resto do plano assume que ele existe e pode precisar de ajuste.

### O que **não** está nos CSVs e precisa vir de outro lugar
- **|S| (número de células transitáveis) por mapa** — calcular a partir dos arquivos `.map`
  do Moving AI que estão no repositório. Necessário para o custo de memória (**A7**).
- **Tempo de pré-computação dos pivôs** — não foi instrumentado (E9). Se for barato reinstrumentar
  (é uma BFS por pivô), vale rodar; se não, registrar como limitação.
- **Baseline h=0 (Dijkstra)** — não existe nos dados. Seria o teto de expansões e permitiria
  normalizar tudo num intervalo adimensional. Registrar como limitação ou gerar, se barato.

---

## 5. As análises, em ordem de prioridade

> **Restrição dura:** o relatório tem **20 páginas no total** e a estatística inferencial
> tem orçamento de **cerca de meia página + no máximo duas figuras**. O objetivo não é
> produzir o máximo de resultados — é produzir os **poucos que mudam o que o texto pode afirmar**.
> Análises que não caibam no relatório ainda são úteis (vão para o repositório), mas
> priorize nesta ordem.

### A1 — Teste da tese central ★ prioridade máxima
A afirmação central do trabalho é que **a hierarquia observada no cenário estático não se
preserva quando o mapa passa a mudar**. Hoje isso é afirmado por inspeção visual de gráfico.
Em linguagem estatística é uma **interação significativa entre estratégia e padrão de degradação**.

- Modelo: `métrica ~ estrategia * padrao * nivel + (1|mapa)`, onde `métrica` é o fator de
  degradação (ou expansões normalizadas). Efeito aleatório por mapa porque as observações
  são aninhadas.
- Se o modelo misto for pesado sobre 51 MB, **agregue primeiro** para células
  `mapa × semente × estrategia × padrao × nivel` e ajuste sobre as médias de célula.
- Reporte: significância da interação `estrategia × padrao`, e **quanto da variância cada fator
  explica** (η²ₚ ou equivalente). A frase-alvo do relatório é do tipo
  *"o padrão de degradação explica X% da variância; a interação com a estratégia é significativa
  (p = …, η²ₚ = …), confirmando que nenhuma estratégia domina em todos os regimes."*
- Verifique pressupostos; se violados, use alternativa robusta (ART ANOVA, permutação) e diga qual.

### A2 — Ranking honesto entre as 6 configurações
6 configurações × 17 mapas é exatamente o cenário de Demšar (2006).
- Teste de **Friedman** sobre os postos por mapa → pós-teste (**Nemenyi**, ou Wilcoxon com
  correção de **Holm**) → **diagrama de diferença crítica (CD)**.
- Fazer duas vezes: **cenário estático** e **sob degradação** (agregando padrões). O contraste
  entre os dois diagramas é, sozinho, a evidência visual da tese do A1.
- **Esta é a figura número 1 candidata para o relatório.**

### A3 — Corrigir os *speedups* (resolve E1 e E2)
- Por mapa: **média geométrica** de `expansoes_manhattan / expansoes_config` sobre as instâncias.
- Depois: média geométrica através dos 17 mapas.
- Justificativa a citar no texto: Fleming & Wallace (1986), *CACM* — média aritmética de razões
  é enviesada e não é invariante à escolha da linha de base.
- **Reporte explicitamente quanto os números mudam** em relação aos 51,98× e 3,10× do texto atual.
  Se mudarem, o texto do relatório precisa ser corrigido.

### A4 — Distribuições e cauda (resolve E6)
- Por configuração, normalizado por mapa: **mediana, IQR, p90, p95, p99** de expansões.
- Uma figura **ECDF** por estratégia.
- O argumento é específico do domínio e é forte: **em jogo, o que estoura o orçamento de quadro
  não é a busca média, é a pior busca do segundo.** Uma heurística com média boa e p99 ruim
  causa engasgo visível. Nenhuma média da tabela atual captura isso.
- **Figura número 2 candidata.**

### A5 — Testes pareados e tamanho de efeito (resolve E3, E4, E5)
- **Wilcoxon signed-rank** sobre diferenças por instância (dados de expansão são fortemente
  assimétricos — não use teste t sem checar).
- Não teste os 15 pares. Teste **quatro**: manhattan×formula, manhattan×memory100,
  formula×memory10, formula×memory100. Correção de **Holm**.
- **Sempre com Cliff's δ ao lado do p-valor.** Com n=116.700 tudo dá p<0,001; o que importa
  é a magnitude. **Nunca reporte p-valor sozinho.**
- Intervalos de confiança por **bootstrap BCa** para as razões e para o fator de degradação.

### A6 — Subotimalidade fina (a partir de `resultados_ratio.csv`)
- Distribuição de `ratio`, não só a média de 12,19%: **fração de instâncias com ratio = 1
  (ótimo), > 1,05, > 1,1, > 1,5**. Isso é uma "taxa de desvio perceptível" e é muito mais
  acionável para um desenvolvedor que a média.
- `ratio` versus `caminho_otimo` (binned): a hipótese do relatório é que o desvio cresce em
  caminhos que exigem contorno. Teste isso.
- Por mapa e por categoria de mapa. O texto atual afirma um pico de 4,19 em `den012d` — confira.

### A7 — Custo de memória e fronteira de Pareto (resolve E8)
- Memória dos pivôs = `|P| × |S| × bytes_por_distancia`. Calcule `|S|` a partir dos `.map`.
  Tabela de 17 linhas × 4 configurações, em MB. **É aritmética, não experimento**, e sustenta
  um terço da conclusão do relatório que hoje está sem número.
- Depois: **fronteira de Pareto** sobre expansões × memória × subotimalidade × robustez.
  Quais das 6 configurações são não-dominadas? A conclusão do relatório afirma que
  "não há estratégia universalmente superior" — a análise de dominância **prova** isso.
  Se alguma configuração for dominada (a de 50 pivôs é candidata), isso também é resultado.

### A8 — Análise das fórmulas sintetizadas (a tangente qualitativa)
O relatório mostra **uma** das 17 fórmulas. As outras dezesseis estão inexploradas.
- Faça o *parse* de `formula_string` (notação prefixa) e extraia: **tamanho da AST** (nº de nós),
  profundidade, frequência de cada operador, se `deltaX` e `deltaY` aparecem ambos,
  se a expressão é simétrica em Δx/Δy, constantes usadas.
- Classifique as 17 em famílias (quadrática pura, linear ponderada, com `max`/`min`, com constantes).
- Correlacione tamanho da AST e família com: `fitness_final`, `tempo_sintese_ms`, categoria do mapa,
  e o *speedup* e a subotimalidade medidos.
- **Achado provável, já visível a olho nu:** as fórmulas são **enormes** (a de `brc203d` e a de
  `brc202d` têm dezenas de nós), apesar de o termo de regularização `0,0005 × ||T||` ter sido
  descrito no relatório como algo que "favorece fórmulas mais compactas, prevenindo *overfitting*".
  **Quantifique isso.** Se a regularização não está funcionando, é um resultado honesto e
  interessante — e conecta com a subotimalidade medida.

### A9 — Reprodutibilidade da síntese (resolve E10, parcialmente)
- `arena` aparece duas vezes com fórmula idêntica e tempos diferentes. Confirme se há outros
  mapas duplicados. Se `arena` for de fato duas execuções independentes que convergiram para a
  mesma expressão, é evidência (fraca, n=1 mapa) de estabilidade do AG — vale reportar como tal,
  com a ressalva do tamanho de amostra.
- **Recomendação separada:** semear deterministicamente todos os RNGs e rodar ~5 sínteses
  independentes por mapa daria a distribuição das fórmulas campeãs. Custo estimado: a soma dos
  tempos de síntese é ~2,5 h por rodada completa, então 5 rodadas ≈ 13 h de máquina.
  **Se der tempo antes de 30/08, rode em segundo plano** — é o ponto mais frágil do trabalho
  perante um parecerista.

### A10 — Contabilizar descartes (resolve E7)
- Quantos pares foram descartados por perda de conectividade, **por padrão e por nível**?
  É resultado em si — provavelmente mostra que o padrão linear fragmenta o mapa muito antes
  dos outros — e mitiga o viés de seleção.

---

## 6. Regras de execução (não negociáveis)

1. **Média geométrica para razões.** Sempre. Aritmética só para grandezas absolutas.
2. **Normalize por mapa antes de agrupar** entre mapas.
3. **Nunca reporte p-valor sem tamanho de efeito.** Com n=116.700, significância é barata.
4. **Não faça *p-hacking*.** Os testes estão listados acima; se você rodar outros por exploração,
   marque-os como exploratórios e aplique correção.
5. **Não invente.** Se algo não pode ser computado a partir dos dados disponíveis, escreva
   "não computável com os dados atuais" e explique o que faltaria.
6. **Seeds fixas** em tudo que for estocástico (bootstrap inclusive). Registre os valores.
7. **Confira contra o texto atual.** Para cada número que o relatório já afirma
   (Seção 3 acima), diga se a sua análise **confirma, corrige ou contradiz**. Isso é a parte
   mais importante do retorno.
8. **Figuras em vetor** (PDF ou SVG) para o relatório, tamanho compatível com meia coluna de
   página A4 em ABNT, legíveis em preto e branco.

---

## 7. O que produzir (contrato de saída)

```
analise/
  RESUMO.md              <- o principal; ver abaixo
  tabelas/*.csv          <- uma tabela agregada por análise, pequenas
  figuras/*.pdf + *.png  <- CD diagram, ECDF, Pareto, e o que mais for pro relatório
  scripts/*.py           <- reproduzíveis, com seeds, rodando do zero
  LIMITACOES.md          <- o que não deu para computar e por quê
```

**`RESUMO.md` é o entregável central.** Máximo 2 páginas. Para cada análise A1–A10:

- **O número.** O resultado, com intervalo de confiança e tamanho de efeito.
- **A frase.** Uma sentença, em português, pronta para entrar no relatório.
- **O veredito.** Confirma / corrige / contradiz o que o texto atual afirma.
- **Cabe no relatório?** Sim (e em qual das 2 figuras) ou não (vai para o repositório).

Não cole tabelas gigantes no `RESUMO.md`. Ele precisa ser lido de uma vez.

---

## 8. Depois

Devolver para a conversa do Cowork: **`RESUMO.md`, `LIMITACOES.md`, os CSVs de `tabelas/`
(são pequenos) e as figuras.** Não precisa mandar os dados brutos nem os scripts —
esses ficam no repositório, que é, ele próprio, produção científica declarada no relatório.

Uma última coisa, e vale para tudo: **o aluno precisa conseguir defender cada número numa
arguição.** Se uma análise produzir um resultado que ele não sabe explicar, ela não deve
entrar no relatório — por mais bonita que seja.
