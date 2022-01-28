from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_glue as glue,
    aws_s3_deployment as s3deploy
)

from .s3_construct import S3Construct

class GlueConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        CrimesTable = "crimes"

        self.glue_role = iam.Role(
            self,
            f"{env_name}-GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )

        s3.scripts_bucket.grant_read(self.glue_role)
        s3.ingest_bucket.grant_read_write(self.glue_role)
        s3.clean_bucket.grant_read_write(self.glue_role)
        s3.publish_bucket.grant_read_write(self.glue_role)

        s3deploy.BucketDeployment(
            self,
            f"{env_name}-DeployGlueJobs",
            sources=[s3deploy.Source.asset("./scripts/glue")],
            destination_bucket=s3.scripts_bucket,
            destination_key_prefix="glue"
        )

        self.ingest_crawler = glue.CfnCrawler(
            self,
            id=f"{env_name}-IngestCrawler",
            name=f"{env_name}-IngestCrawler",
            role=self.glue_role.role_arn,
            database_name=s3.ingest_bucket.bucket_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{s3.ingest_bucket.bucket_name}/{CrimesTable}/"
                    )
                ]
            )
        )

        self.clean_job = glue.CfnJob(
            self,
            id=f"{env_name}-CleanJob",
            name=f"{env_name}-CleanJob",
            role=self.glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name='glueetl',
                python_version='3',
                script_location=f's3://{s3.scripts_bucket.bucket_name}/glue/clean.py'
            ),
            default_arguments={
                "--source_database": s3.ingest_bucket.bucket_name,
                "--source_table": CrimesTable,
                "--target_bucket": s3.clean_bucket.bucket_name,
                "--enable-continuous-cloudwatch-log": "true"
            },
            glue_version="3.0"
        )

        self.clean_crawler = glue.CfnCrawler(
            self,
            id=f"{env_name}-CleanCrawler",
            name=f"{env_name}-CleanCrawler",
            role=self.glue_role.role_arn,
            database_name=s3.clean_bucket.bucket_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{s3.clean_bucket.bucket_name}/{CrimesTable}/"
                    )
                ]
            )
        )
