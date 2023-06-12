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
    SecurityGroup,
    InboundRule,
)
from phidata.docker.config import DockerConfig, DockerImage
from phidata.resource.reference import Reference

from workspace.settings import ws_settings

#
# -*- Resources for the Production Environment
#
# Skip resource deletion when running `phi ws down`
skip_delete: bool = False
# Save resource outputs to workspace/outputs
save_output: bool = True

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
    enabled=False,
    acl="private",
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Secrets for production database
prd_db_secret = SecretsManager(
    name=f"{ws_settings.prd_key}-db-secret",
    secret_files=[ws_settings.ws_root.joinpath("workspace/secrets/prd_db_secrets.yml")],
    skip_delete=skip_delete,
    save_output=save_output,
)
# -*- Secrets for production application
prd_app_secret = SecretsManager(
    name=f"{ws_settings.prd_key}-app-secret",
    secret_files=[
        ws_settings.ws_root.joinpath("workspace/secrets/prd_app_secrets.yml")
    ],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Security Group for the application
prd_app_security_group = SecurityGroup(
    name=f"{ws_settings.prd_key}-security-group",
    enabled=ws_settings.prd_api_enabled or ws_settings.prd_app_enabled,
    description="Security group for the production application",
    inbound_rules=[
        InboundRule(
            description="Allow HTTP traffic from the internet",
            port=80,
            cidr_ip="0.0.0.0/0",
        ),
        InboundRule(
            description="Allow HTTPS traffic from the internet",
            port=443,
            cidr_ip="0.0.0.0/0",
        ),
        InboundRule(
            description="Allow traffic to the FastAPI server",
            port=9090,
            cidr_ip="0.0.0.0/0",
        ),
        InboundRule(
            description="Allow traffic to the Streamlit app",
            port=9095,
            cidr_ip="0.0.0.0/0",
        ),
    ],
    skip_delete=skip_delete,
    save_output=save_output,
)
# -*- Security Group for the database
prd_db_security_group = SecurityGroup(
    name=f"{ws_settings.prd_key}-db-security-group",
    enabled=ws_settings.prd_db_enabled,
    description="Security group for the production database",
    inbound_rules=[
        InboundRule(
            description="Allow inbound traffic from the application security group",
            port=5432,
            source_security_group_id=Reference(
                prd_app_security_group.get_security_group_id
            ),
        )
    ],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- RDS Database Subnet Group
prd_db_subnet_group = DbSubnetGroup(
    name=f"{ws_settings.prd_key}-db-subnet-group",
    enabled=ws_settings.prd_db_enabled,
    subnet_ids=ws_settings.subnet_ids,
    skip_delete=skip_delete,
    save_output=save_output,
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
    aws_secret=prd_db_secret,
    db_subnet_group=prd_db_subnet_group,
    db_security_groups=[prd_db_security_group],
    enable_performance_insights=True,
    # Read MASTER_USERNAME and MASTER_USER_PASSWORD from secrets/prd_db_secrets.yml
    # secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/prd_db_secrets.yml"),
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- ECS cluster
launch_type = "FARGATE"
prd_ecs_cluster = EcsCluster(
    name=f"{ws_settings.prd_key}-cluster",
    ecs_cluster_name=ws_settings.prd_key,
    capacity_providers=[launch_type],
    skip_delete=skip_delete,
    save_output=save_output,
)

# -*- Build container environment
container_env = {
    # Get the OpenAI API key from the local environment
    "OPENAI_API_KEY": getenv("OPENAI_API_KEY", ""),
}
if prd_db.enabled:
    container_env.update(
        {
            # Database configuration
            "DB_HOST": Reference(prd_db.get_db_endpoint),
            "DB_PORT": Reference(prd_db.get_db_port),
            "DB_USER": Reference(prd_db.get_master_username),
            "DB_PASS": Reference(prd_db.get_master_user_password),
            "DB_SCHEMA": Reference(prd_db.get_db_name),
            # Upgrade database on startup using alembic. Used to create tables on first run.
            # "UPGRADE_DB": True,
            # Wait for database to be available before starting the server
            # "WAIT_FOR_DB": True,
        }
    )

# -*- StreamlitApp running on ECS
prd_streamlit = StreamlitApp(
    name=f"{ws_settings.prd_key}-app",
    enabled=ws_settings.prd_app_enabled,
    image=prd_image,
    command=["app", "start", "Home"],
    ecs_task_cpu="1024",
    ecs_task_memory="2048",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    aws_secrets=[prd_app_secret],
    aws_security_groups=[prd_app_security_group],
    create_load_balancer=True,
    env=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Do not wait for the service to stabilize
    wait_for_creation=False,
    # Uncomment to read secrets from secrets/prd_app_secrets.yml
    # secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/prd_app_secrets.yml"),
)

# -*- FastApiServer running on ECS
prd_fastapi = FastApiServer(
    name=f"{ws_settings.prd_key}-api",
    enabled=ws_settings.prd_api_enabled,
    image=prd_image,
    command=["api", "start"],
    ecs_task_cpu="1024",
    ecs_task_memory="2048",
    ecs_cluster=prd_ecs_cluster,
    aws_subnets=ws_settings.subnet_ids,
    aws_secrets=[prd_app_secret],
    aws_security_groups=[prd_app_security_group],
    create_load_balancer=True,
    health_check_path="/v1/ping",
    env=container_env,
    use_cache=ws_settings.use_cache,
    skip_delete=skip_delete,
    save_output=save_output,
    # Uncomment to read secrets from secrets/prd_app_secrets.yml
    # secrets_file=ws_settings.ws_root.joinpath("workspace/secrets/prd_app_secrets.yml"),
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
        secrets=[prd_db_secret, prd_app_secret],
        security_groups=[prd_app_security_group, prd_db_security_group],
        s3_buckets=[prd_data_s3_bucket],
    ),
)
