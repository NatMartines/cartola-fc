-- Uma linha por atleta por rodada, com o que aconteceu NA rodada (não acumulado):
-- se entrou em campo, se a pontuação vale para análise, scouts da rodada e preço pago antes dela.

with base as (

    select * from {{ ref('stg_atletas_rodada') }}

),

-- Qualidade de cada arquivo de rodada
arquivos as (

    select
        temporada,
        rodada,
        count(*)                                  as atletas_no_arquivo,
        max(jogos_oficial)                        as max_jogos,
        count_if(rodada_informada <> rodada)      as linhas_com_rodada_divergente
    from base
    group by 1, 2

),

arquivos_classificados as (

    select
        temporada,
        rodada,
        -- arquivo válido: já tem jogos disputados e informa a mesma rodada do nome do arquivo
        (max_jogos > 0 and linhas_com_rodada_divergente < atletas_no_arquivo / 2) as arquivo_valido,
        -- arquivo anterior era de pré-temporada (ninguém tinha jogado ainda)
        coalesce(lag(max_jogos) over (partition by temporada order by rodada) = 0, false) as anterior_pre_temporada
    from arquivos

),

com_anterior as (

    select
        base.*,
        arq.arquivo_valido,
        arq.anterior_pre_temporada,
        lag(base.jogos_oficial) over (partition by base.temporada, base.atleta_id order by base.rodada) as jogos_anterior
        {%- for scout in lista_scouts() %},
        lag(base.scout_{{ scout | lower }}_acum) over (partition by base.temporada, base.atleta_id order by base.rodada) as scout_{{ scout | lower }}_anterior
        {%- endfor %}
    from base
    inner join arquivos_classificados as arq
        on base.temporada = arq.temporada
       and base.rodada = arq.rodada

),

calculado as (

    select
        *,
        jogos_oficial - coalesce(jogos_anterior, 0) as jogos_na_rodada,
        coalesce(
            entrou_em_campo_fonte,
            case
                -- depois de um arquivo de pré-temporada, o salto em jogos pode incluir a rodada 1:
                -- só conta como "entrou nesta rodada" se pontuou ou se o salto foi de 2 jogos
                when anterior_pre_temporada
                    then (jogos_oficial - coalesce(jogos_anterior, 0) >= 2 or pontos <> 0)
                else jogos_oficial - coalesce(jogos_anterior, 0) > 0
            end
        ) as entrou_em_campo,
        (arquivo_valido and rodada_informada = rodada) as pontos_validos
    from com_anterior

)

select
    temporada,
    rodada,
    atleta_id,
    apelido,
    clube_id,
    posicao_id,
    status_id,
    entrou_em_campo,
    pontos_validos,
    (entrou_em_campo and pontos_validos)    as conta_na_analise,
    pontos,
    preco,
    variacao,
    preco - variacao                        as preco_antes,
    jogos_na_rodada,
    jogos_oficial,
    media_oficial,
    {%- for scout in lista_scouts() %}
    greatest(scout_{{ scout | lower }}_acum - coalesce(scout_{{ scout | lower }}_anterior, 0), 0) as scout_{{ scout | lower }},
    {%- endfor %}
    arquivo_origem,
    carregado_em
from calculado
