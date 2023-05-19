## AI App

This repo contains the code for running an AI App in 2 environments:

1. dev: A development env running on docker
2. prd: A production env running on AWS ECS

## Setup Workspace

> from the `ai-app` dir:

1. Create + activate a virtual env:

```sh
python3 -m venv .venv/aienv
source .venv/aienv/bin/activate
```

2. Install `phidata`:

```sh
pip install phidata
```

3. Setup workspace:

```sh
phi ws setup
```

4. Copy `workspace/example_secrets` to `workspace/secrets`:

```sh
cp -r workspace/example_secrets workspace/secrets
```

Optional: Create `.env` file:

```sh
cp example.env .env
```

## Run AI App locally using docker

The [workspace/dev_resources.py](workspace/dev_resources.py) file contains the code for the dev resources.

1. Install [docker desktop](https://www.docker.com/products/docker-desktop)

2. Start the workspace using:

```sh
phi ws up
```

- Open [localhost:9095](http://localhost:9095) to view the Streamlit App.
- Open [localhost:9090/docs](http://localhost:9090/docs) to view the FastApi docs.
- Open [localhost:8888](http://localhost:8888) to view JupyterLab UI.

If something fails, try running again with debug logs:

```sh
phi ws up -d
```

### Shut down workspace

Shut down resources using:

```sh
phi ws down
```
