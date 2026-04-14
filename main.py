import os
import kagglehub
import matplotlib.pyplot as plt
import pandas as pd
from kagglehub import KaggleDatasetAdapter


# -----------------------------------------------------------------------------------
# FUNÇÃO 1: CARGA DE DADOS (DATA INGESTION)
# Explicação para Apresentação:
# "Utilizamos o kagglehub para garantir que o projeto sempre consuma a versão mais recente
# do dataset oficial, eliminando a necessidade de baixar arquivos manuais (.csv)."
# -----------------------------------------------------------------------------------
def carregarArquivo(nomeArquivo):
    print(f"Iniciando ingestão de dados: {nomeArquivo} via Kaggle API...")
    dados = None
    try:
        dados = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "fidelissauro/combustiveis-brasil",
            nomeArquivo,
        )

        # PONTO CHAVE: Normalização de metadados.
        # " datasets públicos costumam ter acentos e espaços nos nomes das colunas.
        #   Normalizamos tudo para minúsculo e sem acentos para evitar erros de sintaxe futuros."
        dados.columns = (
            dados.columns.str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.lower()
        )

    except Exception as e:
        print(f"Erro na carga de dados: {e}")

    return dados


# -----------------------------------------------------------------------------------
# FUNÇÃO 2: TRATAMENTO (DATA WRANGLING)
# Explicação para Apresentação:
# "Dados crus raramente estão prontos para análise. Aqui fazemos o 'Slicing' (recorte)
# apenas do que importa e transformamos tipos de dados genéricos em Séries Temporais."
# -----------------------------------------------------------------------------------
def tratamentoArquivo(dados):
    if dados is None:
        return None

    print("Iniciando tratamento e limpeza de dados...")

    # 1. Filtro de Escopo: Focamos apenas em colunas de Preço de Revenda (consumidor final).
    colunas_desejadas = [
        "ano",
        "mes",
        "gasolina_comum_preco_revenda_min",
        "gasolina_comum_preco_revenda_max",
        "oleo_diesel_preco_revenda_min",
        "oleo_diesel_preco_revenda_max",
    ]

    colunas_presentes = [col for col in colunas_desejadas if col in dados.columns]
    dados = dados[colunas_presentes]

    # 2. Limpeza: Removemos registros incompletos para não distorcer as médias.
    dados.dropna(inplace=True)

    # 3. Engenharia de Atributos (Data Transformation):
    # "Transformamos as colunas separadas de 'ano' e 'mês' em um objeto Datetime legítimo do Pandas.
    # Isso permite que o Python entenda a cronologia e faça ordenações temporais precisas."
    if "ano" in dados.columns and "mes" in dados.columns:
        df_data = pd.DataFrame({"year": dados["ano"], "month": dados["mes"], "day": 1})
        dados["data"] = pd.to_datetime(df_data)
        dados.sort_values(
            "data", inplace=True
        )  # Garante que o gráfico siga a linha do tempo.

    return dados


# -----------------------------------------------------------------------------------
# FUNÇÃO 3: ANÁLISE E INSIGHTS (DATA ANALYTICS)
# Explicação para Apresentação:
# "Aqui transformamos dados em informação. Calculamos a inflação dos combustíveis
# no período e identificamos picos históricos de variação (volatilidade)."
# -----------------------------------------------------------------------------------
def analiseDados(dados):
    if dados is None:
        return

    print("Gerando indicadores e visualizações...")

    # Métrica de Preço Médio (Simplificada para a análise)
    dados["gasolina_media"] = (
        dados["gasolina_comum_preco_revenda_min"]
        + dados["gasolina_comum_preco_revenda_max"]
    ) / 2
    dados["diesel_media"] = (
        dados["oleo_diesel_preco_revenda_min"] + dados["oleo_diesel_preco_revenda_max"]
    ) / 2

    # Insight 1: Aumento Acumulado
    # "Mostramos o quanto o preço mudou do primeiro registro até o último disponível no dataset."
    aumento_gasolina = (
        dados["gasolina_media"].iloc[-1] - dados["gasolina_media"].iloc[0]
    )
    aumento_diesel = dados["diesel_media"].iloc[-1] - dados["diesel_media"].iloc[0]

    print(f"\n--- RESUMO DO PERÍODO ---")
    print(f"Aumento total acumulado Gasolina: R$ {aumento_gasolina:.2f}")
    print(f"Aumento total acumulado Diesel:   R$ {aumento_diesel:.2f}")

    # Insight 2: Volatilidade (Uso do .diff() do Pandas)
    # "Calculamos a variação mês a mês. Isso ajuda a identificar momentos de crise ou choques de preço."
    dados["var_gasolina"] = dados["gasolina_media"].diff()
    dados["var_diesel"] = dados["diesel_media"].diff()

    # Insight 3: Picos Históricos
    print("\n--- PICOS DE VARIAÇÃO MENSAL ---")
    idx_max_gas = dados["var_gasolina"].idxmax()
    print(
        f"Maior alta Gasolina: {dados.loc[idx_max_gas, 'data'].strftime('%m/%Y')} (R$ {dados.loc[idx_max_gas, 'var_gasolina']:.2f})"
    )

    idx_max_die = dados["var_diesel"].idxmax()
    print(
        f"Maior alta Diesel:   {dados.loc[idx_max_die, 'data'].strftime('%m/%Y')} (R$ {dados.loc[idx_max_die, 'var_diesel']:.2f})"
    )

    # VISUALIZAÇÃO FINAL:
    # "O gráfico de linha é a melhor escolha para séries temporais pois mostra claramente
    # a tendência de alta e a correlação entre os dois combustíveis."
    plt.figure(figsize=(12, 6))
    plt.plot(
        dados["data"],
        dados["gasolina_media"],
        label="Gasolina Comum",
        color="#3498db",
        linewidth=2,
    )
    plt.plot(
        dados["data"],
        dados["diesel_media"],
        label="Óleo Diesel",
        color="#e67e22",
        linewidth=2,
    )

    plt.title("Histórico de Preços de Combustíveis no Brasil (Revenda)", fontsize=14)
    plt.ylabel("Preço Médio (R$)", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()
    
    # ORGANIZAÇÃO DE SAÍDA:
    # "Criamos uma pasta de output para manter a raiz do projeto limpa e organizada."
    os.makedirs('output', exist_ok=True)
    caminho_grafico = os.path.join('output', 'evolucao_precos.png')
    plt.savefig(caminho_grafico)
    print(f"\nVisualização exportada: '{caminho_grafico}' está pronto para ser projetado!")


# -----------------------------------------------------------------------------------
# EXECUÇÃO (MAIN LOOP)
# -----------------------------------------------------------------------------------
if __name__ == "__main__":
    df_cru = carregarArquivo("combustiveis-brasil.csv")
    if df_cru is not None:
        df_limpo = tratamentoArquivo(df_cru)
        analiseDados(df_limpo)
