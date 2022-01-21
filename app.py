#!/usr/bin/env python3

import aws_cdk as cdk

from ab3_data_lake.ab3_data_lake_stack import Ab3DataLakeStack


app = cdk.App()
Ab3DataLakeStack(app, "ab3-data-lake")

app.synth()
