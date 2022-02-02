import sys
from datetime import datetime

import pytz
from awsglue import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import to_timestamp

## @params: [JOB_NAME]
args = getResolvedOptions(sys.argv, [
    "JOB_NAME",
    "source_database",
    "source_table",
    "target_bucket"
])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)
logger = glueContext.get_logger()

out_path = f"s3://{args['target_bucket']}/{args['source_table']}"
date_format = "MM/dd/yyyy hh:mm:ss a"

logger.info(f"Transforming {args['source_database']}/{args['source_table']} into {out_path}")

datasource0: DynamicFrame = glueContext.create_dynamic_frame.from_catalog(
    database = args["source_database"], 
    table_name = args["source_table"], 
    transformation_ctx = "datasource0"
)

transform1 = DynamicFrame.fromDF(
    glue_ctx=glueContext,
    name="transform1",
    dataframe=datasource0.toDF() \
        .withColumn("date", to_timestamp("date", date_format)) \
        .withColumn("updated on", to_timestamp("updated on", date_format))
)

applymapping1 = ApplyMapping.apply(
    frame = transform1, 
    transformation_ctx = "applymapping1",
    mappings = [
        ("id", "long", "id", "long"), 
        ("case number", "string", "case_number", "string"), 
        ("date", "timestamp", "date", "timestamp"), 
        ("block", "string", "block", "string"), 
        ("iucr", "string", "iucr", "string"), 
        ("primary type", "string", "primary_type", "string"), 
        ("description", "string", "description", "string"), 
        ("location description", "string", "location_description", "string"), 
        ("arrest", "boolean", "arrest", "boolean"), 
        ("domestic", "boolean", "domestic", "boolean"), 
        ("beat", "long", "beat", "long"), 
        ("district", "long", "district", "long"), 
        ("ward", "long", "ward", "long"), 
        ("community area", "long", "community_area", "long"), 
        ("fbi code", "string", "fbi_code", "string"), 
        ("x coordinate", "long", "x_coordinate", "long"), 
        ("y coordinate", "long", "y_coordinate", "long"), 
        ("year", "long", "year", "long"), 
        ("updated on", "timestamp", "updated_on", "timestamp"), 
        ("latitude", "double", "latitude", "double"), 
        ("longitude", "double", "longitude", "double"), 
        ("location", "string", "location", "string")
    ]
)

datasink1 = glueContext.write_dynamic_frame.from_options(
    frame=applymapping1, 
    connection_type="s3",
    connection_options={
        "path": out_path,
        "partitionKeys": ["year"]
    },
    format="parquet",
    transformation_ctx = "datasink1"
)

job.commit()
