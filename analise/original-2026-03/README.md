# Análise original — março/2026

Os scripts que produziram as tabelas e figuras da **primeira versão do relatório** — inclusive
os números que a reanálise de agosto depois corrigiu.

| Arquivo | O que faz |
|---|---|
| `analise.py` | imprime 11 blocos de tabelas no terminal; é a fonte da Tabela 4 |
| `gerarGraficos.py` | a figura de degradação |
| `teste.py` | conferência pontual, de uso avulso |
| `figuras/` | as figuras geradas na época |

Esperam os `resultados_*.csv` **no diretório de trabalho**. Não foram adaptados à nova
estrutura de propósito: são o registro de como os números antigos foram produzidos.

> ⚠️ Os números que estes scripts produzem são os **antigos**. O *speedup* de 51,98× sai daqui,
> e está errado — compara duas populações de instâncias diferentes. Ver
> `docs/03-achados-estatisticos.md`, A3. Use `analise/estatistica-2026-08/` para números
> corretos.

## `variante-2026-06/`

As mesmas análises, adaptadas ao esquema de CSV da refatoração de junho (com a coluna `modo`),
mais alguns geradores de figura para SBC/IEEE e a ponte para a implementação original de
Saunders em Octave (`rodar_saunders.py`, `comparar_implementacoes.py`).

**Nunca rodaram sobre dados reais** — o experimento de junho nunca foi executado. A comparação
com o Saunders original ficou preparada e não realizada; o CSV de saída está vazio, só com
cabeçalho, em `dados/resultados_sintese_saunders_VAZIO.csv`.
