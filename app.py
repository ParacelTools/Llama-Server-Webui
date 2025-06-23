# llama-server-webui/app.py

from flask import Flask, request, render_template, redirect, url_for, session
import subprocess
import os
import json
import threading

app = Flask(__name__)
app.secret_key = 'llama_server_secret_key'  # Needed for session management

llama_procs = {}  # key = port, value = subprocess
log_lines = {}    # key = port, value = list of log lines
CONFIG_FILE = 'config.json'

# Default path to llama.cpp directory
def load_default_path():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            return config.get('llama_cpp_dir', os.path.expanduser("~/llama.cpp"))
    return os.path.expanduser("~/llama.cpp")

def save_default_path(path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'llama_cpp_dir': path}, f)

def get_llama_cpp_dir():
    return session.get('llama_cpp_dir', load_default_path())

def get_models_dir():
    return os.path.join(get_llama_cpp_dir(), "models")

def get_examples_dir():
    return os.path.join(get_llama_cpp_dir(), "examples")

def get_instructions_dir():
    return os.path.join(os.path.dirname(__file__), "instructions")

def get_jsons_dir():
    return os.path.join(os.path.dirname(__file__), "jsons")

def get_grammars_dir():
    return os.path.join(get_llama_cpp_dir(), "grammars")

def stream_output(pipe, port):
    global log_lines
    for line in iter(pipe.readline, b''):
        decoded_line = line.decode(errors='replace').rstrip()
        log_lines[port].append(decoded_line)
        if len(log_lines[port]) > 1000:
            log_lines[port] = log_lines[port][-1000:]

@app.route("/")
def index():
    llama_cpp_dir = get_llama_cpp_dir()
    models_dir = get_models_dir()
    examples_dir = get_examples_dir()
    instructions_dir = get_instructions_dir()
    jsons_dir = get_jsons_dir()
    grammars_dir = get_grammars_dir()

    path_error = not os.path.exists(llama_cpp_dir)
    models = os.listdir(models_dir) if os.path.exists(models_dir) else []
    examples = os.listdir(examples_dir) if os.path.exists(examples_dir) else []
    instructions = os.listdir(instructions_dir) if os.path.exists(instructions_dir) else []
    jsons = os.listdir(jsons_dir) if os.path.exists(jsons_dir) else []
    grammars = os.listdir(grammars_dir) if os.path.exists(grammars_dir) else []

    running_ports = list(llama_procs.keys())
    combined_logs = {port: "\n".join(log_lines.get(port, [])) for port in running_ports}

    return render_template("index.html", llama_cpp_dir=llama_cpp_dir, models=models, examples=examples,
                           instructions=instructions, jsons=jsons, grammars=grammars, running_ports=running_ports,
                           path_error=path_error, combined_logs=combined_logs)

@app.route("/set_path", methods=["POST"])
def set_path():
    new_path = request.form.get("llama_cpp_dir", "")
    if new_path:
        expanded_path = os.path.expanduser(new_path)
        session['llama_cpp_dir'] = expanded_path

        if 'save_default' in request.form:
            save_default_path(expanded_path)

    return redirect(url_for('index'))

