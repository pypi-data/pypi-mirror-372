import io
import os
from typing import Optional

import pandas as pd
import sqlalchemy
from azure.storage.blob import BlobClient, BlobServiceClient

from ..common.jragbeer_common_data_eng import dagster_logger, data_path


def adls_upload_folder(
    directory: str = data_path, file_search_string: Optional[str] = None
) -> None:
    """
    This function uploads each file in the specified directory to ADLS.
    :param directory: the directory with the files
    :param file_search_string: a string used to filter the files in the directory
    :return: None
    """
    if file_search_string:
        file_list = [i for i in os.listdir(directory) if file_search_string in i]
    else:
        file_list = [i for i in os.listdir(directory)]

    for each_file in file_list:
        adls_upload_file(directory + each_file, each_file)


def adls_upload_file(file_path: str, blob_name: str = "blob_path_or_name") -> None:
    """
    This function uploads a file to ADLS.
    :param file_path: The path of the file.
    :param blob_name: The name of the file in ADLS
    :return: None
    """
    with open(file_path, "rb") as file_to_upload:
        blob_service_client = BlobServiceClient.from_connection_string(
            os.getenv("adls_connection_string")
        )
        # Instantiate a new ContainerClient
        container_client = blob_service_client.get_container_client(os.getenv("adls_container_name"))
        # Instantiate a new BlobClient
        blob_client = container_client.get_blob_client(blob_name)
        # upload data
        blob_client.upload_blob(file_to_upload, blob_type="BlockBlob", overwrite=True)
        dagster_logger.info(f"""{blob_name} is uploaded to BLOB storage (container: {os.getenv("adls_container_name")})""")


def adls_upload_sql_table(
    engine: sqlalchemy.engine.base.Engine,
    table_name: str = "name_of_sql_table",
) -> None:
    """
    This function reads a table in the database and then outputs it as a file in ADLS.
    :param engine: the SQL Alchemy engine
    :param table_name: the name of the table in SQL
    :return:
    """
    df = pd.read_sql(f"select * from {table_name} ", engine)
    output = df.to_parquet()
    blob = BlobClient.from_connection_string(
        os.getenv("adls_connection_string"), container_name=os.getenv("adls_container_name"), blob_name=table_name
    )
    blob.upload_blob(
        output,
        overwrite=True,
    )
    dagster_logger.info(
        f"""Latest {table_name} is uploaded to BLOB storage (container: {os.getenv("adls_container_name")})"""
    )


def adls_upload_df(
    idf_: pd.DataFrame,
    blob_name: str = "name_of_blob",
    container_name: str = os.getenv("adls_container_name", "adls_container_name"),
) -> None:
    """
    This function takes a dataframe and converts all columns to ADLS friendly data types and then uploads it to ADLS.
    :param df: the dataframe to be uploaded
    :param blob_name: the name of the output file in ADLS
    :return: None
    """
    for col_type, col_name in zip(idf_.dtypes, idf_.columns):
        if col_type == "object":
            idf_[col_name] = idf_[col_name].astype(str)
            idf_[col_name] = [i[:4000] for i in idf_[col_name]]
    output = (
        idf_.reset_index(drop=True)
        .drop_duplicates()
        .replace({"nan": None})
        .to_parquet(index=False)
    )
    blob = BlobClient.from_connection_string(
        os.getenv("adls_connection_string"),
        container_name=str(container_name).lower(),
        blob_name=blob_name,
    )
    blob.upload_blob(
        output,
        overwrite=True,
        timeout=14400,
        connection_timeout=14400,
    )
    dagster_logger.info(
        f"Latest {blob_name} is uploaded to BLOB storage (container: {container_name})"
    )

def adls_download_parquet_file(blob_name: str, input_container_name : str = os.getenv("adls_container_name", "adls_container_name")) -> pd.DataFrame:
    """
    This function downloads a parquet file from ADLS.
    @param blob_name: the name of the blob inside of ADLS
    @return: the dataframe that's downloaded
    """
    blob = BlobClient.from_connection_string(
        os.getenv("adls_connection_string"), container_name=input_container_name, blob_name=blob_name
    )
    # if there's a file that exists in the BLOB
    if blob.exists():
        # Download blob as StorageStreamDownloader object (stored in memory)
        downloaded_blob = blob.download_blob()
        # check if we can read the parquet file, if we can't probably not a parquet file
        try:
            bytes_io = io.BytesIO(downloaded_blob.readall())
            idf = pd.read_parquet(bytes_io)
            return idf
        except Exception:
            dagster_logger.info("Reading BLOB did not work.")
def adls_download_text_file(blob_name: str, input_container_name : str = os.getenv("adls_container_name", "adls_container_name"), save_file:Optional[str]=None) -> Optional[str]:
    """
    This function downloads a parquet file from ADLS.
    @param blob_name: the name of the blob inside of ADLS
    @return: str of the text file
    """
    blob = BlobClient.from_connection_string(
        os.getenv("adls_connection_string", "adls_connection_string"), container_name=input_container_name, blob_name=blob_name
    )
    # if there's a file that exists in the BLOB
    text_data = None
    if blob.exists():
        # Download blob as StorageStreamDownloader object (stored in memory)
        downloaded_blob = blob.download_blob()
        # check if we can read the parquet file, if we can't probably not a parquet file
        try:
            text_data = downloaded_blob.readall().decode("utf-8")
            if save_file:
                with open(save_file, 'w') as f:
                    f.write(text_data)
            return text_data
        except Exception:
            dagster_logger.info("Reading BLOB did not work.")
            return text_data
    return text_data
def adls_replace_nans_with_nulls_in_dfs() -> None:
    """
    Get all of the blobs in the main container and convert the 'nan's in them to None. Then reupload the blob.
    @return: None
    """
    blob_svc = BlobServiceClient.from_connection_string(conn_str=os.getenv("adls_connection_string"))
    dagster_logger.info("\nList blobs in the container")
    container_client = blob_svc.get_container_client(os.getenv("adls_container_name"))
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        if blob.name.endswith(".parquet"):
            try:
                dagster_logger.info(blob.name)
                pdf = adls_download_parquet_file(blob.name)
                adls_upload_df(pdf, blob.name)
            except Exception as ee:
                dagster_logger.info(ee)
