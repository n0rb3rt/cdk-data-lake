from constructs import Construct

from aws_cdk import aws_ec2 as ec2
import aws_cdk as cdk

from .vpc_construct import VpcConstruct

class EC2Construct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, vpc_struct: VpcConstruct, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.bastion = ec2.BastionHostLinux(
            self,
            id=f"{env_name}-Bastion",
            instance_name=f"{env_name}-Bastion",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.AmazonLinuxImage(),
            vpc=vpc_struct.vpc,
            subnet_selection=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            )
        )

        cdk.CfnOutput(
            self,
            f"{env_name}-BastionInstanceId",
            value=self.bastion.instance_id,
            export_name=f"{env_name}-BastionInstanceId"
        )
