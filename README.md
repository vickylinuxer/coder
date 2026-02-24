# coder

Simulates realistic coding activity in your editor by automatically typing Python, Bash, and Jenkins Groovy code snippets into a dummy project — with human-like speed, typos, and random intervals.

Works on **macOS** and **Linux**.

---

## How It Works

1. Creates a dummy project with `.py`, `.sh`, `.groovy`, and `Jenkinsfile` files
2. Opens the editor pointing at the project
3. Continuously picks a random file, opens it, and types a matching code snippet
4. Saves the file and waits a random interval (3–15 seconds) before the next edit

---

## Requirements

- Python 3.8+
- Editor with the `code` CLI available in PATH

### macOS

```bash
bash setup.sh
source venv/bin/activate
```

Go to **System Settings → Privacy & Security → Accessibility** and enable your terminal app.

### Linux / Ubuntu 24.04

Ubuntu 24.04 blocks system-wide `pip` (PEP 668). Use the setup script instead:

```bash
bash setup.sh
source venv/bin/activate
```

This installs `wmctrl`, `python3-xlib`, `python3-venv` via apt and sets up a venv.

---

## Usage

```bash
python3 coder.py [OPTIONS]
```

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--project PATH` | `~/dummy_project` | Where to create the dummy project |
| `-w / --wpm` | `60` | Typing speed in words per minute |
| `-t / --typo-rate` | `0.03` | Typo probability per character (0.0 – 1.0) |
| `-i / --max-interval` | `15` | Max seconds between edits (min 3, max 15) |

### Examples

```bash
# Default settings
python3 coder.py

# Faster typing, custom project path
python3 coder.py --project ~/work/my_project --wpm 80

# Slower, more deliberate typing with fewer typos
python3 coder.py --wpm 40 --typo-rate 0.01 --max-interval 10
```

---

## Stopping

- Press **Ctrl+C** in the terminal
- Or move the mouse to the **top-left corner** of the screen (PyAutoGUI fail-safe)

---

## Dummy Project Structure

```
dummy_project/
├── src/
│   ├── __init__.py
│   ├── pipeline.py
│   ├── utils.py
│   └── config.py
├── scripts/
│   ├── deploy.sh
│   ├── build.sh
│   └── health_check.sh
├── ci/
│   ├── shared_lib.groovy
│   └── deploy_pipeline.groovy
└── Jenkinsfile
```

---

## Snippet Types

| File type | Language |
|-----------|----------|
| `.py` | Python — data processing, config, logging, retry logic |
| `.sh` | Bash — deploy scripts, Docker builds, health checks, log rotation |
| `.groovy` / `Jenkinsfile` | Jenkins Pipeline, shared libs, parallel stages |
