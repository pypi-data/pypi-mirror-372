# Hive-CLI

Hive-CLI is a command-line interface for managing and deploying Hive agent and experiments on Kubernetes and other platforms.

```bash
     ███          █████   █████  ███
    ░░░███       ░░███   ░░███  ░░░
      ░░░███      ░███    ░███  ████  █████ █████  ██████
        ░░░███    ░███████████ ░░███ ░░███ ░░███  ███░░███
         ███░     ░███░░░░░███  ░███  ░███  ░███ ░███████
       ███░       ░███    ░███  ░███  ░░███ ███  ░███░░░
     ███░         █████   █████ █████  ░░█████   ░░██████
    ░░░          ░░░░░   ░░░░░ ░░░░░    ░░░░░     ░░░░░░
```

## Installation

### Install via pip (Not-Available Yet)

```bash
pip install hive-cli
```

### Install from source

```bash
source start.sh
```

## How to run

**Note**: Hive-CLI reads the configuration from a yaml file, by default it will look for the `~/.hive/sandbox-config.yaml`. You can also specify a different configuration file using the `-f` option. Refer to the [config.yaml](./config.yaml) for examples.

Below we assume that you have a `~/.hive/sandbox-config.yaml` file.

### Edit the experiment

`Edit` command will open the configuration file in your default editor (e.g., vim, nano, etc.) for you to modify the experiment configuration. You can also specify a different editor using the `EDITOR` environment variable, by default it will use `vim`.

```bash
hive edit config
```

### Create an experiment

```bash
hive create exp my-experiment
```

### List experiments

```bash
hive show exps
```

### Visit Dashboard

```bash
hive dashboard
```

### Delete an experiment


```bash
hive delete exp my-experiment
```

### More

See `hive -h` for more details.

## Development

**Note**: Hive-CLI will read the `.env` file to load logging configurations. Refer to the `.env.example` file for examples.

### Debugging

Change the log level in `.env` file to `DEBUG` to see more detailed logs.
