from fastapi import FastAPI

from .deployer import ACTIVE_DEPLOYMENTS

app = FastAPI(title="Git Tag Deployments")


@app.get("/deployments")
def list_deployments():
    """
    Returns currently deployed apps (tag + port)
    """
    return {
        name: {"tag": info["tag"], "port": info["port"]}
        for name, info in ACTIVE_DEPLOYMENTS.items()
    }
