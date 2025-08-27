import os
import time
from pprint import pprint
from typing import Callable, Optional, Literal, Any

import dask
import pandas as pd
import paramiko  # type: ignore
import sqlalchemy
from dask.distributed import get_client

from ..common.jragbeer_common_data_eng import (dagster_logger, error_handling,
                                               path)
from ..ubuntu.jragbeer_common_ubuntu import (create_yaml_from_dict,
                                             execute_cmd_ubuntu_sudo,
                                             execute_script_with_cmd,
                                             get_remote_process_ids_ubuntu,
                                             give_write_permission_to_folder,
                                             kill_remote_ubuntu_process_ids)

CLUSTER_TYPE = Literal["SERIAL", "LOCAL", "DISTRIBUTED"]

def update_dask_environment_vars_local(env_dict):
    folder = "/etc/dask"
    execute_cmd_ubuntu_sudo(f"mkdir {folder}")
    give_write_permission_to_folder(folder)
    create_yaml_from_dict(env_dict, "/etc/dask/dask.yaml")

def create_dask_scheduler(hostname:str, username:str, password:str,) -> None:
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    command = (
        "docker exec finance_scheduler bash -c "
        "'cd /opt/dagster/app && "
        "source .venv/bin/activate && "
        "nohup dask scheduler --host 0.0.0.0 > /tmp/dask_scheduler.log 2>&1 &'"
    )

    stdin, stdout, stderr = ssh.exec_command(command)
    dagster_logger.info(f"stdin:{stdin} | stdout:{stdout} | stderr:{stderr}")
    dagster_logger.info(f"Dask Scheduler created on remote machine : {hostname}")

def create_dask_worker(hostname:str, username:str, password:str, scheduler_ip:str='localhost', nworkers: int=1, mem_limit : str = '1GB') -> None:
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    command = (
        "docker exec finance_scheduler bash -c "
        "'cd /opt/dagster/app && "
        "source .venv/bin/activate && "
        f"nohup dask worker tcp://{scheduler_ip}:8786 --nthreads 1 --nworkers {nworkers} --memory-limit {mem_limit} > /tmp/dask_worker.log 2>&1 &'"
    )
    stdin, stdout, stderr = ssh.exec_command(command)
    dagster_logger.info(f"stdin:{stdin} | stdout:{stdout} | stderr:{stderr}")
    dagster_logger.info(f"Dask Worker created on remote machine : {hostname} / {nworkers} workers with {mem_limit} mem. each")

def kill_and_redeploy_dask_home_setup() -> None:
    kill_dask_deployment_home_setup()
    time.sleep(10)
    deploy_dask_home_setup()

def deploy_dask_home_setup() -> None:
    create_dask_scheduler(hostname=os.getenv('cluster_server_1_address'), username=os.getenv('cluster_server_1_username'), password=os.getenv('cluster_server_1_password'),)

    # create worker 1, on same machine as scheduler
    create_dask_worker(hostname=os.getenv('cluster_server_1_address'), username=os.getenv('cluster_server_1_username'), password=os.getenv('cluster_server_1_password'),
                           scheduler_ip="localhost", nworkers=30, mem_limit = '3GB')
    # create worker 2
    create_dask_worker(hostname=os.getenv('cluster_server_2_address'), username=os.getenv('cluster_server_2_username'), password=os.getenv('cluster_server_2_password'),
                           scheduler_ip=os.getenv('cluster_server_1_address'), nworkers=7, mem_limit = '6GB')
    # create worker 3, on work PC
    create_dask_worker(hostname=os.getenv("cluster_server_0_address"), username=os.getenv('cluster_server_0_username'), password=os.getenv('cluster_server_0_password'),
                       scheduler_ip=os.getenv("cluster_server_1_address"), nworkers=5, mem_limit='3GB')

    time.sleep(9)

def kill_dask_deployment_home_setup():
    # server 0 is used for task scheduler and the rest used for dask
    for server_number in [0,1,2]:
        dagster_logger.info('Trying to kill dask processes @: '+os.getenv(f'cluster_server_{server_number}_address'))
        pids_with_dask_before = get_remote_process_ids_ubuntu(os.getenv(f'cluster_server_{server_number}_address'), os.getenv(f'cluster_server_{server_number}_username'), os.getenv(f'cluster_server_{server_number}_password'), 'dask')
        dagster_logger.info(pids_with_dask_before)
        kill_remote_ubuntu_process_ids(os.getenv(f'cluster_server_{server_number}_address'), os.getenv(f'cluster_server_{server_number}_username'), os.getenv(f'cluster_server_{server_number}_password'), pids_with_dask_before)
        time.sleep(5)
        pids_with_dask_after =  get_remote_process_ids_ubuntu(os.getenv(f'cluster_server_{server_number}_address'), os.getenv(f'cluster_server_{server_number}_username'), os.getenv(f'cluster_server_{server_number}_password'), 'dask')
        ctr = 0
        while len(pids_with_dask_after) > 1:
            dagster_logger.info(f"There are still dask processes / {pids_with_dask_after}")
            time.sleep(5)
            pids_with_dask_after =  get_remote_process_ids_ubuntu(os.getenv(f'cluster_server_{server_number}_address'), os.getenv(f'cluster_server_{server_number}_username'), os.getenv(f'cluster_server_{server_number}_password'), 'dask')
            ctr = ctr + 1
            if ctr == 3:
                kill_remote_ubuntu_process_ids(os.getenv(f'cluster_server_{server_number}_address'),
                                               os.getenv(f'cluster_server_{server_number}_username'),
                                               os.getenv(f'cluster_server_{server_number}_password'),
                                               pids_with_dask_after)
            if ctr == 6:
                raise RuntimeError('Could not kill remote processes')

        dagster_logger.info(pids_with_dask_after)
        # for each machine, ensure that there are fewer processes and that only the two grep/ps processes are running
        assert len(pids_with_dask_before) >= len(pids_with_dask_after), "There are more dask tasks now than before"
        assert len(pids_with_dask_after) < 3, "There are more than grep | ps process running dask"

