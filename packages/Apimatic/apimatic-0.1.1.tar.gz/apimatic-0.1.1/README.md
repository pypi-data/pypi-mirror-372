# Apimatic

Universal API docs generator that scans your codebase (Flask, FastAPI, Django, Express) and produces `API_Docs.md` or `openapi.yaml`. Optionally enriches with a local LLM via **Ollama**.

## Install (Python)
```bash
pip install -e .
# or once published
# pip install Apimatic
CLI
Apimatic --src . --format markdown
# auto-detect frameworks from requirements.txt / pyproject.toml / package.json

Apimatic --src api --framework flask fastapi --format openapi --output openapi.yaml

Apimatic --src server --framework express --use-ollama --model llama3:instruct
```

Output
-	API_Docs.md — human-friendly Markdown
-	openapi.yaml — machine-readable OpenAPI 3.1

Ollama (optional)
Install Ollama, pull a model and run with --use-ollama.
ollama pull llama3:instruct

GitHub Action (optional)
Use the provided workflow to regenerate docs on push and commit.
```git
.github/workflows/api-docs.yml
```

npm wrapper (optional)
Publish npm-wrapper/ as a small CLI that invokes the Python module, so Node users can:
```
npm i -g Apimatic
Apimatic --src . --framework express
```

Roadmap
- Parsers: NestJS, Koa, Hapi, DRF viewsets, Spring Boot
- Deeper AST parsing for params/body schemas
- Test suite + fixtures for each framework
- OpenAPI components & schema inference

---

### 🤖 `.github/workflows/api-docs.yml`
```yaml
name: Generate API Docs

on:
  push:
    branches: [ "main" ]

jobs:
  docs:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install Apimatic
        run: |
          pip install .
      
      - name: Generate Markdown
        run: |
          Apimatic --src . --format markdown --output API_Docs.md || true

      - name: Generate OpenAPI
        run: |
          python -c "import yaml" 2>/dev/null || pip install pyyaml
          Apimatic --src . --format openapi --output openapi.yaml || true

      - name: Commit changes
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add API_Docs.md openapi.yaml || true
          git diff --cached --quiet && echo "No changes" || git commit -m "chore(docs): update API docs [auto]"
          git push || true
________________________________________
📦 npm-wrapper/package.json
{
  "name": "Apimatic",
  "version": "0.1.0",
  "description": "Node CLI wrapper for Apimatic (Python)",
  "bin": {
    "Apimatic": "index.js"
  },
  "author": "Matrixxboy",
  "license": "MIT"
}
```
### ▶️ npm-wrapper/index.js

```js
//!/usr/bin/env node
const { spawn } = require("child_process");

const args = process.argv.slice(2);
const proc = spawn(process.env.PYTHON || "python3", ["-m", "Apimatic", ...args], {
  stdio: "inherit",
});
proc.on("close", code => process.exit(code));
```