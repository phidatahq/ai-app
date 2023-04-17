from phidata.docker.config import DockerConfig, DockerImage

from workspace.settings import ws_settings

#
# -*- Docker resources for the prd environment
#

# -*- Prd Image
prd_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.prd_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
    use_cache=ws_settings.use_cache,
)

# -*- DockerConfig defining the prd resources
prd_docker_config = DockerConfig(
    env=ws_settings.prd_env,
    network=ws_settings.ws_name,
    images=[prd_image],
)