def upload_files_to_dask_cluster():
    with sqlalchemy.create_engine(os.getenv("home_connection_string")).begin() as conn:
        running_cluster_location = pd.read_sql("""SELECT var, value FROM
         environment_variables WHERE
         var = 'distributed_dask_cluster'""",  conn)['value'].values[0]
        client = dask.distributed.get_client(running_cluster_location)
        print(f"Using Dask Cluster: {str(client)}")
        client.upload_file('/home/jay/PycharmProjects/finance/finance_data_eng.py')
        print(client)

def process_list_with_dask(input_list: list[Any], func: Callable, num_splits: int, cluster:CLUSTER_TYPE = 'DISTRIBUTED', priority:int = 1, kwargs: Optional[dict[str, Any]] = None,) -> None:
    """
    Split the input list into multiple sublists using Dask and execute the provided function on each split list.

    :param input_list: The input list to be split.
    :param func: The function to be executed on each split list.
    :param num_splits:  The number of splits to create from the input list.
    :param cluster:  Either "local" or "distributed". This function chooses the cluster to send the tasks to.
    :param kwargs:  Sometimes the func needs extra kwargs, this should be a dict if present, else None
    :param priority:  priority, an int with default 1. Higher has a higher priority and will run first on the cluster.
    :return: None
    """

    # Calculate the size of each split
    split_size = len(input_list) // num_splits
    split_size = max(1, split_size)

    # Create the splits using Dask
    splits = [input_list[i:i + split_size] for i in range(0, len(input_list), split_size)]
    dagster_logger.info(f"{num_splits} splits each of around {split_size} size made. {len(input_list)} in total.")
    if cluster == 'DISTRIBUTED':
        running_cluster_location = pd.read_sql("""SELECT var, value FROM
         environment_variables WHERE
         var = 'distributed_dask_cluster'""",  sqlalchemy.create_engine(os.getenv('home_connection_string')))['value'].values[0]
        client = dask.distributed.get_client(running_cluster_location)
        dagster_logger.info(str(running_cluster_location))
        dagster_logger.info(f"Using Distributed Dask Cluster : {str(client)}")

    elif cluster == 'LOCAL':

        try:
            dagster_logger.info("Checking for Running Local Dask Cluster")
            client = dask.distributed.get_client(f"tcp://{os.getenv('local_db_address')}:8786")
            dagster_logger.info(f"Client acquired at tcp://{os.getenv('local_db_address')}:8786")
            client.shutdown()
            dagster_logger.info("Client shutdown")
            time.sleep(15)
        except Exception:
            dagster_logger.info(error_handling())
            dagster_logger.info("No Client found")

        dagster_logger.info('Creating Local Dask Cluster')
        abc = execute_script_with_cmd("/home/jay/PycharmProjects/finance/src/finance/common/finance_launch_dask_cluster.py")
        dagster_logger.info(str(abc))

        running_cluster_location = pd.read_sql("""SELECT var, value FROM
         environment_variables WHERE
         var = 'local_dask_cluster'""",  sqlalchemy.create_engine(os.getenv('home_connection_string')))['value'].values[0]
        client = dask.distributed.get_client(running_cluster_location)
        dagster_logger.info(str(running_cluster_location))
        dagster_logger.info(f"Using Local Dask Cluster : {str(client)}")

    # Create Dask delayed objects for each split and apply the provided function
    if kwargs:
        delayed_results = [dask.delayed(func)(split, **kwargs) for split in splits]
    else:
        delayed_results = [dask.delayed(func)(split) for split in splits]

    with sqlalchemy.create_engine(os.getenv('home_connection_string')).begin() as conn:
        running_cluster_location = pd.read_sql("""SELECT var, value FROM
         environment_variables WHERE
         var = 'distributed_dask_cluster'""",  conn)['value'].values[0]
        client = dask.distributed.get_client(running_cluster_location)

    # Compute the results using Dask's parallel processing capabilities
    output = dask.compute(*delayed_results, priority=priority, )

    return output

def find_number_of_free_dask_workers():
    with sqlalchemy.create_engine(os.getenv('home_connection_string')).begin() as conn:
        running_cluster_location = pd.read_sql(""" SELECT var, value FROM
         environment_variables WHERE
         var = 'distributed_dask_cluster' """, conn)['value'].values[0]
        client = get_client(running_cluster_location)
        pprint(f"Using Dask Cluster: {str(client)}")
        abc = client.processing()
        done = [1 for v in abc.values() if len(v) == 0]
        return sum(done)
