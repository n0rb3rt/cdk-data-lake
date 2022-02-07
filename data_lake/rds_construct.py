from constructs import Construct
from aws_cdk import aws_rds as rds
from aws_cdk import aws_iam as iam
import aws_cdk as cdk

from .vpc_construct import VpcConstruct
from .glue_construct import GlueConstruct

class RdsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, vpc: VpcConstruct, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.cluster = rds.ServerlessCluster(
            self,
            id=f"{env_name}-RdsCluster",
            cluster_identifier=f"{env_name}-RdsCluster",
            vpc=vpc.vpc,
            vpc_subnets=vpc.vpc.private_subnets[0],
            engine=rds.DatabaseClusterEngine.AURORA_POSTGRESQL,
            parameter_group=rds.ParameterGroup.from_parameter_group_name(
                self, 
                "ParameterGroup", 
                "default.aurora-postgresql10"
            )
        )

        cdk.CfnOutput(
            self,
            "RdsClusterEndpoint",
            value=self.cluster.cluster_endpoint.hostname,
            export_name="RdsClusterEndpoint"
        )

        cdk.CfnOutput(
            self,
            "RdsClusterSecretArn",
            value=self.cluster.secret.secret_arn,
            export_name="RdsClusterSecretArn"
        )