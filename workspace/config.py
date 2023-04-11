from phidata.workspace import WorkspaceConfig

from workspace.dev.aws_config import dev_aws_config
from workspace.dev.docker_config import dev_docker_config
from workspace.prd.aws_config import prd_aws_config
from workspace.prd.docker_config import prd_docker_config
from workspace.settings import ws_settings

#
# -*- Define workspace resources using the WorkspaceConfig class
#
workspace = WorkspaceConfig(
    default_env=ws_settings.dev_env,
    default_config="docker",
    aws_region=ws_settings.aws_region,
    docker=[dev_docker_config, prd_docker_config],
    aws=[dev_aws_config, prd_aws_config],
    ws_settings=ws_settings,
)
