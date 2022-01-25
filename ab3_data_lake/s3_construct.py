from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_kms as kms
import aws_cdk.aws_iam as iam

class S3Construct(Construct):

    def __init__(self, scope: Construct, id: str, env_prefix: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_principal = iam.AccountPrincipal(cdk.Aws.ACCOUNT_ID)

        self.s3_kms_key = kms.Key(
            self,
            'OctankKmsKey',
            admins=[account_principal],
            description='Encryption key for data lake S3 buckets',
            removal_policy=cdk.RemovalPolicy.DESTROY,
            alias='octank-kms-key'
        )
        
        self.s3_kms_key.add_to_resource_policy(
            iam.PolicyStatement(
                principals=[account_principal],
                actions=[
                    'kms:Encrypt',
                    'kms:Decrypt',
                    'ksm:ReEncrypt*',
                    'kms:GenerateDataKey*',
                    'kms:DescribeKey'
                ],
                resources=['*']
            )
        )
        
        self.logs_bucket = s3.Bucket(
            self,
            id='octank_logs_bucket',
            access_control=s3.BucketAccessControl.LOG_DELIVERY_WRITE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_key_enabled=True,
            bucket_name=f'{env_prefix}logs',
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.s3_kms_key,
            public_read_access=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            versioned=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED
        )

        self.scripts_bucket = s3.Bucket(
            self,
            id='octank_scripts_bucket',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f'{env_prefix}scripts',
            public_read_access=False,
            removal_policy=cdk.RemovalPolicy.DESTROY,
            versioned=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_PREFERRED
        )

        ingest_lifecycle = s3.LifecycleRule(
            enabled=True,
            expiration=cdk.Duration.days(60),
            noncurrent_version_expiration=cdk.Duration.days(30)
        )

        retention_lifecycle = s3.LifecycleRule(
            enabled=True,
            expiration=cdk.Duration.days(365 * 7),
            noncurrent_version_expiration=cdk.Duration.days(90),
            transitions=[
                s3.Transition(
                    storage_class=s3.StorageClass.INFREQUENT_ACCESS,
                    transition_after=cdk.Duration.days(180)
                ),
                s3.Transition(
                    storage_class=s3.StorageClass.GLACIER,
                    transition_after=cdk.Duration.days(365)
                )
            ]
        )

        self.ingest_bucket = self.create_bucket(
            'octank_ingest_bucket', 
            f'{env_prefix}ingest', 
            self.s3_kms_key,
            self.logs_bucket, 
            ingest_lifecycle
        )

        self.clean_bucket = self.create_bucket(
            'octank_clean_bucket',
            f'{env_prefix}clean',
            self.s3_kms_key,
            self.logs_bucket,
            retention_lifecycle
        )

        self.publish_bucket = self.create_bucket(
            'octank_publish_bucket',
            f'{env_prefix}publish',
            self.s3_kms_key,
            self.logs_bucket,
            retention_lifecycle
        )

        cdk.CfnOutput(
            self,
            'KmsKeyArn',
            value=self.s3_kms_key.key_arn,
            export_name='S3KmsKeyArn'
        )
        cdk.CfnOutput(
            self,
            'AccessLogBucketName',
            value=self.logs_bucket.bucket_name,
            export_name='S3AccessLogsBucket'
        )
        cdk.CfnOutput(
            self,
            'IngestBucketName',
            value=self.ingest_bucket.bucket_name,
            export_name='S3IngestBucket'
        )
        cdk.CfnOutput(
            self,
            'S3CleanBucketName',
            value=self.clean_bucket.bucket_name,
            export_name='S3CleanBucket'
        )
        cdk.CfnOutput(
            self,
            'S3PublishBucketName',
            value=self.publish_bucket.bucket_name,
            export_name='S3PublishBucket'
        )


    def create_bucket(
        self, 
        bucket_id: str, 
        bucket_name: str, 
        kms_key: kms.Key,
        logs_bucket: s3.Bucket, 
        lifecycle: s3.LifecycleRule) -> s3.Bucket:
        
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
            server_access_logs_bucket=logs_bucket,
            server_access_logs_prefix=bucket_name
        )

        bucket_policies = [
            iam.PolicyStatement(
                sid='OnlyAllowSecureTransport',
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=[
                    's3:GetObject',
                    's3:PutObject'
                ],
                resources=[f'{bucket.bucket_arn}/*'],
                conditions={
                    'Bool': {
                        'aws:SecureTransport': 'false'
                    }
                }
            ),
            iam.PolicyStatement(
                sid='BlockUserDelete',
                effect=iam.Effect.DENY,
                principals=[iam.AnyPrincipal()],
                actions=[
                    's3:DeleteBucket'
                ],
                resources=[bucket.bucket_arn],
                conditions={
                    'StringLike': {
                        'aws:userId': f'arn:aws:iam::{cdk.Aws.ACCOUNT_ID}:user/*'
                    }
                }
            )
        ]

        for policy in bucket_policies:
            bucket.add_to_resource_policy(policy)

        return bucket