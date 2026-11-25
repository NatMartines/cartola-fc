-- Uma linha por atleta por arquivo de rodada, com os campos do JSON tipados.
-- Atenção ao significado: o arquivo rodada-N é a foto do mercado DEPOIS da rodada N.
-- pontos = pontuação na rodada N; jogos, média e scouts são ACUMULADOS na temporada.

with fonte as (

    select dados, arquivo_origem, carregado_em
    from {{ source('raw', 'raw_atletas_rodada') }}

)

select
    regexp_substr(arquivo_origem, 'temporada=([0-9]{4})', 1, 1, 'e', 1)::int as temporada,
    regexp_substr(arquivo_origem, 'rodada-([0-9]+)', 1, 1, 'e', 1)::int    as rodada,
    {{ campo_json('atletas.atleta_id', 'int') }}                          as atleta_id,
    {{ campo_json('atletas.apelido') }}                                   as apelido,
    {{ campo_json('atletas.clube_id', 'int') }}                           as clube_id,
    {{ normalizar_posicao(campo_json('atletas.posicao_id')) }}            as posicao_id,
    {{ campo_json('atletas.status_id', 'int') }}                          as status_id,
    {{ campo_json('atletas.rodada_id', 'int') }}                          as rodada_informada,
    {{ campo_json('atletas.pontos_num', 'decimal') }}                     as pontos,
    {{ campo_json('atletas.preco_num', 'decimal') }}                      as preco,
    {{ campo_json('atletas.variacao_num', 'decimal') }}                   as variacao,
    {{ campo_json('atletas.media_num', 'decimal') }}                      as media_oficial,
    {{ campo_json('atletas.jogos_num', 'int') }}                          as jogos_oficial,
    {{ campo_json('atletas.entrou_em_campo', 'bool') }}                   as entrou_em_campo_fonte,
    {%- for scout in lista_scouts() %}
    coalesce({{ campo_json(scout, 'int') }}, 0)                           as scout_{{ scout | lower }}_acum,
    {%- endfor %}
    arquivo_origem,
    carregado_em
from fonte
