import yaml
import socket
import tempfile
import subprocess

from pathlib import Path
from multiprocessing import Process

# Global dict for deployments
ACTIVE_DEPLOYMENTS = {}

DEPLOYMENT_FILE = "deployment.yaml"


def read_deployment_file(file_path=DEPLOYMENT_FILE):
    if not Path(file_path).exists():
        raise FileNotFoundError(f"{file_path} not found")
    with open(file_path) as f:
        data = yaml.safe_load(f)
    return data.get("deployments", [])


def find_free_port(start=8001, end=9000):
    for port in range(start, end):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free port available")


def _run_uvicorn(temp_dir, port, entrypoint):
    """
    Internal function to run uvicorn in the specified directory on the given port.
    This will run in a separate daemon process.
    """
    subprocess.run(
        ["uvicorn", entrypoint, "--host", "0.0.0.0", "--port", str(port)],
        cwd=temp_dir,
    )


def run_app(tag, name, entrypoint="app.main:app"):
    """
    Deploy a git tag:
    - Clone repo to temp dir
    - Checkout tag
    - Start uvicorn in a daemon process
    """
    temp_dir = tempfile.mkdtemp()
    subprocess.run(["git", "clone", ".", temp_dir], check=True)
    subprocess.run(["git", "checkout", tag], cwd=temp_dir, check=True)

    port = find_free_port()

    # Start uvicorn in a daemon process
    p = Process(target=_run_uvicorn, args=(temp_dir, port, entrypoint), daemon=True)
    p.start()

    # Record deployment info
    ACTIVE_DEPLOYMENTS[name] = {"tag": tag, "port": port, "entrypoint": entrypoint}


def deploy_all():
    """
    Deploy all apps listed in deployment.yaml
    """
    deployments = read_deployment_file()
    for d in deployments:
        entrypoint = d.get("entrypoint", "app.main:app")
        run_app(d["git_tag"], d["name"], entrypoint)
