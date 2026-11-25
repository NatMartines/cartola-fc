"""
Baixa os arquivos de rodada do Cartola FC do repositório caRtola (GitHub) e
converte cada um para NDJSON (um JSON por linha), pronto para o stage do Snowflake.

- Fonte:   github.com/henriquepgomide/caRtola  (data/01_raw/AAAA/rodada-N.csv, licença MIT)
- Destino: data/landing/rodadas/temporada=AAAA/rodada-NN.json

Por que JSON e não CSV? A ordem e a quantidade de colunas mudam a cada temporada
(scouts novos, campos que somem). Em JSON cada valor carrega o nome da coluna, então
a RAW (VARIANT) aceita tudo e o dbt escolhe os campos pelo nome.

Só vão para o JSON as colunas usadas na análise (sem nome completo, foto ou slug).
Valores vazios ficam de fora da linha; tudo é guardado como texto (a tipagem é no dbt).

Idempotente: arquivos já baixados são pulados (use --force para baixar de novo).
A rodada 0 (pré-temporada de 2022) é ignorada.

Uso:
  uv run python ingestion/baixar_cartola.py
  uv run python ingestion/baixar_cartola.py --anos 2026
"""

import argparse
import csv
import io
import json
from pathlib import Path

import requests

RAIZ = Path(__file__).resolve().parent.parent
LANDING = RAIZ / "data" / "landing" / "rodadas"
URL = "https://raw.githubusercontent.com/henriquepgomide/caRtola/master/data/01_raw/{ano}/rodada-{rodada}.csv"

CAMPOS = {
    "atletas.atleta_id",
    "atletas.apelido",
    "atletas.rodada_id",
    "atletas.clube_id",
    "atletas.posicao_id",
    "atletas.status_id",
    "atletas.pontos_num",
    "atletas.preco_num",
    "atletas.variacao_num",
    "atletas.media_num",
    "atletas.jogos_num",
    "atletas.entrou_em_campo",
}
SCOUTS = {
    "A", "CA", "CV", "DE", "DP", "DS", "FC", "FD", "FF", "FS", "FT",
    "G", "GC", "GS", "I", "PC", "PI", "PP", "PS", "SG", "V",
}


def converter(texto_csv: str) -> list[str]:
    """CSV da rodada -> lista de linhas JSON só com as colunas permitidas."""
    leitor = csv.DictReader(io.StringIO(texto_csv))
    linhas = []
    for registro in leitor:
        dados = {}
        for chave, valor in registro.items():
            chave = (chave or "").strip()
            valor = (valor or "").strip()
            if valor and (chave in CAMPOS or chave in SCOUTS):
                dados[chave] = valor
        if "atletas.atleta_id" in dados:
            linhas.append(json.dumps(dados, ensure_ascii=False))
    return linhas


def baixar_temporada(ano: int, force: bool, sessao: requests.Session) -> None:
    pasta = LANDING / f"temporada={ano}"
    pasta.mkdir(parents=True, exist_ok=True)
    for rodada in range(1, 39):
        destino = pasta / f"rodada-{rodada:02d}.json"
        if destino.exists() and not force:
            print(f"{ano} rodada {rodada:2}: já existe, pulando")
            continue
        resposta = sessao.get(URL.format(ano=ano, rodada=rodada), timeout=60)
        if resposta.status_code == 404:
            print(f"{ano} rodada {rodada:2}: ainda não publicada, parando a temporada")
            break
        resposta.raise_for_status()
        resposta.encoding = "utf-8-sig"
        linhas = converter(resposta.text)
        destino.write_text("\n".join(linhas) + "\n", encoding="utf-8")
        print(f"{ano} rodada {rodada:2}: {len(linhas):4} atletas -> {destino.relative_to(RAIZ)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--anos", nargs="+", type=int, default=[2022, 2023, 2024, 2025, 2026])
    parser.add_argument("--force", action="store_true", help="baixa de novo mesmo se o arquivo existir")
    args = parser.parse_args()
    with requests.Session() as sessao:
        for ano in args.anos:
            baixar_temporada(ano, args.force, sessao)


if __name__ == "__main__":
    main()
