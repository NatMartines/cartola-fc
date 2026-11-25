select posicao_id, nome, sigla
from {{ ref('posicoes') }}
