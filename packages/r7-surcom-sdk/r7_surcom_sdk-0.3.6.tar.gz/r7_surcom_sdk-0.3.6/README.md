# Surface Command SDK

The `surcom-sdk` provides tools to develop Surface Command data connectors for the Rapid7 platform.

## Installation
* To install the `surcom-sdk`, run:

  ```
  pip install r7-surcom-sdk
  ```

* To verify the installed version, run:

  ```
  surcom --version
  ```

* To install the SDK with the dependencies needed to debug a connector, run:
  ```
  pip install 'r7-surcom-sdk[debug]'
  ```

## Configuration
* Once installed, use the `config init` command to setup the `surcom-sdk`:

  ```
  surcom config init
  ```

## Documentation
* All SDK commands have detailed help hints. Append `--help` to any command to view them:
  ```
  surcom connector --help
  ```