# Código da execução de referência — março/2026

⭐ **É esta versão que gerou todos os dados e todos os números do relatório final.**

Origem: commit `7d18f0b` ("sintese otimizada e multi thread", 20/03/2026), preservado sem
nenhuma edição a partir de uma cópia local que nunca foi sobrescrita.

Compile a partir da **raiz do repositório**:

```fish
make referencia     # -> bin/pathfinding-referencia
```

⚠️ Executar refaz o experimento inteiro (~20 h) e grava os quatro `resultados_*.csv` na raiz
**em modo append** — apague-os antes. Ver `docs/05-como-reproduzir.md`.

- O que este código faz, módulo a módulo: `docs/02-arquitetura-do-codigo.md`
- O que ele tem de errado: `docs/04-problemas-conhecidos.md`
- Por que existem outras duas árvores de código: `docs/00-PROVENIENCIA.md`

`synthesis/SimulatedAnnealing.{h,cpp}` está presente mas **não é chamado** por este `main.cpp`;
só a versão de junho o usa.
