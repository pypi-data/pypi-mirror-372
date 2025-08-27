# Apimatic 🚀  

[![Matrixxboy](https://img.shields.io/badge/github-Matrixxboy-purple.svg)](https://github.com/Matrixxboy)
[![PyPI version](https://badge.fury.io/py/apimatic.svg)](https://pypi.org/project/apimatic/)
[![Downloads](https://static.pepy.tech/badge/apimatic)](https://pepy.tech/project/apimatic)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-blue)](https://pypi.org/project/apimatic/)
[![License](https://img.shields.io/pypi/l/apimatic.svg)](https://github.com/Matrixxboy/Apimatic/blob/main/LICENSE)


A tool to **automatically generate beautiful and comprehensive API documentation** (Markdown/OpenAPI) from your source code.  
Supports **Flask, FastAPI, and more frameworks** with optional **AI-powered enhancements via Ollama**.  

---

## 📦 Installation

```bash
pip install apimatic
````

Upgrade to the latest version:

```bash
pip install --upgrade apimatic
```

---

## ⚡ Usage

```bash
Apimatic [-h] [--src SRC] [--framework [FRAMEWORK ...]] [--format {markdown,openapi}] 
         [--output OUTPUT] [--use-ollama] [--model MODEL]
```

---

## 🔑 Options

| Option                        | Description                                                                      |
| ----------------------------- | -------------------------------------------------------------------------------- |
| `-h, --help`                  | Show help message and exit                                                       |
| `--src SRC`                   | Root directory of the project to scan (Default: current directory)               |
| `--framework [FRAMEWORK ...]` | Force a specific framework (`flask`, `fastapi`, etc.). If omitted, auto-detected |
| `--format {markdown,openapi}` | Output format (`markdown` or `openapi`) – Default: `markdown`                    |
| `--output OUTPUT`             | Path for the generated output file (Default: `API_Docs.md` or `openapi.yaml`)    |
| `--use-ollama`                | Enhance generated docs with descriptions from a local Ollama model               |
| `--model MODEL`               | Ollama model for enhancement (e.g., `llama3:instruct`). Requires `--use-ollama`  |

---

## 📝 Examples

Generate Markdown docs from the current project:

```bash
Apimatic --src . --format markdown --output API_Docs.md
```

Generate OpenAPI spec:

```bash
Apimatic --src . --format openapi --output openapi.yaml
```

Force framework detection (Flask):

```bash
Apimatic --src ./my_flask_app --framework flask
```

Enhance documentation with AI (Ollama model):

```bash
Apimatic --src . --use-ollama --model llama3.2:1b
```

---

## 🤖 Recommended Ollama Models (1–2 GB)

When using `--use-ollama`, you can choose a local model for API explanations.
Here are lightweight models that run well (1–2 GB range):

| Model         | Size    | Why Use It                                                                  |
| ------------- | ------- | --------------------------------------------------------------------------- |
| `llama3.2:1b` | \~1.3GB | Fast, nimble, and great for generating clear API explanations (recommended) |
| `gemma2:2b`   | \~1.6GB | Slightly larger, richer outputs, good balance of quality and size           |
| `dolphin-phi` | \~1.6GB | Alternative small model with solid reasoning ability                        |
| `orca-mini`   | \~1.9GB | Bigger (3B params) but still under 2GB; more context-aware                  |
| `moondream2`  | \~0.8GB | Ultra-light, very fast, but less detailed                                   |

👉 **Recommended Default**: `llama3.2:1b` – best speed + clarity tradeoff.

Example:

```bash
Apimatic --src . --use-ollama --model llama3.2:1b
```

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo, make your changes, and submit a PR.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
