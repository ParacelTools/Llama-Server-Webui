# Llama Server WebUI

A simple Flask-based WebUI for launching `llama-server` from `llama.cpp`.

---

## Features

- Launch and manage multiple servers with custom ports
- Scan models and grammars directories, upload custom jsons and chat templates
- Expose common CLI switches
- Run with or without GPU layers
- Supports advanced samplers
- Live view of running instances and logs

---

## Usage

Clone repo and enter dir:

```bash
git clone https://github.com/PaacelTools/llama-server-webui.git
cd llama-server-webui


Run the app:
chmod +x run.sh
./run.sh

(Or manually:)

bash
Copy
Edit
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 app.py
