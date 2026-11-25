-- Clubes da Série A de 2022 a 2026 (seed) com o escudo, quando a API do Cartola tiver.

select
    c.clube_id,
    c.nome,
    c.sigla,
    e.escudo_data_uri
from {{ ref('clubes') }} as c
left join {{ ref('stg_escudos') }} as e
    on c.clube_id = e.clube_id
