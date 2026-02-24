#!/usr/bin/env python3
"""
Activity Simulator
Creates a dummy project and simulates realistic coding activity across
Python, Bash, and Jenkins Groovy files. Works on macOS and Linux.
Press Ctrl+C to stop.
"""

import os
import sys
import time
import random
import platform
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional

try:
    import pyautogui
except ImportError:
    print("Missing dependency. Install with: pip install pyautogui")
    sys.exit(1)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.02

PLATFORM = platform.system()  # 'Darwin' or 'Linux'

# ─── Python snippets ──────────────────────────────────────────────────────────

PYTHON_SNIPPETS = [
    """\
def process_batch(items: list, batch_size: int = 32) -> list:
    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        processed = [transform(item) for item in batch]
        results.extend(processed)
    return results
""",
    """\
class DataLoader:
    def __init__(self, path: str, shuffle: bool = True):
        self.path = path
        self.shuffle = shuffle
        self._data: list = []

    def load(self) -> list:
        with open(self.path) as f:
            self._data = json.load(f)
        if self.shuffle:
            random.shuffle(self._data)
        return self._data
""",
    """\
def retry(func, max_attempts: int = 3, delay: float = 1.0):
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay * (attempt + 1))
""",
    """\
def parse_config(path: str) -> dict:
    config = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, _, value = line.partition('=')
                config[key.strip()] = value.strip()
    return config
""",
    """\
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log'),
    ]
)
logger = logging.getLogger(__name__)
""",
    """\
def validate_schema(data: dict, schema: dict) -> bool:
    for key, expected_type in schema.items():
        if key not in data:
            raise ValueError(f"Missing required field: {key}")
        if not isinstance(data[key], expected_type):
            raise TypeError(f"Field '{key}' must be {expected_type.__name__}")
    return True
""",
]

# ─── Bash snippets ────────────────────────────────────────────────────────────

BASH_SNIPPETS = [
    """\
#!/bin/bash
set -euo pipefail

LOG_FILE="/var/log/deploy.log"
DEPLOY_DIR="/opt/app"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "Starting deployment..."
cd "$DEPLOY_DIR"
git pull origin main
pip install -r requirements.txt
systemctl restart app.service
log "Deployment complete."
""",
    """\
#!/bin/bash
set -e

ENV="${1:-staging}"
IMAGE_TAG="${2:-latest}"

echo "Building Docker image for env: $ENV"
docker build \\
    --build-arg ENV="$ENV" \\
    --build-arg BUILD_DATE="$(date -u +%Y-%m-%dT%H:%M:%SZ)" \\
    -t "myapp:$IMAGE_TAG" .

echo "Pushing image..."
docker push "myapp:$IMAGE_TAG"
echo "Done."
""",
    """\
#!/bin/bash
# Health check script
ENDPOINT="http://localhost:8080/health"
MAX_RETRIES=5
SLEEP=5

for i in $(seq 1 $MAX_RETRIES); do
    STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$ENDPOINT")
    if [ "$STATUS" = "200" ]; then
        echo "Service healthy (attempt $i)"
        exit 0
    fi
    echo "Attempt $i failed (HTTP $STATUS), retrying in ${SLEEP}s..."
    sleep "$SLEEP"
done

echo "Service failed health check after $MAX_RETRIES attempts"
exit 1
""",
    """\
#!/bin/bash
# Rotate logs older than 7 days
LOG_DIR="/var/log/myapp"
find "$LOG_DIR" -name "*.log" -mtime +7 -exec gzip {} \\;
find "$LOG_DIR" -name "*.log.gz" -mtime +30 -delete
echo "Log rotation complete: $(date)"
""",
]

# ─── Jenkins / Groovy snippets ────────────────────────────────────────────────

