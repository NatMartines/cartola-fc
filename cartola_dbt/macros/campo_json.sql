{#
  Lê um campo do JSON da RAW (coluna VARIANT "dados") pelo nome original da coluna do CSV.
  Os valores chegam como texto; aqui viram o tipo certo. Valor inválido vira nulo (try_cast).

  Uso: {{ campo_json('atletas.pontos_num', 'decimal') }}
  Tipos: 'texto' (padrão), 'int', 'decimal', 'bool'
#}
{% macro campo_json(chave, tipo='texto') -%}
    {%- set bruto -%}nullif(trim(dados:"{{ chave }}"::varchar), ''){%- endset -%}
    {%- if tipo == 'int' -%}
        try_cast({{ bruto }} as number(10, 2))::int
    {%- elif tipo == 'decimal' -%}
        try_cast({{ bruto }} as number(10, 2))
    {%- elif tipo == 'bool' -%}
        try_to_boolean({{ bruto }})
    {%- else -%}
        {{ bruto }}
    {%- endif -%}
{%- endmacro %}
