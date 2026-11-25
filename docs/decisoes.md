# Decisões do projeto

## Escopo

- **Pergunta:** onde estão os pontos no Cartola? Barato ou caro, e a "fase" do jogador ajuda a prever?
- **Período:** 2022 a 2026. Antes de 2022 o formato dos arquivos é outro; 2026 vai até a rodada 34.
- **Tudo no Snowflake**, com o dbt rodando no meu computador (dbt Core + dbt-snowflake), igual ao projeto Voos ANAC.
- **Prazo:** terminar antes do fim do período de teste do Snowflake.

## Ingestão

- **CSV → JSON por linha → VARIANT.** A ordem e a quantidade de colunas mudam a cada temporada. Com `COPY INTO` posicional (`$1, $2...`), cada ano precisaria de um mapeamento. Em JSON, o nome da coluna vai junto com o valor e o dbt lê pelo nome.
- **Só as colunas usadas.** Nome completo, foto e slug ficam fora.
- **Rodada 0 de 2022 ignorada** (pré-temporada).
- **Arquivos com número de dois dígitos** (`rodada-01.json`) para ordenar certo na listagem. O teste `assert_um_arquivo_por_rodada` acusa se o mesmo arquivo subir com dois nomes.

## Entendendo a fonte (o que mais deu trabalho)

- O arquivo `rodada-N` é a foto do mercado **depois** da rodada N. `pontos` é da rodada; `jogos`, `media` e **scouts são acumulados** na temporada. Por isso os scouts da rodada saem da diferença para o arquivo anterior.
- `rodada-1` de **2022 e 2025** é foto de pré-temporada (todos com 0 jogos). `rodada-1` de **2023** informa `rodada_id = 2` e pontos zerados. Nos três casos a pontuação da rodada 1 não existe nos arquivos.
- Na rodada 2 dessas temporadas, o total de jogos pode pular de 0 para 2. Sem a flag `entrou_em_campo` (2022), um salto de 1 jogo não diz se o atleta jogou a rodada 1 ou a 2: só conta como "entrou na rodada 2" se pontuou.
- **Validação:** com essas regras, a média recalculada bate com a média oficial (±0,05) em 95,9% dos atletas em 2024 e 96,9% em 2026. Nas temporadas sem a rodada 1 válida a diferença é esperada, então jogos e média da temporada usam os números oficiais.
- 175 casos de atleta que trocou de clube na mesma temporada: a fato guarda o clube de cada rodada; o mart da temporada mostra o clube da última rodada.

## Projeção

- Para cada jogo, cada método usa **só as rodadas anteriores** (sem vazamento).
- Comparados: média do jogador, média da posição, últimos 3, últimos 5 e a média do jogador puxada para a da posição (shrinkage).
- **Escolha feita em 2022 a 2025 e confirmada em 2026.** Os valores de k entre 5 e 10 dão praticamente o mesmo erro (2,822 a 2,823); fiquei com k = 5 pela simplicidade.
- Os últimos 3 jogos erram 7% a 8% mais que a média da temporada: a "fase" é, em boa parte, ruído.

## Modelagem

- **Fato incremental** (`merge` por temporada, rodada e atleta): ao carregar uma rodada nova, só ela entra.
- **Snapshot** do mercado com estratégia `check` em clube, preço e status. Para ver o histórico funcionando: `dbt run --select int_mercado_atual --vars '{rodada_mercado: 33}'`, `dbt snapshot`, depois `dbt run --select int_mercado_atual` e `dbt snapshot` de novo.
- **Contratos** nos marts lidos pelo dashboard: se um tipo mudar, o build falha antes de quebrar o app.
- **Somas nos marts**, razões calculadas no dashboard (nunca média de médias).
- **Mínimo de 19 jogos** para os rankings.

## Dashboard

- **Duas abas:** "Monte seu time" (projeção da próxima rodada) e "Melhores jogadores/time" (o que já aconteceu, por temporada ou rodada).
- **Próxima rodada vem dos dados:** a aba de projeção sempre usa a rodada seguinte à última carregada; ao carregar uma rodada nova, o dashboard avança sozinho.
- **Time com orçamento:** o app escolhe o time de maior pontuação projetada que cabe nas cartoletas informadas, no esquema escolhido. O setor marcado em "Gastar mais no" vale 50% mais na escolha.
- **Melhores jogadores/time:** com "Todas" as rodadas, usa a média por jogo (mínimo de metade das rodadas jogadas); com uma rodada, usa os pontos daquela rodada. O campo mostra o melhor de cada posição, sem limite de cartoletas.
- **Escudos:** vêm da API pública do Cartola e são gravados numa tabela, porque o app não acessa a internet no trial. A API traz escudos simplificados e não tem imagem para 10 clubes; esses aparecem com uma bolinha nas cores do clube. As imagens não vão para o GitHub.
- **R$ no dashboard:** os preços aparecem como R$ para facilitar a leitura, mas no jogo a moeda é a cartoleta (C$).

## Custo

- Warehouse `WH_CARTOLA` XSMALL, auto-suspend de 60 s, resource monitor `RM_CARTOLA` de 10 créditos.
- Custo final: _preencher com o resultado do `sql/04_encerramento.sql`_.