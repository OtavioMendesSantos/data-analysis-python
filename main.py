import os

import kagglehub
import matplotlib.pyplot as plt
import pandas as pd
from kagglehub import KaggleDatasetAdapter
from sklearn.model_selection import train_test_split


# -----------------------------------------------------------------------------------
# CARGA DE DADOS
# -----------------------------------------------------------------------------------
def carregarArquivo(nomeArquivo):
    print(f"Iniciando ingestão de dados: {nomeArquivo} via Kaggle API...")
    try:
        dados = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "fidelissauro/combustiveis-brasil",
            nomeArquivo,
        )
        # Normalização dos nomes das colunas:
        # 1. 'normalize("NFKD")' decompõe caracteres acentuados (ex: 'á' vira 'a' + '´')
        # 2. 'encode("ascii", "ignore")' remove os acentos (que não são ASCII)
        # 3. 'decode("utf-8")' transforma de volta em string comum
        # 4. 'lower()' garante que todas as colunas sejam minúsculas para facilitar o acesso
        dados.columns = (
            dados.columns.str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.lower()
        )
        return dados
    except Exception as e:
        print(f"Erro na carga de dados: {e}")
        return None


# -----------------------------------------------------------------------------------
# TRATAMENTO
# -----------------------------------------------------------------------------------
def tratamentoArquivo(dados):
    if dados is None:
        return None
    print("Iniciando tratamento e limpeza de dados...")
    colunas_desejadas = [
        "ano",
        "mes",
        "gasolina_comum_preco_revenda_min",
        "gasolina_comum_preco_revenda_max",
        "oleo_diesel_preco_revenda_min",
        "oleo_diesel_preco_revenda_max",
    ]
    colunas_presentes = [col for col in colunas_desejadas if col in dados.columns]

    # Criamos uma cópia explícita para evitar o aviso 'SettingWithCopyWarning'
    dados = dados[colunas_presentes].copy()
    dados = dados.dropna()

    if "ano" in dados.columns and "mes" in dados.columns:
        # O Pandas espera um DataFrame com colunas específicas (year, month, day)
        # para converter em datetime de forma otimizada.
        df_temp_data = pd.DataFrame(
            {"year": dados["ano"], "month": dados["mes"], "day": 1}
        )
        dados["data"] = pd.to_datetime(df_temp_data)
        dados = dados.sort_values("data")
    return dados


# -----------------------------------------------------------------------------------
# CÁLCULO DE INDICADORES
# -----------------------------------------------------------------------------------
def calcularIndicadores(dados):
    if dados is None:
        return None
    print("Calculando métricas e indicadores...")
    # Calculamos a média simples entre o preço mínimo e máximo de revenda
    dados["gasolina_media"] = (
        dados["gasolina_comum_preco_revenda_min"]
        + dados["gasolina_comum_preco_revenda_max"]
    ) / 2
    dados["diesel_media"] = (
        dados["oleo_diesel_preco_revenda_min"] + dados["oleo_diesel_preco_revenda_max"]
    ) / 2

    # .diff() calcula a diferença entre a linha atual e a anterior (variação nominal)
    dados["var_gasolina"] = dados["gasolina_media"].diff()
    dados["var_diesel"] = dados["diesel_media"].diff()
    return dados


# -----------------------------------------------------------------------------------
# AJUSTE PELA INFLAÇÃO
# -----------------------------------------------------------------------------------
def ajustarPelaInflacao(dados):
    if dados is None:
        return None
    print("Calculando deflatores acumulados (IPCA 1999-2024)...")

    # IPCA Anual (Fonte: IBGE - https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/38884-ipca-chega-a-0-56-em-dezembro-e-fecha-o-ano-em-4-62)
    ipca_anual = {
        2024: 4.83,
        2023: 4.62,
        2022: 5.79,
        2021: 10.06,
        2020: 4.52,
        2019: 4.31,
        2018: 3.75,
        2017: 2.95,
        2016: 6.29,
        2015: 10.67,
        2014: 6.41,
        2013: 5.91,
        2012: 5.84,
        2011: 6.50,
        2010: 5.91,
        2009: 4.31,
        2008: 5.90,
        2007: 4.46,
        2006: 3.14,
        2005: 5.69,
        2004: 7.60,
        2003: 9.30,
        2002: 12.53,
        2001: 7.67,
        2000: 5.97,
        1999: 8.94,
    }

    # Cálculo do multiplicador acumulado:
    # Para comparar preços de 2001 com 2024, precisamos multiplicar o preço de 2001
    # por (1 + ipca_2001) * (1 + ipca_2002) ... até (1 + ipca_2023).
    anos = sorted(ipca_anual.keys(), reverse=True)
    multiplicadores = {}
    acumulado = 1.0

    for ano in anos:
        multiplicadores[ano] = acumulado
        acumulado *= 1 + ipca_anual[ano] / 100

    # 'map' aplica o dicionário de multiplicadores com base na coluna 'ano'
    dados["fator_ipca"] = dados["ano"].map(multiplicadores).fillna(1.0)
    dados["gasolina_real"] = dados["gasolina_media"] * dados["fator_ipca"]
    dados["diesel_real"] = dados["diesel_media"] * dados["fator_ipca"]

    return dados


