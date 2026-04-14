# Análise de Preços de Combustíveis no Brasil

Este projeto realiza a coleta, tratamento e análise exploratória de dados sobre os preços de combustíveis no Brasil, utilizando a biblioteca `kagglehub` para baixar os datasets diretamente do Kaggle e `matplotlib` para visualização.

## 🚀 Como Executar o Projeto

Siga os passos abaixo para configurar o ambiente e rodar a análise.

### 1. Pré-requisitos

Certifique-se de ter o **Python 3.10+** instalado em sua máquina.

### 2. Configurar o Ambiente Virtual (venv)

Recomenda-se o uso de um ambiente virtual para isolar as dependências do projeto.

No terminal, na raiz do projeto, execute:

```bash
# Criar o ambiente virtual
python -m venv .venv
```

Agora, ative o ambiente virtual:

- **Linux/macOS:**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell):**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```

### 3. Instalar Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 4. Executar a Análise

Para rodar o script principal:

```bash
python main.py
```

## 📊 Funcionalidades e Análises

O script `main.py` está estruturado em funções para garantir a organização do fluxo de dados:

1.  **Carga de Dados:** Download automático do dataset `combustiveis-brasil.csv` via `kagglehub`.
2.  **Tratamento:** Limpeza de nulos, normalização de colunas e criação de séries temporais.
3.  **Análise Estatística:**
    *   Cálculo da média de preços de revenda (Mín/Máx).
    *   Aumento total acumulado no período.
    *   Identificação dos meses com maior e menor variação de preços.
4.  **Visualização:** Geração de um gráfico de linha comparativo entre Gasolina e Diesel, salvo automaticamente como `evolucao_precos.png`.

## 📂 Dados Utilizados

O projeto consome o dataset [fidelissauro/combustiveis-brasil](https://www.kaggle.com/datasets/fidelissauro/combustiveis-brasil) via `kagglehub`.

---
