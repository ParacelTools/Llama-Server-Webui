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
```
git clone https://github.com/ParacelTools/llama-server-webui.git
cd llama-server-webui
```
Run the script:
```
chmod +x run.sh
./run.sh
```
(Or manually):
```
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
## To Do Yet
- Give the user the option to output server logs to a file
- add an option to do wget downloads to the model directory from Huggingface or where ever
- clean up the active models part of the page
- check if the server was launched with webui, if so, post its url
- edit html so that the categories collapse and expand
- add a presets/config file feature
- add the option to start servers on remote hosts
- check if a server is already running on a selected port and host, prevent the user from launching a new instance