# -----------------------------------------------------------------------------------
# SEPARAÇÃO TREINO E TESTE (70% / 30%)
# -----------------------------------------------------------------------------------
def separarTreinoTeste(dados):
    """
    Esta etapa é crucial para a avaliação de modelos de aprendizado de máquina.
    Separamos os dados para simular dados que o modelo nunca viu antes.
    """
    if dados is None:
        return None, None
    print("\nIniciando separação de treino e teste...")

    # Dividimos em 70% treino e 30% teste
    # random_state garante reprodutibilidade: os mesmos dados sempre serão divididos da mesma forma
    treino, teste = train_test_split(dados, test_size=0.3, random_state=42)

    print(f"- Total de registros: {len(dados)}")
    print(f"- Registros para treino (70%): {len(treino)}")
    print(f"- Registros para teste (30%): {len(teste)}")
    
    os.makedirs("output", exist_ok=True)
    treino.to_csv("output/treino.csv", index=False)
    teste.to_csv("output/teste.csv", index=False)
    print("- Arquivos 'treino.csv' e 'teste.csv' gerados em 'output/'.")

    return treino, teste

# -----------------------------------------------------------------------------------
# VISUALIZAÇÃO - EVOLUÇÃO TEMPORAL
# -----------------------------------------------------------------------------------
def gerarGraficoEvolucao(dados):
    """
    GRÁFICO DE EVOLUÇÃO TEMPORAL (TIME SERIES)

    Representação: Este gráfico de linhas ilustra a trajetória dos preços nominais ao longo do tempo.

    Análise Técnica:gerarGraficoDispersao
    - Eixos: O eixo X representa a cronologia (2001-2023). O eixo Y o valor de revenda em R$.
    - Tendência: Observamos uma tendência de alta secular, comum em ativos afetados pela inflação.
    - Insight: Serve como base comparativa para as análises de valor real e volatilidade.
    """
    if dados is None:
        return
    os.makedirs("output", exist_ok=True)

    print("- Gerando gráfico de evolução temporal...")
    plt.figure(figsize=(12, 6))
    plt.plot(
        dados["data"],
        dados["gasolina_media"],
        label="Gasolina (Nominal)",
        color="#3498db",
        linewidth=2,
    )
    plt.plot(
        dados["data"],
        dados["diesel_media"],
        label="Diesel (Nominal)",
        color="#e67e22",
        linewidth=2,
    )
    plt.title("Histórico de Preços de Combustíveis no Brasil (Nominal)", fontsize=14)
    plt.ylabel("Preço de Revenda (R$)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.3)
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join("output", "evolucao_precos.png"))
    plt.close()


