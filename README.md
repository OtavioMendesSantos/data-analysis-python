# Análise de Preços de Combustíveis no Brasil

Este projeto realiza a coleta e análise exploratória de dados sobre os preços de combustíveis no Brasil, utilizando a biblioteca `kagglehub` para baixar os datasets diretamente do Kaggle.

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

- **Windows (CMD):**

  ```cmd
  .\.venv\Scripts\activate.bat
  ```

### 3. Instalar Dependências

Com o ambiente virtual ativo, instale as bibliotecas necessárias:

```bash
pip install -r requirements.txt
```

### 4. Executar a Análise

Para rodar o script principal e visualizar os primeiros registros dos dados de combustíveis:

```bash
python main.py
```

## 📊 Dados Utilizados

O projeto consome o dataset [fidelissauro/combustiveis-brasil](https://www.kaggle.com/datasets/fidelissauro/combustiveis-brasil) via `kagglehub`.

---
