from pyspark.sql import DataFrame
import pandas as pd
from google.cloud import bigquery

def spark_to_bigquery(spark_df, table_name, project_id="pcb-prod-pds",
                      dataset="PCMC_PORTFOLIO", mode="overwrite"):
    """
    Transfers a PySpark DataFrame to a BigQuery table.

    :param spark_df: The PySpark DataFrame to write.
    :type spark_df: pyspark.sql.DataFrame
    :param table_name: The name of the BigQuery table.
    :type table_name: str
    :param project_id: The Google Cloud project ID.
    :type project_id: str
    :param dataset: The BigQuery dataset name.
    :type dataset: str
    :param mode: Write mode ('overwrite' or 'append').
    :type mode: str
    """
    
    full_table_id = "{}.{}.{}".format(project_id, dataset, table_name)

    (spark_df.write
        .format("bigquery")
        .mode(mode)
        .option("table", full_table_id)
        .option("temporaryGcsBucket", "sas-pcbpds-in")
        .option("writeDisposition", "WRITE_TRUNCATE" if mode == "overwrite" else "WRITE_APPEND")
        .save())

    print("{}D {} in BigQuery table {}".format(mode.capitalize(), table_name, full_table_id))


def bq_to_pd_df(project_id, dataset, table_name):
    client = bigquery.Client(project=project_id)
    query=f"""
    SELECT * FROM `{project_id}.{dataset}.{table_name}`
    """
    df = client.query(query).to_dataframe()
    return df