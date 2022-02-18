import sys

from awsglue import DynamicFrame
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, count, expr, lag, last_day
from pyspark.sql.window import Window

args = getResolvedOptions(
    sys.argv, ["JOB_NAME", "source_database", "source_table", "target_bucket"]
)

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)
logger = glueContext.get_logger()

out_bucket = f"s3://{args['target_bucket']}"

datasource0: DynamicFrame = glueContext.create_dynamic_frame.from_catalog(
    database=args["source_database"],
    table_name=args["source_table"],
    transformation_ctx="datasource0",
)

w = Window.partitionBy("precinct", "primary_type").orderBy("month")

window1 = DynamicFrame.fromDF(
    glue_ctx=glueContext,
    name="window1",
    dataframe=datasource0.toDF()
    .withColumn("month", last_day(col("date")))
    .groupBy("precinct", "primary_type", "month")
    .agg(count("id").alias("monthly_count"))
    .sort("precinct", "primary_type", "month")
    .withColumn("prev_month", lag("month").over(w))
    .withColumn("prev_count", lag("monthly_count").over(w))
    .withColumn(
        "prev_month",
        expr(
            "case when last_day(add_months(prev_month,1)) = last_day(month) then prev_count else null end"
        ),
    )
    .withColumn(
        "monthly_change",
        (col("monthly_count") - col("prev_count")) / col("monthly_count"),
    )
    .drop("prev_month", "prev_count")
    .coalesce(1)
)

datasink2 = glueContext.write_dynamic_frame.from_options(
    frame=window1,
    connection_type="s3",
    connection_options={"path": f"{out_bucket}/crime_trends"},
    format="parquet",
    transformation_ctx="datasink2",
)

job.commit()
