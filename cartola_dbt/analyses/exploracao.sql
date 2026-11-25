-- Consultas usadas para entender a fonte antes de modelar.
-- Compile com: dbt compile --select exploracao  (o SQL fica em target/compiled/)

-- 1. Arquivos de rodada problemáticos: rodada informada diferente do nome ou ninguém com jogos
select
    temporada,
    rodada,
    count(*)                              as atletas,
    max(jogos_oficial)                    as max_jogos,
    count_if(rodada_informada <> rodada)  as rodada_divergente,
    sum(abs(pontos))                      as soma_abs_pontos
from {{ ref('stg_atletas_rodada') }}
where rodada <= 2
group by 1, 2
order by 1, 2;

-- 2. Jogos e scouts são acumulados? (jogos nunca diminui ao longo da temporada)
-- select temporada, atleta_id, rodada, jogos_oficial, scout_g_acum
-- from {{ ref('stg_atletas_rodada') }}
-- where atleta_id = 37281 and temporada = 2025
-- order by rodada;

-- 3. Atletas que trocaram de clube na temporada
-- select temporada, count(*) as atletas
-- from (
--     select temporada, atleta_id
--     from {{ ref('stg_atletas_rodada') }}
--     group by 1, 2
--     having count(distinct clube_id) > 1
-- )
-- group by 1 order by 1;
