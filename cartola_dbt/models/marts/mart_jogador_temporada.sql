-- Uma linha por atleta por temporada: custo-benefício, consistência e valorização.
-- Jogos e média oficiais vêm do último arquivo da temporada (incluem a rodada 1, que não tem
-- arquivo válido em 2022, 2023 e 2025). Os demais indicadores usam só os jogos válidos.

with fato as (

    select * from {{ ref('fct_desempenho') }}

),

jogos_validos as (

    select
        temporada,
        atleta_id,
        count(*)                       as jogos_validos,
        sum(pontos)                    as pontos_validos,
        sum(preco_antes)               as cartoletas_investidas,
        count_if(pontos >= 5)          as jogos_5_ou_mais,
        count_if(pontos >= 10)         as jogos_10_ou_mais
    from fato
    where conta_na_analise
    group by 1, 2

),

scouts as (

    -- a soma das diferenças rodada a rodada devolve o acumulado da temporada
    select temporada, atleta_id, sum(scout_g) as gols, sum(scout_a) as assistencias, sum(scout_ds) as desarmes
    from fato
    group by 1, 2

),

primeira_rodada as (

    select temporada, atleta_id, preco_antes as preco_inicial
    from fato
    qualify row_number() over (partition by temporada, atleta_id order by rodada) = 1

),

ultima_rodada as (

    select temporada, atleta_id, clube_id, posicao_id, preco as preco_final, jogos_oficial, media_oficial
    from fato
    qualify row_number() over (partition by temporada, atleta_id order by rodada desc) = 1

)

select
    u.temporada::number(4, 0)                                            as temporada,
    u.atleta_id::number(38, 0)                                           as atleta_id,
    j.apelido::varchar                                                   as apelido,
    c.nome::varchar                                                      as clube,
    pos.nome::varchar                                                    as posicao,
    u.jogos_oficial::number(38, 0)                                       as jogos,
    u.media_oficial::number(10, 2)                                       as media,
    coalesce(v.jogos_validos, 0)::number(38, 0)                          as jogos_validos,
    coalesce(v.pontos_validos, 0)::number(10, 2)                         as pontos_validos,
    coalesce(v.cartoletas_investidas, 0)::number(10, 2)                  as cartoletas_investidas,
    round(v.pontos_validos / nullif(v.cartoletas_investidas, 0), 3)::number(10, 3) as pontos_por_cartoleta,
    coalesce(v.jogos_5_ou_mais, 0)::number(38, 0)                        as jogos_5_ou_mais,
    coalesce(v.jogos_10_ou_mais, 0)::number(38, 0)                       as jogos_10_ou_mais,
    p.preco_inicial::number(10, 2)                                       as preco_inicial,
    u.preco_final::number(10, 2)                                         as preco_final,
    (u.preco_final - p.preco_inicial)::number(10, 2)                     as valorizacao,
    s.gols::number(38, 0)                                                as gols,
    s.assistencias::number(38, 0)                                        as assistencias,
    s.desarmes::number(38, 0)                                            as desarmes,
    (u.jogos_oficial >= {{ var('min_jogos_ranking') }})::boolean         as elegivel_ranking
from ultima_rodada as u
inner join primeira_rodada as p
    on u.temporada = p.temporada and u.atleta_id = p.atleta_id
inner join scouts as s
    on u.temporada = s.temporada and u.atleta_id = s.atleta_id
left join jogos_validos as v
    on u.temporada = v.temporada and u.atleta_id = v.atleta_id
left join {{ ref('dim_jogador') }} as j
    on u.atleta_id = j.atleta_id
left join {{ ref('dim_clube') }} as c
    on u.clube_id = c.clube_id
left join {{ ref('dim_posicao') }} as pos
    on u.posicao_id = pos.posicao_id
