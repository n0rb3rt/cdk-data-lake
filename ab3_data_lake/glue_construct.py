from constructs import Construct
import aws_cdk.aws_iam as iam
import aws_cdk.aws_glue as glue

from .s3_construct import S3Construct

class GlueETLConstruct(Construct):

    def __init__(self, scope: Construct, id: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        glue_role = iam.Role(
            self,
            'GlueRole',
            assumed_by=iam.ServicePrincipal('glue.amazonaws.com'),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AWSGlueServiceRole')
            ]
        )

        s3.ingest_bucket.grant_read_write(glue_role)

        ingest_crawler = glue.CfnCrawler(
            self,
            'IngestCrawler',
            role=glue_role.role_arn,
            database_name='octank_ab3',
            targets={
                's3Targets': [
                    {'path': f's3://{s3.ingest_bucket.bucket_name}/'}
                ]
            }
        )