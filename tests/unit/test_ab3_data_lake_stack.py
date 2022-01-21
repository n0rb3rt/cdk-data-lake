import aws_cdk as core
import aws_cdk.assertions as assertions
from ab3_data_lake.ab3_data_lake_stack import Ab3DataLakeStack


def test_sqs_queue_created():
    app = core.App()
    stack = Ab3DataLakeStack(app, "ab3-data-lake")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })


def test_sns_topic_created():
    app = core.App()
    stack = Ab3DataLakeStack(app, "ab3-data-lake")
    template = assertions.Template.from_stack(stack)

    template.resource_count_is("AWS::SNS::Topic", 1)
