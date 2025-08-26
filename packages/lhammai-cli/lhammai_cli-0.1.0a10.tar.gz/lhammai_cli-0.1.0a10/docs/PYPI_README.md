<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/dpoulopoulos/lhammai-cli/refs/heads/main/assets/images/lhammai-cli-white.svg">
    <img alt="Lhammai CLI logo" src="https://raw.githubusercontent.com/dpoulopoulos/lhammai-cli/refs/heads/main/assets/images/lhammai-cli-black.svg" width="50%">
  </picture>
</div>

<br>

<div align="center">

[![License](https://img.shields.io/badge/license-apache%202.0-blue)](#license)
[![Tests](https://github.com/dpoulopoulos/lhammai-cli/actions/workflows/test.yml/badge.svg)](https://github.com/dpoulopoulos/lhammai-cli/actions/workflows/test.yml)
[![Publish to PyPI](https://github.com/dpoulopoulos/lhammai-cli/actions/workflows/release.yml/badge.svg)](https://github.com/dpoulopoulos/lhammai-cli/actions/workflows/release.yml)

</div>

<h3 align="center">✨ Interact with any LLM from your terminal</h3>

---

Lhammai CLI allows you to interact with any LLM directly from your terminal using a simple, intuitive interface.
Powered by the [`any-llm`](https://mozilla-ai.github.io/any-llm/) library, it seamlessly connects to various LLM
providers, including OpenAI, Anthropic, and local servers such as Ollama, llamafile, and others. For a full list of
supported providers, see the official [any-llm documentation](https://mozilla-ai.github.io/any-llm/providers/).

The name Lhammai comes from "[Lhammas](https://en.wikipedia.org/wiki/Lhammas),"
[Noldorin](https://en.wikipedia.org/wiki/Sindarin#Creation) for "account of tongues", a work of fictional
sociolinguistics, written by J. R. R. Tolkien in 1937.

## Getting Started

### Prerequisites

- [Python 3.13+](https://www.python.org/downloads/)
- [uv](https://github.com/astral-sh/uv)

### Installation

You can install the package from PyPI using pip (recommended):

```console
pip install "lhammai-cli[ollama]"
```

#### From Source

1. Clone the repository and navigate to the source directory:
   ```console
   git clone https://github.com/dpoulopoulos/lhammai-cli.git && cd lhammai-cli
   ```

2. Install the dependencies using `uv`:
   ```console
   uv sync --group ollama
   ```

3. Activate the virtual environment:

   ```console
   source .venv/bin/activate
   ```

> This installs the necessary dependencies to communicate with a local model via Ollama.

### Usage

To begin, you'll need to run the Ollama server. For this example, you can use Docker for a quick setup.

> This approach has some limitations, especially on a Mac. Since Docker Desktop doesn't support GPUs, it's better to run
> Ollama as a standalone application if you're using a Mac. For more detailed instructions, check the official
> [Ollama documentation](https://github.com/ollama/ollama/tree/main/docs).

1. Run the following command to start the Ollama server in a Docker container:

    a. CPU only:
    ```console
    docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    ```

    b. Nvidia GPU:
    ```console
    docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
    ```

2. Run a model:

    ```console
    docker exec -it ollama ollama run gemma3:4b
    ```

3. Interact with the model:

    ```console
    lhammai Hello!
    ```

> Configure your application by creating a `.env` file in the root directory and adding your options:
> `cp .default.env .env`

You can also pipe content to `lhammai` from standard input. This is useful for analyzing logs, summarizing files, etc.:

```console
cat dev.log | lhammai -p "explain:"
```

# License

See the [LICENSE](LICENSE) file for details.
