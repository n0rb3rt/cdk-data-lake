from aws_cdk import Stack
from constructs import Construct
from data_lake.ec2_construct import EC2Construct

from data_lake.rds_construct import RdsConstruct

from .glue_construct import GlueConstruct
from .quicksight_construct import QuicksightConstruct
from .s3_construct import S3Construct
from .vpc_construct import VpcConstruct
from .workflow_construct import WorkflowConstruct


class DataLakeStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        env_name = "jnme-ab3-v1"
        keypair_name = "USE2KP"

        # Data Lake
        s3 = S3Construct(self, f"{env_name}-S3Construct", env_name, **kwargs)
        glue = GlueConstruct(self, f"{env_name}-GlueConstruct", env_name, s3, **kwargs)
        workflow = WorkflowConstruct(
            self, f"{env_name}-WorkflowConstruct", env_name, glue, **kwargs
        )
        quicksight = QuicksightConstruct(
            self, f"{env_name}-QuicksightConstruct", env_name, s3, **kwargs
        )

        # Source DB
        vpc = VpcConstruct(self, f"{env_name}-VpcConstruct", env_name, **kwargs)
        ec2 = EC2Construct(self, f"{env_name}-Ec2Construct", env_name, keypair_name, vpc)
        rds = RdsConstruct(self, f"{env_name}-RdsConstruct", env_name, vpc, ec2, s3, **kwargs)
        
