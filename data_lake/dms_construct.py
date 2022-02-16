import json

import aws_cdk as cdk
from aws_cdk import aws_dms as dms
from aws_cdk import aws_iam as iam
from constructs import Construct

from .rds_construct import RdsConstruct
from .s3_construct import S3Construct
from .vpc_construct import VpcConstruct


class DmsConstruct(Construct):

    def __init__(self, scope: Construct, id: str, env_name: str, vpc_struct: VpcConstruct, rds_struct: RdsConstruct, s3_struct: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        migration_role = iam.Role(
            self,
            id=f"{env_name}-DmsMigrationRole",
            role_name=f"{env_name}-DmsMigrationRole",
            assumed_by=iam.ServicePrincipal(f"dms.{cdk.Aws.REGION}.amazonaws.com")
        )

        rds_struct.mysql_cluster.secret.grant_read(migration_role)
        s3_struct.ingest_bucket.grant_read_write(migration_role)
        
        subnet_group = dms.CfnReplicationSubnetGroup(
            self,
            id=f"{env_name}-SubnetGroup",
            replication_subnet_group_identifier=f"{env_name}-SubnetGroup",
            replication_subnet_group_description="Subnets for source and target",
            subnet_ids=[subnet.subnet_id for subnet in vpc_struct.vpc.private_subnets]
        )

        replication_instance = dms.CfnReplicationInstance(
            self,
            id=f"{env_name}-ReplicationInstance",
            replication_instance_identifier=f"{env_name}-ReplicationInstance",
            replication_instance_class="dms.t3.medium",
            replication_subnet_group_identifier=subnet_group.replication_subnet_group_identifier.lower(),
            vpc_security_group_ids=[vpc_struct.security_group.security_group_id],
            allocated_storage=50,
            publicly_accessible=False,
            engine_version="3.4.4"
        )

        replication_instance.add_depends_on(subnet_group)

        mysql_endpoint = dms.CfnEndpoint(
            self,
            id=f"{env_name}-MySqlEndpoint",
            endpoint_identifier=f"{env_name}-MySqlEndpoint",
            endpoint_type="source",
            engine_name="mysql",
            my_sql_settings=dms.CfnEndpoint.MySqlSettingsProperty(
                secrets_manager_access_role_arn=migration_role.role_arn,
                secrets_manager_secret_id=rds_struct.mysql_cluster.secret.secret_name
            )
        )

        s3_endpoint = dms.CfnEndpoint(
            self,
            id=f"{env_name}-S3Endpoint",
            endpoint_identifier=f"{env_name}-S3Endpoint",
            endpoint_type="target",
            engine_name="s3",
            s3_settings=dms.CfnEndpoint.S3SettingsProperty(
                bucket_name=s3_struct.ingest_bucket.bucket_name,
                bucket_folder="dms",
                service_access_role_arn=migration_role.role_arn
            )
        )

        replication_task = dms.CfnReplicationTask(
            self,
            id=f"{env_name}-ReplicationTask",
            replication_task_identifier=f"{env_name}-ReplicationTask",
            replication_instance_arn=replication_instance.ref,
            migration_type="full-load",
            source_endpoint_arn=mysql_endpoint.ref,
            target_endpoint_arn=s3_endpoint.ref,
            table_mappings=json.dumps({
                "rules": [
                    {
                        "rule-type": "selection",
                        "rule-id": "1",
                        "rule-name": "1",
                        "object-locator": {
                            "schema-name": "precinct1",
                            "table-name": "crimes"
                        },
                        "rule-action": "include"
                    }
                ]
            })
        )
