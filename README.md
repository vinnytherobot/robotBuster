# 🤖 RobotBuster v2.1

![RobotBuster Banner](assets/banner.png)

**RobotBuster** is a modern, ultra-fast, and professional directory brute-force tool. Built for scalability, performance, and developer collaboration.

---

## ✨ Features

- ⚡ **Asynchronous Core:** Powered by `httpx` and `asyncio` for maximum concurrent throughput.
- 🎨 **Rich CLI:** Professional terminal interface with real-time progress bars and formatted tables.
- 🔍 **Smart Calibration:** Intelligent "Wildcard 404" detection to eliminate false positives.
- 📐 **Scalable Architecture:** Modular design (Core, CLI, Utils, Models) for easy extension.
- 🛡️ **Built-in Quality:** Full type hinting (MyPy), automated linting (Ruff/Black), and robust test suite.
- 📦 **Dev-Friendly:** Integrated with `pre-commit`, `hatch`, and GitHub Actions.

---

## 🚀 Installation

### For Users
```bash
pip install robotbuster
```

### For Developers
1. Clone the repository:
```bash
git clone https://github.com/vinnytherobot/robotBuster.git
cd robotBuster
```

2. Install in editable mode with dev dependencies:
```bash
pip install -e .[dev,test]
```

3. Setup pre-commit hooks:
```bash
pre-commit install
```

---

## 🛠️ Usage

```bash
# Basic scan
robotbuster scan https://example.com -w common.txt

# Ultra-fast scan with high concurrency
robotbuster scan https://example.com -w common.txt -t 50

# Filter specific status codes
robotbuster scan https://example.com -w common.txt -s 200,403,301

# Save results to a file
robotbuster scan https://example.com -w common.txt -o results.txt
```

### Command Help
```console
$ robotbuster scan --help

 Usage: robotbuster scan [OPTIONS] TARGET

 Scan a target URL for hidden directories and routes.

 Arguments:
   TARGET  Target URL to scan (e.g., https://example.com)  [required]

 Options:
   -w, --wordlist PATH      Path to wordlist file  [required]
   -t, --tasks INTEGER      Number of concurrent requests  [default: 20]
   -s, --status TEXT        Comma-separated status codes to filter (default: 200,204,301,302,307,401,403)
   -o, --output PATH        Output file to save found routes
   -T, --timeout FLOAT      Request timeout in seconds  [default: 10.0]
   -d, --delay FLOAT        Delay between requests in seconds  [default: 0.0]
   -ua, --user-agent TEXT   Custom User-Agent string  [default: RobotBuster/2.1]
   -v, --verbose            Enable verbose output (headers, calibration)  [default: False]
   -f, --follow             Follow HTTP redirects  [default: False]
   --help                   Show this message and exit.
```

---

## 🧪 Testing

We use `pytest` for unit and integration tests.

```bash
# Run all tests
pytest

# Run tests with coverage report
pytest --cov=robotbuster
```

---

## 🧩 Extension & Collaboration

RobotBuster is built with a modular structure under `src/robotbuster`:

- **`core/`**: Scanning logic and engine.
- **`cli/`**: Typer-based terminal interface.
- **`models/`**: Pydantic schemas and data structures.
- **`utils/`**: Helper functions for display and wordlist management.

We welcome contributions! Please ensure you run `pre-commit` before submitting PRs.

---

## 👨‍💻 Developed by

- **vinnytherobot**
- [GitHub Profile](https://github.com/vinnytherobot)
- [Project Link](https://github.com/vinnytherobot/robotBuster)

---
> [!IMPORTANT]
> This project is for educational and security testing purposes only. Accessing systems without explicit permission is illegal. Use responsibly.
