import time

from .server import app
from .deployer import deploy_all, ACTIVE_DEPLOYMENTS

import uvicorn


def main():
    """
    Entry point for git-tag-deploy CLI.
    - Deploys all git-tagged apps.
    - Starts FastAPI server on port 5000 to show deployment info.
    """
    print("Starting deployments...")
    deploy_all()

    # Small delay to ensure uvicorn processes start
    time.sleep(1)

    if ACTIVE_DEPLOYMENTS:
        print("\nDeployments started:")
        for name, info in ACTIVE_DEPLOYMENTS.items():
            print(f" - {name}: tag={info['tag']}, port={info['port']}")
    else:
        print("No deployments found.")

    print("\nFastAPI status server running at http://127.0.0.1:5000/deployments")
    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
