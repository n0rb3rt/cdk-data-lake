import sys

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

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

logger.info(f"Transforming {args['source_database']}/{args['source_table']} into {out_path}")

datasource0 = glueContext.create_dynamic_frame.from_catalog(
    database = args["source_database"], 
    table_name = args["source_table"], 
    transformation_ctx = "datasource0"
)

applymapping1 = ApplyMapping.apply(
    frame = datasource0, 
    transformation_ctx = "applymapping1",
    mappings = [
        ("id", "long", "id", "long"), 
        ("case number", "string", "case_number", "string"), 
        ("date", "string", "date", "string"), 
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
        ("updated on", "string", "updated_on", "string"), 
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

