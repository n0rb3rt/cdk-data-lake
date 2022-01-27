from constructs import Construct
from aws_cdk import (
    aws_iam as iam,
    aws_glue as glue,
    aws_s3_deployment as s3deploy
)
import aws_cdk.aws_iam as iam
import aws_cdk.aws_glue as glue


from .s3_construct import S3Construct


class GlueETLConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        glue_role = iam.Role(
            self,
            "GlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )

        s3.scripts_bucket.grant_read(glue_role)
        s3.ingest_bucket.grant_read_write(glue_role)
        s3.clean_bucket.grant_read_write(glue_role)
        s3.publish_bucket.grant_read_write(glue_role)

        s3deploy.BucketDeployment(
            self,
            "DeployGlueJobs",
            sources=[s3deploy.Source.asset("./scripts/glue")],
            destination_bucket=s3.scripts_bucket,
            destination_key_prefix="glue"
        )

        ingest_crawler = glue.CfnCrawler(
            self,
            "IngestCrawler",
            role=glue_role.role_arn,
            database_name=env_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path=f"s3://{s3.ingest_bucket.bucket_name}/crimes/"
                    )
                ]
            )
        )

        clean_job = glue.CfnJob(
            self,
            "CleanJob",
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name='pythonshell',
                python_version='3',
                script_location=f's3://{s3.scripts_bucket.bucket_name}/glue/clean.py'
            )
        )

        clean_job2 = glue.CfnJob(
            self,
            'CleanJob2',
            role=glue_role.role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name='glueetl',
                python_version='3',
                script_location=f's3://{s3.scripts_bucket.bucket_name}/glue/clean2.py'
            ),
            default_arguments={
                "--source_database": env_name,
                "--source_table": "crimes",
                "--target_bucket": s3.clean_bucket.bucket_name,
                "--enable-continuous-cloudwatch-log": "true"
            },
            glue_version="3.0"
        )
