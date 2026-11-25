-- Para cada jogo válido (atleta entrou em campo e a pontuação vale), quanto cada método
-- teria previsto USANDO SÓ AS RODADAS ANTERIORES. Base da avaliação e da projeção.
--
-- Método escolhido (shrinkage): média do jogador "puxada" para a média da posição.
--   projeção = (pontos anteriores + k × média da posição até ali) / (jogos anteriores + k)
-- Com poucos jogos, vale mais a média da posição; com muitos, a do próprio jogador.

{% set k = var('k_shrinkage') %}

with jogos as (

    select temporada, rodada, atleta_id, posicao_id, pontos
    from {{ ref('int_desempenho_rodada') }}
    where conta_na_analise

),

posicao_rodada as (

    select temporada, posicao_id, rodada, sum(pontos) as soma_pontos, count(*) as qtd_jogos
    from jogos
    group by 1, 2, 3

),

posicao_ate_rodada_anterior as (

    select
        temporada,
        posicao_id,
        rodada,
        sum(soma_pontos) over (partition by temporada, posicao_id order by rodada
                               rows between unbounded preceding and 1 preceding)
      / nullif(sum(qtd_jogos) over (partition by temporada, posicao_id order by rodada
                                    rows between unbounded preceding and 1 preceding), 0) as media_posicao_anterior
    from posicao_rodada

),

jogador_ate_rodada_anterior as (

    select
        temporada,
        rodada,
        atleta_id,
        posicao_id,
        pontos,
        count(*)    over (partition by temporada, atleta_id order by rodada
                          rows between unbounded preceding and 1 preceding) as jogos_anteriores,
        sum(pontos) over (partition by temporada, atleta_id order by rodada
                          rows between unbounded preceding and 1 preceding) as soma_anterior,
        avg(pontos) over (partition by temporada, atleta_id order by rodada
                          rows between 3 preceding and 1 preceding)        as media_ultimos_3,
        avg(pontos) over (partition by temporada, atleta_id order by rodada
                          rows between 5 preceding and 1 preceding)        as media_ultimos_5
    from jogos

)

select
    j.temporada,
    j.rodada,
    j.atleta_id,
    j.posicao_id,
    j.pontos,
    j.jogos_anteriores,
    round(j.soma_anterior / nullif(j.jogos_anteriores, 0), 2)  as proj_media_temporada,
    round(p.media_posicao_anterior, 2)                         as proj_media_posicao,
    round(j.media_ultimos_3, 2)                                as proj_ultimos_3,
    round(j.media_ultimos_5, 2)                                as proj_ultimos_5,
    round(
        (coalesce(j.soma_anterior, 0) + {{ k }} * p.media_posicao_anterior)
      / (j.jogos_anteriores + {{ k }}),
        2
    )                                                          as proj_shrinkage
from jogador_ate_rodada_anterior as j
left join posicao_ate_rodada_anterior as p
    on j.temporada = p.temporada
   and j.posicao_id = p.posicao_id
   and j.rodada = p.rodada
