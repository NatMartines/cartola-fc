"""
Envia os arquivos de data/landing/rodadas/ para o stage interno do Snowflake.

  data/landing/rodadas/temporada=AAAA/rodada-NN.json
      -> @CARTOLA.RAW.STG_CARTOLA/rodadas/temporada=AAAA/rodada-NN.json.gz

O PUT compacta em .gz e, com OVERWRITE = FALSE, pula o que já está no stage (idempotente).

Uso:
  uv run python ingestion/enviar_stage.py
"""

import os
from pathlib import Path

import snowflake.connector
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
LANDING = RAIZ / "data" / "landing"
STAGE = "@CARTOLA.RAW.STG_CARTOLA"

load_dotenv(RAIZ / ".env")


def conectar():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        authenticator="SNOWFLAKE_JWT",
        private_key_file=str(RAIZ / os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]),
    )


def main() -> None:
    arquivos = sorted((LANDING / "rodadas").rglob("*.json"))
    if not arquivos:
        raise SystemExit("Nenhum arquivo em data/landing/rodadas/. Rode antes o baixar_cartola.py.")
    conexao = conectar()
    cursor = conexao.cursor()
    try:
        for arquivo in arquivos:
            pasta_relativa = arquivo.parent.relative_to(LANDING).as_posix()  # rodadas/temporada=2025
            destino = f"{STAGE}/{pasta_relativa}/"
            caminho = arquivo.as_posix()  # o PUT pede barras "/" mesmo no Windows
            cursor.execute(f"PUT 'file://{caminho}' '{destino}' AUTO_COMPRESS = TRUE OVERWRITE = FALSE")
            origem, _, _, _, _, _, status, _ = cursor.fetchone()
            print(f"{origem:20} -> {destino:55} {status}")
    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
