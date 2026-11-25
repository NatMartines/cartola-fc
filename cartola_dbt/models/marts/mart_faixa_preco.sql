-- Jogos válidos agrupados pela faixa de preço paga ANTES da rodada.
-- Guarda somas (não médias), para o dashboard recalcular os indicadores com qualquer filtro.

with jogos as (

    select
        temporada,
        posicao_id,
        pontos,
        preco_antes,
        case
            when preco_antes < 5  then 1
            when preco_antes < 10 then 2
            when preco_antes < 15 then 3
            else 4
        end as ordem_faixa
    from {{ ref('fct_desempenho') }}
    where conta_na_analise

)

select
    j.temporada,
    pos.nome                                  as posicao,
    j.ordem_faixa,
    case j.ordem_faixa
        when 1 then 'até C$ 5'
        when 2 then 'C$ 5 a 10'
        when 3 then 'C$ 10 a 15'
        else 'acima de C$ 15'
    end                                       as faixa_preco,
    count(*)                                  as jogos,
    sum(j.pontos)                             as soma_pontos,
    sum(j.preco_antes)                        as soma_cartoletas,
    count_if(j.pontos >= 10)                  as jogos_10_ou_mais
from jogos as j
left join {{ ref('dim_posicao') }} as pos
    on j.posicao_id = pos.posicao_id
group by 1, 2, 3, 4
