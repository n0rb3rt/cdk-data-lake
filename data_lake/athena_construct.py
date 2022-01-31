from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_athena as athena,
    aws_quicksight as quicksight
)

from .s3_construct import S3Construct

class AthenaConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_id = cdk.Aws.ACCOUNT_ID

        self.quicksight_role = iam.Role.from_role_arn(
            self, 
            f"{env_name}-QuicksightRole",
            f"arn:aws:iam::{account_id}:role/aws-quicksight-service-role-v0"
        )

        self.quicksight_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSQuicksightAthenaAccess"
            )
        )

        self.quicksight_role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:GetBucketLocation"
                ],
                resources=[
                    s3.query_bucket.bucket_arn
                ]
            )
        )

        self.quicksight_role.add_to_principal_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts"
                ],
                resources=[
                    f"{s3.query_bucket.bucket_arn}/*"
                ]
            )
        )

        s3.clean_bucket.grant_read(self.quicksight_role)
        s3.query_bucket.grant_read_write(self.quicksight_role)

        self.athena_workgroup = athena.CfnWorkGroup(
            self,
            id=f"{env_name}-WorkGroup",
            name=f"{env_name}-WorkGroup",
            work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
                publish_cloud_watch_metrics_enabled=True,
                result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
                    encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
                        encryption_option="SSE_KMS",
                        kms_key=s3.s3_kms_key.key_arn
                    ),
                    output_location=f"s3://{s3.query_bucket.bucket_name}/results/"
                )
            )
        )

        self.quicksight_datasource = quicksight.CfnDataSource(
            self,
            id=f"{env_name}-AthenaDataSource",
            name=f"{env_name}-AthenaDataSource",
            data_source_parameters=quicksight.CfnDataSource.DataSourceParametersProperty(
                athena_parameters=quicksight.CfnDataSource.AthenaParametersProperty(
                    work_group=self.athena_workgroup.name
                )
            ),
            aws_account_id=account_id,
            data_source_id="athena-data",
            type="ATHENA"
        )

        self.quicksight_datasource.add_depends_on(self.athena_workgroup)