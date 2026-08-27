# Achados da reanálise estatística (agosto/2026)

Resumo executivo de `analise/estatistica-2026-08/`. O detalhamento completo, com a frase pronta
em português para cada achado, está em:

- `docs/historico/ANALISE_RESUMO.md` — os achados e o que cada um autoriza a afirmar
- `docs/historico/ANALISE_DADOS.md` — o que há em cada uma das 34 tabelas
- `docs/historico/ANALISE_LIMITACOES.md` — o que **não** se pode afirmar (L1–L10)
- `docs/historico/ANALISE_CORRECOES_TEXTO.md` — os trechos do relatório a corrigir (C1–C11)
- `docs/historico/BRIEFING_ANALISE_ESTATISTICA.md` — o diagnóstico que motivou a reanálise (E1–E10)

---

## Por que a reanálise existiu

A primeira versão do relatório reportava **apenas média ± desvio-padrão sobre 5 sementes**.
Em revisão, a orientadora pediu explicitamente um "viés estatístico completo". O diagnóstico
listou dez problemas (E1–E10), dos quais os estruturais eram:

- **médias aritméticas de razões** de *speedup* (viés conhecido desde Fleming & Wallace, 1986);
- agregação de expansões através de **17 mapas de escalas muito diferentes**, dominada pelos
  mapas grandes;
- o `±` medindo variabilidade **entre 5 sementes**, não incerteza da estimativa;
- **nenhum teste de hipótese e nenhum tamanho de efeito** em todo o trabalho;
- pares descartados pelo filtro de conectividade **sem contabilização**.

## A correção metodológica central

Três regras, aplicadas uniformemente em todas as 34 tabelas:

1. razões agregam por **média geométrica**, nunca aritmética;
2. expansões são **normalizadas por mapa** antes de agrupar entre mapas;
3. a unidade de replicação para generalizar é o **mapa (n = 17)**, não a instância (n = 116.050) —
   instâncias do mesmo mapa não são independentes.

Uma verificação que só a média geométrica passa, e que serve de defesa em arguição:
`2,799 (Manhattan÷Fórmula) × 2,811 (Fórmula÷Memória-100) = 7,866`, exatamente a razão
Manhattan÷Memória-100 medida em separado. Médias aritméticas de razões não fecham assim.

---

## O placar

| | Achado em uma linha | Veredito sobre o relatório |
|---|---|---|
| **A0** | A memória **é** reprocessada sob degradação; 93,4% das distâncias mudam | **contradiz** §4.3 e §5.4 |
| **A3** | O *speedup* de 51,98× compara memória de uma população com Manhattan de outra → **7,87×** | **corrige** a Tabela 4 |
| **A11** | O desvio de 138,44 é colapso de pivô em bolsão desconexo: 7 previstos, 7 observados | **contradiz** §5.1 |
| **A1** | Interação estratégia × padrão: η²ₚ = 0,241; p ≤ 0,005 por permutação | confirma a tese |
| **A2** | Inversão de hierarquia: Memória-100 vai de posto 1,06 → 2,82; Fórmula de 4,47 → **1,35** | confirma, agora com prova (**Figura 1**) |
| **A4** | Memória-50 tem a 2ª melhor mediana, mas p99 no teto do Dijkstra (39× a mediana) | revela (**Figura 2**) |
| **A5** | 4 comparações pareadas, correção de Holm, δ de Cliff de 0,33 a 0,87 | resolve E3–E5 |
| **A6** | Só **18,48%** dos caminhos da fórmula são ótimos; **44,94%** excedem 1,10 | confirma e acrescenta |
| **A7** | 109 MB de pivôs num só mapa; a síntese custa 777×–12.197× a pré-computação | resolve E8 e E9 |
| **A8** | A regularização por tamanho é inerte: λ‖T‖ ≤ 1,6% da aptidão | **contradiz** §3.4 |
| **A9** | Re-sintetizando com semente fixa, **12 de 13** mapas dão fórmula diferente | **corrige** o estatuto da Tabela 3 |
| **A10** | 89%–99% dos pares são descartados pelo filtro, sem contabilização | resolve E7 |
| **A12** | A fórmula viola admissibilidade em **99,9%** dos pares — e isso **não** prevê subotimalidade | **contradiz** §5.3 |

