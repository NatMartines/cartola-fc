{# Lista de scouts definida em dbt_project.yml (vars.scouts), usada nos loops dos modelos. #}
{% macro lista_scouts() -%}
    {{ return(var('scouts')) }}
{%- endmacro %}
