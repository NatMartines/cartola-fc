{#
  Em 2022 (rodadas 1 a 22) a posição veio como texto ('gol', 'lat'...); nas outras, como número.
  Devolve sempre o id numérico: 1 goleiro, 2 lateral, 3 zagueiro, 4 meia, 5 atacante, 6 técnico.
#}
{% macro normalizar_posicao(coluna) -%}
    {%- set siglas = {'gol': 1, 'lat': 2, 'zag': 3, 'mei': 4, 'ata': 5, 'tec': 6} -%}
    case lower({{ coluna }})
        {%- for sigla, id in siglas.items() %}
        when '{{ sigla }}' then {{ id }}
        {%- endfor %}
        else try_cast({{ coluna }} as number(10, 2))::int
    end
{%- endmacro %}