---

## Os três que mudam o que o texto pode afirmar

### A0 — O relatório diz que a memória não é reprocessada; o código a reprocessa

`main.cpp:227` troca a grade pela degradada e `main.cpp:244` chama `computarDistPivosFixos`,
que roda `bfsPivo` **sobre a grade já degradada**. Medido nos 17 mapas: **93,4% das distâncias
pré-computadas mudam** (mediana; IQR 81,9%–98,0%) e **87,5% das células ficam inalcançáveis**
a partir do pivô. Só as *posições* dos pivôs ficam congeladas.

**Não destrói a tese — reforça.** A fórmula é a menos degradada em **5 dos 5 padrões**, sendo
a única que não recebe nenhuma atualização. Mas a narrativa de mecanismo do §5.4 ("distâncias
que descrevem um mapa que já não existe") está errada: a causa real é que pivôs inalcançáveis
são pulados e a estimativa colapsa para zero.

O efeito do reprocessamento **troca de sinal por padrão**: sob **linear**, recalcular a BFS
*piora* δ em 2,3–2,8× (os pivôs ficam do lado errado da barreira); sob **estocástico**, ajuda
em 2,3–2,7×.

### A3 — O *speedup* de 51,98× compara duas populações de instâncias diferentes

As linhas de memória da Tabela 4 vinham de `resultados_robustez.csv`, que contém só as **23.906
instâncias (20,5%)** que sobreviveram ao filtro de conectividade — os pares mais curtos.
Manhattan e Fórmula vinham de `resultados_base.csv`, com as **116.700**. Sobre os mesmos pares
curtos, **a própria Manhattan expande 2.169,46 nós, não 7.472,95** — um fator de 3,4× que
inflava todos os *speedups* de memória.

| | Fórmula | Mem-10 | Mem-20 | Mem-50 | Mem-100 |
|---|---|---|---|---|---|
| relatório | 3,10× | 17,25× | 30,78× | 33,50× | 51,98× |
| **corrigido** | **2,80×** | **4,70×** | **5,94×** | **7,32×** | **7,87×** |
| IC 95% (17 mapas, BCa) | [2,32; 3,30] | [3,30; 5,43] | [3,94; 6,95] | [4,64; 8,69] | [4,92; 9,39] |

As 12 células da tabela antiga **reproduzem exatamente** sob a regra antiga, o que fecha o
diagnóstico. E a correção elimina uma anomalia: a hierarquia vira **monotônica** em número de
pivôs, então o parágrafo sobre "comportamento não monotônico em 50 pivôs" sai inteiro — era
artefato, não fenômeno.

### A11 — O desvio de 138,44 tem causa geométrica exata

`generatePivots` sorteia o **primeiro** pivô uniformemente entre as células transitáveis. Se ele
cai num bolsão desconexo, **todos** os pivôs ficam presos lá, `dS == dG == -1` em quase toda
consulta, `h ≡ 0`, e o A\* degenera em Dijkstra.

Previsto a partir das componentes conexas: **7 colapsos esperados, 7 observados, as mesmas 7
células** — todas com o primeiro pivô fora da maior componente e `h ≡ 0` em 99,3%–100% das
consultas. Nenhum colapso nos 15 mapas totalmente conexos. Correção de código: sortear o
primeiro pivô dentro da maior componente conexa (uma linha).

---

## O que a reanálise deliberadamente **não** fez

- **Não re-executou o experimento principal.** Os números corrigidos vêm dos mesmos dados
  brutos de março, tratados com estatística correta.
- **Não re-sorteou os pivôs degenerados.** Removê-los seria escolher a amostra pelo resultado;
  o colapso é uma propriedade real do algoritmo como implementado. As tabelas reportam com e sem.
- **Não completou as 85 re-sínteses do A9** — parou em 14, cobrindo 13 dos 17 mapas, por prazo.
  O resultado já é categórico (12 de 13 mapas dão fórmula diferente), mas deve ser reportado
  como "12 de 13 mapas testados", nunca como "todos os mapas".

As dez limitações estão em `docs/historico/ANALISE_LIMITACOES.md`, e as mais consequentes
aparecem também em `docs/04-problemas-conhecidos.md`.
