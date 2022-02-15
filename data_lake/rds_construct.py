from constructs import Construct
from aws_cdk import aws_rds as rds
from aws_cdk import aws_iam as iam
from aws_cdk import aws_ec2 as ec2
import aws_cdk as cdk

from data_lake.ec2_construct import EC2Construct

from .vpc_construct import VpcConstruct
from .glue_construct import GlueConstruct
from .s3_construct import S3Construct

class RdsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, vpc_struct: VpcConstruct, ec2_struct: EC2Construct, s3_struct: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        # mysql_role = iam.Role(
        #     self,
        #     f"{env_name}-MySqlS3Role",
        #     assumed_by=iam.ServicePrincipal("rds.amazonaws.com")
        # )

        # s3_struct.ingest_bucket.grant_read(mysql_role)

        # mysql_parameter_group = rds.ParameterGroup(
        #     self,
        #     f"{env_name}-MySqlParameterGroup",
        #     engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
        #     parameters={
        #         "aurora_load_from_s3_role": mysql_role.role_arn
        #     }
        # )

        self.mysql_cluster = rds.DatabaseCluster(
            self,
            f"{env_name}-MySqlCluster",
            cluster_identifier=f"{env_name}-MySqlCluster",
            engine=rds.DatabaseClusterEngine.AURORA_MYSQL,
            instance_props=rds.InstanceProps(
                instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.SMALL),
                vpc_subnets=ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT
                ),
                vpc=vpc_struct.vpc
            ),
            # parameter_group=mysql_parameter_group,
            instances=1,
            s3_import_buckets=[s3_struct.ingest_bucket],
            # s3_export_buckets=[s3_struct.ingest_bucket]
            
        )

        self.mysql_cluster.connections.allow_default_port_from(ec2_struct.bastion.instance)
        

