from constructs import Construct
import aws_cdk as cdk
from aws_cdk import (
    aws_iam as iam,
    aws_athena as athena,
    aws_quicksight as quicksight
)

from .s3_construct import S3Construct

class QuicksightConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, s3: S3Construct, **kwargs):
        super().__init__(scope, id, **kwargs)

        account_id = cdk.Aws.ACCOUNT_ID
        
        #https://docs.aws.amazon.com/solutions/latest/discovering-hot-topics-using-machine-learning/quicksight-principal-arn.html
        #aws quicksight list-users --region <aws-region> --aws-account-id <account-id> --namespace default
        quicksight_user = "arn:aws:quicksight:us-east-1:121891376456:user/default/Admin/jnmeehan-Isengard"

        self.quicksight_role = iam.Role.from_role_arn(
            self, 
            f"{env_name}-QuicksightRole",
            f"arn:aws:iam::{account_id}:role/aws-quicksight-service-role-v0"
        )

        self.quicksight_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                "service-role/AWSQuicksightAthenaAccess"
            )
        )

        policies = [
            iam.PolicyStatement(
                actions=[
                    "s3:ListBucket",
                    "s3:ListBucketMultipartUploads",
                    "s3:GetBucketLocation"
                ],
                resources=[
                    s3.query_bucket.bucket_arn
                ]
            ),
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:GetObjectVersion",
                    "s3:PutObject",
                    "s3:AbortMultipartUpload",
                    "s3:ListMultipartUploadParts"
                ],
                resources=[
                    f"{s3.query_bucket.bucket_arn}/*"
                ]
            )
        ]

        for p in policies:
            self.quicksight_role.add_to_principal_policy(p)

        s3.clean_bucket.grant_read(self.quicksight_role)
        s3.query_bucket.grant_read_write(self.quicksight_role)

        # data_source_read_only_actions = [
        #     "quicksight:DescribeDataSource",
        #     "quicksight:DescribeDataSourcePermissions",
        #     "quicksight:PassDataSource"
        # ]

        # data_set_read_only_actions = [
        #     "quicksight:DescribeDataSet",
        #     "quicksight:DescribeDataSetPermissions",
        #     "quicksight:PassDataSet",
        #     "quicksight:DescribeIngestion",
        #     "quicksight:ListIngestions"
        # ]

        # self.athena_workgroup = athena.CfnWorkGroup(
        #     self,
        #     id=f"{env_name}-WorkGroup",
        #     name=f"{env_name}-WorkGroup",
        #     work_group_configuration=athena.CfnWorkGroup.WorkGroupConfigurationProperty(
        #         publish_cloud_watch_metrics_enabled=True,
        #         result_configuration=athena.CfnWorkGroup.ResultConfigurationProperty(
        #             encryption_configuration=athena.CfnWorkGroup.EncryptionConfigurationProperty(
        #                 encryption_option="SSE_KMS",
        #                 kms_key=s3.s3_kms_key.key_arn
        #             ),
        #             output_location=f"s3://{s3.query_bucket.bucket_name}/results/"
        #         )
        #     ),
        #     recursive_delete_option=True
        # )

        # self.quicksight_datasource = quicksight.CfnDataSource(
        #     self,
        #     id=f"{env_name}-AthenaDataSource",
        #     name=f"{env_name}-AthenaDataSource",
        #     data_source_parameters=quicksight.CfnDataSource.DataSourceParametersProperty(
        #         athena_parameters=quicksight.CfnDataSource.AthenaParametersProperty(
        #             work_group=self.athena_workgroup.name
        #         )
        #     ),
        #     aws_account_id=account_id,
        #     data_source_id="athena-data",
        #     type="ATHENA",
        #     permissions=[
        #         quicksight.CfnDataSource.ResourcePermissionProperty(
        #             principal=quicksight_user,
        #             actions=data_source_read_only_actions
        #         )
        #     ]
        # )

        # input_columns = [
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="id", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="case_number", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="date", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="block", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="iucr", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="primary_type", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="description", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="location_description", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="arrest", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="domestic", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="beat", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="district", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="ward", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="community_area", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="fbi_code", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="x_coordinate", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="y_coordinate", type="INTEGER"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="updated_on", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="latitude", type="DECIMAL"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="longitude", type="DECIMAL"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="location", type="STRING"
        #     ),
        #     quicksight.CfnDataSet.InputColumnProperty(
        #         name="year", type="STRING"
        #     )
        # ]

        # self.quicksight_dataset = quicksight.CfnDataSet(
        #     self,
        #     id=f"{env_name}-CrimesCleanDataSet",
        #     name=f"{env_name}-CrimesCleanDataSet",
        #     aws_account_id=account_id,
        #     data_set_id="crimes-dataset",
        #     column_groups=[
        #         quicksight.CfnDataSet.ColumnGroupProperty(
        #             geo_spatial_column_group=quicksight.CfnDataSet.GeoSpatialColumnGroupProperty(
        #                 columns=["latitude", "longitude"],
        #                 name="name"
        #             )
        #         )
        #     ],
        #     physical_table_map={
        #         "crimes": quicksight.CfnDataSet.PhysicalTableProperty(
        #             custom_sql=quicksight.CfnDataSet.CustomSqlProperty(
        #                 data_source_arn=self.quicksight_datasource.attr_arn,
        #                 name="crimes",
        #                 sql_query=f'SELECT * FROM "AwsDataCatalog"."{s3.clean_bucket.bucket_name}"."crimes"',
        #                 columns=input_columns
        #             )
        #         )
        #     }
        # )

        # self.quicksight_datasource.add_depends_on(self.athena_workgroup)