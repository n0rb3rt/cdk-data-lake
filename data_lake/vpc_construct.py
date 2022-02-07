from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2


class VpcConstruct(Construct):

    def __init__(self, scope: Construct, id: str, env_name: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.vpc = ec2.Vpc(
            self, 
            f"{env_name}-Vpc", 
            cidr='10.0.0.0/24',
            max_azs=2,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{env_name}-PublicSubnet",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=26
                ),
                ec2.SubnetConfiguration(
                    name=f"{env_name}-PrivateSubnet",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=26
                )
            ]
        )
        
        self.security_group = ec2.SecurityGroup(
            self,
            f"{env_name}-SecurityGroup",
            vpc=self.vpc,
            description='Data Lake security group',
            security_group_name=f"{env_name}-SecurityGroup"
        )
        self.security_group.add_ingress_rule(
            peer=self.security_group,
            connection=ec2.Port.all_traffic(),
            description='Self-referencing ingress rule'
        )
        
        self.vpc.add_gateway_endpoint(
            f"{env_name}-S3Endpoint", 
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        self.vpc.add_interface_endpoint(
            f"{env_name}-GlueEndpoint", 
            service=ec2.InterfaceVpcEndpointAwsService.GLUE,
            security_groups=[self.security_group]
        )
        self.vpc.add_interface_endpoint(
            f"{env_name}-KmsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.KMS,
            security_groups=[self.security_group]
        )

        cdk.CfnOutput(
            self,
            'Vpc',
            value=self.vpc.vpc_id,
            export_name='VpcId'
        )
        cdk.CfnOutput(
            self,
            'VpcAvailabilityZone1',
            value=self.vpc.availability_zones[0],
            export_name='VpcAvailabilityZone1'
        )
        cdk.CfnOutput(
            self,
            'VpcAvailabilityZone2',
            value=self.vpc.availability_zones[1],
            export_name='VpcAvailabilityZone2'
        )
        cdk.CfnOutput(
            self,
            'VpcPrivateSubnet',
            value=self.vpc.private_subnets[0].subnet_id,
            export_name='VpcPrivateSubnet'
        )
        cdk.CfnOutput(
            self,
            'VpcPublicSubnet',
            value=self.vpc.public_subnets[0].subnet_id,
            export_name='VpcPublicSubnet'
        )
        cdk.CfnOutput(
            self,
            'VpcRouteTable1',
            value=self.vpc.private_subnets[0].route_table.route_table_id,
            export_name='VpcPrivateRouteTable'
        )
        cdk.CfnOutput(
            self,
            'VpcRouteTable2',
            value=self.vpc.public_subnets[0].route_table.route_table_id,
            export_name='VpcPublicRouteTable'
        )
        cdk.CfnOutput(
            self,
            'SecurityGroup',
            value=self.security_group.security_group_id,
            export_name='VpcSecurityGroupId'
        )
