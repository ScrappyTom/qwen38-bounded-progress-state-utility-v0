from __future__ import annotations

import argparse
import json
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

from apparatus.canonical import sha256_file, write_json
from apparatus.constants import EXPECTED_SERVER_SHA256, ROOT, TOKENIZER_PROJECTION_SHA256
from apparatus.preflight import run_preflight


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


def wait_ready(base_url: str, process: subprocess.Popen[bytes], timeout: int = 180) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"tokenizer server exited during startup: {process.returncode}")
        try:
            with urllib.request.urlopen(base_url + "/health", timeout=2) as response:
                value = json.loads(response.read())
            if value.get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise RuntimeError("tokenizer server did not become ready")


def execute(server: Path, tokenizer: Path, host: str, port: int) -> dict:
    server = server.resolve()
    tokenizer = tokenizer.resolve()
    if not server.is_file() or sha256_file(server) != EXPECTED_SERVER_SHA256:
        raise RuntimeError("CPU tokenizer server hash mismatch")
    if not tokenizer.is_file() or sha256_file(tokenizer) != TOKENIZER_PROJECTION_SHA256:
        raise RuntimeError("tokenizer projection hash mismatch")
    if port_open(host, port):
        raise RuntimeError(f"preflight port already open: {host}:{port}")
    cache = ROOT / ".cache" / f"tokenizer-preflight-{time.time_ns()}"
    cache.mkdir(parents=True)
    arguments = [str(server), "-m", str(tokenizer), "--alias", "qwen38-tokenizer-projection", "--host", host, "--port", str(port), "--gpu-layers", "0", "-c", "1024", "--threads", "2", "--parallel", "1", "--no-warmup", "--jinja", "--reasoning", "off", "--no-webui", "--no-mmproj"]
    process: subprocess.Popen[bytes] | None = None
    lifecycle = {"schema_version": "bounded-progress-state-offline-runtime-v0", "measured_inference": False, "chat_completions_called": False, "server_arguments": arguments, "port": port, "gpu_used": False, "released": False}
    try:
        with (cache / "stdout.log").open("wb") as stdout, (cache / "stderr.log").open("wb") as stderr:
            process = subprocess.Popen(arguments, stdout=stdout, stderr=stderr, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
            lifecycle["pid"] = process.pid
            wait_ready(f"http://{host}:{port}", process)
            result = run_preflight(f"http://{host}:{port}", server, tokenizer)
            lifecycle["preflight_passed"] = bool(result["verification_passed"])
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=30)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=30)
        deadline = time.monotonic() + 15
        while port_open(host, port) and time.monotonic() < deadline:
            time.sleep(0.25)
        lifecycle["port_open_after"] = port_open(host, port)
        lifecycle["released"] = not lifecycle["port_open_after"] and process is not None and process.poll() is not None
        write_json(ROOT / "provenance" / "OFFLINE_RUNTIME_RELEASE.json", lifecycle)
    return lifecycle


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--server-executable", type=Path, required=True)
    parser.add_argument("--tokenizer-projection", type=Path, required=True)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=18083)
    args = parser.parse_args()
    result = execute(args.server_executable, args.tokenizer_projection, args.host, args.port)
    print(json.dumps(result, sort_keys=True))
    return 0 if result.get("preflight_passed") and result.get("released") else 1


if __name__ == "__main__":
    raise SystemExit(main())
