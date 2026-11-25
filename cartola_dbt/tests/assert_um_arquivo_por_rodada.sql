-- Cada rodada deve vir de um único arquivo. Se o mesmo arquivo for enviado com outro nome
-- (ex. rodada-1.json e rodada-01.json), as linhas duplicariam.
select temporada, rodada, count(distinct arquivo_origem) as arquivos
from {{ ref('stg_atletas_rodada') }}
group by 1, 2
having count(distinct arquivo_origem) > 1
