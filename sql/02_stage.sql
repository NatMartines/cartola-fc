-- 02 · Formato de arquivo e stage interno

USE ROLE CARTOLA_DEV;
USE WAREHOUSE WH_CARTOLA;
USE SCHEMA CARTOLA.RAW;

-- Um JSON por linha (NDJSON), compactado em .gz pelo PUT
CREATE FILE FORMAT IF NOT EXISTS FF_JSON
  TYPE = JSON
  STRIP_NULL_VALUES = TRUE
  COMPRESSION = AUTO;

-- Stage interno: a "pasta" dentro do Snowflake
CREATE STAGE IF NOT EXISTS STG_CARTOLA
  FILE_FORMAT = (FORMAT_NAME = 'FF_JSON');

-- Depois do enviar_stage.py, confira os arquivos:
-- LIST @STG_CARTOLA/rodadas/;