GROOVY_SNIPPETS = [
    """\
pipeline {
    agent { label 'docker' }

    environment {
        REGISTRY = 'registry.example.com'
        IMAGE    = 'myapp'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }
        stage('Build') {
            steps {
                sh 'docker build -t ${REGISTRY}/${IMAGE}:${BUILD_NUMBER} .'
            }
        }
        stage('Test') {
            steps {
                sh 'pytest tests/ --junitxml=results.xml'
            }
            post {
                always { junit 'results.xml' }
            }
        }
        stage('Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'registry-creds',
                    usernameVariable: 'USER',
                    passwordVariable: 'PASS'
                )]) {
                    sh 'docker login -u $USER -p $PASS ${REGISTRY}'
                    sh 'docker push ${REGISTRY}/${IMAGE}:${BUILD_NUMBER}'
                }
            }
        }
    }

    post {
        failure {
            slackSend channel: '#ci',
                      message: "Build failed: ${env.BUILD_URL}"
        }
    }
}
""",
    """\
def call(Map config = [:]) {
    def branch  = config.branch  ?: 'main'
    def timeout = config.timeout ?: 30

    pipeline {
        agent any
        options {
            timeout(time: timeout, unit: 'MINUTES')
            disableConcurrentBuilds()
        }
        stages {
            stage('Deploy') {
                steps {
                    script { deploy(branch: branch) }
                }
            }
        }
    }
}
""",
    """\
stage('Integration Tests') {
    parallel {
        stage('API Tests') {
            steps { sh 'pytest tests/api/ -v' }
        }
        stage('UI Tests') {
            steps { sh 'pytest tests/ui/ -v --headless' }
        }
        stage('Load Tests') {
            steps {
                sh 'locust -f tests/load/locustfile.py --headless -u 100 -r 10 --run-time 1m'
            }
        }
    }
}
""",
    """\
def runWithRetry(int maxAttempts = 3, Closure body) {
    int attempt = 0
    while (attempt < maxAttempts) {
        try {
            body()
            return
        } catch (Exception e) {
            attempt++
            if (attempt == maxAttempts) throw e
            echo "Attempt ${attempt} failed: ${e.message}. Retrying..."
            sleep(time: 10, unit: 'SECONDS')
        }
    }
}
""",
]

# ─── Project structure ────────────────────────────────────────────────────────

PROJECT_FILES: Dict[str, str] = {
    "src/__init__.py":           "# Package init\n",
    "src/pipeline.py":           "# Data pipeline\nimport json\nimport time\nimport random\n\n",
    "src/utils.py":              "# Utilities\nimport os\nimport logging\n\n",
    "src/config.py":             "# Configuration\nDEBUG = False\nVERSION = '1.0.0'\n\n",
    "scripts/deploy.sh":         "#!/bin/bash\n# Deployment script\n\n",
    "scripts/build.sh":          "#!/bin/bash\n# Build script\n\n",
    "scripts/health_check.sh":   "#!/bin/bash\n# Health check\n\n",
    "Jenkinsfile":               "// Main Jenkins pipeline\n\n",
    "ci/shared_lib.groovy":      "// Shared library\n\n",
    "ci/deploy_pipeline.groovy": "// Deploy pipeline\n\n",
}

# File extension → snippet pool
SNIPPET_MAP: Dict[str, List[str]] = {
    ".py":     PYTHON_SNIPPETS,
    ".sh":     BASH_SNIPPETS,
    ".groovy": GROOVY_SNIPPETS,
    "":        GROOVY_SNIPPETS,   # Jenkinsfile has no extension
}


# ─── Project setup ────────────────────────────────────────────────────────────

def check_linux_deps() -> None:
    """Warn about missing dependencies on Linux / Ubuntu 24.04."""
    if not os.environ.get("DISPLAY"):
        print(
            "Warning: DISPLAY is not set.\n"
            "Ubuntu 24.04 defaults to Wayland, but this script requires X11.\n"
            "Fix: log out and select 'Ubuntu on Xorg' at the login screen,\n"
            "     or launch with:  DISPLAY=:0 python3 coder.py\n"
        )

    missing = []
    for tool in ("wmctrl", "xdotool"):
        if subprocess.run(["which", tool], capture_output=True).returncode != 0:
            missing.append(tool)
    if len(missing) == 2:
        print(
            "Warning: neither wmctrl nor xdotool found.\n"
            "Install one:  sudo apt install wmctrl\n"
        )


def create_project(base: Path) -> None:
    base.mkdir(parents=True, exist_ok=True)
    for rel_path, content in PROJECT_FILES.items():
        fpath = base / rel_path
        fpath.parent.mkdir(parents=True, exist_ok=True)
        if not fpath.exists():
            fpath.write_text(content)
    print(f"Project ready at: {base}")


