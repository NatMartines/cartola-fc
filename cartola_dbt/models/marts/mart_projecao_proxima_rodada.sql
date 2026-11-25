-- Projeção de pontos para a próxima rodada da temporada atual, para cada atleta do mercado.
-- Mesma fórmula avaliada em mart_avaliacao_projecao, agora usando todas as rodadas já jogadas.

{% set k = var('k_shrinkage') %}

with fato as (

    select * from {{ ref('fct_desempenho') }}
    where temporada = {{ var('temporada_atual') }}

),

ultima_rodada as (

    select max(rodada) as rodada from fato

),

jogador as (

    select atleta_id, count(*) as jogos_validos, sum(pontos) as soma_pontos
    from fato
    where conta_na_analise
    group by 1

),

posicao as (

    select posicao_id, avg(pontos) as media_posicao
    from fato
    where conta_na_analise
    group by 1

),

mercado as (

    select f.*
    from fato as f
    inner join ultima_rodada as u
        on f.rodada = u.rodada

)

select
    {{ var('temporada_atual') }}::number(4, 0)                        as temporada,
    (u.rodada + 1)::number(38, 0)                                     as rodada_projetada,
    m.atleta_id::number(38, 0)                                        as atleta_id,
    dj.apelido::varchar                                               as apelido,
    c.nome::varchar                                                   as clube,
    pos.nome::varchar                                                 as posicao,
    st.nome::varchar                                                  as status,
    m.preco::number(10, 2)                                            as preco,
    coalesce(j.jogos_validos, 0)::number(38, 0)                       as jogos_validos,
    round(j.soma_pontos / nullif(j.jogos_validos, 0), 2)::number(10, 2) as media_temporada,
    round(
        (coalesce(j.soma_pontos, 0) + {{ k }} * p.media_posicao) / (coalesce(j.jogos_validos, 0) + {{ k }}),
        2
    )::number(10, 2)                                                  as pontos_projetados,
    round(
        (coalesce(j.soma_pontos, 0) + {{ k }} * p.media_posicao) / (coalesce(j.jogos_validos, 0) + {{ k }})
      / nullif(m.preco, 0),
        3
    )::number(10, 3)                                                  as projetados_por_cartoleta
from mercado as m
cross join ultima_rodada as u
left join jogador as j
    on m.atleta_id = j.atleta_id
left join posicao as p
    on m.posicao_id = p.posicao_id
left join {{ ref('dim_jogador') }} as dj
    on m.atleta_id = dj.atleta_id
left join {{ ref('dim_clube') }} as c
    on m.clube_id = c.clube_id
left join {{ ref('dim_posicao') }} as pos
    on m.posicao_id = pos.posicao_id
left join {{ ref('status_atleta') }} as st
    on m.status_id = st.status_id
