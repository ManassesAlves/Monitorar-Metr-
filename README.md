# 🚇 Monitor Metrô SP - Agente de Vigilância & ETL

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)
![GitHub Actions](https://img.shields.io/badge/GitHub_Actions-Automation-2088FF?style=for-the-badge&logo=github-actions)
![Telegram](https://img.shields.io/badge/Telegram-Bot_API-2CA5E0?style=for-the-badge&logo=telegram)
![Status](https://img.shields.io/badge/Status-Operational-green?style=for-the-badge)

Este projeto consiste em um **agente autônomo** que monitora em tempo real a situação das linhas do Metrô e CPTM de São Paulo. Ele opera 100% na nuvem (Serverless) utilizando **GitHub Actions**, sem custo de infraestrutura.

O sistema verifica mudanças de status, notifica instantaneamente via **Telegram** e armazena um histórico detalhado em **CSV** para futuras análises de dados (BI).

---

## ⚙️ Funcionalidades

* **📡 Monitoramento Contínuo:** Consulta a API do *Direto dos Trens* em intervalos programados (Cron Job).
* **🔔 Alerta Inteligente:** Envia notificações no Telegram apenas quando há alteração de status (ex: de "Normal" para "Velocidade Reduzida").
* **📝 Descrição Detalhada:** A notificação inclui o motivo da falha (ex: "Interferência na via", "Chuva"), se disponível.
* **💾 Engenharia de Dados (ETL):** Persistência de dados. Cada incidente é registrado automaticamente no arquivo `historico_metro.csv` para auditoria e análise estatística.
* **☁️ Arquitetura Serverless:** Roda inteiramente no GitHub Actions, utilizando persistência de estado via commit automático no próprio repositório.

---

## 🏗️ Arquitetura da Solução

O fluxo de dados segue a seguinte lógica:

1.  **Trigger:** O GitHub Actions inicia o workflow a cada X minutos.
2.  **Extração:** O script Python consulta a API pública de status.
3.  **Transformação & Comparação:**
    * Carrega o estado anterior salvo no JSON.
    * Compara com o estado atual.
4.  **Ação (Se houver mudança):**
    * Envia mensagem formatada para o Bot do Telegram.
    * Adiciona uma nova linha no Dataset histórico (`historico_metro.csv`).
5.  **Carga (Load):** Realiza um *commit* e *push* dos arquivos atualizados de volta para o repositório.

---

## 🛠️ Como Configurar

### Pré-requisitos
* Uma conta no GitHub.
* Um Bot no Telegram (criado via @BotFather).

### Passo a Passo

1.  **Clone este repositório:**
    ```bash
    git clone [https://github.com/ManassesAlves/Monitorar-Metro.git](https://github.com/ManassesAlves/Monitorar-Metro.git)
    ```
    *(Nota: Se o link acima der erro, verifique se o nome do repositório no navegador é exatamente Monitorar-Metro)*

2.  **Configure os Segredos (Secrets):**
    No seu repositório no GitHub, vá em `Settings` > `Secrets and variables` > `Actions` e adicione:
    * `TELEGRAM_TOKEN`: O token gerado pelo BotFather.
    * `TELEGRAM_CHAT_ID`: Seu ID numérico (ou do grupo) para receber as mensagens.

3.  **Ajuste a Frequência (Opcional):**
    No arquivo `.github/workflows/monitoramento.yml`, edite a linha do cron:
    ```yaml
    - cron: '*/15 * * * *' # Roda a cada 15 minutos
    ```

---

## 📊 Estrutura dos Dados Gerados

O arquivo `historico_metro.csv` é gerado automaticamente e serve como fonte para dashboards (Power BI / Excel).

| Data       | Hora     | Dia_Semana | Linha              | Status_Novo         | Status_Anterior | Descricao |
|:-----------|:---------|:-----------|:-------------------|:--------------------|:----------------|:----------|
| 2023-10-01 | 08:30:00 | Segunda    | Linha 3 - Vermelha | Velocidade Reduzida | Operação Normal | Chuva     |
| 2023-10-01 | 09:15:00 | Segunda    | Linha 3 - Vermelha | Operação Normal     | Velocidade Reduzida | -      |

---

## 🚀 Tecnologias Utilizadas

* **Python 3.9+**
* **Libs:** `requests`, `json`, `csv`, `os`, `datetime`
* **GitHub Actions** (CI/CD para automação)
* **Git** (Versionamento e persistência de estado)

---

## ⚠️ Aviso Legal

Este projeto utiliza a API pública do serviço **Direto dos Trens** para fins educacionais e de monitoramento pessoal. Todos os créditos dos dados pertencem aos mantenedores do serviço original.

---

**Desenvolvido por Manasses Alves**
