import html
import math
from itertools import combinations

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Cartola FC: cada cartoleta conta", page_icon="⚽", layout="wide")

# Tema escuro, mesmo padrão do projeto Voos ANAC (cabeçalho laranja, destaque em verde)
st.markdown(
    """
    <style>
      .stApp {background: #15181E;}
      /* Margens: espaço à direita para o dashboard terminar antes do botão Run do Snowflake */
      .block-container {padding-top: 0.6rem !important; padding-bottom: 0 !important;
                        padding-left: 1.5rem !important; padding-right: 7rem !important;}
      h4 {font-size: 0.95rem !important; margin: 0 0 0.1rem 0 !important; padding: 0 !important;
          color: #F2F2F2 !important;}
      .sub {font-size: 0.75rem; color: #9AA0AA; margin-bottom: 0.4rem;}

      .cabecalho {
          display: flex; align-items: center; gap: 12px;
          background: linear-gradient(90deg, #C2531C, #E8743B);
          border-radius: 8px; padding: 8px 18px; margin-bottom: 0.3rem;
      }
      .cabecalho .icone {
          width: 34px; height: 34px; border-radius: 50%; background: #ffffff; color: #E8743B;
          display: flex; align-items: center; justify-content: center; font-size: 18px;
      }
      .cabecalho .titulo {font-size: 1.3rem; font-weight: 700; color: #ffffff; line-height: 1.2;}
      .cabecalho .subtitulo {font-size: 0.75rem; color: #FDE3D3;}

      /* Abas: a ativa com traço laranja */
      [data-baseweb="tab-list"] {gap: 22px;}
      [data-baseweb="tab"] p {font-size: 0.95rem !important;}
      [data-baseweb="tab-highlight"] {background-color: #E8743B !important;}

      /* Caixas dos filtros com borda laranja */
      [data-testid="stSelectbox"] [data-baseweb="select"] > div,
      [data-testid="stMultiSelect"] [data-baseweb="select"] > div {
          outline: 1px solid #E8743B !important; outline-offset: -1px; border-radius: 8px !important;
      }
      [data-testid="stWidgetLabel"] p {font-weight: 700 !important;}

      [data-testid="stMetric"] {
          background: #20252D; border: 1px solid #2B313A; border-left: 5px solid #E8743B;
          border-radius: 8px; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35); padding: 4px 16px;
      }
      [data-testid="stMetricLabel"] p {font-size: 0.7rem !important; color: #9AA0AA !important;
                                       text-transform: uppercase; letter-spacing: 0.03em;}
      [data-testid="stMetricValue"] {font-size: 1.45rem !important; font-weight: 700; color: #ffffff;}

      [class*="st-key-cartao"] {
          background: #20252D !important; border: 1px solid #2B313A !important;
          border-radius: 8px !important; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35) !important;
          padding: 12px 16px !important;
      }

      /* Campo de futebol realista (SVG) e cartões dos jogadores */
      /* Campo e painel na mesma grade: começam e terminam juntos, campo alinhado à esquerda com os filtros */
      .tela {display: grid; grid-template-columns: minmax(0, 0.46fr) minmax(0, 1fr); gap: 24px; align-items: stretch;}
      .tela > .campo {height: auto; min-height: 600px; width: 100%; aspect-ratio: auto; margin: 0;}
      .tela > .direita {display: flex; flex-direction: column; min-width: 0;}
      .tela > .direita > .lado {flex: 1;}
      .campo-m {width: 100%; aspect-ratio: auto; margin: 0;}
      .ranking-m {display: flex; flex-direction: column; box-sizing: border-box; background: #20252D;
                  border: 1px solid #2B313A; border-radius: 8px; padding: 10px 14px;
                  box-shadow: 0 2px 8px rgba(0,0,0,.35); font-size: 0.8rem; color: #C9CDD3;}
      .ranking-m h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .ranking-m .lista {flex: 1;}
      .tela > .direita > .ranking {flex: 1; display: flex; flex-direction: column; background: #20252D;
                                   border: 1px solid #2B313A; border-radius: 8px; padding: 10px 14px;
                                   box-shadow: 0 2px 8px rgba(0,0,0,.35); font-size: 0.8rem; color: #C9CDD3;}
      .tela > .direita > .ranking h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .tela > .direita > .ranking .lista {flex: 1;}
      .campo {position: relative; height: 600px; aspect-ratio: 68 / 100; margin: 0 auto;
              border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(0,0,0,.6);}
      .campo svg.gramado {position: absolute; inset: 0; width: 100%; height: 100%;}
      .jogador {position: absolute; transform: translate(-50%, -50%); text-align: center; width: 108px;
                filter: drop-shadow(0 3px 4px rgba(0,0,0,.6));}
      .escudo {width: 36px; height: 36px; margin: 0 auto 1px; display: flex; align-items: center;
               justify-content: center;}
      .escudo img {max-width: 36px; max-height: 36px;}
      .bola {width: 34px; height: 34px; border-radius: 50%; border: 2px solid #fff;
             display: flex; align-items: center; justify-content: center; font-size: 9.5px; font-weight: 800;
             color: #fff; text-shadow: 0 0 3px #000, 0 0 3px #000;}
      .jogador .nome {display: inline-block; background: #111418; color: #fff; font-weight: 700; font-size: 11px;
                      padding: 2px 7px; border-radius: 4px 4px 0 0; max-width: 104px; white-space: nowrap;
                      overflow: hidden; text-overflow: ellipsis; vertical-align: bottom;}
      .selos {display: flex; justify-content: center; font-size: 10px; font-weight: 700; color: #fff;}
      .selos span {white-space: nowrap;}
      .selos .pt {background: #22B35E; padding: 1px 6px; border-radius: 0 0 0 4px;}
      .selos .pr {background: #E8743B; padding: 1px 6px; border-radius: 0 0 4px 0;}
      /* tamanhos maiores só dentro do campo */
      .campo .jogador {width: 150px;}
      .campo .escudo {width: 48px; height: 48px;}
      .campo .escudo img {max-width: 48px; max-height: 48px;}
      .campo .bola {width: 44px; height: 44px; font-size: 12px;}
      .campo .jogador .nome {font-size: 14px; padding: 3px 9px; max-width: 146px;}
      .campo .selos {font-size: 12.5px;}
      .campo .selos .pt, .campo .selos .pr {padding: 2px 8px;}

      /* Escalação em lista */
      .lista {width: 100%; border-collapse: collapse; font-size: 0.8rem; color: #E8E8E8;}
      .lista th {color: #9AA0AA; font-weight: 600; text-align: left; padding: 3px 6px; border-bottom: 1px solid #2B313A;}
      .lista td {padding: 6px 6px; border-bottom: 1px solid #2B313A; vertical-align: middle;}
      .lista td.r, .lista th.r {text-align: right;}
      .lista td.g {color: #22B35E; font-weight: 700;}
      .lista td.c, .lista th.c {text-align: center; width: 52px;}
      .lista td.c .escudo {margin: 0 auto;}
      .lista .escudo, .lista .escudo img {width: 22px; height: 22px; max-width: 22px; max-height: 22px; margin: 0;}
      .lista .bola {width: 20px; height: 20px; font-size: 6.5px; border-width: 1px;}

      /* Painel do time: grade com alturas alinhadas ao campo */
      .painel {display: grid; grid-template-columns: repeat(6, 1fr); gap: 14px; align-content: start;}
      .painel .card {background: #20252D; border: 1px solid #2B313A; border-radius: 8px; padding: 10px 14px;
                     box-shadow: 0 2px 8px rgba(0,0,0,.35); font-size: 0.8rem; color: #C9CDD3; min-width: 0;}
      .painel .card h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .painel .kpi {grid-column: span 2; border-left: 5px solid #E8743B;}
      .painel .kpi span {font-size: 0.7rem; color: #9AA0AA; text-transform: uppercase; letter-spacing: .03em;}
      .painel .kpi div {font-size: 1.5rem; font-weight: 700; color: #fff; line-height: 1.3;}
      .painel .meia {grid-column: span 3;}
      .painel .inteira {grid-column: span 6;}
      .painel .nota {grid-column: span 6; font-size: 0.75rem; color: #9AA0AA; line-height: 1.4;}
      .painel .tecnico {display: flex; align-items: center; gap: 12px; font-size: 0.85rem;}
      .painel .tecnico b {color: #F2F2F2; font-size: 0.95rem;}
      .mini {display: grid; grid-template-columns: repeat(3, 1fr); gap: 8px; margin-top: 10px;}
      .mini div {background: #15181E; border-radius: 6px; padding: 6px 8px;}
      .mini span {font-size: 0.62rem; color: #9AA0AA; text-transform: uppercase; letter-spacing: .03em;}
      .mini p {margin: 0; font-size: 1.05rem; font-weight: 700; color: #fff; line-height: 1.3;}
      .mini small {font-size: 0.66rem; color: #9AA0AA;}
      .kpis3 {display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 14px;}
      .lado {display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: stretch;}
      .pilha {display: flex; flex-direction: column; gap: 14px;}
      .pilha > .card:last-child {flex: 1;}
      .nota-card {font-size: 0.75rem !important; line-height: 1.45; color: #9AA0AA !important;}
      .sem-esticar > .card:last-child {flex: 0 0 auto;}
      .compacto .lista td {padding: 3px 6px;}
      .compacto .lista .escudo, .compacto .lista .escudo img {width: 20px; height: 20px; max-width: 20px; max-height: 20px;}
      .dest {display: flex; align-items: center; gap: 10px; padding: 5px 0; border-bottom: 1px solid #2B313A;}
      .dest:last-child {border-bottom: none;}
      .dest .escudo, .dest .escudo img {width: 26px; height: 26px; max-width: 26px; max-height: 26px; margin: 0;}
      .dest .bola {width: 24px; height: 24px; font-size: 7px; border-width: 1px;}
      .dest .txt {flex: 1; min-width: 0; display: flex; flex-direction: column;}
      .dest .txt span {font-size: 0.68rem; color: #9AA0AA;}
      .dest .txt b {color: #F2F2F2; font-size: 0.85rem;}
      .dest .val {font-weight: 700; color: #22B35E; white-space: nowrap;}
      .iguais > .card {flex: 1 1 0; display: flex; flex-direction: column;}
      .iguais .mini {margin-top: auto;}
      .iguais .tecnico {margin: auto 0;}
      .escudo.grande, .escudo.grande img {width: 58px; height: 58px; max-width: 58px; max-height: 58px;}
      .escudo.grande .bola {width: 54px; height: 54px; font-size: 14px;}
      .heroi {display: flex; flex-direction: column; align-items: center; gap: 3px; margin: auto 0;}
      .heroi b {font-size: 1.1rem; color: #fff;}
      .heroi span {color: #9AA0AA; font-size: 0.8rem;}
      .rosca {display: flex; align-items: center; gap: 22px; flex: 1;}
      .anel {width: 160px; height: 160px; border-radius: 50%; flex: none; position: relative;}
      .anel .miolo {position: absolute; inset: 22px; border-radius: 50%; background: #20252D;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;}
      .anel .miolo span {font-size: 0.7rem; color: #9AA0AA;}
      .anel .miolo b {font-size: 1.15rem; color: #fff;}
      .leg.forte .nome, .leg.forte b {color: #22B35E;}
      .legendas {flex: 1; min-width: 0;}
      .leg {display: flex; align-items: center; gap: 8px; margin: 6px 0; font-size: 0.85rem;}
      .leg i {width: 11px; height: 11px; border-radius: 3px; display: inline-block; flex: none;}
      .leg .nome {flex: 1; color: #C9CDD3;}
      .leg b {color: #fff; white-space: nowrap;}
      .leg .pct {color: #9AA0AA; width: 38px; text-align: right;}
      .metades {display: grid; grid-template-columns: 1fr 1fr; gap: 28px;}
      .par {display: grid; grid-template-columns: 1fr 1fr; gap: 14px; align-items: stretch;}
      .par > .card {display: flex; flex-direction: column;}
      .par .mini {margin-top: auto;}
      .metade {display: flex; flex-direction: column; min-width: 0;}
      .metade h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .metade .mini {margin-top: auto;}
      .divisoria > .metade + .metade {border-left: 1px solid #2B313A; padding-left: 28px; margin-left: -14px;}
      .pilha .card {background: #20252D; border: 1px solid #2B313A; border-radius: 8px; padding: 10px 14px;
                    box-shadow: 0 2px 8px rgba(0,0,0,.35); font-size: 0.8rem; color: #C9CDD3; min-width: 0;}
      .pilha .card h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .pilha .tecnico {display: flex; align-items: center; gap: 12px; font-size: 0.85rem;}
      .pilha .tecnico b {color: #F2F2F2; font-size: 0.95rem;}
      .cartao-setor {display: flex; flex-direction: column;}
      .cartao-setor .barras {flex: 1; display: flex; flex-direction: column; justify-content: space-evenly;}
      .cartao-setor .setor {font-size: 0.85rem;}
      .cartao-setor .setor .rot {width: 92px; white-space: nowrap;}
      .cartao-setor .setor .trilho {height: 14px; border-radius: 7px;}
      .cartao-setor .setor .trilho div {border-radius: 7px;}
      .lado .card, .kpis3 .card {background: #20252D; border: 1px solid #2B313A; border-radius: 8px;
                                 padding: 10px 14px; box-shadow: 0 2px 8px rgba(0,0,0,.35);
                                 font-size: 0.8rem; color: #C9CDD3; min-width: 0;}
      .lado .card h5 {margin: 0 0 8px 0; font-size: 0.9rem; color: #F2F2F2; font-weight: 700;}
      .kpis3 .kpi {border-left: 5px solid #E8743B;}
      .kpis3 .kpi span {font-size: 0.7rem; color: #9AA0AA; text-transform: uppercase; letter-spacing: .03em;}
      .kpis3 .kpi div {font-size: 1.5rem; font-weight: 700; color: #fff; line-height: 1.3;}
      .lado .tecnico {display: flex; align-items: center; gap: 12px; font-size: 0.85rem;}
      .lado .tecnico b {color: #F2F2F2; font-size: 0.95rem;}
      .nota {font-size: 0.75rem; color: #9AA0AA; line-height: 1.4; margin-top: 12px;}
      .duas {display: grid; grid-template-columns: 1fr 1fr; gap: 0 28px;}

      .caixa {background: #20252D; border: 1px solid #2B313A; border-radius: 8px; padding: 10px 14px;
              font-size: 0.8rem; color: #C9CDD3; margin-bottom: 10px;}
      .caixa b.t {display: block; color: #F2F2F2; font-size: 0.9rem; margin-bottom: 6px;}
      .tecnico {display: flex; align-items: center; gap: 10px;}
      .tecnico .escudo {margin: 0;}
      .setor {display: flex; align-items: center; gap: 8px; margin: 5px 0;}
      .setor .rot {width: 78px;}
      .setor .trilho {flex: 1; height: 10px; background: #2B313A; border-radius: 5px;}
      .setor .trilho div {height: 100%; border-radius: 5px;
                          background: linear-gradient(90deg, #14532D, #22B35E 70%, #7CE3A2);}
      .setor .trilho div.apagada {opacity: .35;}
      .setor .val {width: 62px; text-align: right; font-weight: 700; color: #F2F2F2;}

      /* Mapa de calor em HTML (cores calculadas no Python: o mesmo resultado em qualquer navegador) */
      .calor {display: grid; grid-template-columns: 78px repeat(4, 1fr); gap: 4px; margin-top: 4px;}
      .calor .ch {text-align: center; font-size: 0.72rem; color: #C9CDD3; padding-bottom: 2px;}
      .calor .rl {font-size: 0.78rem; color: #E8E8E8; display: flex; align-items: center;
                  justify-content: flex-end; padding-right: 8px;}
      .calor .cel {height: 30px; border-radius: 5px; display: flex; align-items: center; justify-content: center;
                   gap: 7px; color: #fff;}
      .calor .cel b {font-size: 0.85rem;}
      .calor .cel small {font-size: 0.66rem; opacity: .8;}
      .calor .cel.melhor {outline: 2px solid #fff; outline-offset: -2px;}
      .legenda-calor {display: flex; align-items: center; justify-content: flex-end; gap: 8px; margin-top: 8px;
                      font-size: 0.7rem; color: #9AA0AA;}
      .legenda-calor .barra {width: 170px; height: 8px; border-radius: 4px;
                             background: linear-gradient(90deg, #2A3038, #22B35E);}

      /* Rankings em HTML */
      .rk {display: flex; gap: 10px; align-items: center; height: 27px; font-size: 0.8rem; color: #E8E8E8;}
      .rk .pos {width: 20px; height: 20px; border-radius: 50%; flex: none; color: #fff;
                display: flex; align-items: center; justify-content: center;
                font-size: 0.68rem; font-weight: 700;}
      .rk .corpo {flex: 1; min-width: 0;}
      .rk .linha {display: flex; justify-content: space-between; gap: 8px;}
      .rk .nome {white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
      .rk .nome b {font-weight: 700;}
      .rk .info {color: #9AA0AA;}
      .rk .valor {font-weight: 700; flex: none;}
      .rk .valor span {color: #9AA0AA; font-weight: 400;}
      .rk .trilho {height: 4px; background: #2B313A; border-radius: 2px; margin-top: 2px;}
      .rk .trilho div {height: 100%; border-radius: 2px;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Constantes ----------
session = st.connection("snowflake").session()

COR_DESTAQUE = "#22B35E"   # verde: destaque (melhor resultado)
COR_BASE = "#5B6B80"       # cinza-azulado: demais
COR_LARANJA = "#E8743B"
COR_TEXTO = "#E8E8E8"
COR_CINZA = "#9AA0AA"
# Aba Melhores jogadores/time: altura do campo e espaço ocupado pelos números + "Ordenar por".
# Se o fim do ranking não bater com o fim do campo, ajuste ALTURA_TOPO_M (maior = ranking mais baixo).
ALTURA_CAMPO_M = 640
ALTURA_TOPO_M = 168
LAYOUT_PAINEL = "L"   # L = escalação de lado; mais caro e setores do mesmo tamanho, juntos na altura da escalação
VARIANTE = "2"
ALTURA_CARTAO = 322
ALTURA = 228
ORDEM_POSICOES = ["Goleiro", "Lateral", "Zagueiro", "Meia", "Atacante", "Técnico"]

# Sigla e as duas cores principais de cada clube (só cores, sem escudos)
CLUBES = {
    "Flamengo": ("FLA", "#C8102E", "#111111"), "Botafogo": ("BOT", "#111111", "#FFFFFF"),
    "Corinthians": ("COR", "#111111", "#FFFFFF"), "Bahia": ("BAH", "#0055A4", "#D52B1E"),
    "Fluminense": ("FLU", "#7A1E3A", "#00843D"), "Vasco": ("VAS", "#111111", "#FFFFFF"),
    "Palmeiras": ("PAL", "#006437", "#FFFFFF"), "São Paulo": ("SAO", "#D52B1E", "#111111"),
    "Santos": ("SAN", "#FFFFFF", "#111111"), "Bragantino": ("RBB", "#FFFFFF", "#D52B1E"),
    "Atlético-MG": ("CAM", "#111111", "#FFFFFF"), "Cruzeiro": ("CRU", "#003DA5", "#FFFFFF"),
    "Grêmio": ("GRE", "#0D80BF", "#111111"), "Internacional": ("INT", "#D52B1E", "#FFFFFF"),
    "Juventude": ("JUV", "#00843D", "#FFFFFF"), "Vitória": ("VIT", "#D52B1E", "#111111"),
    "Criciúma": ("CRI", "#F6C700", "#111111"), "Goiás": ("GOI", "#00843D", "#FFFFFF"),
    "Sport": ("SPT", "#D52B1E", "#111111"), "Athletico-PR": ("CAP", "#D52B1E", "#111111"),
    "Coritiba": ("CFC", "#00543C", "#FFFFFF"), "Avaí": ("AVA", "#0055A4", "#FFFFFF"),
    "Chapecoense": ("CHA", "#00843D", "#FFFFFF"), "América-MG": ("AME", "#00843D", "#111111"),
    "Ceará": ("CEA", "#111111", "#FFFFFF"), "Fortaleza": ("FOR", "#0055A4", "#D52B1E"),
    "Remo": ("REM", "#0A2A66", "#FFFFFF"), "Atlético-GO": ("ACG", "#D52B1E", "#111111"),
    "Cuiabá": ("CUI", "#00843D", "#F6C700"), "Mirassol": ("MIR", "#F6C700", "#00843D"),
}

# Esquemas do Cartola: quantos jogadores de cada posição
ESQUEMAS = {
    "4-3-3": {"Goleiro": 1, "Lateral": 2, "Zagueiro": 2, "Meia": 3, "Atacante": 3},
    "4-4-2": {"Goleiro": 1, "Lateral": 2, "Zagueiro": 2, "Meia": 4, "Atacante": 2},
    "3-4-3": {"Goleiro": 1, "Lateral": 0, "Zagueiro": 3, "Meia": 4, "Atacante": 3},
    "3-5-2": {"Goleiro": 1, "Lateral": 0, "Zagueiro": 3, "Meia": 5, "Atacante": 2},
    "4-5-1": {"Goleiro": 1, "Lateral": 2, "Zagueiro": 2, "Meia": 5, "Atacante": 1},
    "5-3-2": {"Goleiro": 1, "Lateral": 2, "Zagueiro": 3, "Meia": 3, "Atacante": 2},
    "5-4-1": {"Goleiro": 1, "Lateral": 2, "Zagueiro": 3, "Meia": 4, "Atacante": 1},
}
SETORES = {"Goleiro": "Defesa", "Lateral": "Defesa", "Zagueiro": "Defesa",
           "Meia": "Meio-campo", "Atacante": "Ataque", "Técnico": "Técnico"}
PESO_PRIORIDADE = 1.5      # o setor escolhido vale 50% mais na hora de escalar


# ---------- Dados ----------
def ler(tabela: str) -> pd.DataFrame:
    df = session.table(f"CARTOLA.MARTS.{tabela}").to_pandas()
    df.columns = [c.lower() for c in df.columns]
    return df


@st.cache_data(ttl=3600)
def carregar() -> dict:
    jogadores = ler("MART_JOGADOR_TEMPORADA")
    jogadores["temporada"] = jogadores["temporada"].astype("int64")
    jogadores["valorizacao"] = jogadores["valorizacao"].astype("float64")

    projecao = ler("MART_PROJECAO_PROXIMA_RODADA")
    projecao["temporada"] = projecao["temporada"].astype("int64")
    for c in ["preco", "pontos_projetados", "media_temporada"]:
        projecao[c] = projecao[c].astype("float64")
    projecao["jogos_validos"] = projecao["jogos_validos"].astype("int64")

    rodadas = ler("MART_JOGADOR_RODADA")
    for c in ["temporada", "rodada"]:
        rodadas[c] = rodadas[c].astype("int64")
    for c in ["pontos", "preco_antes", "variacao"]:
        rodadas[c] = rodadas[c].astype("float64")

    clubes = ler("DIM_CLUBE")
    escudos = {r.nome: r.escudo_data_uri for r in clubes.itertuples()
               if isinstance(r.escudo_data_uri, str) and r.escudo_data_uri}
    return {"jogadores": jogadores, "projecao": projecao, "rodadas": rodadas, "escudos": escudos}


# ---------- Formatação ----------
def br_int(n) -> str:
    return f"{int(n):,}".replace(",", ".")


def br_num(x, casas: int = 2) -> str:
    if x is None or pd.isna(x):
        return "–"
    return f"{x:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def br_sinal(x) -> str:
    """+R$ 6,47 / −R$ 1,76"""
    if x is None or pd.isna(x):
        return "–"
    return f"{'+' if x >= 0 else '−'}R$ {br_num(abs(x))}"


def br_pct(p) -> str:
    return "–" if p is None or pd.isna(p) else f"{p:.1f}%".replace(".", ",")


ESCUDOS = {}   # nome do clube -> imagem do escudo (preenchido depois de carregar os dados)


def bola(clube: str) -> str:
    """Escudo do clube (da dim_clube). Sem escudo, uma bolinha com a sigla e as cores do clube."""
    sigla, c1, c2 = CLUBES.get(clube, (str(clube)[:3].upper(), "#3A414C", "#20252D"))
    if clube in ESCUDOS:
        return (f"<div class='escudo'><img src='{ESCUDOS[clube]}' alt='{html.escape(sigla)}' "
                f"title='{html.escape(str(clube))}'></div>")
    return (f"<div class='escudo'><div class='bola' style='background:linear-gradient(90deg,{c1} 50%,{c2} 50%)'>"
            f"{html.escape(sigla)}</div></div>")


# ---------- Escalação com orçamento ----------
def fronteira(opcoes: list) -> list:
    """Mantém só as combinações que valem a pena: para cada custo, a de maior pontuação."""
    opcoes.sort(key=lambda o: (o[0], -o[1]))
    melhores, maior = [], float("-inf")
    for custo, score, ids in opcoes:
        if score > maior:
            melhores.append((custo, score, ids))
            maior = score
    return melhores


def escalar(cand: pd.DataFrame, contagem: dict, orcamento: float, prioridade: str):
    """Escolhe o time de maior pontuação (com peso no setor prioritário) que cabe no orçamento.
    cand precisa das colunas: id, posicao, valor, custo."""
    cand = cand.dropna(subset=["valor", "custo"]).copy()
    cand["score"] = cand["valor"] * cand["posicao"].map(
        lambda p: PESO_PRIORIDADE if SETORES.get(p) == prioridade else 1.0)
    cand["ratio"] = cand["score"] / cand["custo"].clip(lower=0.5)
    atual = [(0.0, 0.0, ())]
    for posicao, n in list(contagem.items()) + [("Técnico", 1)]:
        if n == 0:
            continue
        grupo = cand[cand["posicao"] == posicao]
        if len(grupo) < n:
            return None
        # candidatos: os melhores, os de melhor custo-benefício e os mais baratos
        idx = (set(grupo.nlargest(12, "score").index) | set(grupo.nlargest(8, "ratio").index)
               | set(grupo.nsmallest(4, "custo").index))
        ids = list(idx)
        custos = dict(zip(ids, grupo.loc[ids, "custo"].astype(float)))
        scores = dict(zip(ids, grupo.loc[ids, "score"].astype(float)))
        combos = [(sum(custos[i] for i in c), sum(scores[i] for i in c), c)
                  for c in combinations(ids, n)]
        combos = fronteira(combos)
        juntos = [(c1 + c2, s1 + s2, i1 + i2) for c1, s1, i1 in atual for c2, s2, i2 in combos
                  if c1 + c2 <= orcamento + 1e-9]
        if not juntos:
            return None
        atual = fronteira(juntos)
    melhor = max(atual, key=lambda o: o[1])
    return cand.loc[list(melhor[2])]


def posicoes_no_campo(time: pd.DataFrame) -> list:
    """(x%, y%) de cada jogador: ataque em cima, goleiro embaixo."""
    lugares = []
    def linha(df, y, x_ini=10, x_fim=90):
        n = len(df)
        if n >= 4:
            # 4 ou 5 na mesma posição: duas linhas (mais aberta na frente, mais fechada atrás)
            frente, tras = df.iloc[0::2], df.iloc[1::2]
            linha(frente, y - 7, x_ini, x_fim)
            linha(tras, y + 8, x_ini + 15, x_fim - 15)
            return
        for i, (_, r) in enumerate(df.iterrows()):
            x = 50 if n == 1 else x_ini + (x_fim - x_ini) * i / (n - 1)
            lugares.append((r, x, y))
    linha(time[time["posicao"] == "Atacante"], 14, 20, 80)
    linha(time[time["posicao"] == "Meia"], 39, 18, 82)
    laterais = time[time["posicao"] == "Lateral"]
    zagueiros = time[time["posicao"] == "Zagueiro"]
    if len(laterais):
        # laterais mais altos e abertos; zagueiros mais atrás e fechados
        linha(laterais, 61, 13, 87)
        linha(zagueiros, 75, 34 if len(zagueiros) == 2 else 24, 66 if len(zagueiros) == 2 else 76)
    else:
        linha(zagueiros, 71, 20, 80)
    linha(time[time["posicao"] == "Goleiro"], 91)
    return lugares


def gramado_svg() -> str:
    """Campo visto de cima, nas proporções oficiais (68 x 105 m), com faixas de corte e todas as marcações."""
    faixas = "".join(
        f"<rect x='0' y='{i * 105}' width='680' height='105' fill='{'#2E8B3E' if i % 2 else '#349A45'}'/>"
        for i in range(10))
    l = "stroke='rgba(255,255,255,.85)' stroke-width='3' fill='none'"
    return (
        "<svg class='gramado' viewBox='0 0 680 1050' preserveAspectRatio='none'>"
        "<defs><radialGradient id='sombra' cx='50%' cy='50%' r='75%'>"
        "<stop offset='60%' stop-color='rgba(0,0,0,0)'/><stop offset='100%' stop-color='rgba(0,0,0,.35)'/>"
        f"</radialGradient></defs>{faixas}<rect width='680' height='1050' fill='url(#sombra)'/>"
        f"<rect x='30' y='30' width='620' height='990' {l}/><line x1='30' y1='525' x2='650' y2='525' {l}/>"
        f"<circle cx='340' cy='525' r='75' {l}/><circle cx='340' cy='525' r='4' fill='white'/>"
        f"<rect x='155' y='30' width='370' height='165' {l}/><rect x='250' y='30' width='180' height='55' {l}/>"
        f"<circle cx='340' cy='140' r='4' fill='white'/><path d='M 280 195 A 75 75 0 0 0 400 195' {l}/>"
        f"<rect x='155' y='855' width='370' height='165' {l}/><rect x='250' y='965' width='180' height='55' {l}/>"
        f"<circle cx='340' cy='910' r='4' fill='white'/><path d='M 280 855 A 75 75 0 0 1 400 855' {l}/>"
        "<rect x='300' y='14' width='80' height='16' fill='none' stroke='white' stroke-width='3'/>"
        "<rect x='300' y='1020' width='80' height='16' fill='none' stroke='white' stroke-width='3'/>"
        f"<path d='M30 45 A15 15 0 0 0 45 30' {l}/><path d='M635 30 A15 15 0 0 0 650 45' {l}/>"
        f"<path d='M30 1005 A15 15 0 0 1 45 1020' {l}/><path d='M650 1005 A15 15 0 0 0 635 1020' {l}/>"
        "</svg>")


def campo_html(time: pd.DataFrame, rotulo_valor: str) -> str:
    partes = [f"<div class='campo'>{gramado_svg()}"]
    for r, x, y in posicoes_no_campo(time):
        partes.append(
            f"<div class='jogador' style='left:{x:.0f}%;top:{y:.0f}%' "
            f"title='{html.escape(r['apelido'])} · {html.escape(str(r['clube']))}'>"
            f"{bola(r['clube'])}<div class='nome'>{html.escape(r['apelido'])}</div>"
            f"<div class='selos'><span class='pt'>{br_num(r['valor'])} {rotulo_valor}</span>"
            f"<span class='pr'>R$ {br_num(r['custo'])}</span></div></div>")
    partes.append("</div>")
    return "".join(partes)


def lista_html(time: pd.DataFrame, duas_colunas: bool = False) -> str:
    """Escalação do goleiro ao técnico; em duas tabelas lado a lado quando duas_colunas=True."""
    siglas = {"Goleiro": "GOL", "Lateral": "LAT", "Zagueiro": "ZAG", "Meia": "MEI", "Atacante": "ATA", "Técnico": "TEC"}
    ordem = {p: i for i, p in enumerate(["Goleiro", "Lateral", "Zagueiro", "Meia", "Atacante", "Técnico"])}
    t = time.assign(o=time["posicao"].map(ordem)).sort_values(["o", "valor"], ascending=[True, False])
    def tabela(df):
        linhas = "".join(
            f"<tr><td class='c'>{bola(r.clube)}</td><td>{siglas.get(r.posicao, '')}</td>"
            f"<td><b>{html.escape(r.apelido)}</b></td>"
            f"<td class='r'>{br_num(r.custo)}</td><td class='r g'>{br_num(r.valor)}</td></tr>"
            for r in df.itertuples())
        return (f"<table class='lista'><tr><th class='c'>Time</th><th>Pos</th><th>Jogador</th><th class='r'>R$</th>"
                f"<th class='r'>Pts</th></tr>{linhas}</table>")
    if duas_colunas:
        metade = (len(t) + 1) // 2
        return f"<div class='metades'>{tabela(t.iloc[:metade])}{tabela(t.iloc[metade:])}</div>"
    return tabela(t)


def mais_caro_html(time: pd.DataFrame, historico: pd.DataFrame, rotulo_periodo: str) -> str:
    """Cartão do jogador mais caro da escalação (sem o técnico): preço, pontos no período e melhor rodada."""
    jogadores_time = time[time["posicao"] != "Técnico"]
    caro = jogadores_time.loc[jogadores_time["custo"].idxmax()]
    jogos = historico[historico["atleta_id"] == caro["id"]]
    if jogos.empty:
        total, n, melhor_pts, melhor_rodada = None, 0, None, None
    else:
        total, n = jogos["pontos"].sum(), len(jogos)
        melhor = jogos.loc[jogos["pontos"].idxmax()]
        melhor_pts, melhor_rodada = melhor["pontos"], int(melhor["rodada"])
    escudo_grande = bola(caro["clube"]).replace("class='escudo'", "class='escudo grande'", 1)
    return (
        f"<div class='card'><h5>💰 Mais caro do time</h5>"
        f"<div class='heroi'>{escudo_grande}<b>{html.escape(caro['apelido'])}</b>"
        f"<span>{html.escape(str(caro['posicao']))} · {html.escape(str(caro['clube']))}</span></div>"
        "<div class='mini'>"
        f"<div><span>Preço</span><p style='color:{COR_LARANJA}'>R$ {br_num(caro['custo'])}</p></div>"
        f"<div><span>Pontos {rotulo_periodo}</span><p>{br_num(total, 1)}</p>"
        f"<small>em {n} jogo{'s' if n != 1 else ''}</small></div>"
        f"<div><span>Melhor rodada</span><p style='color:{COR_DESTAQUE}'>{br_num(melhor_pts, 1)} pts</p>"
        f"<small>{'rodada ' + str(melhor_rodada) if melhor_rodada else ''}</small></div>"
        "</div></div>")


def rosca_setores_html(gasto: pd.Series, prioridade: str) -> str:
    """Rosca contínua em degradê (sem cortes entre as fatias), com o total no meio
    e legenda com valor e % de cada setor."""
    setores = ["Ataque", "Meio-campo", "Defesa", "Técnico"]
    cores = {"Ataque": "#A7F0C2", "Meio-campo": "#4CC97E", "Defesa": "#1E8C4A", "Técnico": "#14532D"}
    total = float(sum(gasto.get(s, 0) for s in setores))
    # cada cor fica no meio da fatia do setor; entre elas, o navegador faz a transição suave
    inicio, meios = 0.0, []
    for setor in setores:
        angulo = 360 * float(gasto.get(setor, 0)) / total if total else 90
        meios.append((setor, inicio + angulo / 2))
        inicio += angulo
    base = meios[0][1]
    paradas = ", ".join(f"{cores[st]} {m - base:.1f}deg" for st, m in meios) + f", {cores[meios[0][0]]} 360deg"
    legenda = []
    for setor in setores:
        valor = float(gasto.get(setor, 0))
        pct = 100 * valor / total if total else 0
        destaque = prioridade not in ("", "Equilibrado") and setor == prioridade
        apagado = prioridade not in ("", "Equilibrado", setor)
        legenda.append(
            f"<div class='leg{' forte' if destaque else ''}' style='opacity:{0.4 if apagado else 1}'>"
            f"<i style='background:{cores[setor]}'></i><span class='nome'>{setor}</span>"
            f"<b>R$ {br_num(valor, 1)}</b><span class='pct'>{pct:.0f}%</span></div>")
    anel = (f"<div class='anel' style='background:conic-gradient(from {base:.1f}deg, {paradas})'>"
            f"<div class='miolo'><span>total</span><b>R$ {br_num(total, 1)}</b></div></div>")
    return (f"<div class='card'><h5>Cartoletas por setor</h5><div class='rosca'>{anel}"
            f"<div class='legendas'>{''.join(legenda)}</div></div></div>")


def painel_html(time: pd.DataFrame, nome_total: str, orcamento: float, prioridade: str,
                explicacao: str, rotulo_valor: str, cartao_destaque: str) -> str:
    """Resumo do time numa grade só, com as alturas alinhadas ao campo."""
    custo = time["custo"].sum()
    gasto = time.assign(setor=time["posicao"].map(SETORES)).groupby("setor")["custo"].sum()
    maior = gasto.max()
    barras = "".join(
        f"<div class='setor'><span class='rot'>{s}</span><div class='trilho'><div style='width:"
        f"{100 * gasto.get(s, 0) / maior:.0f}%' class='{'apagada' if prioridade not in ('', 'Equilibrado', s) else ''}'>"
        f"</div></div><span class='val'>R$ {br_num(gasto.get(s, 0), 1)}</span></div>"
        for s in ["Ataque", "Meio-campo", "Defesa", "Técnico"])
    kpis = (f"<div class='card kpi'><span>{nome_total}</span><div>{br_num(time['valor'].sum(), 1)}</div></div>"
            f"<div class='card kpi'><span>Custo do time</span><div>R$ {br_num(custo)}</div></div>"
            f"<div class='card kpi'><span>Sobram</span><div>R$ {br_num(orcamento - custo)}</div></div>")
    setor = f"<div class='card cartao-setor'><h5>Cartoletas por setor</h5><div class='barras'>{barras}</div></div>"
    escalacao = f"<div class='card'><h5>Escalação</h5>{lista_html(time)}</div>"
    nota = (f"<div class='nota'><b>Como o time é escolhido:</b> {explicacao} O setor escolhido em "
            f"\"Gastar mais no\" vale 50% mais na escolha.</div>")
    if LAYOUT_PAINEL == "L":
        setor_igual = rosca_setores_html(gasto, prioridade)
        return (f"<div class='kpis3'>{kpis}</div><div class='lado'><div class='pilha iguais'>{cartao_destaque}"
                f"{setor_igual}</div><div class='pilha'>{escalacao}</div></div>")
    if LAYOUT_PAINEL in ("P", "U"):
        escalacao2 = f"<div class='card'><h5>Escalação</h5>{lista_html(time, duas_colunas=True)}</div>"
        setor_igual = f"<div class='card cartao-setor'><h5>Cartoletas por setor</h5><div class='barras'>{barras}</div></div>"
        if LAYOUT_PAINEL == "U":
            # um cartão só, dividido ao meio na mesma linha das duas tabelas da Escalação
            mais_caro_sem_card = cartao_destaque.replace("<div class='card'>", "<div class='metade'>", 1)
            setor_sem_card = setor_igual.replace("<div class='card cartao-setor'>", "<div class='metade cartao-setor'>", 1)
            resumo = f"<div class='card'><div class='metades divisoria'>{mais_caro_sem_card}{setor_sem_card}</div></div>"
            return f"<div class='kpis3'>{kpis}</div><div class='pilha'>{resumo}{escalacao2}</div>{nota}"
        return (f"<div class='kpis3'>{kpis}</div><div class='pilha'><div class='par'>{cartao_destaque}{setor_igual}</div>"
                f"{escalacao2}</div>{nota}")
    if LAYOUT_PAINEL == "B":
        # números, mais caro e setores empilhados à esquerda; escalação na altura toda à direita
        return (f"<div class='lado'><div class='pilha'><div class='kpis3'>{kpis}</div>{cartao_destaque}{setor}</div>"
                f"<div class='pilha'>{escalacao}</div></div>{nota}")
    # A: números em cima; embaixo, mais caro + setores à esquerda e escalação à direita
    setor_compacto = setor.replace("card cartao-setor", "card")
    if VARIANTE == "1":
        # nota de como o time é escolhido ocupa o espaço que sobra embaixo dos setores
        nota_card = nota.replace("class='nota'", "class='card nota-card'")
        return (f"<div class='kpis3'>{kpis}</div><div class='lado'><div class='pilha'>{cartao_destaque}"
                f"{setor_compacto}{nota_card}</div><div class='pilha'>{escalacao}</div></div>")
    if VARIANTE == "3":
        # escalação mais compacta, alinhada com mais caro + setores
        return (f"<div class='kpis3'>{kpis}</div><div class='lado compacto'><div class='pilha sem-esticar'>"
                f"{cartao_destaque}{setor_compacto}</div><div class='pilha'>{escalacao}</div></div>{nota}")
    # 2: cartão de destaques do time embaixo dos setores
    linha = time[time["posicao"] != "Técnico"].assign(ppc=lambda x: x["valor"] / x["custo"])
    capitao = linha.loc[linha["valor"].idxmax()]
    eficiente = linha.loc[linha["ppc"].idxmax()]
    barato = linha.loc[linha["custo"].idxmin()]
    def item(icone, titulo, r, valor):
        return (f"<div class='dest'>{bola(r['clube'])}<div class='txt'><span>{icone} {titulo}</span>"
                f"<b>{html.escape(r['apelido'])}</b></div><div class='val'>{valor}</div></div>")
    destaques = (
        "<div class='card'><h5>⭐ Destaques do time</h5>"
        + item("©", "Capitão sugerido", capitao, f"{br_num(capitao['valor'])} {rotulo_valor}")
        + item("💰", "Melhor custo-benefício", eficiente, f"{br_num(eficiente['ppc'])} pts/R$")
        + item("🪙", "Mais barato", barato, f"R$ {br_num(barato['custo'])}")
        + "</div>")
    return (f"<div class='kpis3'>{kpis}</div><div class='lado'><div class='pilha'>{cartao_destaque}"
            f"{setor_compacto}{destaques}</div><div class='pilha'>{escalacao}</div></div>{nota}")


# ---------- Gráficos ----------
def ranking_html(linhas: list) -> str:
    maximo = max(l["valor"] for l in linhas)
    partes = []
    for i, l in enumerate(linhas, start=1):
        cor = COR_DESTAQUE if i <= 3 else COR_BASE
        largura = 100 * l["valor"] / maximo if maximo else 0
        partes.append(
            f"<div class='rk' title='{html.escape(l['dica'], quote=True)}'>"
            f"<div class='pos' style='background:{cor}'>{i}</div>"
            f"<div class='corpo'><div class='linha'>"
            f"<span class='nome'><b>{html.escape(l['nome'])}</b> <span class='info'>{html.escape(l['info'])}</span></span>"
            f"<span class='valor'>{l['texto']}</span></div>"
            f"<div class='trilho'><div style='width:{largura:.1f}%;background:{cor}'></div></div>"
            f"</div></div>"
        )
    return "".join(partes)


dados = carregar()
ESCUDOS.update(dados["escudos"])

# ---------- Cabeçalho ----------
st.markdown(
    """
    <div class="cabecalho">
      <div class="icone">⚽</div>
      <div>
        <div class="titulo">Cartola FC: cada cartoleta conta</div>
        <div class="subtitulo">Onde gastar, quem escalar e quem rende mais · 2022 a 2026</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

projecao = dados["projecao"]
rodada = int(projecao["rodada_projetada"].max())
temporada_proj = int(projecao["temporada"].max())
# a próxima rodada vem dos dados: última rodada carregada + 1 (depois da 38, a temporada acabou)
aba_time, aba_melhores = st.tabs(["⚽ Monte seu time", "🏆 Melhores jogadores/time"])

# =====================================================================
# ABA 1 · ESCALAR PARA A PRÓXIMA RODADA (projeção)
# =====================================================================
with aba_time:
    if rodada > 38:
        st.info(f"A temporada {temporada_proj} terminou: não há próxima rodada para projetar.")
    else:
        st.markdown(f"<div class='sub' style='font-size:0.85rem;margin:2px 0 8px'>Escalar o time para a "
                    f"rodada {rodada} da temporada de {temporada_proj}</div>",
                    unsafe_allow_html=True)
        f2, f3, f4, f5 = st.columns([0.9, 1.1, 1.3, 1.1])
        esquema = f2.selectbox("Esquema", list(ESQUEMAS.keys()), key="esquema_time")
        orcamento = f3.number_input("Cartoletas (R$)", min_value=50.0, max_value=300.0, value=120.0, step=5.0,
                                    help="Use 300 para montar o time sem limite de cartoletas.")
        prioridade = f4.selectbox("Gastar mais no", ["Equilibrado", "Ataque", "Meio-campo", "Defesa"])
        so_provaveis = f5.selectbox("Status", ["Só prováveis", "Todos"]) == "Só prováveis"
        base = projecao[projecao["status"] == "Provável"] if so_provaveis else projecao
        cand = pd.DataFrame({"id": base["atleta_id"], "apelido": base["apelido"], "clube": base["clube"],
                             "posicao": base["posicao"], "valor": base["pontos_projetados"],
                             "custo": base["preco"]})
        explicacao = (f"Os jogadores com mais pontos projetados para a rodada {rodada} da temporada de {temporada_proj} que "
                      "cabem nas cartoletas. Projeção = média do jogador puxada para a média da posição "
                      "(erra 2% menos que a média simples).")
        historico = dados["rodadas"][dados["rodadas"]["temporada"] == temporada_proj]

        time = escalar(cand.reset_index(drop=True), ESQUEMAS[esquema], orcamento,
                       prioridade if prioridade != "Equilibrado" else "")
        if time is None:
            st.warning(f"Não dá para montar um {esquema} com R$ {br_num(orcamento)}. Aumente as cartoletas.")
        else:
            painel = painel_html(time, "Pontos projetados", orcamento, prioridade, explicacao, "pts",
                                 mais_caro_html(time, historico, f"em {temporada_proj}"))
            st.markdown(f"<div class='tela'>{campo_html(time[time['posicao'] != 'Técnico'], 'pts')}"
                        f"<div class='direita'>{painel}</div></div>", unsafe_allow_html=True)

# =====================================================================
# ABA 2 · MELHORES JOGADORES (temporada inteira ou uma rodada)
# =====================================================================
with aba_melhores:
    rodadas_df = dados["rodadas"]
    m1, m2, m3, _ = st.columns([1, 1, 1, 1.6])
    temporadas = sorted(rodadas_df["temporada"].unique(), reverse=True)
    temporada = m1.selectbox("Temporada", temporadas, index=1 if len(temporadas) > 1 else 0,
                             key="temporada_melhores")
    da_temporada = rodadas_df[rodadas_df["temporada"] == temporada]
    lista_rodadas = sorted(da_temporada["rodada"].unique())
    escolha = m2.selectbox("Rodada", ["Todas"] + [str(r) for r in lista_rodadas], key="rodada_melhores")
    esquema_m = m3.selectbox("Esquema", list(ESQUEMAS.keys()), key="esquema_melhores")

    if escolha == "Todas":
        # temporada inteira: média por jogo, mínimo de jogos = metade das rodadas jogadas
        minimo = max(1, (max(lista_rodadas) + 1) // 2)
        ultimo_clube = da_temporada.sort_values("rodada").groupby("atleta_id")["clube"].last()
        tabela = (da_temporada.groupby(["atleta_id", "apelido", "posicao"], as_index=False, dropna=False)
                  .agg(jogos=("pontos", "size"), pontos=("pontos", "sum"), investido=("preco_antes", "sum"),
                       custo=("preco_antes", "mean")))
        tabela["clube"] = tabela["atleta_id"].map(ultimo_clube)
        tabela = tabela[tabela["jogos"] >= minimo]
        tabela["media"] = tabela["pontos"] / tabela["jogos"]
        valoriz = (dados["jogadores"][dados["jogadores"]["temporada"] == temporada]
                   .set_index("atleta_id")["valorizacao"])
        tabela["valorizacao"] = tabela["atleta_id"].map(valoriz)
        titulo_periodo, rotulo_campo, nome_total = f"{temporada}", "méd", "Soma das médias"
        nota = f"Temporada {temporada} inteira · média por jogo · mínimo de {minimo} jogos válidos."
    else:
        r = int(escolha)
        tabela = (da_temporada[da_temporada["rodada"] == r]
                  .rename(columns={"variacao": "valorizacao"})
                  .assign(jogos=1, investido=lambda x: x["preco_antes"], custo=lambda x: x["preco_antes"],
                          media=lambda x: x["pontos"]))
        titulo_periodo, rotulo_campo, nome_total = f"rodada {r} de {temporada}", "pts", "Pontos do time"
        nota = f"Rodada {r} de {temporada} · só quem entrou em campo · valorização = variação de preço na rodada."
    tabela["ppc"] = tabela["pontos"] / tabela["investido"].where(tabela["investido"] > 0)

    # campo: o melhor de cada posição no esquema escolhido (sem limite de cartoletas)
    cand = pd.DataFrame({"id": tabela["atleta_id"], "apelido": tabela["apelido"], "clube": tabela["clube"],
                         "posicao": tabela["posicao"], "valor": tabela["media"], "custo": tabela["custo"]})
    time_m = escalar(cand.reset_index(drop=True), ESQUEMAS[esquema_m], 10_000, "")

    if time_m is None:
        st.warning("Não há jogadores suficientes nesse período para montar o esquema.")
        st.stop()
    jogadores_m = time_m[time_m["posicao"] != "Técnico"]
    melhor = jogadores_m.loc[jogadores_m["valor"].idxmax()]

    # campo à esquerda (mesma largura e alinhamento da 1ª aba); números, ordenação e ranking à direita
    col_campo, col_dir = st.columns([0.46, 1], gap="medium")
    col_campo.markdown(campo_html(jogadores_m, rotulo_campo).replace(
        "<div class='campo'>", f"<div class='campo campo-m' style='height:{ALTURA_CAMPO_M}px'>", 1),
        unsafe_allow_html=True)
    with col_dir:
        st.markdown(
            f"<div class='kpis3'><div class='card kpi'><span>{nome_total}</span><div>{br_num(jogadores_m['valor'].sum(), 1)}</div></div>"
            f"<div class='card kpi'><span>Custo do time</span><div>R$ {br_num(time_m['custo'].sum())}</div></div>"
            f"<div class='card kpi'><span>Melhor do time</span><div>{html.escape(melhor['apelido'])}</div></div></div>",
            unsafe_allow_html=True)
        ordem = st.radio("Ordenar o ranking por", ["🏆 Pontos", "💰 Custo-benefício", "📈 Valorização", "⭐ Média"],
                         horizontal=True, key="ordem_melhores")
        coluna = {"🏆 Pontos": "pontos", "💰 Custo-benefício": "ppc", "📈 Valorização": "valorizacao",
                  "⭐ Média": "media"}[ordem]
        top = tabela.dropna(subset=[coluna]).sort_values(coluna, ascending=False).head(10)
        linhas = "".join(
            f"<tr><td class='c'>{i}</td><td class='c'>{bola(t.clube)}</td><td><b>{html.escape(t.apelido)}</b></td>"
            f"<td>{html.escape(str(t.posicao))}</td><td class='r'>{int(t.jogos)}</td>"
            f"<td class='r'>{br_num(t.media)}</td><td class='r g'>{br_num(t.pontos, 1)}</td>"
            f"<td class='r'>{br_num(t.ppc)}</td>"
            f"<td class='r' style='color:{COR_LARANJA if (t.valorizacao or 0) >= 0 else COR_CINZA}'>"
            f"{br_sinal(t.valorizacao)}</td></tr>"
            for i, t in enumerate(top.itertuples(), start=1))
        tabela_html = (
            "<table class='lista'><tr><th class='c'>#</th><th class='c'>Time</th><th>Jogador</th><th>Pos</th>"
            "<th class='r'>Jogos</th><th class='r'>Média</th><th class='r'>Pontos</th><th class='r'>Pts/R$</th>"
            f"<th class='r'>Valorização</th></tr>{linhas}</table>")
        st.markdown(
            f"<div class='card ranking-m' style='height:{ALTURA_CAMPO_M - ALTURA_TOPO_M}px'>"
            f"<h5>Ranking dos jogadores · {titulo_periodo}</h5>{tabela_html}</div>",
            unsafe_allow_html=True)