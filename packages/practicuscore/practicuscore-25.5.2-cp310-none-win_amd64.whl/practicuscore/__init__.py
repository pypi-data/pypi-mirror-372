"""
# Practicus AI SDK v25.5.2

## Overview
Welcome to the Practicus AI SDK, a Python library that allows you to interact with Practicus AI Regions,
manage Workers, deploy and manage machine learning Models and Apps, and orchestrate distributed jobs.

This SDK provides an intuitive Pythonic interface for common operations, such as:
- Connecting to Practicus AI Regions and managing their resources.
- Creating and working with Workers and Workspaces.
- Building and deploying ML models and GenAI apps, managing data connections
- Running distributed workloads (Spark, Dask, Torch) seamlessly.
- Accessing notebooks, experiments tracking, and more.

## Key Functionality
Below are some of the helper classes, interfaces and functions for interacting with Practicus AI platform.

### Helper Classes
These static wrapper classes provide convenient `entrypoints` and `abstractions` for common operations,
allowing you to work with Practicus AI resources efficiently:

- `regions`: Manage and interact with Practicus AI Regions, handle login, workers, etc.
- `models`: Deploy and manage ML models, view model prefixes and versions.
- `apps`: Deploy and manage GenAI focused apps and APIs and their versions.
- `workflows`: Deploy and manage workflows (e.g., Airflow DAGs).
- `connections`: Manage and create data source connections (e.g., S3, SQL).
- `distributed`: Work with distributed job clusters and frameworks.
- `auth`: Authentication helpers for logging in and out of regions.
- `engines`: Interact with data processing engines like Spark.
- `experiments`: Manage experiment tracking services, such as MLFlow.
- `notebooks`: Access Jupyter notebooks running on workers.
- `quality`: Code quality (linting, formatting) utilities.
- `containers`: Build and use custom container images.
- `vault`: Secret manager methods to save, retrieve and delete secrets in Practicus AI Vault.
- `git`: Git helper methods to sync remote repositories.
- `mq`: Helper for RabbitMQ operations.
- `notify`: Sending notifications like emails, and if configures, text messages.
- `db`: Helper for Database operations.
- `addons`: Helper methods for Practicus AI Add-ons.
- `sql`: Helper methods for Practicus AI SQL parser, query executor and analytics features.
- `metadata`: Helper methods for Practicus AI Metadata service.

### Core Classes
These core classes represent the primary entities you'll interact with the most:

- `Region`: Represents a Practicus AI Region (control plane) where you can manage workers, models, apps, and connections.
- `Worker`: Represents a compute resource (pod) in the Region where you can run tasks, load data, open notebooks, and more.
- `Process`: Represents an OS-level process running on a Worker that can load and manipulate data, run transformations,
  execute code snippets, build models, and perform predictions—all directly on the Worker.

### Sample Usage

```python
import practicuscore as prt

# Connect to the default region
region = prt.get_default_region()

# Create a worker
worker = region.create_worker()

# Deploy a model
dynamic_url, version_url, meta_url = region.deploy_model(
    deployment_key="my-model-service", prefix="my-prefix", model_name="my-model"
)

# Run a task on a worker
_, success = prt.run_task("analysis.py", files_path="project_code/")
print("Task successful:", success)
```

### Alias Functions

In addition to using the `Region` or it's helper `regions` classes directly, the SDK provides some alias functions
as shortcuts that directly map to commonly used methods in a selected (or default) region. This allows you to perform
actions without explicitly fetching or referencing a `Region` object first:

- `get_default_region()`: Retrieves the default Practicus AI region previously configured.
- `create_worker()`: Creates a new worker (pod) in the default or current region.
- `current_region()`: Returns the currently selected region, if any.
- `get_local_worker()`: Returns the worker representing the current environment if the code is running inside one.
- `get_or_create_worker()`: Retrieves an existing worker or creates a new one if none is suitable.
- `running_on_a_worker()`: Checks if the current code is executing on a Practicus AI worker.
- `get_region()`: Retrieves a specific region by key (username@host_dns).
- `get_region_list()`: Returns a list of all configured and accessible regions.
- `region_factory()`: Creates a `Region` instance from a given configuration.
- `set_default_region()`: Changes which region is considered the default.
- `create_workspace()`: Creates a new Practicus AI Workspace (an interactive development environment).
- `run_task()`: Runs a given Python or shell script task on a worker in the default or specified region.

These aliases simplify calls to region-dependent functions, making code more concise and direct.
For example:

```python
import practicuscore as prt

# Instead of:
region = prt.get_default_region()
worker = region.create_worker()

# You can do:
worker = prt.create_worker()
```

## Practicus AI Documentation
For help on getting started with the Practicus AI platform and tutorials, please visit:
[Practicus AI Documentation](https://docs.practicus.ai)

"""

