import datetime
import io
import os
import re
import subprocess
import time
from typing import Iterable, Optional, Union, Any, Callable

import numpy as np
import paramiko  # type: ignore
import yaml  # type: ignore

from ..common.jragbeer_common_data_eng import dagster_logger, error_handling

class SshClient:
    "A wrapper of paramiko.SSHClient"
    TIMEOUT = 4
    def __init__(self, host, port, username, password, key=None, passphrase=None):
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        if key is not None:
            key = paramiko.RSAKey.from_private_key(io.StringIO(key), password=passphrase)
        self.client.connect(host, port, username=username, password=password, pkey=key, timeout=self.TIMEOUT)

    def close(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def execute(self, command, sudo=False):
        feed_password = False
        if sudo and self.username != "root":
            command = "sudo -S -p '' %s" % command
            feed_password = self.password is not None and len(self.password) > 0
        stdin, stdout, stderr = self.client.exec_command(command)
        if feed_password:
            stdin.write(self.password + "\n")
            stdin.flush()
        return {'out': stdout.readlines(),
                'err': stderr.readlines(),
                'retval': stdout.channel.recv_exit_status()}


def execute_confirm_wait(func: Callable) -> Callable:
    def inner(*args, **kwargs):
        try:
            func(*args, **kwargs)
            # dagster_logger.info(f"{args}, {kwargs} is done! ({func.__name__})")
        except TypeError:
            func()
            # dagster_logger.info(f"it's done! ({func.__name__})")
        time.sleep(0.05)
        return func
    return inner

def execute_script_with_cmd(script_name:str) -> str:
    output = execfile(script_name)
    dagster_logger.info(str(output))
    return str(output)

def execute_cmd_ubuntu_sudo(commands: list[str] | str) -> Optional[str]:
    output = None
    try:
        if isinstance(commands, str):
            commands = commands.split()

        sp = subprocess.Popen(['sudo', '-S'] + commands, stdin=subprocess.PIPE, stderr=subprocess.PIPE,
                  universal_newlines=True)
        output, err = sp.communicate(os.getenv("cluster_server_0_password", "cluster_server_0_password") + '\n')

        # Decode the output and error from bytes to string
        # Print the output and error
        if output:
            # This will give you the output of the command being executed
            dagster_logger.info(f"Command output: {output}")
        if err:
            print(f"Error:\n{err}")
    except Exception:
        dagster_logger.info(error_handling())
    return output

def execute_cmd_ubuntu_normal(commands: list[str] | str) -> Optional[str]:
    output_str = None
    try:
        output = subprocess.run(commands, shell=True, check=True)

        # Decode the output and error from bytes to string
        # Print the output and error
        if output.returncode == 0:
            # This will give you the output of the command being executed
            try:
                output_str = output.stdout.decode('utf-8')
            except Exception:
                output_str = output.stdout
            dagster_logger.info(f"Command output: {output_str}")
    except Exception:
        dagster_logger.info(error_handling())
    return output_str

def execfile(filepath, globals=None, locals=None):
    if globals is None:
        globals = {}
    globals.update({
        "__file__": filepath,
        "__name__": "__main__",
    })
    with open(filepath, 'rb') as file:
        exec(compile(file.read(), filepath, 'exec'), globals, locals)

def kill_remote_ubuntu_process_ids(hostname:str, username:str, password:str, pid:Union[str,Iterable]):
    if isinstance(pid, str):
        pid = pid.split()
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)
    # Run command to get memory usage stats
    python_command = 'sudo kill -9 ' + ' '.join(pid)
    print(python_command)
    stdin, stdout, stderr = ssh.exec_command(python_command)
    py_output = stdout.read().decode().strip()
    print(py_output)
    print('remote killing of pids done')

def get_remote_process_ids_ubuntu(hostname:str, username:str, password:str, search_string:str=''):
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    # Run command to show matching processes excluding defunct ones
    list_command = f"ps aux | grep '{search_string}' | grep -v '<defunct>' | grep -v 'grep'"
    stdin, stdout, stderr = ssh.exec_command(list_command)
    process_output = stdout.read().decode().strip()
    print(process_output)

    # Extract PIDs of those non-defunct processes
    pid_command = f"ps aux | grep '{search_string}' | grep -v '<defunct>' | grep -v 'grep' | awk '{{print $2}}'"
    stdin, stdout, stderr = ssh.exec_command(pid_command)
    pid_output = stdout.read().decode().strip()
    pid_list = pid_output.split()

    return pid_list

