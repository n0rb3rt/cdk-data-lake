import aws_cdk as cdk
import aws_cdk.aws_iam as iam
import aws_cdk.aws_kms as kms
import aws_cdk.aws_s3 as s3
from constructs import Construct


class S3Construct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_principal = iam.AccountPrincipal(cdk.Aws.ACCOUNT_ID)

        ingest_lifecycle = s3.LifecycleRule(
            enabled=True,
            expiration=cdk.Duration.days(60),
            noncurrent_version_expiration=cdk.Duration.days(30),
        )

        retention_lifecycle = s3.LifecycleRule(
            enabled=True,
            expiration=cdk.Duration.days(365 * 7),
            noncurrent_version_expiration=cdk.Duration.days(90),
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=cdk.Duration.days(180),
                ),
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=cdk.Duration.days(365),
                ),
            ],
        )

        self.s3_kms_key = kms.Key(
            self,
            f"{env_name}-KmsKey",
            admins=[account_principal],
            description="Encryption key for data lake S3 buckets",
            removal_policy=cdk.RemovalPolicy.DESTROY
        )

        self.s3_kms_key.add_to_resource_policy(
            iam.PolicyStatement(
                principals=[account_principal],
                actions=[
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "ksm:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:DescribeKey",
                ],
                resources=["*"],
            )
        )

        self.scripts_bucket = s3.Bucket(
            self,
            id=f"{env_name}-ScriptsBucket",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f"{env_name}-scripts",
            public_read_access=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            versioned=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED,
            auto_delete_objects=True
        )

        self.ingest_bucket = self.create_bucket(
            f"{env_name}-IngestBucket",
            f"{env_name}-ingest",
            self.s3_kms_key,
            ingest_lifecycle,
        )

        self.clean_bucket = self.create_bucket(
            f"{env_name}-CleanBucket",
            f"{env_name}-clean",
            self.s3_kms_key,
            retention_lifecycle,
        )

        self.publish_bucket = self.create_bucket(
            f"{env_name}-PublishBucket",
            f"{env_name}-publish",
            self.s3_kms_key,
            retention_lifecycle,
        )

        cdk.CfnOutput(
            self,
            "S3ScriptsBucketName",
            value=self.scripts_bucket.bucket_name,
            export_name="ScriptsBucket",
        )
        cdk.CfnOutput(
            self,
            "S3IngestBucketName",
            value=self.ingest_bucket.bucket_name,
            export_name="IngestBucket",
        )
        cdk.CfnOutput(
            self,
            "S3CleanBucketName",
            value=self.clean_bucket.bucket_name,
            export_name="CleanBucket",
        )
        cdk.CfnOutput(
            self,
            "S3PublishBucketName",
            value=self.publish_bucket.bucket_name,
            export_name="PublishBucket",
        )

    def create_bucket(
        self,
        bucket_id: str,
        bucket_name: str,
        kms_key: kms.Key,
        lifecycle: s3.LifecycleRule,
    ) -> s3.Bucket:

        bucket = s3.Bucket(
            self,
            id=bucket_id,
            bucket_name=bucket_name,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            public_read_access=False,
            bucket_key_enabled=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=kms_key,
            lifecycle_rules=[lifecycle],
            removal_policy=cdk.RemovalPolicy.DESTROY,
            versioned=True,
            object_ownership=s3.ObjectOwnership.OBJECT_WRITER,
            auto_delete_objects=True
        )

        bucket_policies = [
            iam.PolicyStatement(
                sid="OnlyAllowSecureTransport",
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject", "s3:PutObject"],
                resources=[f"{bucket.bucket_arn}/*"],
                conditions={"Bool": {"aws:SecureTransport": "false"}},
            ),
            iam.PolicyStatement(
                sid="BlockUserDelete",
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=["s3:DeleteBucket"],
                resources=[bucket.bucket_arn],
                conditions={
                    "StringLike": {
                        "aws:userId": f"arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:user/*"
                    }
                },
            ),
        ]

        for policy in bucket_policies:
            bucket.add_to_resource_policy(policy)

        return bucket