@app.route("/start", methods=["POST"])
def start():
    global llama_procs, log_lines

    port = int(request.form.get("port", "8080"))
    if port in llama_procs:
        return f"Server already running on port {port}!", 400

    model = request.form["model"]
    no_webui = 'no_webui' in request.form
    use_gpu_layers = 'use_gpu_layers' in request.form
    gpu_layers = request.form.get("gpu_layers", "99")
    n_ctx = request.form.get("n_ctx", "4096")
    threads = request.form.get("threads", "4")
    batch_size = request.form.get("batch_size", "512")
    mlock = 'mlock' in request.form
    flash_attn = 'flash_attn' in request.form
    verbose = 'verbose' in request.form
    chat_template_mode = request.form.get("chat_template_mode", "none")
    chat_template_text = request.form.get("chat_template_text", "").strip()
    chat_template_file = request.form.get("chat_template_file", "").strip()
    json_schema_mode = request.form.get("json_schema_mode", "none")
    json_schema_text = request.form.get("json_schema_text", "").strip()
    json_schema_file = request.form.get("json_schema_file", "").strip()
    grammar_mode = request.form.get("grammar_mode", "none")
    grammar_text = request.form.get("grammar_text", "").strip()
    grammar_file = request.form.get("grammar_file", "").strip()

    samplers = request.form.get("samplers", "penalties;dry;top_n_sigma;top_k;typ_p;top_p;min_p;xtc;temperature")
    seed = request.form.get("seed", "-1")
    temp = request.form.get("temp", "0.8")
    top_k = request.form.get("top_k", "40")
    top_p = request.form.get("top_p", "0.9")
    min_p = request.form.get("min_p", "0.1")
    xtc_probability = request.form.get("xtc_probability", "0.0")
    xtc_threshold = request.form.get("xtc_threshold", "0.1")
    typical = request.form.get("typical", "1.0")
    repeat_last_n = request.form.get("repeat_last_n", "64")
    repeat_penalty = request.form.get("repeat_penalty", "1.0")
    presence_penalty = request.form.get("presence_penalty", "0.0")
    frequency_penalty = request.form.get("frequency_penalty", "0.0")
    dry_multiplier = request.form.get("dry_multiplier", "0.0")
    dry_base = request.form.get("dry_base", "1.75")
    dry_allowed_length = request.form.get("dry_allowed_length", "2")
    dry_penalty_last_n = request.form.get("dry_penalty_last_n", "-1")
    dry_sequence_breaker = request.form.get("dry_sequence_breaker", "")
    dynatemp_range = request.form.get("dynatemp_range", "0.0")
    dynatemp_exp = request.form.get("dynatemp_exp", "1.0")
    mirostat = request.form.get("mirostat", "0")
    mirostat_lr = request.form.get("mirostat_lr", "0.1")
    mirostat_ent = request.form.get("mirostat_ent", "5.0")

    other_args = request.form.get("other_args", "")

    llama_cpp_dir = get_llama_cpp_dir()
    models_dir = get_models_dir()

    cmd = [
        os.path.join(llama_cpp_dir, "build/bin/llama-server"),
        "--model", os.path.join(models_dir, model),
        "--ctx-size", n_ctx,
        "--threads", threads,
        "--batch-size", batch_size,
        "--port", str(port)
    ]
    if no_webui:
        cmd += ["--no-webui"]

    if use_gpu_layers:
        cmd += ["--n-gpu-layers", gpu_layers]

    if mlock:
        cmd += ["--mlock"]

    if flash_attn:
        cmd += ["--flash-attn"]

    if verbose:
        cmd += ["--verbose"]

    if chat_template_mode == "text" and chat_template_text:
        cmd += ["--chat-template", chat_template_text]
    elif chat_template_mode == "file" and chat_template_file:
        cmd += ["--chat-template-file", os.path.join(get_instructions_dir(), chat_template_file)]

    if json_schema_mode == "text" and json_schema_text:
        cmd += ["--json-schema", json_schema_text]
    elif json_schema_mode == "file" and json_schema_file:
        cmd += ["--json-schema-file", os.path.join(get_jsons_dir(), json_schema_file)]

    if grammar_mode == "text" and grammar_text:
        cmd += ["--grammar", grammar_text]
    elif grammar_mode == "file" and grammar_file:
        cmd += ["--grammar-file", os.path.join(get_grammars_dir(), grammar_file)]

    cmd += [
        "--samplers", samplers,
        "--seed", seed,
        "--temp", temp,
        "--top-k", top_k,
        "--top-p", top_p,
        "--min-p", min_p,
        "--xtc-probability", xtc_probability,
        "--xtc-threshold", xtc_threshold,
        "--typical", typical,
        "--repeat-last-n", repeat_last_n,
        "--repeat-penalty", repeat_penalty,
        "--presence-penalty", presence_penalty,
        "--frequency-penalty", frequency_penalty,
        "--dry-multiplier", dry_multiplier,
        "--dry-base", dry_base,
        "--dry-allowed-length", dry_allowed_length,
        "--dry-penalty-last-n", dry_penalty_last_n
    ]

    if dry_sequence_breaker:
        cmd += ["--dry-sequence-breaker", dry_sequence_breaker]

    cmd += [
        "--dynatemp-range", dynatemp_range,
        "--dynatemp-exp", dynatemp_exp,
        "--mirostat", mirostat,
        "--mirostat-lr", mirostat_lr,
        "--mirostat-ent", mirostat_ent
    ]

    if other_args:
        cmd += other_args.split()

    print("Launching on port", port, ":", " ".join(cmd))
    log_lines[port] = [f"Launching on port {port}: " + " ".join(cmd)]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    llama_procs[port] = proc
    threading.Thread(target=stream_output, args=(proc.stdout, port), daemon=True).start()

    return redirect(url_for('index'))

@app.route("/stop", methods=["POST"])
def stop():
    global llama_procs, log_lines
    port = int(request.form.get("port_to_stop"))

    if port in llama_procs:
        llama_procs[port].terminate()
        llama_procs[port] = None
        del llama_procs[port]
        del log_lines[port]

    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)