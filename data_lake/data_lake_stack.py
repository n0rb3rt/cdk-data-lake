from constructs import Construct
from aws_cdk import Stack

from data_lake.athena_construct import AthenaConstruct

from .vpc_construct import VpcConstruct
from .s3_construct import S3Construct
from .glue_construct import GlueConstruct
from .workflow_construct import WorkflowConstruct
from .athena_construct import AthenaConstruct

class DataLakeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = 'jnme-ab3-v1'

        vpc = VpcConstruct(self, f"{env_name}-VpcConstruct", env_name, **kwargs)
        s3 = S3Construct(self, f"{env_name}-S3Construct", env_name, **kwargs)
        glue = GlueConstruct(self, f"{env_name}-GlueConstruct", env_name, s3, **kwargs)
        workflow = WorkflowConstruct(self, f"{env_name}-WorkflowConstruct", env_name, glue, **kwargs)
        athena = AthenaConstruct(self, f"{env_name}-AthenaConstruct", env_name, s3, **kwargs)
