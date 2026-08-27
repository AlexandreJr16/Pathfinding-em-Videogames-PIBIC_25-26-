#!/bin/bash
# L5: estende a quantificação "distâncias frescas vs congeladas" (A0) às outras
# quatro sementes. O programa é idempotente — pula (mapa,semente) já medidos —
# então interromper e reinvocar é seguro.
cd "$(dirname "$0")/../../../codigo/medicoes-2026-08" || exit 1
MAPAS="arena arena2 brc000d brc100d brc101d brc201d brc202d brc203d den000d den005d den011d den012d den500d den501d den602d hrt201n lak506d"
for s in 123 456 789 1011; do
  for m in $MAPAS; do
    taskset -c 6,7 nice -n 19 ./verifica_reprocessamento "$m" "$s" 2>&1 | tail -1
  done
  echo ">>> semente $s completa"
done
echo ">>> L5 concluído"
