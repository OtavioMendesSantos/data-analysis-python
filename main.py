import kagglehub
from kagglehub import KaggleDatasetAdapter

file_path = "combustiveis-brasil.csv"  

# [link dataset](https://www.kaggle.com/datasets/fidelissauro/combustiveis-brasil?select=combustiveis-estados.csv)

# CSV's disponíveis
# "combustiveis-estados.csv" 
# "combustiveis-regioes.csv"
# "combustiveis-brasil.csv"


df = kagglehub.dataset_load(
    KaggleDatasetAdapter.PANDAS,
    "fidelissauro/combustiveis-brasil",
    file_path,
)

print("Primeiros 5 registros:\n", df.head())