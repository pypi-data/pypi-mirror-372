# 🤖 AI Automated Code Repair Agent

![AI Code Repair Agent Banner](https://placehold.co/1200x300/0f172a/ffffff?text=AI+Automated+Code+Repair+Agent&font=raleway)

**AI Automated Code Repair Agent** is a professional, autonomous CLI tool that executes Python scripts, detects crashes, and uses an AI-driven workflow to analyze, repair, and **securely verify fixes** before recommending them. It packages everything you need—from intelligent error parsing to isolated Docker-based verification—so you can point it at a script and get reliable, reproducible results.

**PyPI Package:** [**ai-code-repair-agent**](https://pypi.org/project/ai-code-repair-agent/)

---

## ✨ Core Features

- **🤖 Autonomous End-to-End Workflow:** Run `agent <script.py>` and let the tool handle execution, crash detection, analysis, patching, and reporting.
- **🧠 AI-Powered Code Generation (Gemini):** Sends rich error context to Google's **Gemini LLM** to propose logical, high-quality fixes—not just syntax band-aids.
- **🛡️ Secure Sandbox Verification:** Builds an **isolated Docker container** on the fly, runs tests, and **accepts only verified solutions**.
- **🔮 Auto-Dependency & Environment Discovery:** Inspects the target script to infer third‑party dependencies and auto‑generate `requirements.txt` and a `Dockerfile`.
- **🎯 Environment-Aware Diagnostics:** Distinguishes code bugs from environment issues (e.g., **ModuleNotFoundError**) and recommends precise `pip install` commands when appropriate.
- **📦 Professional CLI Experience:** Distributed via PyPI with a user-friendly `agent configure` command for easy setup and a built-in Docker prerequisite check.

---

## 🧭 Decision Workflow

### First-Time User Setup

```mermaid
graph TD
    A[New User] --> B[pip install ai-code-repair-agent];
    B --> C[agent configure];
    C --> D[Enters API Key];
    D --> E[✅ Agent is ready to use];
```

### Main Repair Workflow

```mermaid
graph TD
    A[User executes `agent <script_path>`] --> B{Docker Running?};
    B -- No --> C[❌ End: Advise user to start Docker];
    B -- Yes --> D[ProcessRunner executes script];
    D --> E{Crash Detected?};
    E -- No --> F[✅ End: Success];
    E -- Yes --> G[ErrorParser analyzes traceback];
    G --> H{Error Type?};
    H -- ModuleNotFoundError --> I[👩‍🏫 Reporter advises `pip install` & exits];
    H -- Other Error --> J[ContextManager retrieves faulty function];
    J --> K[AICore sends context to Gemini LLM];
    K --> L[Receives proposed code fix];
    L --> M[🛡️ SandboxVerifier begins test];
    M --> N{Test Passed?};
    N -- Yes --> O[🎉 Reporter shows success & diff];
    N -- No --> P[❌ Reporter shows failure];

    style C fill:#e63946,stroke:#333,stroke-width:2px
    style I fill:#f9f,stroke:#333,stroke-width:2px
```

---

## 🏗️ System Architecture

This project is modular for clarity, testability, and extensibility.

- **`agent/cli.py`** — Orchestrator & CLI (`argparse`), handles `configure` command, Docker prerequisite check, and full workflow.
- **`agent/process_runner.py`** — Executes target scripts (`subprocess`), captures stdout/stderr, determines crash state.
- **`agent/error_parser.py`** — Parses Python tracebacks into structured data via regex.
- **`agent/context_manager.py`** — Extracts faulty function context using `ast` for high-signal AI prompts.
- **`agent/ai_core.py`** — Prompts and calls **Google Gemini**, securely loading API key from a `.env` in the user's home directory.
- **`agent/sandbox_verifier.py`** — Uses Docker SDK to build sandbox environments, apply patches, and verify.
- **`agent/reporter.py`** — Provides human-friendly output with **colorama** and clean diffs.

---

## 🛠️ Tech Stack

| Category          | Technology                                                                         |
| ----------------- | ---------------------------------------------------------------------------------- |
| **Core Language** | Python 3.9+                                                                        |
| **Execution**     | `subprocess`, `tempfile`, `pathlib`                                                |
| **Analysis**      | `ast`, `inspect`, `re`, `traceback`, `difflib`, `stack-data`                       |
| **AI**            | Google Gemini via `google-generativeai`                                            |
| **Sandboxing**    | Docker & Docker SDK for Python; auto-generated `Dockerfile` and `requirements.txt` |
| **CLI & UX**      | `argparse`, `colorama`, interactive `agent configure` command                      |
| **Packaging**     | PyPI with `pyproject.toml`, versioned CLI entry point                              |

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Docker Desktop:** Required for creating isolated sandboxes. [Download Docker Desktop](https://www.docker.com/products/docker-desktop).

### Installation & Configuration

```bash
pip install ai-code-repair-agent
agent configure
```

---

## 🧪 Usage

```bash
agent path/to/your/buggy_script.py
agent path/to/script_with_args.py --input data.csv --output results.json
```

---

## 🧩 Design Principles

- **Safety First:** AI-generated code is **never** trusted without sandbox verification.
- **Minimal Friction:** One-time setup, then zero-config runs.
- **Clear Boundaries:** Distinguishes environment issues from logic bugs.
- **Modular & Extensible:** Clean interfaces for easy customization and future enhancements.
- **Reproducible:** Dockerized tests ensure consistent behavior across environments.

---

## 🔍 Example Module Layout

```
ai_code_repair_agent/
└─ agent/
   ├─ __init__.py
   ├─ cli.py              # CLI orchestrator, configure command, Docker check
   ├─ process_runner.py   # Run target script, capture outputs
   ├─ error_parser.py     # Parse tracebacks
   ├─ context_manager.py  # Extract faulty function via AST
   ├─ ai_core.py          # Prompt & call Gemini, load API key
   ├─ sandbox_verifier.py # Build Docker envs & verify
   └─ reporter.py         # Colorized results & diffs
```

---

## 🧱 Security & Privacy

- **No source exfiltration:** Only error-specific context is sent to the AI.
- **Ephemeral sandboxes:** Containers are temporary and removed post-execution.
- **Secrets management:** API keys securely stored in a `.env` file in your home directory.

---

## 📜 License

Distributed under the **MIT License**. See `LICENSE` for details.

---

## 👤 Author

**Darshan S**

- GitHub: [@darshan0106](https://github.com/darshan0106)
- LinkedIn: [Darshan Sivakumar](https://www.linkedin.com/in/darshan-sivakumar)
