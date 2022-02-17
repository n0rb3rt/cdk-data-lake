from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from constructs import Construct

from data_lake.ec2_construct import EC2Construct

from .s3_construct import S3Construct
from .vpc_construct import VpcConstruct


class RdsConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, vpc_struct: VpcConstruct, ec2_struct: EC2Construct, s3_struct: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

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
            instances=1,
            s3_import_buckets=[s3_struct.ingest_bucket],
        )

        # self.mysql_cluster.connections.allow_default_port_from(ec2_struct.bastion.instance)
        self.mysql_cluster.connections.allow_default_port_internally
