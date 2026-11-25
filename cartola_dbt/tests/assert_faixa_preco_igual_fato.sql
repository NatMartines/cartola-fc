-- A soma de jogos e pontos do mart_faixa_preco precisa bater com a fato (nenhum jogo perdido ou duplicado).
with mart as (
    select sum(jogos) as jogos, sum(soma_pontos) as pontos from {{ ref('mart_faixa_preco') }}
),
fato as (
    select count(*) as jogos, sum(pontos) as pontos from {{ ref('fct_desempenho') }} where conta_na_analise
)
select *
from mart cross join fato
where mart.jogos <> fato.jogos
   or abs(mart.pontos - fato.pontos) > 0.01
