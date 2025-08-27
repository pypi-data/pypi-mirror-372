# Antigranular Enterprise: Secure, Privacy-Preserving Data Science in Jupyter and Python Environments

The `antigranular_enterprise` package is a specialized client designed for secure and private interactions with the Antigranular Enterprise platform. It supports data analysis and model training in both Jupyter notebook and standard Python interactive shell environments, emphasizing privacy and data protection. This documentation provides guidance on installing, configuring, and utilizing the client package to fully integrate the capabilities of Antigranular Enterprise into your data science workflows.

## Installation

To integrate Antigranular Enterprise with your environment, install the package using pip:

```bash
pip install antigranular_enterprise
```

This command installs the `antigranular_enterprise` package and its necessary dependencies, setting up your environment for secure, privacy-preserving data science operations.

## Configuration

### Initial Configuration

Configure the package to communicate with your Antigranular Enterprise instance. Essential parameters include:

- **AGENT Jupyter Server URL**: URL for the proxy server routing requests to the Antigranular platform.
- **AGENT Jupyter Server Port**: Port on which the proxy listens.
- **AGENT Console URL**: URL for accessing the Antigranular management console.
- **TLS Enabled**: Set to `true` if TLS is enabled for the proxy to ensure secure communication.

### Configuration Methods

Configure your environment to interact with the Antigranular Enterprise platform in a way that best suits your setup and preferences.

#### Direct Configuration via UI URL

This is the simplest and recommended method for configuration:

1. **Navigate to the UI Configuration Page**: Open your browser and visit `https://<ui_url>/config/client`.
2. **Copy the Configuration Code**: The page will display a pre-formatted configuration snippet.
3. **Execute the Configuration Code**: Run the copied code in your environment to automatically load the configuration.

   ```python
   import antigranular_enterprise as ag
   ag.load_config("https://<ui_url>/config/client", profile='default')
   ```

#### Using `write_config`

Alternatively, you can manually set up the configuration:

1. **Import the Package**: Begin by importing `antigranular_enterprise`.

   ```python
   import antigranular_enterprise as ag
   ```

2. **Write the Configuration**:

   Save your configuration settings using the `write_config` method:

   ```python
   ag.write_config(profile='default', yaml_config="""
   agent_jupyter_url: <Jupyter URL>
   agent_jupyter_port: <Jupyter Port>
   agent_console_url: <Console URL>
   tls_enabled: true
   """)
   ```

   Replace placeholders with the appropriate values for your environment.

## Client Login and Execution

### Jupyter Notebook

#### Login

Log in to the Antigranular Enterprise services from Jupyter notebooks:

```python
client = ag.login("<api_key>")
```

After entering your API key, a UI notification or link will prompt you for approval. Once approved, your session starts, allowing secure interactions with the Antigranular platform.

#### Executing Commands

In Jupyter notebooks, use the `%%ag` magic command to execute code securely on the server:

```python
%%ag
ag_print("hello", "world")
```

### Python Interactive Shell

#### Login and Execution Script

This script demonstrates a simple login to the Antigranular server, executes a basic print command, and displays the server's response directly.

**script.py**:

```python

import antigranular_enterprise as ag

# Login and execute a remote command
session = ag.login("Your_API_Key")
response = session.execute("ag_print('Hello', 'World!')")
print(response)

# Export a server variable to the local environment, passing the globals() dictionary to the execute method
session.execute("var = 'test'; export(var, 'varlocal')", globals())
print(varlocal)  # Outputs: test

# Terminate the session
terminate_session_response = session.terminate_session()
print(terminate_session_response)  # Outputs: {'status': 'ok'}

```
Output:
```plaintext
> python script.py
Connected to Antigranular server session id: <masked>
Hello World!
Setting up exported variable in local environment: varlocal
test
{'status': 'ok'}
```

### Supported Methods for both Jupyter and Non-Jupyter Environments

All package methods are supported within these sessions, including:

- **`interrupt_kernel()`**: Interrupts the currently running kernel.
- **`terminate_session()`**: Terminates the session and cleans up resources.
- **`privacy_odometer()`**: Returns the amount of epsilon and delta used.
- **`private_import()`**: Imports a user-provided model or dataset into the AG server securely.

## Features and Usage

The `antigranular_enterprise` package offers a suite of features for secure data analysis and model training, with robust support for privacy regulations. It is designed to integrate seamlessly into Jupyter notebooks and Python interactive shells, enhancing the data science workflow with privacy-preserving capabilities.

For further information or support, please consult the Antigranular Enterprise platform's detailed documentation or contact our support team directly.