# jragbeer_common

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0) [![Python 3.10](https://shields.io/pypi/pyversions/astyle)](https://www.python.org/downloads/release/python-310/) [![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)

## Overview

A Python utility library containing common functions and tools used across various projects. This library provides reusable components for:

- Data processing and engineering
- Azure blob storage operations
- Dask distributed computing
- Ubuntu system operations

## Features

- **Data Engineering Utilities**

  - DataFrame manipulation and cleaning
  - SQL database operations
  - Email notifications
  - Date/time processing
  - Logging configuration

- **Azure Integration**

  - Blob storage upload/download
  - Parquet file handling
  - Container management
  - Batch operations

- **Dask Distributed Computing**

  - Cluster deployment and management
  - Worker allocation
  - Task scheduling
  - Remote execution

- **Ubuntu System Operations**
  - Remote command execution
  - Process management
  - System monitoring
  - File operations

## Installation

1. Install `uv` (recommended):

```bash
pip install uv
```

2. Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

3. Install the package:

```bash
uv pip install jragbeer-common
```

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/jragbeer/jragbeer_common.git
cd jragbeer_common
```

2. Create a virtual environment and install dependencies:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

3. Install development dependencies:

```bash
uv pip install -e ".[dev]"
```

4. Install pre-commit hooks:

```bash
pre-commit install
```

## Usage

```python
from jragbeer_common import (
    jragbeer_common_data_eng,
    jragbeer_common_azure,
    jragbeer_common_dask,
    jragbeer_common_ubuntu
)

# Data Engineering
jragbeer_common_data_eng.parse_date_features(df)

# Azure Operations
jragbeer_common_azure.adls_upload_file("path/to/file", "blob_name")

# Dask Operations
jragbeer_common_dask.deploy_dask_home_setup()

# Ubuntu Operations
jragbeer_common_ubuntu.execute_cmd_ubuntu_sudo("command")
```

## Environment Variables

The following environment variables are required:

```bash
# Azure Storage
adls_connection_string="your_connection_string"
adls_container_name="your_container"

# Database
local_db_username="username"
local_db_password="password"
local_db_address="address"
local_db_port="port"

# Cluster Configuration
cluster_server_1_address="address"
cluster_server_1_username="username"
cluster_server_1_password="password"
```

## Building and Distribution

1. Build the package:

```bash
uv build
```

2. Install locally for testing:

```bash
uv pip install dist/jragbeer_common-0.2.0-py3-none-any.whl
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting:

```bash
pre-commit run --all-files
pytest
```

5. Submit a pull request

## License

Copyright 2024 Julien Ragbeer

Licensed under the Apache License, Version 2.0
