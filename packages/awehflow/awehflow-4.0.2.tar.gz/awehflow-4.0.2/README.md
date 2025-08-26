# awehflow

![coverage report](https://gitlab.com/spatialedge/awehflow/badges/master/coverage.svg)
![pipeline status](https://gitlab.com/spatialedge/awehflow/badges/master/pipeline.svg)

**awehflow** is a configuration-driven framework for Apache Airflow that dynamically generates DAGs from simple HOCON or YAML files. It comes with built-in metrics, logging, and alerting to streamline your data orchestration.

## Core Concepts

- **Configuration-Driven**: Define complex DAGs using a clear, hierarchical configuration. No need to write repetitive Python code for each pipeline.
- **Dynamic DAG Generation**: **awehflow** automatically constructs and orchestrates Airflow DAGs based on your configurations.
- **Built-in Observability**: Comes with out-of-the-box event handlers for persisting metrics to a database and alerters for notifications on pipeline status.
- **Extensible**: Easily add your own custom event handlers and alerters to integrate with any service.

## Getting Started

- [**Getting Started Guide**](./docs/getting-started.md): A step-by-step guide on how to get your first **awehflow** pipeline up and running.

## Configuration Reference

- [**Configuration Guide**](./docs/config-files.md): A detailed walkthrough of the configuration system.

## Custom Operators and Sensors

**awehflow** includes a collection of custom operators and sensors to extend Airflow's functionality. While these custom operators provide specialized capabilities, **awehflow** is fully compatible with all standard Airflow operators. You can use any operator available in your Airflow environment by referencing its fully qualified class name in your configuration.

- [**Operators Guide**](./docs/operators): Detailed documentation for all custom operators.
- [**Sensors Guide**](./docs/sensors.md): Detailed documentation for all custom sensors.

## Command-Line Interface (CLI)

**awehflow** includes a CLI for generating and validating configurations.

- [**CLI Documentation**](./awehflow_cli/README.md): A complete reference for all CLI commands.

## Advanced Features

### Event Handlers & Alerters

**awehflow** has a built-in event system that allows you to run custom code in response to pipeline events. Alerters are a special type of event handler designed for sending notifications.

- [**Alerts Guide**](./docs/alerts.md): A detailed guide on how to configure and use alerters.

## Troubleshooting

- [**Troubleshooting Guide**](./docs/troubleshooting-debugging.md): Solutions for common issues and debugging tips.

## For Developers

### Development Environment Setup
To contribute to **awehflow**, follow these steps to set up a development environment for a specific Airflow version.

1.  **Install Miniconda**: Follow the official instructions.
2.  **Create Conda Environment (x86 on Mac ARM)**: If you are on an ARM-based Mac, create an x86-emulated environment. Add this function to your `.zsh