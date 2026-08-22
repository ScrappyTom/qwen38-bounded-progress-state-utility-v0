from __future__ import annotations

import argparse
import json
import re
import shutil
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

from apparatus.canonical import write_json
from apparatus.constants import CONTEXT_TOKENS, LLAMA_BUILD, MODEL_ALIAS, ROOT, STAGE_B_MAXIMUM_CALLS
from apparatus.custody import require_authorization, require_clean_head, verify_runtime_files
from apparatus.modelio import get_json
from apparatus.stage_b import run_stage_b


def gpu_state() -> dict[str, Any]:
    result = subprocess.run(["nvidia-smi", "--query-gpu=index,name,memory.used,memory.free,memory.total,utilization.gpu", "--format=csv,noheader,nounits"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True)
    return {"returncode": result.returncode, "stdout": result.stdout.strip(), "stderr": result.stderr.strip()}


def llama_processes() -> list[str]:
    result = subprocess.run(["tasklist", "/FI", "IMAGENAME eq llama-server.exe", "/FO", "CSV", "/NH"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, text=True)
    return [line.strip() for line in result.stdout.splitlines() if "llama-server.exe" in line.lower()]


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def wait_ready(base_url: str, process: subprocess.Popen[bytes], timeout_seconds: int = 300) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"llama-server exited during startup: {process.returncode}")
        try:
            if get_json(base_url, "/health").get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("llama-server did not become healthy")


def server_arguments(server: Path, model: Path, host: str, port: int, runtime: Path) -> list[str]:
    slots = runtime / "slots"
    slots.mkdir(parents=True, exist_ok=True)
    return [str(server), "-m", str(model), "--alias", MODEL_ALIAS, "--host", host, "--port", str(port), "--gpu-layers", "all", "--fit", "off", "-c", "25000", "--flash-attn", "on", "-ctk", "q8_0", "-ctv", "q8_0", "--kv-unified", "-b", "512", "-ub", "256", "--threads", "7", "--threads-batch", "8", "--parallel", "1", "--cache-prompt", "--cache-ram", "0", "--slot-save-path", str(slots), "--no-context-shift", "--jinja", "--reasoning", "off", "--reasoning-format", "deepseek", "--reasoning-budget", "0", "--no-reasoning-preserve", "--temp", "0.7", "--top-p", "0.8", "--top-k", "20", "--min-p", "0.0", "--presence-penalty", "1.5", "--repeat-penalty", "1.0", "--metrics", "--slots", "--no-webui", "--no-mmproj", "--verbose", "--log-file", str(runtime / "llama-server.log")]


def verify_endpoint(base_url: str, model: Path) -> dict[str, Any]:
    health = get_json(base_url, "/health")
    props = get_json(base_url, "/props")
    generation = props.get("default_generation_settings", {})
    errors = []
    if health.get("status") != "ok": errors.append(f"health={health.get('status')!r}")
    if props.get("model_alias") != MODEL_ALIAS: errors.append(f"alias={props.get('model_alias')!r}")
    if props.get("build_info") != LLAMA_BUILD: errors.append(f"build={props.get('build_info')!r}")
    if generation.get("n_ctx") != CONTEXT_TOKENS: errors.append(f"n_ctx={generation.get('n_ctx')!r}")
    reported = props.get("model_path")
    if reported and Path(str(reported)).resolve() != model.resolve(): errors.append(f"model_path={reported!r}")
    if errors: raise RuntimeError("endpoint identity failed: " + "; ".join(errors))
    return props


def execute(run_id: str, server: Path, model: Path, host: str, port: int) -> dict[str, Any]:
    require_authorization("stage-b", STAGE_B_MAXIMUM_CALLS)
    head = require_clean_head()
    runtime_files = verify_runtime_files(server.resolve(), model.resolve())
    existing = llama_processes()
    if existing: raise RuntimeError(f"llama-server isolation failed: {existing}")
    if port_open(host, port): raise RuntimeError(f"intended port is open: {host}:{port}")
    runtime = ROOT / ".cache" / "runtime" / run_id
    if runtime.exists(): raise RuntimeError(f"runtime path exists: {runtime}")
    runtime.mkdir(parents=True)
    arguments = server_arguments(server.resolve(), model.resolve(), host, port, runtime)
    lifecycle: dict[str, Any] = {"schema_version": "bounded-progress-state-stage-b-runtime-v0", "run_id": run_id, "standalone_commit": head, "started_at_unix": time.time(), "gpu_before": gpu_state(), "existing_llama_processes_before": existing, "port_open_before": False, "server_arguments": arguments, "passed": False}
    process: subprocess.Popen[bytes] | None = None
    run_created = False
    try:
        with (runtime / "stdout.log").open("wb") as stdout, (runtime / "stderr.log").open("wb") as stderr:
            process = subprocess.Popen(arguments, stdout=stdout, stderr=stderr, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            lifecycle["server_pid"] = process.pid
            base_url = f"http://{host}:{port}"
            wait_ready(base_url, process)
            lifecycle["gpu_after_load"] = gpu_state()
            startup_log = (runtime / "llama-server.log").read_text(encoding="utf-8", errors="replace")
            offloads = [(int(used), int(total)) for used, total in re.findall(r"offloaded\s+(\d+)/(\d+)\s+layers to GPU", startup_log)]
            if next(((used, total) for used, total in reversed(offloads) if total == 66), None) != (66, 66):
                raise RuntimeError("exact CUDA profile did not offload 66/66 main-model layers")
            props = verify_endpoint(base_url, model.resolve())
            custody = {"schema_version": "bounded-progress-state-runtime-custody-v0", "runtime_files": runtime_files, "endpoint_props": props, "gpu_after_load": lifecycle["gpu_after_load"], "main_offloaded_layers_before_calls": [66, 66], "model_calls_before_custody": 0}
            result = run_stage_b(run_id, base_url, custody)
            run_created = True
            lifecycle["run_result"] = result
            lifecycle["passed"] = result["passed_apparatus_integrity"] and result["model_calls"] <= STAGE_B_MAXIMUM_CALLS
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try: process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=30)
        deadline = time.monotonic() + 30
        while port_open(host, port) and time.monotonic() < deadline: time.sleep(0.5)
        lifecycle["port_open_after"] = port_open(host, port)
        lifecycle["llama_processes_after"] = llama_processes()
        lifecycle["gpu_after_stop"] = gpu_state()
        lifecycle["finished_at_unix"] = time.time()
        write_json(runtime / "runtime-lifecycle.json", lifecycle)
        if run_created:
            model_root = ROOT / "runs" / run_id / "model"
            write_json(model_root / "runtime-lifecycle.json", lifecycle)
            write_json(model_root / "server-arguments.json", arguments)
            logs = model_root / "logs"; logs.mkdir(parents=True, exist_ok=True)
            for name in ("llama-server.log", "stdout.log", "stderr.log"):
                source = runtime / name
                if source.is_file(): shutil.copy2(source, logs / name)
    return lifecycle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--server-executable", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18080)
    args = parser.parse_args()
    result = execute(args.run_id, args.server_executable, args.model, args.host, args.port)
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
