-- Um escudo por clube, já no formato que o navegador mostra direto (data URI).

select
    clube_id::int                                                   as clube_id,
    'data:' || coalesce(tipo_imagem, 'image/png') || ';base64,' || imagem_base64 as escudo_data_uri
from {{ source('raw', 'raw_escudos') }}
where imagem_base64 is not null
qualify row_number() over (partition by clube_id order by carregado_em desc) = 1
