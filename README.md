## AI App

This repo contains the code for running the AI App in 2 environments:

1. dev: A development env running on docker
2. prd: A production env running on AWS ECS

## Setup Workspace (for new developers)

1. Clone the git repo

> from the `ai-app` dir:

2. Create + activate a virtual env:

```sh
python3 -m venv aienv
source aienv/bin/activate
```

3. Install `phidata`:

```sh
pip install phidata
```

4. Setup workspace:

```sh
phi ws setup
```

5. Copy `workspace/example_secrets` to `workspace/secrets`:

```sh
cp -r workspace/example_secrets workspace/secrets
```

6. Optional: Create `.env` file:

```sh
cp example.env .env
```

## Run AI App locally using docker

The `workspace/dev_resources.py` file contains the code for the `dev` resources.

1. Install [docker desktop](https://www.docker.com/products/docker-desktop)

2. Optional: Set OpenAI Key

If you have an `OPENAI_API_KEY`, set the environment variable using

```sh
export OPENAI_API_KEY=sk-***
```

**OR** set in the `.env` file

3. Start the workspace using:

```sh
phi ws up dev:docker
```

- Open [localhost:9095](http://localhost:9095) to view the Streamlit App.
- Open [localhost:9090/docs](http://localhost:9090/docs) to view the FastApi docs.
- Open [localhost:8888](http://localhost:8888) to view JupyterLab UI.

## Update python libraries

The `pyproject.toml` file is the [standard](https://peps.python.org/pep-0621/) for configuring python projects. This project is already configured to manage libraries using `pyproject.toml`, which is then used to generate the `requirements.txt` file.

### To add new python libraries

1. Add libraries to the dependencies section in the `pyproject.toml` file.

2. Update `requirements.txt` file using helper script:

```sh
./scripts/upgrade.sh
```

**OR**

You can also generate the requirements.txt file using `pip-compile`:

```sh
pip-compile --no-annotate --pip-args "--no-cache-dir" \
-o requirements.txt \
pyproject.toml
```

## Update development environment

To update the development environment:

1. Build a new development image
2. Re-run containers using the new image

To build a new image, set the following values in the `workspace/settings.py` file:

```python
    # -*- Image Settings
    # Repository for images
    image_repo="your-image-repo",
    # Build images locally
    build_images=True,
```

### Rebuild dev images and re-run containers

Rebuild dev images and re-run containers using the `phi` cli

```sh
phi ws up dev:docker -f
```

**OR** use a helper script

```sh
./scripts/build_dev_image.sh
```

## Shut down dev environment

Delete dev resources using:

```sh
phi ws down dev:docker
```

## Run AI App in production on AWS

The `workspace/prd_resources.py` file contains the code for the `prd` resources.

To run in production:

1. Build production image
2. Create AWS resources

To build the production image, set the following values in the `workspace/settings.py` file:

```python
    # -*- Image Settings
    # Repository for images
    image_repo="your-image-repo",
    # Build images locally
    build_images=True,
    # Push images after building
    push_images=True,
```

### Build production image

**Important:** If you are using ECR, authenticate with ECR before pushing images.

```sh
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [account].dkr.ecr.[region].amazonaws.com
```

Build production image using the `phi` cli

```sh
phi ws up prd:docker
```

**OR** use the helper script

```sh
./scripts/build_prd_image.sh
```

### Create AWS resources

```sh
phi ws up prd:aws
```

## Update production environment

To update your production environment:

1. Build a new production image
2. Update AWS resources

### Rebuild production image

**Important:** If you are using ECR, authenticate with ECR before pushing images.

```sh
aws ecr get-login-password --region [region] | docker login --username AWS --password-stdin [account].dkr.ecr.[region].amazonaws.com
```

Build production image using the `phi` cli

```sh
phi ws up prd:docker -f
```

**OR** use the helper script

```sh
./scripts/build_prd_image.sh
```

### Update AWS resources

1. If you updated the CPU, Memory or Environment, then update the production task definition

```sh
phi ws patch prd:aws:td
```

2. Update production ECS Service

```sh
phi ws patch prd:aws:service
```

Note: If you **ONLY** want to pick up the new image, you do not need to update the task definition and can only update the service using

```sh
phi ws patch prd:aws:service
```

### Shut down production environment

Delete production resources using:

```sh
phi ws down prd:aws
```
