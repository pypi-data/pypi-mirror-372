import datetime
import os
import subprocess
from typing import Optional

import numpy as np
import pandas as pd
import sqlalchemy
from tqdm import tqdm

from ..azure.jragbeer_common_azure import adls_upload_file
from ..common.jragbeer_common_data_eng import (dagster_logger, data_path,
                                               error_handling, today)
from ..dask.jragbeer_common_dask import process_list_with_dask
from ..ubuntu.jragbeer_common_ubuntu import execute_cmd_ubuntu_sudo, execute_cmd_ubuntu_normal

# MYSQL
def mysql_create_database(host, port, username, password, database_name):
    """
    Create a MySQL database using the mysqladmin command.

    Args:
        host (str): The MySQL server hostname or IP address.
        port (int): The MySQL server port.
        username (str): The MySQL username for authentication.
        password (str): The MySQL password for authentication.
        database_name (str): The name of the database to be created.

    Returns:
        bool: True if the database is created successfully, False otherwise.
    """
    try:
        # Construct the mysqladmin command to create the database
        cmd = [
            "/bin/mysqladmin",
            f"--host={host}",
            f"--port={port}",
            f"--user={username}",
            f"--password={password}",
            "create",
            database_name,
        ]

        # Use subprocess.Popen to execute the command
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            print(f"Database '{database_name}' created successfully.")
            return True
        else:
            print(f"Error creating database '{database_name}': {stderr.decode()}")
            return False
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
def mysql_backup_database(database_name: str):
    dagster_logger.info(f"{database_name} dump starting now")
    t = [r"mysqldump", rf"-h{os.getenv('local_db_address')}", rf"-u{os.getenv('local_db_username')}",
         rf"-p{os.getenv('local_db_password')}",
         rf"{database_name}", rf"--result-file={data_path + database_name}_dump_latest.sql"]
    print(t)
    execute_cmd_ubuntu_sudo(t)
    dagster_logger.info(f"{database_name} complete in {datetime.datetime.now() - today} ")
