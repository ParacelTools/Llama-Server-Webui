# Llama Server WebUI

A simple Flask-based WebUI for launching `llama-server` from `llama.cpp`.

---

## Features

- Launch and manage multiple servers with custom ports
- Scan models and grammars directories, upload custom jsons and chat templates
- Expose CLI switches
- Run with or without GPU layers (if llama.cpp is built with cuda toolkit or whatever)
- Supports advanced sampler ordering and options
- Live view of running instances and logs (sorta)

---

## Usage
(you must have llama.cpp installed FIRST! see https://github.com/ggml-org/llama.cpp)

Clone repo and enter dir:

```bash
git clone https://github.com/ParacelTools/llama-server-webui.git
cd llama-server-webui


Run the app:
chmod +x run.sh
./run.sh

(Or manually:)

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
