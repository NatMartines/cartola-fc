-- Fato central: uma linha por atleta por rodada (2022 a 2026), com a projeção feita antes da rodada.
-- Incremental: ao carregar uma rodada nova, só as linhas novas são inseridas (merge pela chave).

{{
    config(
        materialized='incremental',
        unique_key=['temporada', 'rodada', 'atleta_id'],
        incremental_strategy='merge',
        on_schema_change='append_new_columns'
    )
}}

select
    d.temporada,
    d.rodada,
    d.atleta_id,
    d.clube_id,
    d.posicao_id,
    d.status_id,
    d.entrou_em_campo,
    d.pontos_validos,
    d.conta_na_analise,
    d.pontos,
    p.proj_shrinkage            as pontos_projetados,
    d.preco_antes,
    d.preco,
    d.variacao,
    d.jogos_oficial,
    d.media_oficial,
    {%- for scout in lista_scouts() %}
    d.scout_{{ scout | lower }},
    {%- endfor %}
    d.carregado_em
from {{ ref('int_desempenho_rodada') }} as d
left join {{ ref('int_projecao') }} as p
    on d.temporada = p.temporada
   and d.rodada = p.rodada
   and d.atleta_id = p.atleta_id
{% if is_incremental() %}
where d.carregado_em > (select max(carregado_em) from {{ this }})
{% endif %}