def mysql_import_dump(host, port, username, password, database_name, dump_file_path):
    """
    Imports a MySQL database dump into a specified database.

    Args:
        host (str): The MySQL server hostname or IP address.
        port (int): The MySQL server port.
        username (str): The MySQL username for authentication.
        password (str): The MySQL password for authentication.
        database_name (str): The name of the database where the dump will be imported.
        dump_file_path (str): The path to the MySQL dump file to import.

    Returns:
        bool: True if the import was successful, False otherwise.
    """
    try:
        # Construct the MySQL command to import the dump
        cmd = [
            "/bin/mysql",
            f"--host={host}",
            f"--port={port}",
            f"--user={username}",
            f"--password={password}",
            f"--database={database_name}",
            "--execute=source " + dump_file_path,
        ]

        # Execute the command
        subprocess.run(cmd, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error importing MySQL dump: {e}")
        return False
def mysql_restore_databases():
    for finance_db in [
        "finance_1mins",
        "finance_5mins",
        "finance_daily",
        "finance_fundamental_data",
        "finance_standard",
        "gov",
        "home",
                       ]:
        try:
            success = mysql_create_database(host="localhost",
                                            port=3306,
                                            username=os.getenv('local_db_username'),
                                            password=os.getenv('local_db_password'),
                                            database_name=finance_db,
                                            )
            if success:
                print(f"Database '{finance_db}' created successfully.")
            else:
                print(f"Failed to create database '{finance_db}'.")
        except Exception:
            pass
        try:
            dagster_logger.info(f"{finance_db} restore starting now")
            success = mysql_import_dump(host="localhost",
                                            port=3306,
                                            username=os.getenv('local_db_username'),
                                            password=os.getenv('local_db_password'),
                                            database_name=finance_db,
                                            dump_file_path=f"{data_path.replace('/','//') + finance_db}_dump_latest.sql"
                                            )
            dagster_logger.info(f"{finance_db} complete in {datetime.datetime.now() - today} ")
            if success:
                print(f"Database '{finance_db}' successfully imported.")
            else:
                print(f"Failed to import database '{finance_db}'.")
        except Exception:
            pass

# POSTGRES
def postgres_query_to_remove_duplicate_rows(table_name:str, conn_string:str):
    sql_query = f"""
            WITH cte AS (
            SELECT
                ctid,  -- PostgreSQL's unique row identifier
                ROW_NUMBER() OVER (PARTITION BY * ORDER BY ctid) AS rn
            FROM {table_name}
        )
        DELETE FROM {table_name}
        WHERE ctid IN (
            SELECT ctid FROM cte WHERE rn > 1
        );
    """
    print(sql_query)
    print(conn_string)

def pg_restore_database(sql_file_path: str, database_name:str,) -> None:
    """
    Uses `psql` to load a .sql file into a PostgreSQL database.
    Creates the database if it doesn't exist.

    1. Check if the database exists
    2. Load the SQL file

    Parameters:
    - sql_file_path (str): Path to the .sql file.
    - database_name (str): Database to create/use.

    Returns:
        None
    """
    if not os.path.exists(sql_file_path):
        raise FileNotFoundError(f"SQL file not found: {sql_file_path}")

    user = os.getenv('local_db_username')
    password = os.getenv('local_db_password')
    host = os.getenv('local_db_address')
    port = os.getenv('local_db_port')
    print(host)

    # Step 1: Load the SQL file
    print(f"Running SQL file '{sql_file_path}' into database '{database_name}'...")
    run_sql_cmd = [rf"PGPASSWORD={password}",
        "psql",
        "-U", user,
        "-h", host,
        "-p", str(port),
        "-d", database_name,
        "-f", sql_file_path
    ]
    execute_cmd_ubuntu_sudo(run_sql_cmd)
    print("SQL file executed successfully.")

def pg_backup_database(database_name: str, host:str, password:str, user:str, port:str, file_location:str = "/home/jay/PycharmProjects/jragbeer_home/data/") -> None:
    """
    Creates a backup (dump) of a PostgreSQL database and saves it to a .sql file.

    This function uses `pg_dump` to export the specified PostgreSQL database to a SQL dump file,
    saving the output to a path constructed as `{data_path}{database_name}_dump_latest.sql`.

    Environment Variables Required:
    - local_db_address: the hostname or IP address of the PostgreSQL server
    - local_db_username: the username for authentication
    - local_db_password: the password for authentication (used via PGPASSWORD)

    Args:
        database_name (str): The name of the PostgreSQL database to back up.
        host (str): The hostname or IP address of the PostgreSQL server
        password (str): The password for the PostgreSQL user
        user (str): The username for the PostgreSQL user
        port (str): The port for the PostgreSQL server

    Logs:
        - Start and completion time of the dump process.
    """
    dagster_logger.info(f"{database_name} dump starting now")

    t = [rf"PGPASSWORD={password}",
        "pg_dump",
        rf"-h{host}",
        rf"-U{user}",
        rf"-d{database_name}",
        rf"-p{port}",
        rf"-f{file_location}pg_{database_name}_dump_latest.sql"
    ]
    dagster_logger.info(t)
    output = execute_cmd_ubuntu_sudo(t)
    if not output:
        dagster_logger.info(f"{database_name} dump failed with SUDO.")
        dagster_logger.info(error_handling())
        execute_cmd_ubuntu_normal(t)
    dagster_logger.info(f"{database_name} completed in {datetime.datetime.now() - today} ")

def sql_table_drop_duplicates_single(new_engine: sqlalchemy.Engine, table_name:str) -> None:
    """
    This function will drop duplicate tables using pandas.
    Args:
        new_engine: The sql engine of the database
        table_name: The name of the table to drop duplicates.

    Returns:
        None
    """
    try:
        tmp_df = pd.read_sql(f'select * from ``{table_name}``', new_engine)
    except Exception:
        try:
            tmp_df = pd.read_sql(f'select * from {table_name}', new_engine)
        except Exception:
            tmp_df = pd.read_sql(f'select * from ```{table_name}```', new_engine)

    print(f"\tTable has {len(tmp_df.index)} rows at start")
    try:
        tmp_df = tmp_df.sort_values('Datetime')
    except Exception:
        try:
            tmp_df = tmp_df.sort_values('Date')
        except Exception:
            pass
    try:
        tmp_df['Datetime'] = tmp_df['Datetime'].apply(lambda x: x.replace(tzinfo=None))
    except Exception:
        try:
            tmp_df['Date'] = tmp_df['Date'].apply(lambda x: x.replace(tzinfo=None))
        except Exception:
            pass
    tmp_df=tmp_df.drop_duplicates()
    print(f"\tTable has {len(tmp_df.index)} rows at end")

    tmp_df.to_sql(f"{table_name}", new_engine, index=False, if_exists='replace')
    print(f'{table_name} replaced')

def sql_table_drop_duplicates(list_of_table_names: list[str], connection_string: str | None =None, database:str | None =None) -> None:
    """
    This function will call the sql_table_drop_duplicates_single on each of the tables provided.
    Either the connection string or the database name must be provided.

    Args:
        list_of_table_names: The names of the tables to drop duplicates.
        connection_string (str): The connection string of the database. Defaults to None.
        database: The name of the database. Defaults to None.

    Returns:
        None
    """
    if connection_string:
        db_url = connection_string
    else:
        if not database:
            raise ValueError("either connection_string or database must be provided.")
        db_url = f"postgresql://{os.getenv('local_db_username')}:{os.getenv('local_db_password')}@{os.getenv('local_db_address')}:{os.getenv('local_db_port')}/{database}"
    new_engine = sqlalchemy.create_engine(db_url)
    print(new_engine)
    for ii, table_name in enumerate(tqdm(list_of_table_names)):
        print(ii, table_name)
        if ii % 25 == 0:
            dagster_logger.info(f'Dropping Duplicates on {table_name}')
        try:
            sql_table_drop_duplicates_single(new_engine, table_name)
        except Exception:
            dagster_logger.info(error_handling())

def db_drop_duplicates(database: str = '5mins', num_splits:int = 4 ) -> None:
    """
    This function will drop duplicates in tables in the database requested. It uses dask and parallel processing to
    split the tables in num_splits groups. Each group is processed by a core via dask.
    Args:
        database: The name of the database to drop duplicates for
        num_splits: The number of splits to use for splitting the data into for parallel processing

    Returns:
        None

    """
    # print time this function starts
    now = datetime.datetime.now()
    dagster_logger.info(now)
    db_url = f"postgresql://{os.getenv('local_db_username')}:{os.getenv('local_db_password')}@{os.getenv('local_db_address')}:{os.getenv('local_db_port')}/{database}"
    # flatten list of tables
    list_of_tables = get_all_sql_table_names(connection_string=db_url)
    process_list_with_dask(list_of_tables, sql_table_drop_duplicates, num_splits, 'distributed',
                           priority=2,
                           kwargs={"database":database})

def copy_backup_to_cloud(database_name: str, local_backup_folder:str) -> None:
    """
    This is a wrapper for adls_upload_file() function that sends the backup .sql file to the cloud storage bucket.
    Args:
        database_name: The name of the database to send to Azure
        local_backup_folder (str): The location of the folder where the backup will be stored
    Returns:
        None
    """
    dagster_logger.info(f"{database_name} migrating to BLOB")
    adls_upload_file(local_backup_folder + f"pg_{database_name}_dump_latest.sql", f"database_backups/{database_name}_dump_latest.sql")
    dagster_logger.info(f"{database_name} migration to BLOB complete.")

def backup_databases(databases:list[str], local_backup_folder:str, db: str ='postgres', host:str | None = None, port: int | str| None = None) -> None:
    """
    This function is used to backup the databases. It runs the backup_database() function and then uploads the backup to
    the Azure Blob Storage bucket.

    Args:
        databases (list[str]): The names of the databases to backup.
        db (str): The name of the database type.
        local_backup_folder (str): The location of the folder where the backup will be stored
        host (str): The hostname/address of the local db to backup

    Returns: None

    """
    if not host:
        host = os.getenv("local_db_address")
    password = os.getenv("local_db_password")
    user = os.getenv('local_db_username')
    if not port:
        port = os.getenv("local_db_port")
    else:
        port = str(port)

    for db_name in databases:

        if db == 'mysql':
            mysql_backup_database(db_name)
        else:
            pg_backup_database(db_name, host=host, password=password, user=user, port = port, file_location=local_backup_folder)
        copy_backup_to_cloud(db_name, local_backup_folder)

def get_all_sql_table_names(user=None, hostname=None, password=None, port=None, database=None,
                            connection_string=None) -> list[str]:
    """
    This function returns a list of all SQL table names in the database. It uses sqlalchemy.

    Args:
        user: The username of the database.
        hostname: The hostname of the database.
        password: The password for the database user.
        port: The port to use.
        database: The name of the database to use.
        connection_string: The connection string.

    Returns:
        list: The list of SQL table names.
    """
    if connection_string:
        db_url = connection_string
    else:
        # Build the database URL
        if not all([user, hostname, password, port, database]):
            raise ValueError(
                f"Not all of user={user}, hostname={hostname}, password={password}, port={port}, database={database} are filled.")
        db_url = f"postgresql://{user}:{password}@{hostname}:{port}/{database}"

    # Create a SQLAlchemy engine
    engine = sqlalchemy.create_engine(db_url)

    # Reflect the tables
    metadata = sqlalchemy.MetaData()
    metadata.reflect(bind=engine)

    # Get the table names
    table_names = list(metadata.tables.keys())

    # Close the engine connection
    engine.dispose()
    return table_names


