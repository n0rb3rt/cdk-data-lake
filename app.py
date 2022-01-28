#!/usr/bin/env python3

import aws_cdk as cdk

from data_lake.data_lake_stack import DataLakeStack


app = cdk.App()
DataLakeStack(app, "ab3-data-lake")

app.synth()
