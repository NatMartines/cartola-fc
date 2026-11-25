{{ config(severity='warn') }}
-- Validação contra o número oficial: em temporadas com a rodada 1 válida (2024 e 2026),
-- a média recalculada com os jogos válidos deve bater com a média do Cartola (±0,05)
-- em pelo menos 90% dos atletas com 5 jogos ou mais. Retorna as temporadas que falham.
with comparacao as (
    select
        temporada,
        abs(pontos_validos / nullif(jogos_validos, 0) - media) <= 0.05 as bate
    from {{ ref('mart_jogador_temporada') }}
    where jogos >= 5
      and temporada in (2024, 2026)
)
select temporada, avg(iff(bate, 1, 0)) as pct_que_bate
from comparacao
group by 1
having avg(iff(bate, 1, 0)) < 0.9
