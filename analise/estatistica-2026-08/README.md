# Reanálise estatística — agosto/2026

13 scripts (A0…A12) que releem os dados brutos de março e refazem toda a estatística.
**34 tabelas + 2 figuras, em ~3 minutos.**

```fish
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
set -x HEURISTICAS_DADOS ~/caminho/para/02-dados-brutos   # os CSVs brutos, do Drive
.venv/bin/python scripts/run_all.py
```

A execução é determinística (semente global `20260820`): as tabelas geradas batem **byte a
byte** com as versionadas em `tabelas/`.

## Estrutura

```
scripts/     a0…a12 + comum.py (regras de agregação) + run_all.py (orquestrador)
tabelas/     34 CSVs — o resultado
figuras/     fig1 diagrama CD (a inversão de hierarquia), fig2 ECDF
medicoes/    insumos: as medições em C++ de codigo/medicoes-2026-08/
```

## As três regras que mudam quase todos os números

Concentradas em `scripts/comum.py`:

1. razões agregam por **média geométrica**, nunca aritmética;
2. expansões são **normalizadas por mapa** antes de agrupar entre mapas;
3. a unidade de replicação para generalizar é o **mapa (n = 17)**, não a instância (n = 116.050).

`comum.py` também deduplica `arena` em toda carga e expõe `celulas_degeneradas()`, que
identifica onde a heurística de memória colapsou.

## Onde ler os resultados

- Resumo: `docs/03-achados-estatisticos.md`
- Tabela a tabela: `docs/historico/ANALISE_DADOS.md`
- Achados com a frase pronta em português: `docs/historico/ANALISE_RESUMO.md`
- O que **não** se pode afirmar: `docs/historico/ANALISE_LIMITACOES.md`
- Correções a fazer no texto do relatório: `docs/historico/ANALISE_CORRECOES_TEXTO.md`
- Como parar e retomar a re-síntese longa do A9: `docs/historico/ANALISE_RETOMAR.md`

A ordem das etapas em `run_all.py` importa: `a7` depende de `a2` e `a6`; `a8` de `a3` e `a6`;
`a0` de `a1`.
