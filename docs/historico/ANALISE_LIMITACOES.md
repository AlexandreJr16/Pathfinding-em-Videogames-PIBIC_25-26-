# Limitações — o que não deu para computar, e por quê

Seguindo a regra 5 do briefing: onde algo não é computável com os dados disponíveis, isto
está registrado como tal, com o que faltaria para computá-lo.

---

## L1 — O descarte de pares não é separável por nível de bloqueio
`main.cpp:217-224` seleciona os pares válidos **uma vez**, no estado de 30% de bloqueio, e
usa esse mesmo conjunto nos níveis de 10%, 20% e 30%. Não há como recuperar, dos CSVs,
quantos pares teriam sobrevivido a 10% ou a 20% — essa informação nunca foi gravada.

O que se pode dizer é a taxa por padrão no estado de 30% (A10). Para separar por nível
seria preciso reinstrumentar o laço de seleção e re-executar a robustez inteira.

## L2 — A comparação **entre padrões de degradação** está confundida e não tem conserto pleno
Consequência de L1. Cada padrão sobrevive com uma população de pares diferente e não
aninhada: 0,75% (linear) a 10,73% (estocástico), com caminho ótimo mediano de 5 a 111
células e expansões médias de Manhattan de 10 a 2.825. A interseção dos cinco padrões tem
**71 instâncias** — pouco para sustentar uma comparação pareada.

Mitigação aplicada (A1): reajuste do modelo dentro da faixa de comprimento de caminho comum
aos cinco padrões ([15, 19] células), onde a interação estratégia × padrão **sobrevive**
(η²ₚ = 0,123 contra 0,241 no modelo completo). Isso sustenta que a interação não é puro
artefato de seleção, mas **não** recupera a comparabilidade das magnitudes de δ entre
padrões. Qualquer afirmação do tipo "o padrão X é mais hostil que o padrão Y" deve vir com
essa ressalva.

A comparação **entre estratégias**, essa sim, é limpa: as 6 configurações rodam sobre
exatamente o mesmo par origem-destino, dentro da mesma linha do CSV.

## L3 — `tempo_ms` não é uma medição confiável de desempenho
Medição única por instância, sem aquecimento, sem repetições, sem isolamento de CPU nem
controle de frequência, com o binário compilado em `-O3 -march=native -ffast-math` numa
máquina compartilhada com o resto do experimento. A própria duplicata de `arena` mostra o
problema: as duas execuções dão **expansões idênticas** (o A\* é determinístico) e **tempos
diferentes**.

Re-executar não conserta: sem um protocolo de *benchmark* (n repetições, pinagem de núcleo,
descarte de outliers, governador de frequência fixo) o número continuaria sem sentido. Por
isso toda a análise lidera com **expansões de nós**, que são determinísticas e comparáveis,
e trata tempo como indicativo. Recomendação para o texto: manter a coluna de tempo na
Tabela 4, mas não sustentar nenhuma conclusão nela.

## L4 — As fórmulas reportadas continuam sendo amostras de tamanho 1
`GeneticAlgorithm.cpp:19,68` (versão original) semeia `initPopulation` e `reproduction` a
partir de `std::random_device`. As fórmulas de `resultados_sintese.csv` vieram de uma
execução não reprodutível cada.

O que **foi** feito (A9): re-síntese semeada numa cópia do código em que essa entropia
virou parâmetro explícito, com `grammar(42)`, `operators(42)` e o conjunto de treino mantidos
fixos — isolando exatamente a variabilidade que afetou os resultados reportados. O plano era
5 sementes x 17 mapas = 85 sínteses (~17 h); **executaram-se 14 sínteses, cobrindo 13 dos 17
mapas com a semente 1, mais uma segunda semente em `arena`.** Os 4 mapas sem cobertura são
`den500d`, `den501d`, `den602d` e `hrt201n`. A execução foi encerrada por prazo, não por
falha.

O resultado é categórico mesmo assim — 12 dos 13 mapas dão fórmula diferente — porque a
pergunta é qualitativa ("a síntese reencontra a mesma fórmula?") e a resposta é negativa em
quase toda a amostra. O que **não** se pode afirmar com n=1 semente por mapa é a *distribuição*
das campeãs: quantas famílias distintas existem, ou qual a variância da aptidão entre
sementes. Só `arena` tem n=2 (CV da aptidão = 0,001). Reportar como "12 de 13 mapas testados",
nunca como "todos os mapas".

