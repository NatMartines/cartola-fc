"""
Baixa os escudos dos clubes da API pública do Cartola e grava no Snowflake
(CARTOLA.RAW.RAW_ESCUDOS), para o dashboard mostrar o escudo de cada jogador.

- Fonte: API do Cartola, endpoint /clubes (dados de cada clube com os links dos escudos).
- Destino: tabela RAW_ESCUDOS com a imagem em base64. O app do Streamlit in Snowflake não
  acessa a internet no trial, então a imagem precisa estar dentro do Snowflake.
- A API traz escudos simplificados (sigla sobre um escudo padrão) e não tem imagem para
  alguns clubes; esses aparecem no dashboard com uma bolinha nas cores do clube.
- As imagens NÃO vão para o GitHub: ficam só no Snowflake.

Idempotente: apaga e grava de novo a tabela inteira a cada execução.

Uso:
  uv run python ingestion/carregar_escudos.py
"""

import base64
import os
from pathlib import Path

import requests
import snowflake.connector
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")

URLS_API = [
    "https://api.cartola.globo.com/clubes",
    "https://api.cartolafc.globo.com/clubes",
]
CABECALHOS = {"User-Agent": "Mozilla/5.0 (projeto de estudo cartola-fc)"}


def conectar():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema="RAW",
        authenticator="SNOWFLAKE_JWT",
        private_key_file=str(RAIZ / os.environ["SNOWFLAKE_PRIVATE_KEY_PATH"]),
    )


def buscar_clubes(sessao: requests.Session) -> dict:
    for url in URLS_API:
        try:
            resposta = sessao.get(url, headers=CABECALHOS, timeout=30)
            if resposta.ok:
                print(f"API: {url}")
                return resposta.json()
            print(f"{url} respondeu {resposta.status_code}, tentando a próxima")
        except requests.RequestException as erro:
            print(f"{url} falhou ({erro}), tentando a próxima")
    raise SystemExit("Não consegui acessar a API do Cartola. Me manda o print desta mensagem.")


def links_por_tamanho(escudos: dict) -> list:
    """O campo 'escudos' traz um link por tamanho (ex. '60x60', '45x45', '30x30').
    Devolve os links do maior para o menor, para tentar o próximo se um não existir (404)."""
    if not isinstance(escudos, dict) or not escudos:
        return []
    def area(chave: str) -> int:
        try:
            largura, altura = chave.lower().split("x")
            return int(largura) * int(altura)
        except ValueError:
            return 0
    return [escudos[k] for k in sorted(escudos, key=area, reverse=True) if escudos[k]]


def main() -> None:
    linhas = []
    with requests.Session() as sessao:
        clubes = buscar_clubes(sessao)
        # a API devolve {"262": {...}, "263": {...}}; por garantia aceita também uma lista
        registros = clubes.values() if isinstance(clubes, dict) else clubes
        for clube in registros:
            links = links_por_tamanho(clube.get("escudos"))
            if not links:
                print(f"{clube.get('abreviacao', '?'):4} sem escudo na API, pulando")
                continue
            imagem, url = None, None
            for link in links:
                tentativa = sessao.get(link, headers=CABECALHOS, timeout=30)
                if tentativa.ok and tentativa.content:
                    imagem, url = tentativa, link
                    break
            if imagem is None:
                print(f"{clube.get('abreviacao', '?'):4} nenhum tamanho de escudo baixou, pulando")
                continue
            tipo = imagem.headers.get("Content-Type", "image/png").split(";")[0]
            linhas.append((
                int(clube["id"]),
                clube.get("abreviacao"),
                clube.get("nome"),
                tipo,
                base64.b64encode(imagem.content).decode("ascii"),
                url,
            ))
            print(f"{clube.get('abreviacao', '?'):4} ok ({len(imagem.content)} bytes)")

    if not linhas:
        raise SystemExit("Nenhum escudo baixado. Me manda o print desta saída.")

    conexao = conectar()
    cursor = conexao.cursor()
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS RAW_ESCUDOS (
                clube_id      NUMBER,
                sigla         VARCHAR,
                nome          VARCHAR,
                tipo_imagem   VARCHAR,
                imagem_base64 VARCHAR,
                url_origem    VARCHAR,
                carregado_em  TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()::TIMESTAMP_NTZ
            )
        """)
        cursor.execute("TRUNCATE TABLE RAW_ESCUDOS")
        cursor.executemany(
            "INSERT INTO RAW_ESCUDOS (clube_id, sigla, nome, tipo_imagem, imagem_base64, url_origem) "
            "VALUES (%s, %s, %s, %s, %s, %s)",
            linhas,
        )
        print(f"{len(linhas)} escudos gravados em CARTOLA.RAW.RAW_ESCUDOS")
    finally:
        cursor.close()
        conexao.close()


if __name__ == "__main__":
    main()
