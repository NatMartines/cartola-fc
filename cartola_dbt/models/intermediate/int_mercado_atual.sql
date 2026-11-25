-- Situação de cada atleta no mercado na rodada mais recente da temporada atual
-- (clube, preço e status). Fonte do snapshot snap_jogador_mercado.
-- Para simular a evolução do mercado rodada a rodada (a variável vai no RUN da view):
--   dbt run --select int_mercado_atual --vars '{rodada_mercado: 33}'
--   dbt snapshot
--   dbt run --select int_mercado_atual
--   dbt snapshot

with temporada_atual as (

    select *
    from {{ ref('stg_atletas_rodada') }}
    where temporada = {{ var('temporada_atual') }}
      and rodada <= {{ var('rodada_mercado') }}

)

select
    atleta_id,
    apelido,
    clube_id,
    posicao_id,
    status_id,
    preco,
    rodada
from temporada_atual
where rodada = (select max(rodada) from temporada_atual)