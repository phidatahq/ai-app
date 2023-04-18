from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import AwsResourceGroup, S3Bucket, EcsCluster

from workspace.prd.docker_resources import prd_image
from workspace.settings import ws_settings

#
# -*- AWS Resources for the prd environment
#

# -*- Settings
launch_type = "FARGATE"
api_key = f"{ws_settings.prd_key}-api"
app_key = f"{ws_settings.prd_key}-app"

# -*- S3 bucket for prd data
prd_data_s3_bucket = S3Bucket(
    name=f"{ws_settings.prd_key}-data",
    acl="private",
)

# -*- ECS cluster for running services
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
)

# -*- StreamlitApp running on ECS
prd_streamlit = StreamlitApp(
    name=app_key,
    enabled=ws_settings.prd_app_enabled,
    image=prd_image,
    command=["app", "start", "Home"],
    ecs_task_cpu="512",
    ecs_task_memory="1024",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=ws_settings.security_groups,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from a file
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/app_secrets.yml"),
)

# -*- FastApiServer running on ECS
prd_fastapi = FastApiServer(
    name=api_key,
    enabled=ws_settings.prd_api_enabled,
    image=prd_image,
    command=["api", "start"],
    ecs_task_cpu="512",
    ecs_task_memory="1024",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=ws_settings.security_groups,
    # Get the OpenAI API key from the environment if available
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
    # Read secrets from a file
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/api_secrets.yml"),
)

#
# -*- AwsConfig defining the prd resources
#
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    apps=[prd_streamlit, prd_fastapi],
    resources=AwsResourceGroup(
        s3_buckets=[prd_data_s3_bucket],
    ),
)
