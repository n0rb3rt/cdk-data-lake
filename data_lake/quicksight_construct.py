import aws_cdk as cdk
from aws_cdk import aws_iam as iam
from constructs import Construct

from .s3_construct import S3Construct


class QuicksightConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.quicksight_role = iam.Role.from_role_arn(
            self, 
            f"{env_name}-QuicksightRole",
            f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:role/aws-quicksight-service-role-v0"
        )

        self.quicksight_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSQuicksightAthenaAccess"
            )
        )

        s3.ingest_bucket.grant_read(self.quicksight_role)
        s3.clean_bucket.grant_read(self.quicksight_role)
        s3.publish_bucket.grant_read(self.quicksight_role)
