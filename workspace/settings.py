from pathlib import Path

from phidata.workspace.settings import WorkspaceSettings

#
# -*- Define workspace settings using the WorkspaceSettings class
#
ws_settings = WorkspaceSettings(
    # Workspace name: used for naming cloud resources
    ws_name="ai-app",
    # Path to the workspace root
    ws_root=Path(__file__).parent.parent.resolve(),
    # -*- Dev settings
    dev_env="dev",
    # -*- Dev Apps
    dev_app_enabled=True,
    dev_api_enabled=True,
    dev_jupyter_enabled=True,
    dev_redis_enabled=True,
    # -*- Production settings
    prd_env="prd",
    # -*- Production Apps
    prd_app_enabled=True,
    prd_api_enabled=True,
    prd_redis_enabled=True,
    # -*- AWS settings
    # Region for AWS resources
    aws_region="us-east-1",
    # Availability Zones for AWS resources
    aws_az1="us-east-1a",
    aws_az2="us-east-1b",
    # aws_az3="us-east-1c",
    # Subnet IDs for AWS resources
    # subnet_ids=None,
    # Security Groups for AWS resources
    # security_groups=None,
    # -*- Image Settings
    # Repository for images
    # image_repo="your-repo",
    # Build images locally
    # build_images=True,
    # Push images after building
    # push_images=True,
)
