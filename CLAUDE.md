# CLAUDE.md — devworker

## Project Overview

A Python automation script that simulates realistic human coding activity in your editor. It creates a dummy project and continuously types code snippets (Python, Bash, Groovy/Jenkins) with human-like speed, typos, and random intervals.

**Platforms:** macOS, Linux

---

## Project Structure

```
vscode-activity-simulator/
├── simulator.py        # Main application — all logic in a single file (~503 lines)
├── requirements.txt    # Python dependencies (pyautogui>=0.9.54)
└── README.md           # Usage documentation
```

At runtime, the simulator creates a dummy project (default: `~/dummy_project`):
```
dummy_project/
├── src/         # Python files (.py)
├── scripts/     # Bash scripts (.sh)
├── ci/          # Groovy pipelines (.groovy)
└── Jenkinsfile  # Jenkins pipeline
```

---

## Tech Stack

- **Language:** Python 3.8+
- **Key Dependency:** `pyautogui >= 0.9.54` (GUI automation)
- **System Tools:** `osascript` (macOS), `wmctrl`/`xdotool` (Linux)
- **VS Code CLI:** `code` must be in PATH
- **No build system, no test suite**

---

## Key Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run with defaults (60 WPM, 3% typo rate, up to 15s intervals)
python3 simulator.py

# Custom options
python3 simulator.py --project ~/work/my_project --wpm 80
python3 simulator.py --wpm 40 --typo-rate 0.01 --max-interval 10

# Stop
# Ctrl+C  OR  move mouse to top-left corner (PyAutoGUI failsafe)
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--project PATH` | `~/dummy_project` | Dummy project location |
| `-w / --wpm` | `60` | Typing speed (words per minute) |
| `-t / --typo-rate` | `0.03` | Typo probability per character (0.0–1.0) |
| `-i / --max-interval` | `15` | Max seconds between edits (min 3, max 15) |

---

## Architecture

`simulator.py` is organized as a functional, single-file script:

| Section | Purpose |
|---------|---------|
| `PYTHON_SNIPPETS`, `BASH_SNIPPETS`, `GROOVY_SNIPPETS` | Pre-defined code pools per language |
| `SNIPPET_MAP` | Maps file extension → snippet pool |
| `PROJECT_FILES` | Template for dummy project structure |
| `create_project()` | Initializes dummy project on disk |
| `open_vscode()` / `open_file_in_vscode()` | VS Code launch and file opening |
| `focus_vscode()` | Brings VS Code to foreground (platform-aware: AppleScript vs wmctrl/xdotool) |
| `human_type()` | Core typing engine — WPM pacing, Gaussian jitter, random typos with backspace correction, natural pauses at `.`, `:`, `(`, `)` |
| `simulate()` | Main loop: pick file → open → type → save → wait |
| `main()` | CLI argument parsing and entry point |

**Platform abstraction:** `PLATFORM = platform.system()` constant drives all OS-specific branching (keyboard shortcuts, window management).

---

## Setup Notes

### macOS
Go to **System Settings → Privacy & Security → Accessibility** and enable your terminal app (Terminal, iTerm2, etc.).

### Linux
Install a window manager tool:
```bash
sudo apt install wmctrl   # preferred
# or
sudo apt install xdotool
```

---

## Important Constraints

- `--max-interval` is capped at 15 seconds maximum
- `pyautogui.FAILSAFE = True` — moving mouse to top-left corner aborts the simulation
- VS Code must be installed and `code` CLI must be on PATH
- No tests exist — this is a single-purpose automation utility
