-- Uma linha por atleta, com o apelido, a posição e o clube mais recentes.

with historico as (

    select
        atleta_id,
        apelido,
        posicao_id,
        clube_id,
        temporada,
        rodada
    from {{ ref('int_desempenho_rodada') }}

),

resumo as (

    select
        atleta_id,
        min(temporada)            as primeira_temporada,
        max(temporada)            as ultima_temporada,
        count(distinct temporada) as temporadas
    from historico
    group by 1

),

mais_recente as (

    select atleta_id, apelido, posicao_id, clube_id
    from historico
    qualify row_number() over (partition by atleta_id order by temporada desc, rodada desc) = 1

)

select
    r.atleta_id,
    m.apelido,
    m.posicao_id    as posicao_id_atual,
    m.clube_id      as clube_id_atual,
    r.primeira_temporada,
    r.ultima_temporada,
    r.temporadas
from resumo as r
inner join mais_recente as m
    on r.atleta_id = m.atleta_id