from .log_manager import get_logger, Log, set_logging_level
from .api_base import (
    WorkerConfig,
    ImageConfig,
    DistJobType,
    DistJobConfig,
    GitConfig,
    MQConfig,
    APIExecutionTarget,
    APIRiskProfile,
    APIScope,
    APISpec,
    GatewayModel,
    GatewayGuardrail,
    GatewayConfig,
    TrinoPolicyRequest,
    TrinoRowFilter,
    TrinoColumnMaskRule,
    TrinoColumnMask,
)
from .region_manager import Region, regions, auth
from .worker_manager import Worker
from .proc_manager import Process
from .engine_helper import engines
from .experiment_helper import experiments
from .workflow_helper import workflows
from .model_helper import models
from .model_server import ModelServer
from .app_helper import apps
from .notebook_helper import notebooks
from .dist_job import distributed
from .util import quality, PrtList
from .cli import main
from .conn_helper import connections
from .container_helper import containers
from .vault_helper import vault
from .git_helper import git
from .mq_helper import mq
from .notify_helper import notify
from .db_helper import db
from .addon_helper import addons
from .sql_helper import sql
from .metadata_helper import metadata
# Adding new helpers classes? Also add to docs at the top of this file.

# Alias functions to select region methods. Alternative to calling directly from a selected region instance.
get_default_region = regions.get_default_region
create_worker = regions.create_worker
current_region = regions.current_region
get_local_worker = regions.get_local_worker
get_or_create_worker = regions.get_or_create_worker
running_on_a_worker = regions.running_on_a_worker
get_region = regions.get_region
get_region_list = regions.get_region_list
region_factory = regions.region_factory
set_default_region = regions.set_default_region
create_workspace = regions.create_workspace
run_task = regions.run_task
api = apps.api


__all__ = [
    # Aliases to key classes
    "regions",
    "models",
    "apps",
    "workflows",
    "connections",
    "distributed",
    "auth",
    "engines",
    "experiments",
    "notebooks",
    "quality",
    "containers",
    "vault",
    "git",
    "mq",
    "notify",
    "db",
    "addons",
    "sql",
    "metadata",
    # Primary classes for most of the core functionality
    "Region",
    "Worker",
    "Process",
    # Aliases to logging
    "get_logger",
    "Log",
    "set_logging_level",
    # Aliases to key pydantic models
    "WorkerConfig",
    "ImageConfig",
    "DistJobType",
    "DistJobConfig",
    "GitConfig",
    "MQConfig",
    "PrtList",
    "APIExecutionTarget",
    "APIRiskProfile",
    "APIScope",
    "APISpec",
    "GatewayModel",
    "GatewayGuardrail",
    "GatewayConfig",
    "TrinoPolicyRequest",
    "TrinoRowFilter",
    "TrinoColumnMaskRule",
    "TrinoColumnMask",
    # Aliases to other key classes
    "ModelServer",
    # Alias to select region methods
    "get_default_region",
    "create_worker",
    "current_region",
    "get_local_worker",
    "get_or_create_worker",
    "running_on_a_worker",
    "get_region",
    "get_region_list",
    "region_factory",
    "set_default_region",
    "create_workspace",
    "run_task",
    "api",
]


__version__ = "25.5.2"
logger = get_logger(Log.USER)


def trust_local_certificates():
    try:
        from .core_conf import core_conf_glbl

        if core_conf_glbl.network__trust_local_certificates:
            _logger = get_logger(Log.SDK)
            _logger.debug("Trusting SSL certificates in local OS store.")
            import truststore

            truststore.inject_into_ssl()
    except:
        logger.error(
            "Could not trust local operating system certificate store. "
            "Your private Certificate Authority (CA) certs might not work.",
            exc_info=True,
        )


trust_local_certificates()


def __dir__():
    return __all__


if __name__ == "__main__":
    main()
