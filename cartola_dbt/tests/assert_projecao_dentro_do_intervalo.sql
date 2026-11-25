-- A projeção é uma média ponderada de médias: precisa ficar entre a menor e a maior pontuação
-- possível da temporada. Valores fora indicam erro de fórmula.
with limites as (
    select min(pontos) as minimo, max(pontos) as maximo
    from {{ ref('fct_desempenho') }}
    where conta_na_analise
)
select p.*
from {{ ref('mart_projecao_proxima_rodada') }} as p
cross join limites as l
where p.pontos_projetados < l.minimo
   or p.pontos_projetados > l.maximo