Isso também **não** torna reprodutíveis os números já publicados: para isso as fórmulas
teriam de ser resintetizadas de forma semeada e todo o experimento a jusante (base, ratio,
robustez) refeito, o que não cabe no prazo.

Recomendação: declarar no texto que a síntese, como executada, não é reprodutível, e que a
correção (semear os dois geradores) é de duas linhas.

## L5 — Só uma semente de degradação por padrão foi verificada no teste de reprocessamento
O experimento de A0 (`medicoes/reprocessamento*.csv`) roda os 17 mapas com a semente 42.
A conclusão sobre *se* há reprocessamento é estrutural (vem do código) e não depende de
semente. Já a quantificação de *quanto* o reprocessamento vale — a comparação entre δ com
distâncias frescas e congeladas — é de uma semente só, e a direção do efeito varia por
padrão. Tratar essas magnitudes como ilustrativas, não como estimativas.

Uma segunda semente (123) chegou a ser iniciada e foi abandonada por prazo em 4 dos 17 mapas;
esses dados parciais **não** entram em nenhuma tabela — o A0 filtra sementes incompletas
automaticamente (`a0_reprocessamento.py`, checagem de 60 linhas por célula).

## L6 — `caminho_otimo < 1` em 45 pares, com `ratio` forçado a 1,0
`main.cpp:175` define `ratio = (resD.path.size() <= 1) ? 1.0 : ...`, de modo que pares sem
caminho recebem ρ = 1,0 (aparentemente ótimos). São 45 linhas em 116.050, concentradas em 6
mapas. Foram excluídas do A6. O efeito no ρ médio é da ordem de 10⁻⁴ — irrelevante no
número, mas é um defeito de instrumentação que vale corrigir no código.

## L7 — A duplicata de `arena` estava sendo contada duas vezes
`main.cpp:73-86` abre os quatro CSVs em modo `ios::app`, e `arena` foi processado duas
vezes. Todos os números do relatório incluem esses 650 pares em dobro (3.900 linhas em
`resultados_base.csv`, 12.900 em `resultados_robustez.csv`). Como `arena` é o menor e mais
fácil mapa, o efeito é puxar médias agrupadas para baixo — é a origem da diferença entre o
7.472,95 do relatório e o 7.514,59 deduplicado. Todas as análises aqui deduplicam.

## L8 — O baseline de Dijkstra foi medido agora, mas fora da execução original
`medicoes/dijkstra.csv` traz as expansões do A\* com h = 0 para as 23.210 instâncias
(o valor não depende de semente). Ele é usado para normalizar expansões entre mapas de
escalas diferentes. Ressalva: foi produzido por um programa auxiliar compilado com `-O2`
(e não `-O3 -march=native`), no mesmo código-fonte de `astar.cpp`. Como a métrica é
contagem de nós expandidos, e não tempo, isso não afeta o resultado.

## L9 — O tamanho de efeito no nível da instância não deve ser lido como poder estatístico
Com n = 116.050 pares pareados, todo teste de Wilcoxon devolve p abaixo do menor float
representável. Esses p-valores estão reportados por completude, mas o número que sustenta
afirmação é o δ de Cliff e, sobretudo, o intervalo de confiança sobre os **17 mapas** — a
unidade em que faz sentido generalizar, já que instâncias do mesmo mapa não são
independentes. Onde os dois níveis discordarem, vale o de mapa.

## L10 — Fora de escopo por decisão explícita
- **Variante "congelada" da robustez** (distâncias do mapa original, como o texto afirma):
  medida apenas de forma ilustrativa em A0. O experimento completo não foi refeito.
- **Re-sorteio dos pivôs degenerados**: mantidos de propósito. Removê-los seria escolher a
  amostra pelo resultado; o colapso é uma propriedade real do algoritmo como implementado.
  As tabelas reportam com e sem.
- **Mais de 100 pivôs**, **mapas fora do conjunto DAO**, **atualização incremental das
  distâncias**: continuam como trabalho futuro, sem dados.
