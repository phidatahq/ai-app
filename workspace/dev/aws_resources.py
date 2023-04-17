from phidata.aws.config import AwsConfig
from phidata.aws.resource.group import AwsResourceGroup, S3Bucket

from workspace.settings import ws_settings

#
# -*- AWS Resources for the dev environment
#

# -*- S3 bucket for dev data
dev_data_s3_bucket = S3Bucket(
    name=f"{ws_settings.dev_key}-data",
    acl="private",
)

# -*- AwsConfig defining the dev resources
dev_aws_config = AwsConfig(
    env=ws_settings.dev_env,
    resources=AwsResourceGroup(
        s3_buckets=[dev_data_s3_bucket],
    ),
)
