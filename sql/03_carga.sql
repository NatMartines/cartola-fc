-- 03 · Tabela RAW e carga com COPY INTO

USE ROLE CARTOLA_DEV;
USE WAREHOUSE WH_CARTOLA;
USE SCHEMA CARTOLA.RAW;

-- Uma linha por atleta por arquivo de rodada. O JSON inteiro fica numa coluna VARIANT:
-- a ordem e a quantidade de colunas mudam a cada temporada, e o dbt escolhe os campos pelo nome.
CREATE TABLE IF NOT EXISTS RAW_ATLETAS_RODADA (
  dados          VARIANT,
  arquivo_origem VARCHAR,
  carregado_em   TIMESTAMP_NTZ
);

-- Rodar de novo não duplica: o Snowflake pula arquivos já carregados (histórico de 64 dias)
COPY INTO RAW_ATLETAS_RODADA
FROM (
  SELECT $1, METADATA$FILENAME, CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
  FROM @STG_CARTOLA/rodadas/
)
FILE_FORMAT = (FORMAT_NAME = 'FF_JSON');

-- Conferência: arquivos e linhas por temporada (esperado: 186 arquivos, 141.918 linhas)
SELECT
  REGEXP_SUBSTR(arquivo_origem, 'temporada=([0-9]{4})', 1, 1, 'e', 1) AS temporada,
  COUNT(DISTINCT arquivo_origem) AS arquivos,
  COUNT(*)                       AS linhas
FROM RAW_ATLETAS_RODADA
GROUP BY 1
ORDER BY 1;
