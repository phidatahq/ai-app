from os import getenv

from phidata.app.fastapi import FastApiServer
from phidata.app.streamlit import StreamlitApp
from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import (
    AwsResourceGroup,
    DbInstance,
    DbSubnetGroup,
    EcsCluster,
    S3Bucket,
    SecretsManager,
)
from phidata.docker.config import DockerConfig, DockerImage

from workspace.settings import ws_settings

#
# -*- Resources for the Production Environment
#
# Skip resource creation when running `phi ws up`
skip_create: bool = False
# Skip resource  deletion when running `phi ws down`
skip_delete: bool = False

# -*- Production Image
prd_image = DockerImage(
    name=f"{ws_settings.image_repo}/{ws_settings.ws_name}",
    tag=ws_settings.prd_env,
    enabled=ws_settings.build_images,
    path=str(ws_settings.ws_root),
    platform="linux/amd64",
    pull=ws_settings.force_pull_images,
    push_image=ws_settings.push_images,
    skip_docker_cache=ws_settings.skip_image_cache,
)

# -*- S3 bucket for production data
prd_data_s3_bucket = S3Bucket(
    name=f"{ws_settings.prd_key}-data",
    acl="private",
)

# -*- Secrets manager for production secrets
prd_secrets = SecretsManager(
    name=f"{ws_settings.prd_key}-secrets",
    secrets_dir=ws_settings.ws_root.joinpath("workspace/secrets"),
)

# -*- RDS Database Subnet Group
prd_db_subnet_group = DbSubnetGroup(
    name=f"{ws_settings.prd_key}-db-sg",
    enabled=ws_settings.prd_db_enabled,
    subnet_ids=ws_settings.subnet_ids,
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- RDS Database Instance
db_engine = "postgres"
prd_db = DbInstance(
    name=f"{ws_settings.prd_key}-db",
    enabled=ws_settings.prd_db_enabled,
    engine=db_engine,
    engine_version="15.3",
    db_name="ai",
    allocated_storage=128,
    # NOTE: For production, use a larger instance type.
    # Last checked price: $0.0.0650 per hour = ~$50 per month
    db_instance_class="db.t4g.medium",
    availability_zone=ws_settings.aws_az1,
    db_subnet_group=prd_db_subnet_group,
    enable_performance_insights=True,
    # vpc_security_group_ids=[],
    # Read MASTER_USERNAME and MASTER_USER_PASSWORD from secrets/db_secrets.yml
    secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/db_secrets.yml"),
    skip_create=skip_create,
    skip_delete=skip_delete,
)

# -*- ECS cluster
launch_type = "FARGATE"
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
)

# -*- StreamlitApp running on ECS
prd_streamlit = StreamlitApp(
    name="ai-app-prd",
    enabled=ws_settings.prd_app_enabled,
    image=prd_image,
    command=["app", "start", "Home"],
    ecs_task_cpu="1024",
    ecs_task_memory="2048",
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secrets],
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=[],
    # Get the OpenAI API key from the local environment
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
)

# -*- FastApiServer running on ECS
prd_fastapi = FastApiServer(
    name="ai-api-prd",
    enabled=ws_settings.prd_api_enabled,
    image=prd_image,
    command=["api", "start"],
    ecs_task_cpu="1024",
    ecs_task_memory="2048",
    ecs_cluster=prd_ecs_cluster,
    aws_secrets=[prd_secrets],
    aws_subnets=ws_settings.subnet_ids,
    # aws_security_groups=[],
    # Get the OpenAI API key from the local environment
    env={"OPENAI_API_KEY": getenv("OPENAI_API_KEY", "")},
    use_cache=ws_settings.use_cache,
)

# -*- DockerConfig defining the prd resources
prd_docker_config = DockerConfig(
    env=ws_settings.prd_env,
    network=ws_settings.ws_name,
    images=[prd_image],
)

# -*- AwsConfig defining the prd resources
prd_aws_config = AwsConfig(
    env=ws_settings.prd_env,
    apps=[prd_streamlit, prd_fastapi],
    resources=AwsResourceGroup(
        db_instances=[prd_db],
        db_subnet_groups=[prd_db_subnet_group],
        secrets=[prd_secrets],
        s3_buckets=[prd_data_s3_bucket],
    ),
)