# -----------------------------------------------------------------------------------
# VISUALIZAÇÃO - AJUSTE PELA INFLAÇÃO
# -----------------------------------------------------------------------------------
def gerarGraficoInflacao(dados):
    """
    GRÁFICO DE AJUSTE PELA INFLAÇÃO (PODER DE COMPRA REAL)

    Este gráfico é o "divisor de águas" da análise econométrica, pois desconta a desvalorização
    da moeda para mostrar o custo real do combustível ao longo das décadas.

    Análise Técnica:
    - Preço Nominal (Linha Cinza Pontilhada): Representa o valor "de etiqueta" que o consumidor
      via na bomba em cada época.
    - Preço Real (Linha Verde Sólida): Representa o custo da época recalculado para o poder
      de compra de Janeiro de 2024, utilizando o IPCA acumulado.
    - Área Sombreada: Ilustra visualmente o "imposto inflacionário" ou a perda de valor
      substancial do Real frente ao tempo.

    Insight Econômico: Se a linha verde estiver caindo ou estável enquanto a cinza sobe,
    significa que o aumento percebido pelo brasileiro é puramente inflacionário (perda de valor da moeda).
    Se ambas as linhas sobem juntas, houve um aumento real de custo (ex: crises internacionais de petróleo).
    """
    if dados is None:
        return
    os.makedirs("output", exist_ok=True)

    print("- Gerando gráfico de ajuste pela inflação...")
    plt.figure(figsize=(12, 6))
    plt.plot(
        dados["data"],
        dados["gasolina_real"],
        label="Gasolina (Preço Real - IPCA)",
        color="#27ae60",
        linewidth=2,
    )
    plt.plot(
        dados["data"],
        dados["gasolina_media"],
        label="Gasolina (Preço de Etiqueta)",
        color="#bdc3c7",
        linestyle="--",
    )
    plt.fill_between(
        dados["data"],
        dados["gasolina_media"],
        dados["gasolina_real"],
        color="#27ae60",
        alpha=0.1,
    )

    plt.title("Poder de Compra: Preço Real da Gasolina (Base 2024)", fontsize=14)
    plt.ylabel("R$ (Ajustado pelo IPCA)", fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(os.path.join("output", "ajuste_inflacao.png"))
    plt.close()


# -----------------------------------------------------------------------------------
# VISUALIZAÇÃO - CORRELAÇÃO DE DISPERSÃO
# -----------------------------------------------------------------------------------
def gerarGraficoDispersao(dados):
    """
    GRÁFICO DE DISPERSÃO (SCATTER PLOT)

    Representação: Este gráfico ilustra a relação direta entre os preços da gasolina e do diesel.

    Análise Técnica:
    - Eixos: O eixo X representa a gasolina, e o eixo Y o diesel (R$).
    - Tendência Visual: Os pontos formam uma linha reta ascendente, indicando alta proporcionalidade.
    - Coeficiente de Pearson: O valor próximo de 0.99 indica uma correlação linear positiva quase perfeita.

    Resumo: Demonstra que os preços estão fortemente atrelados; as variações de um refletem quase
    perfeitamente no outro devido à política de preços e fatores macroeconômicos.
    """
    if dados is None:
        return
    os.makedirs("output", exist_ok=True)

    print("- Gerando gráfico de dispersão e correlação...")
    correlacao = dados["gasolina_media"].corr(dados["diesel_media"])
    plt.figure(figsize=(8, 8))
    plt.scatter(
        dados["gasolina_media"], dados["diesel_media"], alpha=0.5, color="#2ecc71"
    )

    plt.title(f"Dispersão Gasolina vs Diesel (Pearson: {correlacao:.4f})", fontsize=14)
    plt.xlabel("Preço Gasolina (R$)", fontsize=12)
    plt.ylabel("Preço Diesel (R$)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join("output", "correlacao_dispersao.png"))
    plt.close()


# -----------------------------------------------------------------------------------
# VISUALIZAÇÃO - BOXPLOT (DETECÇÃO DE OUTLIERS)
# -----------------------------------------------------------------------------------
def gerarBoxPlot(dados):
    """
    GRÁFICO BOXPLOT (IDENTIFICAÇÃO DE OUTLIERS)

    Este gráfico é fundamental para responder se existem valores atípicos.
    - A "caixa" central contém 50% dos dados.
    - Os pontos acima ou abaixo dos "bigodes" são os outliers.

    Análise: Em combustíveis, os outliers no topo geralmente representam períodos de crise
    ou picos inflacionários repentinos.
    """
    if dados is None:
        return
    os.makedirs("output", exist_ok=True)

    print("- Gerando boxplot para detecção de outliers...")
    plt.figure(figsize=(10, 6))
    
    # Criamos o boxplot para Gasolina e Diesel (Preços Reais)
    dados.boxplot(column=["gasolina_real", "diesel_real"], grid=False, patch_artist=True,
                 boxprops=dict(facecolor="#ecf0f1", color="#2c3e50"),
                 medianprops=dict(color="#e74c3c", linewidth=2))

    plt.title("Distribuição e Outliers: Preços Reais (Base 2024)", fontsize=14)
    plt.ylabel("Preço Ajustado (R$)", fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join("output", "boxplot_outliers.png"))
    plt.close()

# -----------------------------------------------------------------------------------
# EXECUÇÃO (MAIN LOOP)
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    df = carregarArquivo("combustiveis-brasil.csv")
    if df is not None:
        df = tratamentoArquivo(df)
        df = calcularIndicadores(df)
        df = ajustarPelaInflacao(df)

        print("\nGerando visualizações em 'output/'...")
        gerarGraficoEvolucao(df)
        gerarGraficoInflacao(df)
        gerarGraficoDispersao(df)
        gerarBoxPlot(df)

        df_treino, df_teste = separarTreinoTeste(df)

        print("\nProcessamento concluído com sucesso!")
