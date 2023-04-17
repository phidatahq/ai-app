from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.app.redis.stack import RedisStack
from phidata.docker.config import DockerConfig
from phidata.docker.resource.image import DockerImage

from workspace.dev.jupyter.lab import dev_jupyter_lab
from workspace.settings import ws_settings

#
# -*- Docker resources for the dev environment
#

# -*- Dev Image
dev_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    # platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

# -*- StreamlitApp running on port 9095
dev_streamlit = StreamlitApp(
    name=f"{ws_settings.ws_name}-app",
    enabled=ws_settings.dev_app_enabled,
    image=dev_image,
    command="app start Home",
    mount_workspace=True,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/app_secrets.yml"),
)

# -*- FastApiServer running on port 9090
dev_fastapi = FastApiServer(
    name=f"{ws_settings.ws_name}-api",
    enabled=ws_settings.dev_api_enabled,
    image=dev_image,
    command="api start -r",
    mount_workspace=True,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/api_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/api_secrets.yml"),
)

# -*- RedisStack running on port 6379
dev_redis = RedisStack(
    enabled=ws_settings.dev_redis_enabled,
    use_cache=ws_settings.use_cache,
)

# -*- DockerConfig defining the dev resources
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_streamlit, dev_fastapi, dev_redis, dev_jupyter_lab],
)
