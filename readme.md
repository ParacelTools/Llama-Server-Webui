# Llama Server WebUI

A simple Flask-based WebUI for launching `llama-server` from `llama.cpp`.

---

## Features

- Launch multiple servers with custom ports
- Scan models, instructions, jsons, grammars directories
- Expose all common CLI switches
- Run with or without GPU layers
- Supports --no-webui and advanced samplers
- Live view of running instances and logs

---

## Usage

### 1?? Clone repo and enter dir:

```bash
git clone https://github.com/YOUR-REPO/llama-server-webui.git
cd llama-server-webui


Run the app:
bash
Copy
Edit
./run.sh

(Or manually:)

bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py