from constructs import Construct
from aws_cdk import (
    Duration,
    Stack,
    aws_iam as iam,
    aws_sqs as sqs,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
)
from .glue_construct import GlueETLConstruct
from .s3_construct import S3Construct
from .vpc_construct import VpcConstruct


class Ab3DataLakeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_prefix = 'jnme-ab3-v1-'

        vpc = VpcConstruct(self, 'OctankVpcConstruct', **kwargs)
        s3 = S3Construct(self, 'OctankS3Construct', env_prefix, **kwargs)
        glue = GlueETLConstruct(self, 'OctankGlueConstruct', s3, **kwargs)
