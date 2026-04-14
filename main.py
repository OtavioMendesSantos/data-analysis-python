import kagglehub
import matplotlib.pyplot as plt  # Matplotlib é uma biblioteca de visualização de dados em Python. O módulo pyplot (apelidado de plt) é a parte que você usa para criar gráficos
import pandas as pd  # engenharia de dados
from kagglehub import KaggleDatasetAdapter


# carregar o arquivo usando kagglehub
def carregarArquivo(nomeArquivo):
    print(f"carga de arquivo: {nomeArquivo} via kagglehub")
    dados = None
    try:
        # Carregando a última versão utilizando a função atualizada
        dados = kagglehub.dataset_load(
            KaggleDatasetAdapter.PANDAS,
            "fidelissauro/combustiveis-brasil",
            nomeArquivo,
        )

        # Normalização básica de nomes de colunas (removendo acentos e convertendo para minúsculas)
        # para garantir compatibilidade com o código de tratamento
        dados.columns = (
            dados.columns.str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("utf-8")
            .str.lower()
        )

    except Exception as e:
        print(f"Não foi possivel carregar o arquivo: {e}")

    return dados


# tratamento do arquivo
def tratamentoArquivo(dados):
    if dados is None:
        return None

    print("tratamento do arquivo")

    # descricao basica do arquivo
    print(dados.info())
    print(dados.head())
    print(dados.tail())
    print(dados.describe())

    # manter somente as colunas desejadas
    # nota: nomes de colunas já foram normalizados para minúsculas em carregarArquivo
    colunas_desejadas = [
        "ano",
        "mes",
        "gasolina_comum_preco_revenda_min",
        "gasolina_comum_preco_revenda_max",
        "oleo_diesel_preco_revenda_min",
        "oleo_diesel_preco_revenda_max",
    ]

    # Verifica se as colunas existem antes de filtrar
    colunas_presentes = [col for col in colunas_desejadas if col in dados.columns]
    dados = dados[colunas_presentes]

    # remover nulos
    dados.dropna(inplace=True)

    # criar coluna de data
    if "ano" in dados.columns and "mes" in dados.columns:
        # Criar um DataFrame auxiliar para garantir a compatibilidade com pd.to_datetime
        df_data = pd.DataFrame({"year": dados["ano"], "month": dados["mes"], "day": 1})
        dados["data"] = pd.to_datetime(df_data)

        # ordenar
        dados.sort_values("data", inplace=True)

    print(dados.info())
    print(dados.shape)

    return dados


# analise de dados
def analiseDados(dados):
    if dados is None:
        return

    print("analise do arquivo")

    # criar média dos preços
    dados["gasolina_media"] = (
        dados["gasolina_comum_preco_revenda_min"]
        + dados["gasolina_comum_preco_revenda_max"]
    ) / 2

    dados["diesel_media"] = (
        dados["oleo_diesel_preco_revenda_min"] + dados["oleo_diesel_preco_revenda_max"]
    ) / 2

    # crescimento total
    aumento_gasolina = (
        dados["gasolina_media"].iloc[-1] - dados["gasolina_media"].iloc[0]
    )
    aumento_diesel = dados["diesel_media"].iloc[-1] - dados["diesel_media"].iloc[0]

    print(f"Aumento total gasolina: {aumento_gasolina:.2f}")
    print(f"Aumento total diesel: {aumento_diesel:.2f}")

    # variação mês a mês
    dados["var_gasolina"] = dados["gasolina_media"].diff()
    dados["var_diesel"] = dados["diesel_media"].diff()

    # maior e menor aumento
    print("\nGasolina:")
    print(dados.loc[dados["var_gasolina"].idxmax()][["data", "var_gasolina"]])
    print(dados.loc[dados["var_gasolina"].idxmin()][["data", "var_gasolina"]])

    print("\nDiesel:")
    print(dados.loc[dados["var_diesel"].idxmax()][["data", "var_diesel"]])
    print(dados.loc[dados["var_diesel"].idxmin()][["data", "var_diesel"]])

    # gráfico
    plt.figure(figsize=(12, 6))
    plt.plot(dados["data"], dados["gasolina_media"], label="Gasolina")
    plt.plot(dados["data"], dados["diesel_media"], label="Diesel")

    plt.title("Evolução dos preços (Gasolina vs Diesel)")
    plt.xlabel("Data")
    plt.ylabel("Preço (R$)")
    plt.legend()
    plt.xticks(rotation=45)

    plt.tight_layout()
    # plt.show() # Removido para execução em ambiente CLI, mas mantido como comentário
    plt.savefig("evolucao_precos.png")
    print("\nGráfico salvo como 'evolucao_precos.png'")


# Fluxo principal
if __name__ == "__main__":
    dados = carregarArquivo("combustiveis-brasil.csv")
    # CSVs disponíveis: "combustiveis-estados.csv", "combustiveis-regioes.csv", "combustiveis-brasil.csv"
    if dados is not None:
        dados = tratamentoArquivo(dados)
        analiseDados(dados)