def get_remote_stats_ubuntu(hostname:str, username:str, password:str):
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password)

    # Run command to get memory usage stats
    memory_command = "free -m | awk 'NR==2{print $2,$3,$4,$5,$6,$7}'"
    stdin, stdout, stderr = ssh.exec_command(memory_command)
    mem_output = stdout.read().decode().strip()
    # Extract memory usage stats from the output
    total, used, free, shared, buff_cache, available = mem_output.split()

    # Run commands to get CPU and memory usage
    cpu_command = "top -bn1 | grep '%Cpu(s)' | awk '{print $2 + $4}'"
    stdin, stdout, stderr = ssh.exec_command(cpu_command)
    cpu_usage = float(stdout.read().decode().strip())

    # Return memory usage stats
    mem = {
        'Total': int(total),
        'Used': int(used),
        'Free': int(free),
        'Available': int(available),
        'Percent': int(int(used)/int(total)),
    }

    # Run command to get memory usage stats
    python_command = "ps aux | grep python | awk '{print $6}'"
    stdin, stdout, stderr = ssh.exec_command(python_command)
    py_output = stdout.read().decode().strip()
    python_memory_usage_kB = sum([int(i) for i in py_output.split()])

    # Run command to get Python process memory usage
    sql_command = "ps aux | grep sql | awk '{print $6}'"
    stdin, stdout, stderr = ssh.exec_command(sql_command)
    sql_output = stdout.read().decode().strip()
    sql_memory_usage_kB = sum([int(i) for i in sql_output.split()])

    # Run command to get the number of CPU cores
    cpu_cores_command = "nproc"
    stdin, stdout, stderr = ssh.exec_command(cpu_cores_command)
    cpu_cores_output = int(stdout.read().decode().strip())

    # Run command to get CPU frequency
    cpu_freq_command = """ lscpu | grep "MHz" """
    stdin, stdout, stderr = ssh.exec_command(cpu_freq_command)
    cpu_freq_output = stdout.read().decode().strip()
    cpu_freq_output = int(re.findall(r"(\d+)(CPU)?", cpu_freq_output)[0][0])

    # Run command to get operating system information
    os_command = """lsb_release -a | grep "Description" """
    stdin, stdout, stderr = ssh.exec_command(os_command)
    os_output = stdout.read().decode().strip()
    os_output = str(os_output).split(":")[1].strip()

    # Run command to get CPU model
    cpu_model_command = "lscpu | grep 'Model name'"
    stdin, stdout, stderr = ssh.exec_command(cpu_model_command)
    cpu_model_output = stdout.read().decode().strip().split(":")[1].strip()


    ip_command = "ip addr show | grep 'inet '"
    stdin, stdout, stderr = ssh.exec_command(ip_command)
    ip_output = stdout.read().decode().strip()
    ip_output = re.findall(r"inet\s(192.168.\d+.\d+)", ip_output)[0]

    # Close the SSH connection
    ssh.close()
    output_dict = {'memory_' + k.lower() + "_MB": v for k, v in mem.items()}
    output_dict.update({'cpu_pct': cpu_usage,  # gives a single float value
                        'cpu_cores': cpu_cores_output,
                        'cpu_freq': cpu_freq_output,
                        'pc_network_address': ip_output,
                        "pc_os": os_output,
                        "pc_cpu": cpu_model_output,
                        'python_memory_usage_GB': np.round(python_memory_usage_kB / 1024 ** 2, 2),
                        'sql_memory_usage_GB': np.round(sql_memory_usage_kB / 1024 ** 2, ),
                        "query_time": str(datetime.datetime.now())})
    return output_dict

def move_file_to_remote_pc(hostname:str, username:str, password:str, local_path:str="/etc/dask/dask.yaml", remote_path:str="/home/jay/PycharmProjects/home/dask.yaml"):
    # SSH into the remote machine
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username, password=password, )
    sftp = ssh.open_sftp()
    try:
        sftp.put(localpath=local_path, remotepath=remote_path)
        print("File upload complete.")
    except Exception as e:
        print(f"Upload failed: {e}")
    sftp.close()
    ssh.close()
    if local_path == "/etc/dask/dask.yaml":
        client = SshClient(host=hostname, port=22, username=username, password=password)
        try:
            ret = client.execute(command="""sudo mkdir /etc/dask/""" , sudo=True)
            print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
            ret = client.execute(command="""sudo chmod -R 777 /etc/dask/""" , sudo=True)
            print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
            ret = client.execute(command="""sudo mv /home/jay/PycharmProjects/jragbeer_home/dask.yaml /etc/dask/dask.yaml""" , sudo=True)
            print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])

        finally:
            client.close()
            dagster_logger.info("Done")

def give_write_permission_to_folder(folder_path:str):
    execute_cmd_ubuntu_sudo(f"sudo chmod -R 777 {folder_path}")

def create_yaml_from_dict(input_dict: dict[Any, Any], name_of_yaml:str|None=None) -> str:
    if name_of_yaml:
        ff = open(name_of_yaml, 'w+')
        yamll = yaml.dump(input_dict, ff, allow_unicode=True)
    else:
        yamll = yaml.dump(input_dict, allow_unicode=True)
    return yamll

def update_repo_on_remote_machine(hostname:str, username:str, password:str, repo:str) -> None:
    """
    This logs onto the remote machine and updates the repo using 'git pull' command.
    Args:
        hostname: The address of the target machine
        username: The username of the target machine
        password: The password of the target machine
        repo: The name of the repo to update

    Returns:
        None

    """
    client = SshClient(host=hostname, port=22, username=username, password=password)
    try:
        cmd = f"""cd /home/jay/PycharmProjects/{repo}/; git pull"""
        ret = client.execute(command=cmd, )
        print("  ".join(ret["out"]), "  E ".join(ret["err"]), ret["retval"])
    finally:
        client.close()
