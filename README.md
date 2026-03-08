# 🤖 RobotBuster v2.0

![RobotBuster Banner](assets/banner.png)

**RobotBuster** is a modern, ultra-fast, and intuitive route enumeration (directory brute-force) tool written in Python. Now featuring full asynchronous support and a premium terminal interface.

---

## ✨ What's New?

- ⚡ **Extreme Speed:** Built with `httpx` and `asyncio` to handle hundreds of concurrent requests.
- 🎨 **Modern Interface:** Fully redesigned UI using the `rich` library, featuring real progress bars, organized tables, and vibrant colors.
- 📊 **Detailed Summary:** Final table with all results organized by status code and response body size.
- 🛠️ **Configurable:** Full control over concurrency, status code filters, and file output.
- 🔍 **Smart Calibration:** Automatically detects "Wildcard 404" responses to filter out false positives.

---

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/vinnyrobot/robotBuster.git
cd robotBuster
```

2. Install dependencies:
```bash
python -m pip install -r requirements.txt
```

---

## 🛠️ Usage

```console
$ python robotBuster.py --help

usage: robotBuster.py [-h] -u URL -w WORDLIST [-t TASKS] [-s STATUS] [-o OUTPUT] [-v]

RobotBuster v2.0 - Fast & Modern Route Enumerator

options:
  -h, --help            show this help message and exit
  -u URL, --url URL     Target URL (e.g., http://example.com)
  -w WORDLIST, --wordlist WORDLIST
                        Path to wordlist file
  -t TASKS, --tasks TASKS
                        Number of concurrent tasks (default: 20)
  -s STATUS, --status STATUS
                        Comma-separated status codes to filter (default: 200,204,301,302,307,401,403)
  -o OUTPUT, --output OUTPUT
                        Output file to save found routes
  -v, --version         show tool version and exit
```

### Examples:

**Ultra-fast scan (50 concurrent tasks):**
```bash
python robotBuster.py -u https://target.com -w common.txt -t 50
```

**Saving results to a file:**
```bash
python robotBuster.py -u https://target.com -w common.txt -o results.txt
```

**Filtering by specific status codes:**
```bash
python robotBuster.py -u https://target.com -w common.txt -s 200,403
```

---

## 👨‍💻 Developed by

- **vinnytherobot**
- [GitHub Profile](https://github.com/vinnytherobot)
- [Project Link](https://github.com/vinnytherobot/robotBuster)

---
*This project is for educational and security testing purposes only. Use responsibly.*
