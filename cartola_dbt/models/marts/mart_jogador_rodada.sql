-- Uma linha por jogo válido (atleta entrou em campo e a pontuação vale), com nomes prontos para o
-- dashboard. Base do "time do período": o app escolhe a temporada e o intervalo de rodadas
-- (ex.: rodadas 1 a 4 ≈ um mês; 1 a 38 = a temporada inteira).

select
    f.temporada,
    f.rodada,
    f.atleta_id,
    j.apelido,
    c.nome          as clube,
    p.nome          as posicao,
    f.pontos,
    f.preco_antes,
    f.variacao
from {{ ref('fct_desempenho') }} as f
left join {{ ref('dim_jogador') }} as j
    on f.atleta_id = j.atleta_id
left join {{ ref('dim_clube') }} as c
    on f.clube_id = c.clube_id
left join {{ ref('dim_posicao') }} as p
    on f.posicao_id = p.posicao_id
where f.conta_na_analise