def open_editor(project_path: Path) -> None:
    try:
        subprocess.Popen(
            ["code", str(project_path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        print("Opened editor. Waiting for it to load...")
        time.sleep(4)
    except FileNotFoundError:
        print("Warning: editor CLI not found. Please open your editor manually.")


def open_file_in_editor(filepath: Path) -> None:
    try:
        subprocess.Popen(
            ["code", "-g", str(filepath)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        pass


# ─── Window focus (platform-specific) ────────────────────────────────────────

def focus_editor() -> bool:
    """Bring the editor to the foreground. Returns True on success."""
    if PLATFORM == "Darwin":
        result = subprocess.run(
            ["osascript", "-e",
             'tell application "Visual Studio Code" to activate'],
            capture_output=True,
        )
        return result.returncode == 0

    elif PLATFORM == "Linux":
        for cmd in [
            ["wmctrl", "-a", "Visual Studio Code"],
            ["xdotool", "search", "--name", "Visual Studio Code",
             "windowactivate", "--sync"],
        ]:
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode == 0:
                return True

    elif PLATFORM == "Windows":
        result = subprocess.run(
            ["powershell", "-WindowStyle", "Hidden", "-c",
             "Add-Type -AssemblyName Microsoft.VisualBasic; "
             "[Microsoft.VisualBasic.Interaction]::AppActivate('Visual Studio Code')"],
            capture_output=True,
        )
        return result.returncode == 0

    return False


# ─── Typing engine ────────────────────────────────────────────────────────────

def human_type(text: str, wpm: int, typo_rate: float) -> None:
    chars_per_sec = (wpm * 5) / 60
    base_delay = 1.0 / chars_per_sec
    i = 0

    while i < len(text):
        char = text[i]

        # Occasional typo + backspace correction
        if char.isalpha() and random.random() < typo_rate:
            wrong = random.choice("abcdefghijklmnopqrstuvwxyz")
            pyautogui.write(wrong, interval=0)
            time.sleep(base_delay * random.uniform(0.8, 1.5))
            pyautogui.hotkey("backspace")
            time.sleep(base_delay * random.uniform(1.0, 2.0))

        # Natural pauses after structural characters
        if char in ".:()" :
            time.sleep(base_delay * random.uniform(1.5, 3.0))
        elif char == "\n":
            pyautogui.press("enter")
            time.sleep(base_delay * random.uniform(2.0, 4.0))
            i += 1
            continue
        elif char == "\t":
            pyautogui.press("tab")
            time.sleep(base_delay * random.uniform(0.8, 1.2))
            i += 1
            continue

        pyautogui.write(char, interval=0)
        jitter = random.gauss(0, base_delay * 0.3)
        time.sleep(max(0.01, base_delay + jitter))
        i += 1


# ─── Simulation loop ──────────────────────────────────────────────────────────

def pick_file(project: Path) -> Path:
    files = [f for f in project.rglob("*") if f.is_file()]
    return random.choice(files)


def pick_snippet(filepath: Path) -> str:
    ext = filepath.suffix
    pool = SNIPPET_MAP.get(ext, PYTHON_SNIPPETS)
    return random.choice(pool)


def go_to_end() -> None:
    """Move cursor to end of file."""
    if PLATFORM == "Darwin":
        pyautogui.hotkey("command", "end")
    else:
        pyautogui.hotkey("ctrl", "end")
    time.sleep(0.3)


def save_file() -> None:
    if PLATFORM == "Darwin":
        pyautogui.hotkey("command", "s")
    else:
        pyautogui.hotkey("ctrl", "s")


def simulate(project: Path, wpm: int, typo_rate: float, max_interval: int) -> None:
    print(f"\nSimulation running — wpm={wpm}, max_interval={max_interval}s")
    print("Move mouse to top-left corner OR Ctrl+C to stop.\n")

    try:
        while True:
            filepath = pick_file(project)
            snippet  = pick_snippet(filepath)

            print(f"  [{time.strftime('%H:%M:%S')}] Editing {filepath.relative_to(project)} ...")

            open_file_in_editor(filepath)
            time.sleep(1.2)
            focus_editor()
            time.sleep(0.8)

            go_to_end()
            human_type(snippet, wpm, typo_rate)
            save_file()

            wait = random.uniform(3, max_interval)
            print(f"  Saved. Next edit in {wait:.1f}s ...")
            # Jiggle mouse 1 px and back — VMware Tools translates this to host
            # cursor movement, resetting the Windows idle/lock timer.
            pyautogui.moveRel(1, 0, duration=0)
            pyautogui.moveRel(-1, 0, duration=0)
            time.sleep(wait)

    except pyautogui.FailSafeException:
        print("\nFail-safe triggered (mouse top-left). Stopped.")
    except KeyboardInterrupt:
        print("\nStopped by user.")


# ─── Entry point ──────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simulate realistic coding activity (macOS & Linux)."
    )
    parser.add_argument(
        "--project",
        default=str(Path.home() / "dummy_project"),
        help="Path for the dummy project (default: ~/dummy_project)",
    )
    parser.add_argument(
        "-w", "--wpm",
        type=int, default=60,
        help="Typing speed in WPM (default: 60)",
    )
    parser.add_argument(
        "-t", "--typo-rate",
        type=float, default=0.03,
        metavar="RATE",
        help="Typo probability per character 0.0-1.0 (default: 0.03)",
    )
    parser.add_argument(
        "-i", "--max-interval",
        type=int, default=15,
        metavar="SECONDS",
        help="Max seconds between edits (default: 15, min 3)",
    )
    args = parser.parse_args()

    if args.max_interval > 15:
        parser.error("--max-interval cannot exceed 15 seconds.")

    if PLATFORM == "Linux":
        check_linux_deps()

    project = Path(args.project).expanduser()
    create_project(project)
    open_editor(project)

    print("Starting in 5 seconds — make sure your editor is visible...")
    time.sleep(5)

    simulate(project, args.wpm, args.typo_rate, args.max_interval)


if __name__ == "__main__":
    main()
