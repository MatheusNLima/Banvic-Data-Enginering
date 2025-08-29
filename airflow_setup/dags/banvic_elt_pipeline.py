import logging
import pendulum
import os
from datetime import timedelta
from typing import List

from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.operators.empty import EmptyOperator

logger = logging.getLogger(__name__)

SOURCE_CONN_ID = "postgres_banvic_source"
DW_CONN_ID = "postgres_data_warehouse"
DATA_LAKE_PATH = "/opt/airflow/data_lake"
POSTGRES_TABLES: List[str] = [
    "agencias",
    "clientes",
    "colaborador_agencia",
    "colaboradores",
    "contas",
    "propostas_credito",
]

@dag(
    dag_id="banvic_elt_pipeline",
    start_date=pendulum.datetime(2025, 8, 26, tz="UTC"),
    schedule="35 4 * * *",
    catchup=True,
    tags=["banvic", "data-engineering-challenge"],
    default_args={"owner": "airflow", "retries": 2, "retry_delay": timedelta(minutes=5)},
)
def banvic_elt_pipeline():
    start = EmptyOperator(task_id="start")

    @task
    def extrair_tabelas_postgres(**kwargs) -> str:
        data_execucao = kwargs["ds_nodash"]
        hook = PostgresHook(postgres_conn_id=SOURCE_CONN_ID)
        pasta_saida = os.path.join(DATA_LAKE_PATH, data_execucao, "postgres")
        os.makedirs(pasta_saida, exist_ok=True)

        for tabela in POSTGRES_TABLES:
            caminho = os.path.join(pasta_saida, f"{tabela}.csv")
            try:
                hook.copy_expert(sql=f"COPY {tabela} TO STDOUT WITH CSV HEADER", filename=caminho)
                logger.info("Extraído %s para %s", tabela, caminho)
            except Exception:
                logger.exception("Falha ao extrair tabela %s", tabela)
                raise

        return pasta_saida

    @task
    def extrair_csv_transacoes(**kwargs) -> str:
        data_execucao = kwargs["ds_nodash"]
        origem = "/opt/airflow/data_source/transacoes.csv"
        pasta_saida = os.path.join(DATA_LAKE_PATH, data_execucao, "csv")
        os.makedirs(pasta_saida, exist_ok=True)
        destino = os.path.join(pasta_saida, "transacoes.csv")
        import shutil

        if not os.path.exists(origem):
            logger.error("Arquivo de transacoes nao encontrado: %s", origem)
            raise FileNotFoundError(origem)

        shutil.copy(origem, destino)
        logger.info("Arquivo de transacoes copiado para %s", destino)
        return pasta_saida
    @task
    def carregar_para_dw(pasta_postgres: str, pasta_csv: str) -> None:
        hook = PostgresHook(postgres_conn_id=DW_CONN_ID)
        pastas = [pasta_postgres, pasta_csv]

        for pasta in pastas:
            if not os.path.isdir(pasta):
                logger.warning("Pasta nao existe, pulando: %s", pasta)
                continue
            for nome_arquivo in os.listdir(pasta):
                if nome_arquivo.endswith(".csv"):
                    caminho = os.path.join(pasta, nome_arquivo)
                    tabela = os.path.splitext(nome_arquivo)[0]
                    try:
                        hook.copy_expert(
                            sql=f"TRUNCATE TABLE {tabela}; COPY {tabela} FROM STDIN WITH CSV HEADER",
                            filename=caminho,
                        )
                        logger.info("Carregado %s para %s", caminho, tabela)
                    except Exception:
                        logger.exception("Falha ao carregar %s para a tabela %s", caminho, tabela)
                        raise

    end = EmptyOperator(task_id="end")

    tarefa_postgres = extrair_tabelas_postgres()
    tarefa_csv = extrair_csv_transacoes()
    tarefa_carga = carregar_para_dw(tarefa_postgres, tarefa_csv)

    start >> [tarefa_postgres, tarefa_csv] >> tarefa_carga >> end

dag_instance = banvic_elt_pipeline()