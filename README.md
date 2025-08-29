# Banvic-Data-Enginering
Passo 1: Criar o Arquivo
Dentro da pasta principal do seu projeto (banvic_challenge), crie um novo arquivo de texto e nomeie-o exatamente como README.md.
Passo 2: Adicionar o Conteúdo
Copie e cole todo o texto abaixo para dentro do seu arquivo README.md. Ele está formatado e pronto. A única coisa que você talvez queira mudar é a primeira linha, para adicionar seu nome se desejar.
# Desafio de Engenharia de Dados - BanVic por Matheus Nunes Lima

## Visão Geral do Projeto

Este projeto implementa um pipeline de dados ELT (Extract, Load, Transform) que atende aos requisitos do desafio BanVic. O pipeline é responsável por extrair dados de duas fontes distintas, armazená-los em um Data Lake local e carregá-los em um Data Warehouse PostgreSQL. Todo o processo é orquestrado pelo Apache Airflow e totalmente containerizado com Docker para garantir a reprodutibilidade.

A arquitetura segue o fluxo abaixo:
1.  **Extração Paralela:** Dados de 6 tabelas de um banco PostgreSQL e de um arquivo CSV de transações são extraídos simultaneamente.
2.  **Armazenamento em Data Lake:** Os dados extraídos são salvos no sistema de arquivos local no formato CSV, seguindo a convenção de nomenclatura `YYYYMMDD/<fonte>/<tabela>.csv`.
3.  **Carregamento no Data Warehouse:** Após a conclusão bem-sucedida de todas as extrações, os arquivos CSV são carregados nas tabelas de destino em um Data Warehouse PostgreSQL. As tabelas são truncadas antes da carga para garantir a idempotência.

## Pré-requisitos
*   Docker
*   Docker Compose V2

## Como Executar o Projeto

Siga os passos abaixo para configurar e executar o ambiente completo.

### 1. Iniciar o Banco de Dados de Origem
Navegue até a pasta `source_db` no seu terminal e execute:
docker compose up -d
Este comando iniciará um container PostgreSQL na porta 55432 da sua máquina, simulando o banco de dados de produção do BanVic.

2. Iniciar o Ambiente Airflow e o Data Warehouse
Em um novo terminal, navegue até a pasta airflow_setup e execute:


docker compose up -d
Este comando iniciará todos os serviços do Airflow e o Data Warehouse. Aguarde cerca de 2-3 minutos para que todos os containers iniciem e se estabilizem.
Nota: As conexões do Airflow (postgres_banvic_source e postgres_data_warehouse) são criadas automaticamente através de variáveis de ambiente definidas no docker-compose.yaml.

3. Preparar o Data Warehouse
Para que o pipeline possa carregar os dados, as tabelas de destino precisam existir.
Use um cliente de banco de dados (como DBeaver ou pgAdmin) para se conectar ao Data Warehouse usando as seguintes credenciais:
Host: localhost
Porta: 5433
Banco de Dados: data_warehouse
Usuário: dw_user
Senha: dw_password
Abra o arquivo airflow_setup/sql/create_tables.sql.
Copie e execute todo o conteúdo do script no seu cliente de banco de dados. Isso criará as tabelas vazias no DW.

4. Executar o Pipeline no Airflow
Acesse a interface web do Airflow no seu navegador: http://localhost:8080.
Faça login com:
Usuário: airflow
Senha: airflow
Na lista de DAGs, encontre banvic_elt_pipeline.
Ative a DAG clicando no botão de toggle à esquerda do nome.
Para iniciar uma execução, clique no botão "Play" (▶️) à direita.
Verificando os Resultados
Após a execução bem-sucedida da DAG:
Data Lake: Os arquivos CSV extraídos estarão na pasta airflow_setup/data_lake/, organizados por data.
Data Warehouse: Conecte-se ao banco de dados na porta 5433 e verifique que as tabelas (ex: public.clientes, public.transacoes) agora contêm dados.
