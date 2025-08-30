# InfraGPT - Your devops co-pilot 🤖 on Terminal

InfraGPT lets you interactively generate and execute infrastructure commands using large language models (LLMs) in your terminal.
InfraGPT works best with OpenAI GPT-4o and Anthropic Claude Sonet models.

![PyPI](https://img.shields.io/pypi/v/infragpt)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/priyanshujain/infragpt/deploy.yml)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/priyanshujain/infragpt/publish.yml)

<!-- [![asciicast](https://asciinema.org/a/w4YKOCP5zcYF0bSlZ2JSLczs8.svg)](https://asciinema.org/a/w4YKOCP5zcYF0bSlZ2JSLczs8) -->

![Alt Text](../docs/assets/infragpt.gif)



## Features

- **Infrastructure Commands**: Generate and execute infrastructure commands using natural language
- **Slackbot**: Integrate InfraGPT with Slack to generate commands from messages and take actions (coming soon)

## Installation

### Using pip

Using pip to install packages system-wide is [not recommended](https://peps.python.org/pep-0668/).
pip is a general-purpose package installer for both libraries and apps with no environment isolation. pipx is made specifically for application installation, as it adds isolation yet still makes the apps available in your shell: pipx creates an isolated environment for each application and its associated packages.

pipx does not ship with pip, but installing it is often an important part of bootstrapping your system.

Instead, install InfraGPT using `pipx` in the next section.

### Using pipx

```
# Install pipx if you don't have it
pip install --user pipx
pipx ensurepath

# Install infragpt
pipx install infragpt
```

### From Source

1. Clone the repository:
   ```
   git clone https://github.com/priyanshujain/infragpt.git
   cd infragpt
   ```

2. Install in development mode:
   ```
   pip install -e .
   ```

## Credentials Management

InfraGPT requires API keys to work. There are three ways to provide credentials, in order of priority:

### 1. Command Line Parameters

```bash
# Using OpenAI GPT-4o
infragpt --model gpt4o --api-key "your-openai-api-key"

# Using Anthropic Claude
infragpt --model claude --api-key "your-anthropic-api-key"
```

### 2. Configuration File

InfraGPT stores credentials in `~/.config/infragpt/config.yaml` and uses them automatically on subsequent runs. This file is created:
- When you provide credentials interactively
- Automatically on first run if environment variables are available
- When you use command line parameters

### 3. Environment Variables

Set one or more of these environment variables:

```bash
# For OpenAI GPT-4o
export OPENAI_API_KEY="your-openai-api-key"

# For Anthropic Claude
export ANTHROPIC_API_KEY="your-anthropic-api-key"

# Optionally specify the model
export INFRAGPT_MODEL="gpt4o"  # or "claude"
```

**Model Selection Rules**:
- If both API keys are set, InfraGPT uses OpenAI by default unless specified otherwise
- If only one API key is set, the corresponding model is used automatically
- If a model is explicitly selected (via command line or INFRAGPT_MODEL), the corresponding API key must be available

When environment variables are available, InfraGPT will automatically save the detected model and API key to the configuration file for future use.

If no credentials are found from any of these sources, if an empty API key is detected, or if an invalid API key is provided, InfraGPT will prompt you to select a model and enter your API key interactively at startup, before accepting any commands.

**API Key Validation:**
- The application validates API keys by making a small test request to the service provider
- When entering credentials interactively, API keys are validated immediately
- Invalid keys from environment variables or the config file are detected at startup
- The system will continue prompting until valid credentials are provided
- All validated credentials are automatically saved to the config file

## Usage

Launch InfraGPT in interactive mode:

```
infragpt
```

Once in interactive mode, enter natural language prompts at the prompt:

```
> create a new VM instance called test-vm in us-central1 with 2 CPUs
```

Specify the model to use:

```
infragpt --model claude
```

Use keyboard shortcuts in interactive mode:
- `Ctrl+D` to exit the application
- `Ctrl+C` to clear the current input and start a new prompt

### Command History

View your recent command history:

```
infragpt history
```

Limit the number of entries:

```
infragpt history --limit 20
```

Filter by interaction type:

```
infragpt history --type command_execution
```

Export your history to a file:

```
infragpt history --export history.jsonl
```

## Example Commands

- "Create a new GKE cluster with 3 nodes in us-central1"
- "List all storage buckets"
- "Create a Cloud SQL MySQL instance named 'mydb' in us-west1"
- "Set up a load balancer for my instance group 'web-servers'"

## Options

### Interactive Mode Options
- `--model`, `-m`: Choose the LLM model (gpt4o or claude)
- `--api-key`, `-k`: Provide an API key for the selected model
- `--verbose`, `-v`: Enable verbose output

## Contributing

For information on how to contribute to InfraGPT, including development setup, release process, and CI/CD configuration, please see the [CONTRIBUTING.md](CONTRIBUTING.md) file.
