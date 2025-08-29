# TetraScience Python Connector SDK <!-- omit in toc -->

## Version <!-- omit in toc -->

v2.0.0

## Table of Contents <!-- omit in toc -->

- [Summary](#summary)
- [Usage](#usage)
  - [`Connector` Class](#connector-class)
    - [Creating and running a connector](#creating-and-running-a-connector)
    - [Starting the connector and running](#starting-the-connector-and-running)
      - [Configuring `TdpApi`](#configuring-tdpapi)
  - [Proxy support](#proxy-support)
  - [Initialization of `TdpApi`](#initialization-of-tdpapi)
    - [Connector example](#connector-example)
  - [Commands](#commands)
    - [Lifecycle methods and hooks](#lifecycle-methods-and-hooks)
    - [Additional `Connector` commands](#additional-connector-commands)
    - [Custom commands](#custom-commands)
  - [Polling](#polling)
- [Logging](#logging)
  - [Logger usage](#logger-usage)
  - [Setting log levels](#setting-log-levels)
  - [CloudWatch logging and standalone connector support](#cloudwatch-logging-and-standalone-connector-support)
- [OpenAPI code generation](#openapi-code-generation)
  - [Using the generated API client](#using-the-generated-api-client)
    - [Example usage](#example-usage)
    - [Retrieving connector data with filtering](#retrieving-connector-data-with-filtering)
      - [Using `TdpApi` (async)](#using-tdpapi-async)
      - [Using `TdpApiSync` (synchronous)](#using-tdpapisync-synchronous)
      - [Using `Connector` class methods](#using-connector-class-methods)
- [Local testing with standalone connectors](#local-testing-with-standalone-connectors)
  - [Prerequisites](#prerequisites)
  - [Setup process](#setup-process)
    - [Step 1: build your local connector image](#step-1-build-your-local-connector-image)
    - [Step 2: use the standalone installer](#step-2-use-the-standalone-installer)
    - [Step 3: environment configuration](#step-3-environment-configuration)
    - [Step 4: running your local connector](#step-4-running-your-local-connector)
    - [Alternative: running containerless locally](#alternative-running-containerless-locally)
  - [Important notes](#important-notes)
- [Running tests](#running-tests)
- [Changelog](#changelog)
  - [v2.0.0](#v200)
  - [v1.0.1](#v101)
  - [v1.0.0](#v100)
  - [v0.9.0](#v090)
  - [v0.8.0](#v080)
  - [v0.7.0](#v070)
  - [v0.6.0](#v060)
  - [v0.5.0](#v050)
  - [v0.4.0](#v040)
  - [v0.3.0](#v030)
  - [v0.2.0](#v020)
  - [v0.1.0](#v010)

## Summary

The TetraScience Python Connectors SDK provides utilities and APIs for building TetraScience [pluggable connectors](https://developers.tetrascience.com/docs/tetra-connectors) in Python. Connectors are containerized applications used for transferring data between the Tetra Data Platform (TDP) and other systems. Some examples of existing connectors:

- The [S3 connector](https://developers.tetrascience.com/docs/tetra-amazon-s3-connector) receives file events from an S3 bucket via an SQS queue and pulls the corresponding objects into TDP
- The [Kepware KEPServerEX connector](https://developers.tetrascience.com/docs/tetra-kepserverex-connector) pulls tags from KEPServerEX over MQTT and writes corresponding JSON files to TDP
- The [LabX connector](https://developers.tetrascience.com/docs/tetra-labx-connector) can connect to multiple LabX instances and retrieve completed tasks. The LabX connector was written using this Python SDK

## Usage

### `Connector` Class

The `Connector` class is the core component of the SDK.
It provides methods and hooks to manage the lifecycle of a connector, handle commands, perform periodic tasks, and
interact with TDP.

#### Creating and running a connector

To create a `Connector` instance, you need to provide a `TdpApi` instance and optional `ConnectorOptions`. The `TdpApi` instance is the class that interacts with TDP

```python
from ts_sdk_connectors_python.connector import Connector, ConnectorOptions
from ts_sdk_connectors_python.tdp_api import TdpApi

tdp_api = TdpApi()
connector = Connector(tdp_api=tdp_api, options=ConnectorOptions())
```

#### Starting the connector and running

```python

async def main():
    tdp_api = TdpApi()
    connector = Connector(tdp_api=tdp_api, options=ConnectorOptions())
    await connector.start()
    while True:
        await asyncio.sleep(1)

asyncio.run(main())
```

##### Configuring `TdpApi`

Required configuration values for `TdpApi` can be provided either as instance args or pulled from environment variables. If any arguments are not provided, they are pulled from the environment variables.

```python
# manually provide configuration values
tdp_api = TdpApi(
    aws_region="us-east-1",
    org_slug="tetrascience-yourorg",
    hub_id="your-hub-id",
    connector_id="your-connector-id",
    datalake_bucket="your-datalake-bucket",
    stream_bucket="your-stream-bucket",
    tdp_certificate_key="your-tdp-certificate-key",
    jwt_token_parameter="your-jwt-token-parameter",
    tdp_endpoint="https://api.tetrascience.com",
    outbound_command_queue="your-outbound-command-queue",
    kms_key_id="your-kms-key-id",
    artifact_type="connector",
    connector_token="your-connector-token",
    local_certificate_pem_location="path/to/your/certificate.pem"
)
```

```python
# Automatically pull all args from environment variables
tdp_api = TdpApi()
```

```python
# Some arguments provided and remaining args pulls from environment variables
tdp_api = TdpApi(datalake_bucket="your-datalake-bucket")
```

The following environment variables are used by the `TdpApiConfig` class to configure the TetraScience Data Platform API client. Note that not all of them are necessarily relevant:

| Variable Name                     | Description                                                   |
| --------------------------------- | ------------------------------------------------------------- |
| `AWS_REGION`                      | The AWS region to use.                                        |
| `ORG_SLUG`                        | The organization slug for the TetraScience Data Platform.     |
| `HUB_ID`                          | The hub ID for the connector.                                 |
| `CONNECTOR_ID`                    | The unique identifier for the connector.                      |
| `DATALAKE_BUCKET`                 | The name of the datalake bucket.                              |
| `STREAM_BUCKET`                   | The name of the stream bucket.                                |
| `TDP_CERTIFICATE_KEY`             | The key for the TDP certificate.                              |
| `JWT_TOKEN_PARAMETER`             | Name of the SSM parameter that contains the JWT token. Used  Used by non-standalone connectors          |
| `TDP_ENDPOINT`                    | The base URL for the TetraScience Data Platform API.          |
| `OUTBOUND_COMMAND_QUEUE`          | The queue name for outbound commands.                         |
| `KMS_KEY_ID`                      | The KMS key ID.                                               |
| `ARTIFACT_TYPE`                   | The type of artifact (e.g., `connector`, `data-app`).         |
| `CONNECTOR_TOKEN`                 | The JWT authentication token for the connector. Used for standalone connectors to request initial AWS credentials                  |
| `LOCAL_CERTIFICATE_PEM_LOCATION`  | The local certificate PEM file location.                      |

### Proxy support

In addition to the above environment variables, the connector uses proxy settings
determined from the environment variables `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY`.
For connectors on a Hub, the connector sets these environment variables based on
the Hub's proxy settings. For standalone connectors, the standalone installer will
set lowercase versions of these variables. The connector checks the environment,
and in the case where lowercase versions exist but uppercase ones don't, it copies
the lowercase values over to uppercase.

### Initialization of `TdpApi`

`TdpApi` must initialize the AWS and HTTP clients before it can communicate with the connector's AWS services and connector endpoints in TDP.

```python
tdp_api = TdpApi()
await tdp_api.init_client(proxy_url = "127.0.0.1:3128")  # your proxy URL here, if needed
files = tdp_api.get_connector_files(...)
...
```

#### Connector example

Here is an example of a custom connector that prints "Hello World" on a scheduled interval:

```python
from typing import Optional
from ts_sdk_connectors_python.connector import Connector, ConnectorOptions
from ts_sdk_connectors_python.custom_commands import register_command
from ts_sdk_connectors_python.tdp_api import TdpApi
from ts_sdk_connectors_python.utils import Poll

class BasicScheduledConnector(Connector):
    """Prints hello world on a scheduled interval"""

    def __init__(
        self,
        tdp_api: TdpApi,
        schedule_interval: int,
        options: Optional[ConnectorOptions] = None,
    ):
        super().__init__(tdp_api=tdp_api, options=options)
        self.poll: Optional[Poll] = None
        self.schedule_interval = schedule_interval

    async def on_start(self):
        await super().on_start()
        self._start_polling()

    async def on_stop(self):
        await super().on_stop()
        self._stop_polling()

    @register_command("TetraScience.Connector.PollingExample.SetScheduleInterval")
    async def set_schedule_interval(self, schedule_interval: str):
        self.schedule_interval = float(schedule_interval)
        self._stop_polling()
        self._start_polling()

    def _start_polling(self):
        if not self.poll:
            self.poll = Poll(self.execute_on_schedule, self.schedule_interval)
            self.poll.start()

    def _stop_polling(self):
        if self.poll:
            self.poll.stop()
            self.poll = None

    async def execute_on_schedule(self):
        print("HELLO WORLD")


# Usage
import asyncio

async def main():
    tdp_api = TdpApi()
    await api.init_client()
    connector = BasicScheduledConnector(tdp_api=tdp_api, schedule_interval=5)
    await connector.start()
    await asyncio.sleep(10)
    await connector.shutdown()

asyncio.run(main())
```

This example demonstrates how to create a custom connector that prints "Hello World" every 5 seconds and allows the schedule interval to be updated via a custom command. For more information on registering commands, see below.

### Commands

TDP communicates with connectors via the [command service](https://developers.tetrascience.com/docs/command-service). The data acquisition service in TDP uses a set of commands we refer to as "lifecycle commands". The `Connector` class implements a command listener and has several methods that are invoked when lifecycle commands come in.

#### Lifecycle methods and hooks

*Starting and Initializing methods*

- **start**: Starts the connector and its main activities.
  - Triggers:
    - None. Almost all connectors will call this from `main.py`, the default entrypoint of the container
  - Default implementation:
    - calls `on_initializing` hook
    - loads connector details (*does not call `on_connector_updated`*)
    - starts metrics collection, heartbeat, and command listener tasks
    - if the connector's operating status is `RUNNING`, calls `on_start` hook
    - calls `on_initialized` hook
- **on_initializing**: A developer-defined hook that is called at the beginning of the default implementation of `Connector.start`
  - Triggers:
    - None. In default implementation, called once by `Connector.start`
  - Default implementation:
    - None
- **on_initialized**: A developer-defined hook that is called at the end of the default implementation of `Connector.start`
  - Triggers:
    - None. In default implementation, called once by `Connector.start`
  - Default implementation:
    - None
- **on_start**: A developer-defined hook that runs when the connector's operating status is set to `RUNNING`
  - Triggers (any of the following):
    - A command with action `TetraScience.Connector.Start` is received
      - this corresponds to setting the connector operating status to`RUNNING`
    - During `Connector.start` if the connector's operating status is `RUNNING`
      - this typically happens when a disabled connector is "enabled as `RUNNING`"
  - Default implementation:
    - reloads connector config, which subsequently calls `on_connector_updated`

*Running methods*

- **on_connector_updated**: A developer-defined hook that gets called when the connector
details are updated. Because this corresponds to config changes and is also triggered indirectly by `on_start`, it is the most common place to initialize resources for the connector to work with third-party systems. Since it is also triggered by `on_stop`, checking that the connector's operating status is `RUNNING` before starting any data ingestion is important
  - Triggers (any of the following):
    - A command with action `TetraScience.Connector.UpdateConfig` is received.
      - sent by the data acquisition service after valid configuration is applied
    - A command with action `TetraScience.Connector.Start` is received.
      - invoked by base implementation of `Connector.on_start`
    - A command with action `TetraScience.Connector.Stop` is received.
      - invoked by base implementation of `Connector.on_stop`
  - Default Implementation:
    - None
- **validate_config**: A developer defined method that determines if a given connector config is valid:
  - Triggers:
    - A command with action `TetraScience.Connector.ValidateConfig` is received
      - sent by the platform when a user attempts to save connector config
  - Default implementation:
    - always returns `{"valid": true}`

*Idle and Disable/Shutdown methods*

- **shutdown**: A method called when the connector and its container will be stopped
  - Triggers:
    - A command with action `TetraScience.Connector.Shutdown` is received.
      - sent by the platform when a user disables the connector
  - Default implementation:
    - calls `on_shutdown`
    - stops metrics collection, heartbeat, and command listener tasks
- **on_shutdown**: A developer-defined hook that runs when the connector is stopping. Connector specific cleanup can usually be implemented here without overriding `shutdown`
  - Triggers:
    - A command with action `TetraScience.Connector.Shutdown` is received.
      - sent by the platform when a user disables the connector
  - Default Implementation:
    - None
- **on_stop**: A developer-defined hook that runs when the connector's operating status is set to `IDLE`
  - Triggers (any of the following):
    - A command with action `TetraScience.Connector.Stop` is received.
      - this corresponds to setting the connector operating status to `IDLE`
  - Default Implementation:
    - reloads connector config, which subsequently calls `on_connector_updated`

#### Additional `Connector` commands

The `Connector` class also supports some other commands. These can be sent using the [commands API](https://developers.tetrascience.com/reference/ag-create-command)


| Action Name                               | `Connector` Method Called                                 | Description                                                                                                                                                                                                                        | Triggers                                                                               | Side-Effects                                                                |
| ----------------------------------------- | --------------------------------------------- |------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------| -------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| TetraScience.Connector.ListCustomCommands | `handle_get_available_custom_commands`        | This method returns a list of available custom commands registered to the connector.                                                                                                                                               |                                                                                        |                                                                             |
| TetraScience.Connector.SetLogLevel        | `set_log_level`                               | This method is used to set the log level of the connector dynamically. Supported levels `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.                                                                                           | User sends a command to set the log level                                              | Adjusts the verbosity of logs without restarting the connector              |
| *custom commands*                         | *specified by `@register_command` decorators* | Custom commands registered using the `@register_command` decorator.                                                                                                                                                                |                                                                                        |                                                                             |

#### Custom commands

Custom commands are user-defined commands that can be registered by developers
to extend the functionality of a connector. This can be useful for implementing
capabilities that you want the connector to have, but only to use on demand. One
example would be ingesting historical data from a given time window for a connector
that typically only receives new data. Another example might be requests for the
connector to send information to a third-party system. This gives TDP pipelines
a way to call upon the connector to act on their behalf.

`Connector` implements a command listener that both listens to all the previously
mentioned standard commands, and also checks a connector-specific registry for
custom commands. Custom commands are registered using the `@register_command` decorator.
The decorator takes a string argument that corresponds to the `action` of the
command. The convention for action names is `TetraScience.Connector.<ConnectorName>.<CustomActionName>`,
as in the following example:

```python
from ts_sdk_connectors_python.custom_commands import register_command
from ts_sdk_connectors_python.connector import Connector

class MyConnector(Connector):
    @register_command("TetraScience.Connector.ExampleConnector.MyCustomAction")
    def my_custom_action(self, body: dict):
        print(f"Action called with body: {body}")
        return None
```

[Commands](docs/commands.md) contains further technical details on custom command and command registration.

The return type of the custom command method should be either `None`, a dictionary, or a string that can be converted into a dictionary.
Specifically, you can refer to the `ts_sdk_connectors_python.models.CommandResponseBody` type for more details.

### Polling

The SDK provides a `Poll` class that allows repeated execution of a target function at a specified interval.
This is useful for tasks that need to be performed periodically, such as checking the status of a resource or polling an API.

For more details on how to use the `Poll` class, refer to the [Polling Documentation](docs/poll.md).

## Logging

The SDK provides a logger to facilitate structured logging. This logger supports multi-threading, asynchronous operations, logger inheritance, and upload to CloudWatch.

Log messages are in JSON format for uptake into CloudWatch. The following are examples of log messages.

```text
{"level":"debug","message":"Loading TDP certificates from local volume /etc/tetra/tdp-cert-chain.pem","extra":{"context":"ts_sdk_connectors_python.AuthenticatedClientCreator"}}
{"level":"info","message":"TDP certificates loaded from local volume /etc/tetra/tdp-cert-chain.pem","extra":{"context":"ts_sdk_connectors_python.AuthenticatedClientCreator"}}
{"level":"info","message":"Client initialized","extra":{"context":"ts_sdk_connectors_python.tdp_api_base","orgSlug":"tetrascience-yourorg","connectorId":"3eca48c9-3eb2-4414-a491-a8dda151da50"}}
{"level":"info","message":"Starting metrics task: cpu_usage_metrics_provider","extra":{"context":"ts_sdk_connectors_python.metrics"}}
{"level":"info","message":"Starting metrics task: memory_used_metrics_provider","extra":{"context":"ts_sdk_connectors_python.metrics"}}
```

### Logger usage

The CloudWatch logger supports logger inheritance, allowing you to create child loggers that inherit the configuration
and context of their parent loggers. This is useful for organizing log messages by component or module.

The `get_logger` method will return a logger that inherits from the connector SDK's root logger. Simply give the logger
a useful name and begin using the logger. A new logger name will created by adding new suffix (see below).
Providing the `extra` argument will add additional information present in all log messages with the logger. The `extra`
argument can also be provided to any of the log methods (`info`, `debug`, `warning`, `error`, `critical`).

Example usage:

```python
from ts_sdk_connectors_python.logger import get_logger
# Create a parent logger
parent_logger = get_logger("parent_logger", extra={"foo": "bar"})

assert parent_logger.name == 'ts_sdk_connectors_python.parent_logger'

parent_logger.info('my message', extra={'baz': 'bazoo'})
```

```text
# expected log message
# note that 'foo' and 'baz' are included as 'extra'
# note that the logger name is also given in the 'extra.context'
{"level":"info","message":"my message","extra":{"context":"ts_sdk_connectors_python.parent_logger","foo":"bar","baz":"bazoo"}}
```

The following methods are provided to create logs at various levels:

```text
logger.debug('Use this for detailed debug information. This is the lowest level and by default not
 emitted by the logger')
logger.info('Use this for general info. This is the default level for connectors')
logger.warning('Use this for warnings')
logger.error('Use this for errors. Note the exc_info which can provide stack trace info', exc_info=True)
logger.critical('Use this for critical errors that cause failure')
```

You may also create child loggers by using the `get_child` method, which will just add another suffix to an existing
logger and merge provided `extra`.

```python
# Create a child logger that inherits from the parent logger
child_logger = parent_logger.get_child("child", extra={"baz": "qux"})
assert child_logger.name == 'ts_sdk_connectors_python.parent_logger.child_logger'

# Log messages using the child logger
child_logger.info("This is a message from the child logger")
```

```text
# note the extra is merged with the parent extra
{"level":"info","message":"my message","extra":{"context":"ts_sdk_connectors_python.parent_logger.child_logger","foo":"bar","baz":"qux"}}
```

### Setting log levels

To reduce the volume of logs, you can set the log level. The supported levels are `NOTSET`, `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`.
This can be done via the `set_root_connector_sdk_log_level` method:

```python
from ts_sdk_connectors_python.logger import set_root_connector_sdk_log_level

set_root_connector_sdk_log_level("DEBUG")
```

By default, all loggers made by `get_logger` will have an `NOTSET` log level, meaning they all inherit their effective
log level from the root connector SDK. It is therefore *not recommended* to set the log level for any child loggers.
Instead, use the `set_root_connector_sdk_log_level` method.

`Connector` also implements the command `TetraScience.Connector.SetLogLevel` which allows you to set the log level of the connector dynamically. Here is an example command request:

```json
{
  "payload": {
    "level": "DEBUG"
  },
  "action": "TetraScience.Connector.SetLogLevel",
  "targetId": "your-connector-id"
}
```

### CloudWatch logging and standalone connector support

If the connector is in standalone mode (meaning `CONNECTOR_TOKEN` env var is set), logs will get uploaded to AWS
CloudWatch in addition to getting logged to console. Logging and CloudWatch reporting occurs on a separate processing
thread apart from the main connector processing thread. Uploading to CloudWatch occurs in batches and whenever a batch
size is hit or on a set interval. Relevant envvars related to these settings can be found in `constants.py`.

The `CloudWatchReporter` class is responsible for managing the buffering and flushing of log events to AWS CloudWatch.
It handles the following tasks:

- Buffering log events.
- Flushing buffered log events to CloudWatch based on certain conditions (e.g., buffer size limit, flush interval).
- Managing the CloudWatch log stream and log group.
- Handling errors during the flushing process.

Flushing log events to AWS CloudWatch occurs for a number of reasons:

- The buffer reaches its size limit.
- The flush interval is reached.
- The flush limit is reached.
- The connector is started.
- The connector is stopped.
- An explicit flush is triggered.

## OpenAPI code generation

This project uses code generation to build client libraries for interacting with the data acquisition service in TDP based on the OpenAPI specification of the service. The generated code is placed in the `ts_sdk_connectors_python/openapi_codegen` directory.

**Typical users of the SDK will not need to generate this code.** For Tetra developers, details are available [here](ts_sdk_connectors_python/openapi_codegen/README.md)

### Using the generated API client

The generated API client is used within the `TdpApi` class to interact with the TDP REST API.
The `TdpApi` class provides asynchronous methods, while the `TdpApiSync` class provides synchronous methods.

#### Example usage

```python
from ts_sdk_connectors_python.tdp_api import TdpApi
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import SaveConnectorValueRequest

async def main():
    api = TdpApi()
    await api.init_client()

    connector_id = "your_connector_id"
    raw_data = [
        SaveConnectorValueRequest(
            key="a-string",
            value={"some_json_field": "some_secret_value"},
            secure=True
        )
    ]

    response = await api.save_connector_data(connector_id, raw_data)
    print(response)

# Run the main function in an async event loop
import asyncio
asyncio.run(main())
```

For synchronous usage, use the `TdpApiSync` class:

```python
from ts_sdk_connectors_python.tdp_api_sync import TdpApiSync
from ts_sdk_connectors_python.openapi_codegen.connectors_api_client.models import SaveConnectorValueRequest

def main():
    api = TdpApiSync()
    api.init_client()

    connector_id = "your_connector_id"
    raw_data = [
        SaveConnectorValueRequest(
            key="a-string",
            value={"some_json_field": "some_secret_value"},
            secure=True
        )
    ]

    response = api.save_connector_data(connector_id, raw_data)
    print(response)

    # retrieve parsed DTO object, if available
    print(response.parsed)

# Run the main function
main()
```

#### Retrieving connector data with filtering

The Python SDK supports server-side filtering when retrieving connector data. This allows you to efficiently retrieve only the data you need by specifying keys at the API level.

##### Using `TdpApi` (async)

```python
from ts_sdk_connectors_python.tdp_api import TdpApi

async def main():
    api = TdpApi()
    await api.init_client()

    connector_id = "your_connector_id"

    # Get all connector data (no filtering)
    all_data = await api.get_connector_data(connector_id)
    print(f"All data: {len(all_data.parsed.values)} items")

    # Get specific keys only (server-side filtering)
    filtered_data = await api.get_connector_data(
        connector_id,
        keys="key1,key2,key3"  # Comma-separated list of keys
    )
    print(f"Filtered data: {len(filtered_data.parsed.values)} items")

asyncio.run(main())
```

##### Using `TdpApiSync` (synchronous)

```python
from ts_sdk_connectors_python.tdp_api_sync import TdpApiSync

def main():
    api = TdpApiSync()
    api.init_client()

    connector_id = "your_connector_id"

    # Get specific keys only (server-side filtering)
    filtered_data = api.get_connector_data(
        connector_id,
        keys="key1,key2"
    )
    print(f"Filtered data: {len(filtered_data.parsed.values)} items")

main()
```

##### Using `Connector` class methods

The `Connector` class provides convenient methods that automatically use server-side filtering:

```python
from ts_sdk_connectors_python.connector import Connector
from ts_sdk_connectors_python.tdp_api import TdpApi

async def main():
    api = TdpApi()
    await api.init_client()

    connector = Connector(api)

    # Get specific values (uses server-side filtering automatically)
    values = await connector.get_values(["key1", "key2"])
    print(f"Retrieved {len(values)} values")

    # Get single value
    single_value = await connector.get_value("key1")
    if single_value:
        print(f"Value for key1: {single_value.value}")

    # Direct access to connector data with filtering
    data = await connector.get_values(
        keys=["key1", "key2"],
    )
    print(f"Direct access: {len(data)} items")

asyncio.run(main())
```

Refer to the `TdpApi` and `TdpApiSync` class methods for more details on available API interactions.

## Local testing with standalone connectors

For local development and testing, you can use standalone connectors to test your connector implementation against TDP resources while running your code locally. This approach allows you to:

- Test your connector logic without deploying to a Hub
- Debug and iterate quickly during development
- Validate your connector against real TDP services

### Prerequisites

1. **Build your local Docker image**: Ensure you have built a local Docker image of your connector
2. **Access to TDP environment**: You need access to a TDP organization and appropriate permissions
3. **Standalone installer**: Access to the TetraScience standalone connector installer

### Setup process

#### Step 1: build your local connector image

First, build your connector as a Docker image locally. This typically involves:

```bash
# Example build command (adjust based on your connector's Dockerfile)
docker build -t my-connector:local .
```

#### Step 2: use the standalone installer

1. Run the standalone connector installer provided by TetraScience
2. When prompted for the connector image during installation, **provide your local image name** instead of an official image:
   ```
   # Instead of using an official image like:
   # tetrascience/my-connector:v1.0.0

   # Use your local build:
   my-connector:local
   ```

3. The installer will:
   - Set up the necessary TDP resources (tokens, certificates, etc.)
   - Configure environment variables for standalone operation
   - Create the appropriate Docker run configuration pointing to your local image

#### Step 3: environment configuration

The standalone installer will configure the following key environment variables:

- `CONNECTOR_TOKEN`: Authentication token for standalone deployment
- `TDP_ENDPOINT`: TDP API endpoint
- `ORG_SLUG`: Your organization identifier
- `CONNECTOR_ID`: The connector instance ID
- Other TDP-specific configuration as needed

#### Step 4: running your local connector

After setup, your connector will run using your local Docker image but connect to real TDP services for authentication, data storage, and command processing.

#### Alternative: running containerless locally

It is also possible for testing to run the connector locally without Docker:

- Skip Step 1 above
- Get the connector token and standalone installer in Step 2, but do not run it
- From the `installer.sh` file, you can extract values for the environment variables (other than `CONNECTOR_TOKEN`, which you can get as part of Step 2) and export them. The necessary environment variables are those mentioned in [Configuring `TdpApi`](#configuring-tdpapi)
- In Step 4, run the entrypoint of the connector directly

### Important notes

- Ensure your local Docker image is built before running the standalone installer
- The standalone installer handles all TDP resource provisioning and configuration
- Your local connector will have the same capabilities as a Hub-deployed connector
- Use this method for development and testing; production deployments should use Hub or standalone deployment of the official image

## Running tests

Unit tests and integration tests are located in the `__tests__/unit` and `__tests__/integration` directories,
respectively. To run unit tests, execute:

```sh
poetry run pytest
```

To run integration tests against the TDP API, export the connector environment variables for tests and run:

```sh
poetry run pytest --integration
```

It is easiest to run the integration tests by following the procedure described in [Local testing with standalone connectors](#local-testing-with-standalone-connectors).

## Changelog

### v2.0.0

- **Breaking**: change connector helper methods to throw `ConnectorError` on unexpected API behavior instead of returning `None`
- For standalone connectors, capture logs before CloudWatch reporter initialization in buffer to be uploaded later
- Sort log events by timestamp before sending to CloudWatch
- Add filtering to `Connector.get_values`
- Add option to disable TLS verification to `TdpApi.create_httpx_instance`

### v1.0.1

- Add automatic batching to `Connector.get_files` and `Connector.save_files`
- Add necessary S3 metadata to support `destination_id` for file uploads

### v1.0.0

- Fix bug where proxy settings were loaded at wrong time from Hub
- Add synchronous init_client method for `TdpApiSync`


### v0.9.0

- Add enum of health status to `models.py`
- Add ability to read connector manifest file
- Add support for user agent strings
- Refactor SDK to use AWS class
- Update aioboto3 to use upstream fix
- Add health reporting to CloudWatch logger
- Move some methods from Node SDK `TdpClient` to Python `Connector` class
- Fix crash loops for connectors unable to start in RUNNING

### v0.8.0

- Add CI Pipeline to release PR builds to JFrog
- Add consistent AWS sessions through AWS class; fix cloud/hub/standalone deployment issues in v0.7.0
- ELN-661: Update Poll class to add default error handling and logging features

### v0.7.0

- Update README to include logger practices
- Add HTTP request timeouts and SQS request timeouts
- Fix bugs causing tdpApi.upload_file to fail with error when using additional checksums
- Fix bug where the SDK ignore envar AWS_REGION in client init
- Support missing ConnectorFileDto.errorCount

### v0.6.0

- Fix a 400 Bad Request error caused by the TDP API client having an `Authorization` header that conflicted with the S3 presigned URL authentication

### v0.5.0

- Fix bug where Connector.start fails when given an uninitialized TdpApi
- Improve logging in connector.start()

### v0.4.0

- Implement CloudWatchReporter and logger to provide consistent logging by the SDK for local and cloudwatch logs
- Fix bugs in parsing ConnectorFileDto objects which formerly resulted in raised exceptions
- Introduce partial standalone deployment support for AWS and logger initialization

### v0.3.0

- Add support to fetch connector JWT from AWS, allowing cloud connector deployment
- Use type SaveConnectorFilesRequest the signature of TdpApi.update_connector_files() and TdpApiSync.update_connector_files()
- Make CommandResponse.status optional to help with parsing messages from the command queue

### v0.2.0

- Add `upload_file` method to `TdpApi`, `TdpApiSync` and `Connector` classes
- Bug fix for command request and response data validation
- Bug fix for parsing the incoming command body for `validate_config_by_version`

### v0.1.0

- Initial version
