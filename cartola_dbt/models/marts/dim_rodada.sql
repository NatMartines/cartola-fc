-- Uma linha por rodada de cada temporada: a dimensão de tempo do projeto.
-- A fonte não tem datas, só temporada e rodada. Também mostra se o arquivo da rodada é válido
-- (a rodada 1 de 2022, 2023 e 2025 não é).

select
    temporada,
    rodada,
    count(*)                                  as atletas_no_mercado,
    count_if(conta_na_analise)                as jogos_validos,
    count_if(pontos_validos) > count(*) / 2   as arquivo_valido
from {{ ref('int_desempenho_rodada') }}
group by 1, 2