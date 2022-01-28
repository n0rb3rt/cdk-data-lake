from constructs import Construct
from aws_cdk import Stack

from .vpc_construct import VpcConstruct
from .s3_construct import S3Construct
from .glue_construct import GlueConstruct
from .workflow_construct import WorkflowConstruct

class Ab3DataLakeStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = 'jnme-ab3-v1'

        vpc = VpcConstruct(self, 'OctankVpcConstruct', env_name, **kwargs)
        s3 = S3Construct(self, 'OctankS3Construct', env_name, **kwargs)
        glue = GlueConstruct(self, 'OctankGlueConstruct', env_name, s3, **kwargs)
        workflow = WorkflowConstruct(self, 'OctankWorkflowConstruct', env_name, glue, **kwargs)
