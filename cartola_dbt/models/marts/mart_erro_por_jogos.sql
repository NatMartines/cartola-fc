-- Erro médio de cada método de projeção conforme quantos jogos válidos o atleta já tinha
-- antes da rodada (20 = 20 ou mais). Temporadas fechadas, sem técnicos.
-- Mostra que misturar com a média da posição ajuda mais no começo da temporada.

with base as (

    select
        least(jogos_anteriores, 20) as jogos_anteriores,
        pontos,
        proj_media_temporada,
        proj_ultimos_3,
        proj_shrinkage
    from {{ ref('int_projecao') }}
    where jogos_anteriores >= 1
      and posicao_id <> 6
      and temporada < {{ var('temporada_atual') }}
      and proj_media_posicao is not null
      and proj_shrinkage is not null

)

select
    jogos_anteriores,
    count(*)                                              as previsoes,
    round(avg(abs(pontos - proj_media_temporada)), 3)     as erro_media_jogador,
    round(avg(abs(pontos - proj_ultimos_3)), 3)           as erro_ultimos_3,
    round(avg(abs(pontos - proj_shrinkage)), 3)           as erro_jogador_posicao
from base
group by 1