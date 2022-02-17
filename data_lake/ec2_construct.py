import aws_cdk as cdk
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from .vpc_construct import VpcConstruct


class EC2Construct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, vpc_struct: VpcConstruct, **kwargs):
        super().__init__(scope, id, **kwargs)

        # ubuntu_image = ec2.MachineImage.from_ssm_parameter(
        #     "/aws/service/canonical/ubuntu/server/focal/stable/current/amd64/hvm/ebs-gp2/ami-id",
        #     os = ec2.OperatingSystemType.LINUX
        # )

        self.bastion = ec2.BastionHostLinux(
            self,
            id=f"{env_name}-Bastion",
            instance_name=f"{env_name}-Bastion",
            instance_type=ec2.InstanceType("t2.micro"),
            vpc=vpc_struct.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            init=ec2.CloudFormationInit.from_elements(
                ec2.InitFile.from_asset("/home/ssm-user/download_crimes_data.sh", "./scripts/bash/download_crimes_data.sh"),
                ec2.InitFile.from_asset("/home/ssm-user/crimes_table.sql", "./scripts/sql/crimes_table.sql"),
            )
        )
