from os import getenv

from phidata.app.jupyter import JupyterLab
from phidata.docker.resource.image import DockerImage

from workspace.settings import ws_settings

#
# -*- Jupyter Docker resources
#

# -*- Jupyter image
dev_jupyter_image = DockerImage(
    name=f"{ws_settings.image_repo}/jupyter-{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=(ws_settings.build_images and ws_settings.dev_jupyter_enabled),
    path=str(ws_settings.ws_root),
    # platform="linux/amd64",
    dockerfile="workspace/dev/jupyter/jupyter.Dockerfile",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

# -*- JupyterLab running on port 8888
dev_jupyter_lab = JupyterLab(
    name=f"{ws_settings.ws_name}-lab",
    enabled=ws_settings.dev_jupyter_enabled,
    image=dev_jupyter_image,
    mount_workspace=True,
    # The jupyter_lab_config file is mounted when creating the image
    jupyter_config_file="/usr/local/jupyter/jupyter_lab_config.py",
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    # Read secrets from secrets/dev_jupyter_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath(
        "workspace/secrets/dev_jupyter_secrets.yml"
    ),
    use_cache=ws_settings.use_cache,
)
