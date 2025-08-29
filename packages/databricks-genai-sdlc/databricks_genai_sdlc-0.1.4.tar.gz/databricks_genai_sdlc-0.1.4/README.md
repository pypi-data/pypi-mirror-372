# databricks-genai-sdlc

A Python library to automate the **Software Development Life Cycle (SDLC)** on **Databricks** using **Generative AI**.  
It can generate **documents, PySpark/SQL code, and test cases**, and push outputs directly to **GitHub**.

---

## 🚀 Features

- 📄 **Document Generator** – Create High Level Design (HLD) & Low Level Design (LLD).  
- 🏗️ **Code Generator** – Auto-generate SQL / PySpark code.  
- ✅ **Test Generator** – Build unit tests with sample data.  
- 🔄 **GitHub Integration** – Push code & documents to your repo/branch automatically.  
- 🔑 Works with **Databricks PAT**, **GitHub Tokens**, and **workspace details**.  

---

## 📦 Installation

Install from PyPI:

```bash
pip install databricks-genai-sdlc
```

Upgrade to the latest version:

```bash
pip install --upgrade databricks-genai-sdlc
```

---

## 🛠️ Basic Usage

```python
from sdlc_databricks import SDLC_DATABRICKS

sdlc = SDLC_DATABRICKS(
    GITHUB_API='https://api.github.com',
    GITHUB_REPO='your-repo-name',                     # e.g., org/project
    GITHUB_BRANCH='feature-001',                      # target branch for commits
    GITHUB_TOKEN='your-github-token',                 # GitHub PAT
    FILE_PATH='volume/requirements/BRD.pdf',          # Path to input BRD/document
    DOC_GENERATOR_MODEL='databricks-llm',             # Databricks-hosted LLM for docs
    CODE_GENERATOR_MODEL='databricks-llm',            # Databricks-hosted LLM for code
    DATABRICKS_PAT='your-databricks-pat',             # Databricks token
    WORKSPACE_URL='https://<your-workspace>.cloud.databricks.com',
    GITHUB_USERNAME='your-github-username',
    LANGUAGE='SQL'                                    # or 'PySpark'
)

sdlc.run_sdlc()
```

This will:  
1. Load the input requirement file (`FILE_PATH`).  
2. Generate **documents, code, and test cases**.  
3. Push everything automatically to the specified **GitHub repo & branch**.  

---

## 🔑 Authentication Setup

1. **Databricks PAT**  
   - Generate from: *Databricks → User Settings → Access Tokens*.  

2. **GitHub Token**  
   - Generate from: *GitHub → Settings → Developer Settings → Personal Access Tokens*.  

3. **GitHub Repo & Branch**  
   - Repo in format `org/repo`.  
   - Branch must exist (or will be created).  

---

## 📂 Example Project Structure (PySpark)

When you run `sdlc.run_sdlc()` with `LANGUAGE='PySpark'`, the library generates a **modular PySpark project** with the following structure:

```
project_name/
│
├── src/
│   ├── __init__.py
│   ├── module1.py             # Auto-generated PySpark/SQL code
│   └── module2.py             # Additional logic/utilities
│
├── tests/
│   ├── test_module1.py        # PyTest unit tests for module1
│   └── test_module2.py        # PyTest unit tests for module2
│
├── data/                      # Sample input data (if applicable)
├── requirements.txt           # List of dependencies (minimal)
├── pyproject.toml             # Project metadata (name, version, description, authors)
├── README.md                  # Auto-generated usage instructions
├── LICENSE
└── .gitignore                 # Git ignore rules
```

👉 This structure follows **best practices**:  
- `src/` → source code (clean separation).  
- `tests/` → test cases aligned with modules.  
- `data/` → optional sample datasets for testing pipelines.  
- `requirements.txt` / `pyproject.toml` → lightweight dependency + project metadata.  
- `README.md`, `LICENSE`, `.gitignore` → standard project hygiene.  

---

## 🎯 End-to-End Example

```python
from sdlc_databricks import SDLC_DATABRICKS

sdlc = SDLC_DATABRICKS(
    GITHUB_API='https://api.github.com',
    GITHUB_REPO='myorg/myrepo',
    GITHUB_BRANCH='feature-sdlc',
    GITHUB_TOKEN='ghp_xxx123',
    FILE_PATH='volume/requirements/BRD.pdf',
    DOC_GENERATOR_MODEL='databricks-llm',
    CODE_GENERATOR_MODEL='databricks-llm',
    DATABRICKS_PAT='dapi123...',
    WORKSPACE_URL='https://adb-1234567890.11.azuredatabricks.net',
    GITHUB_USERNAME='mygithubid',
    LANGUAGE='PySpark'
)

sdlc.run_sdlc()
```

---

## ❓ FAQs

**Q. Which languages are supported?**  
- SQL  
- PySpark  

**Q. Where are outputs stored?**  
- Locally under the project folder (`src/`, `tests/`, etc.)  
- Also pushed to GitHub (repo + branch specified).  

**Q. What models can I use?**  
- Only **Databricks-hosted LLM models** are supported.  

---

## 📌 Support

For issues and feature requests, please raise a ticket in the project repository.  
