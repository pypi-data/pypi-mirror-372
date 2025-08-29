# Apimatic 🚀  

[![Matrixxboy](https://img.shields.io/badge/github-Matrixxboy-purple.svg)](https://github.com/Matrixxboy)
[![PyPI version](https://badge.fury.io/py/Apimatic.svg)](https://pypi.org/project/Apimatic/)
[![Downloads](https://static.pepy.tech/badge/Apimatic)](https://pepy.tech/project/Apimatic)
[![Python Version](https://img.shields.io/badge/python-%3E%3D3.9-blue)](https://pypi.org/project/Apimatic/)
[![License](https://img.shields.io/pypi/l/Apimatic.svg)](https://github.com/Matrixxboy/Apimatic/blob/main/LICENSE)


A tool to **automatically generate beautiful and comprehensive API documentation** (Markdown/OpenAPI) from your source code.  
Supports **Flask, FastAPI, and more frameworks** with optional **AI-powered enhancements via Ollama, OpenAI, Google Gemini, and Groq**.  

---

## 📦 Installation

```bash
pip install Apimatic
```

Upgrade to the latest version:

```bash
pip install --upgrade Apimatic
```

---

## ⚡ Usage

Apimatic now uses commands to separate actions.

**1. Generate Documentation:**
```bash
apimatic generate [OPTIONS]
```

**2. Configure API Keys:**
```bash
apimatic config [OPTIONS]
```

---

## 🔑 Configuration

To use AI enhancements from providers like OpenAI, Google Gemini, or Groq, you must set an API key.

```bash
# Set your OpenAI API key
apimatic config --set-openai-key YOUR_API_KEY

# Set your Google Gemini API key
apimatic config --set-gemini-key YOUR_API_KEY

# Set your Groq API key
apimatic config --set-groq-key YOUR_API_KEY
```
The key will be stored securely in your home directory.

---

## ⚙️ Generation Options

| Option | Description |
| --- | --- |
| `-h, --help` | Show help message and exit |
| `--src SRC` | Root directory of the project to scan (Default: current directory) |
| `--framework [FRAMEWORK ...]` | Force a specific framework (`flask`, `fastapi`, etc.). If omitted, auto-detected |
| `--format {markdown}` | Output format (Default: `markdown`) |
| `--output OUTPUT` | Path for the generated output file (Default: `API_Docs.md`) |
| `--use-ollama` | Enhance with a local Ollama model |
| `--ollama-model MODEL` | Ollama model to use (e.g., `phi3:mini`) |
| `--use-openai` | Enhance with an OpenAI model |
| `--openai-model MODEL` | OpenAI model to use (e.g., `gpt-4o-mini`) |
| `--use-google-gemini` | Enhance with a Google Gemini model |
| `--google-gemini-model MODEL` | Gemini model to use (e.g., `gemini-1.5-flash`) |
| `--use-groq` | Enhance with a Groq model |
| `--groq-model MODEL` | Groq model to use (e.g., `llama3-8b-8192`) |

---

## 📝 Examples

**Basic Generation:**
```bash
# Generate Markdown docs from the current project
apimatic generate --src . --output API_Docs.md
```

**Force Framework:**
```bash
# Force detection for a Flask app
apimatic generate --src ./my_flask_app --framework flask
```

**AI-Enhanced Documentation:**

First, set your key:
```bash
apimatic config --set-openai-key sk-xxxxxxxx
```
Then, generate with enhancement:
```bash
# Use OpenAI's gpt-4o-mini model
apimatic generate --src . --use-openai --openai-model gpt-4o-mini

# Use Google Gemini
apimatic generate --src . --use-google-gemini

# Use Groq's fast Mixtral model
apimatic generate --src . --use-groq

# Use a local Ollama model
apimatic generate --src . --use-ollama --ollama-model phi3:mini
```

---

## 🤖 Recommended AI Models

| Provider | Recommended Model | Notes |
| --- | --- | --- |
| **Ollama (Local)** | `phi3:mini`, `llama3:8b` | Fast, free, and runs on your machine. Great for privacy. |
| **OpenAI** | `gpt-4o-mini` | Excellent balance of cost, speed, and intelligence. |
| **Google Gemini** | `gemini-1.5-flash` | Fast and cost-effective model from Google. |
| **Groq** | `llama3-8b-8192` | Incredibly fast inference speeds. |

---

## 🤝 Contributing

Contributions are welcome! Please fork the repo, make your changes, and submit a PR.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
