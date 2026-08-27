> **Situação em 22/08/2026 — este documento é opcional.**
> As sínteses do A9 foram **encerradas por prazo** com 14 de 85 concluídas (13 dos 17 mapas),
> e o resultado já é conclusivo com esse n — ver A9 em `DADOS.md` e L4 em `LIMITACOES.md`.
> **Nada abaixo precisa ser executado para a entrega.** Os checkpoints interrompidos estão
> preservados em `medicoes/sintese/_incompletos_backup/`; este manual descreve como retomá-los
> caso um dia se queira completar as 85.

---

# Como parar e retomar a síntese

O experimento A9 (85 sínteses semeadas) é o único trabalho longo do pacote: ~12 h em 6
núcleos. Ele foi montado para que **nenhuma parada custe retrabalho relevante** — desligar
a máquina no meio, matar o processo ou dar Ctrl-C são todos seguros.

## Comandos

```bash
cd ~/Downloads/analise\ esta/analise

.venv/bin/python scripts/sintese_pool.py --status   # onde está
.venv/bin/python scripts/sintese_pool.py            # roda / continua de onde parou
.venv/bin/python scripts/sintese_pool.py --merge    # consolida o CSV final
```

Para **parar**: `Ctrl-C` no terminal do pool, ou `pkill -f sintese_pool`. Os workers
recebem SIGTERM, terminam a geração em curso, gravam checkpoint e saem. Para **continuar**:
rode o mesmo comando de novo. Não há estado escondido — o que está no disco é a verdade.

Opções: `--workers N` (padrão 6), `--cores 0-5` (quais núcleos usar), `--ckpt N` (gerações
entre checkpoints, padrão 5), `--nice N` (padrão 19, prioridade mínima).

## As três camadas de proteção

| camada | granularidade | pior perda |
|---|---|---|
| resultado por tarefa | 1 das 85 sínteses | — tarefas prontas nunca são refeitas |
| checkpoint por geração | 5 de 100 gerações | ~5% de uma tarefa |
| parada por sinal | geração em curso | nada |

Tudo é gravado com **arquivo temporário + `rename`**, que é atômico no Linux: nunca existe
um arquivo pela metade, mesmo se a energia cair no meio da escrita.

## Onde ficam as coisas

```
medicoes/sintese/
  <mapa>__<semente>.csv     resultado final — existir significa "pronto"
  <mapa>__<semente>.ckpt    estado parcial — some quando a tarefa conclui
  <mapa>__<semente>.lock    tarefa reivindicada por um worker vivo
medicoes/sintese_repetida.csv   consolidado (regerado a cada tarefa concluída)
medicoes/pool.log               log do supervisor
```

Um `.lock` cujo dono morreu é detectado (o PID não existe mais) e a tarefa volta para a
fila automaticamente. Por isso é seguro rodar dois pools ao mesmo tempo, e é seguro
reinvocar depois de uma queda sem limpar nada à mão.

## Por que a retomada não altera os resultados

Cada síntese é determinística dada `(mapa, semente)`: `grammar(42)`, `operators(42)` e o
conjunto de treino (`srand(42)`) são fixos, e só a semente do AG varia entre rodadas. O
checkpoint guarda a população inteira, mais o estado dos **três** geradores `mt19937`
(gramática, operadores e AG), serializados pelos `operator<<`/`operator>>` da própria
biblioteca padrão.

As fórmulas são guardadas em notação prefixa e reconstruídas por um parser. Isso é exato
porque `getRandomConstant()` gera `round(x*10)/10` — uma casa decimal — e `toString()`
imprime com `%.1f`; mutação e crossover apenas movem ou substituem subárvores, nunca alteram
constantes aritmeticamente. Logo texto → AST → texto é bit a bit idêntico.

**Verificado na prática, duas vezes.** O teste em `arena` (execução ininterrupta contra
execução partida em três, interrompida nas gerações 32 e 58) deu fórmula, fitness e AST
idênticos — mas `arena` converge sempre para a mesma expressão, então não distingue uma
dessincronia de gerador. O teste decisivo foi em **`den011d`**, cuja campeã tem 34 nós:
ininterrupta e partida em três pedaços produzem a **mesma fórmula caractere a caractere**,
o mesmo fitness (2,819742) e a mesma AST (34 nós, profundidade 12).

**E os resultados são compatíveis com o programa monolítico original**, que compilava com
OpenMP e 12 threads. Isso decorre do código — em `evolve()` o `#pragma omp parallel for` só
escreve em `population[i].fitness`, cada iteração toca um índice próprio, `aStar` aloca todo
o estado localmente, e `fitness = tm/tf` vem de dois inteiros somados dentro de uma única
thread; não há redução entre threads. Confirmado na prática em `arena2` (fórmula de 65 nós):
o monolítico deu fitness 4,72395 e o worker de uma thread deu 4,723952 — mesmo valor, só
muda a precisão de impressão, que o `--merge` normaliza.

## Se algo der errado

- `--status` mostra em que geração cada tarefa parou.
- Uma tarefa que falhe (código diferente de 0 e 130) volta para a fila na próxima invocação.
- Para refazer uma tarefa do zero: apague `medicoes/sintese/<mapa>__<semente>.csv` e o
  `.ckpt` correspondente.
- Para conferir se o consolidado bate com os arquivos por tarefa:
  `.venv/bin/python scripts/sintese_pool.py --merge` e compare a contagem de linhas.
