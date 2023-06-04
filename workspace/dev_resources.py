from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.postgres import PostgresDb
from phidata.app.streamlit import StreamlitApp
from phidata.docker.config import DockerConfig
from phidata.docker.resource.image import DockerImage

from workspace.jupyter.lab import dev_jupyter
from workspace.settings import ws_settings

#
# -*- Resources for the Development Environment
#

# -*- Development Image
dev_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.dev_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    # Uncommen to use a specific platform for the image
    # platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    # Uncomment to push dev images
    # push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
)

# -*- Development database running on port 9315:5432
dev_db = PostgresDb(
    name="ai-db-dev",
    enabled=ws_settings.dev_db_enabled,
    db_schema="ai",
    # Connect to this db on port 9315
    container_host_port=9315,
    # Read POSTGRES_USER and POSTGRES_PASSWORD from secrets/db_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/db_secrets.yml"),
)

# -*- StreamlitApp running on port 9095
dev_streamlit = StreamlitApp(
    name="ai-app-dev",
    enabled=ws_settings.dev_app_enabled,
    image=dev_image,
    command="app start Home",
    mount_workspace=True,
    # Get the OpenAI API key from the local environment
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/app_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/app_secrets.yml"),
)

# -*- FastApiServer running on port 9090
dev_fastapi = FastApiServer(
    name="ai-api-dev",
    enabled=ws_settings.dev_api_enabled,
    image=dev_image,
    command="api start -r",
    mount_workspace=True,
    # Get the OpenAI API key from the local environment
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from secrets/api_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/api_secrets.yml"),
)

# -*- DockerConfig defining the dev resources
dev_docker_config = DockerConfig(
    env=ws_settings.dev_env,
    network=ws_settings.ws_name,
    apps=[dev_db, dev_streamlit, dev_fastapi, dev_jupyter],
)
