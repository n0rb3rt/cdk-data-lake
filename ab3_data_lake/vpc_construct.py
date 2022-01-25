from constructs import Construct
import aws_cdk as cdk
import aws_cdk.aws_ec2 as ec2


class VpcConstruct(Construct):

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        vpc = ec2.Vpc(
            self, 
            'OctankVpc', 
            cidr='10.0.0.0/24',
            max_azs=2,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            nat_gateways=1,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name='Public-Subnet',
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=26
                ),
                ec2.SubnetConfiguration(
                    name='Private-Subnet',
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT,
                    cidr_mask=26
                )
            ]
        )
        
        security_group = ec2.SecurityGroup(
            self,
            'OctankSecurityGroup',
            vpc=vpc,
            description='Data Lake security group',
            security_group_name='OctankSecurityGroup'
        )
        security_group.add_ingress_rule(
            peer=security_group,
            connection=ec2.Port.all_traffic(),
            description='Self-referencing ingress rule'
        )
        
        vpc.add_gateway_endpoint(
            'S3Endpoint', 
            service=ec2.GatewayVpcEndpointAwsService.S3
        )
        vpc.add_interface_endpoint(
            'GlueEndpoint', 
            service=ec2.InterfaceVpcEndpointAwsService.GLUE,
            security_groups=[security_group]
        )
        vpc.add_interface_endpoint(
            'KmsEndpoint',
            service=ec2.InterfaceVpcEndpointAwsService.KMS,
            security_groups=[security_group]
        )

        cdk.CfnOutput(
            self,
            'Vpc',
            value=vpc.vpc_id,
            export_name='VpcId'
        )
        cdk.CfnOutput(
            self,
            'VpcAvailabilityZone1',
            value=vpc.availability_zones[0],
            export_name='AvailabilityZone1'
        )
        cdk.CfnOutput(
            self,
            'VpcAvailabilityZone2',
            value=vpc.availability_zones[1],
            export_name='AvailabilityZone2'
        )
        cdk.CfnOutput(
            self,
            'VpcPrivateSubnet',
            value=vpc.private_subnets[0].subnet_id,
            export_name='PrivateSubnet'
        )
        cdk.CfnOutput(
            self,
            'VpcPublicSubnet',
            value=vpc.public_subnets[0].subnet_id,
            export_name='PublicSubnet'
        )
        cdk.CfnOutput(
            self,
            'VpcRouteTable1',
            value=vpc.private_subnets[0].route_table.route_table_id,
            export_name='PrivateRouteTable'
        )
        cdk.CfnOutput(
            self,
            'VpcRouteTable2',
            value=vpc.public_subnets[0].route_table.route_table_id,
            export_name='PublicRouteTable'
        )
        cdk.CfnOutput(
            self,
            'SecurityGroup',
            value=security_group.security_group_id,
            export_name='SecurityGroupId'
        )
