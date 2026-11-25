-- Erro médio absoluto (MAE) de cada método de projeção, em pontos.
-- Só jogos em que o atleta já tinha 3 jogos válidos antes, sem técnicos.
-- Mesmos jogos para todos os métodos, para a comparação ser justa.

{% set metodos = {
    'proj_media_temporada': ['Média do jogador na temporada', 1],
    'proj_media_posicao':   ['Média da posição', 2],
    'proj_ultimos_3':       ['Últimos 3 jogos', 3],
    'proj_ultimos_5':       ['Últimos 5 jogos', 4],
    'proj_shrinkage':       ['Média do jogador puxada para a da posição (k = ' ~ var('k_shrinkage') ~ ')', 5],
} %}

with base as (

    select
        *,
        case when temporada = {{ var('temporada_atual') }}
             then '{{ var('temporada_atual') }}'
             else '2022 a {{ var('temporada_atual') - 1 }}'
        end as periodo
    from {{ ref('int_projecao') }}
    where jogos_anteriores >= 3
      and posicao_id <> 6
      and proj_shrinkage is not null
      and proj_media_posicao is not null

)

{% for coluna, info in metodos.items() %}
select
    periodo,
    {{ info[1] }}                                 as ordem,
    '{{ info[0] }}'                               as metodo,
    count(*)                                      as previsoes,
    round(avg(abs(pontos - {{ coluna }})), 3)     as erro_medio_absoluto
from base
group by 1
{% if not loop.last %}union all{% endif %}
{% endfor %}
