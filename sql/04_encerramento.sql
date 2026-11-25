-- 04 · Encerramento: deixar tudo parado e conferir o custo

USE ROLE ACCOUNTADMIN;

-- Nada fica ligado: o warehouse já suspende sozinho em 60 s, mas garantimos
ALTER WAREHOUSE WH_CARTOLA SUSPEND;

-- Créditos gastos pelo warehouse do projeto
SELECT
  DATE_TRUNC('day', start_time) AS dia,
  ROUND(SUM(credits_used), 2)   AS creditos
FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE warehouse_name = 'WH_CARTOLA'
GROUP BY 1
ORDER BY 1;

-- Créditos do app Streamlit e de outros serviços (a view pode levar até 3 h para atualizar)
SELECT
  service_type,
  ROUND(SUM(credits_used), 2) AS creditos
FROM SNOWFLAKE.ACCOUNT_USAGE.METERING_DAILY_HISTORY
WHERE usage_date >= '2026-11-16'
GROUP BY 1
ORDER BY 2 DESC;
