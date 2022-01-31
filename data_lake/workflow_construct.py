from constructs import Construct
from aws_cdk import (
    aws_glue as glue
)

from .glue_construct import GlueConstruct

class WorkflowConstruct(Construct):
    def __init__(self, scope: Construct, id: str, env_name: str, glue_struct: GlueConstruct, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.workflow = glue.CfnWorkflow(
            self, 
            id=f"{env_name}-Workflow",
            name=f"{env_name}-Workflow"
        )

        self.crawl_ingest_trigger = glue.CfnTrigger(
            self,
            id=f"{env_name}-CrawlIngestTrigger",
            name=f"{env_name}-CrawlIngestTrigger",
            workflow_name=self.workflow.name,
            type="ON_DEMAND", #TODO: scheduled
            actions=[glue.CfnTrigger.ActionProperty(crawler_name=glue_struct.ingest_crawler.name)]
        )

        self.run_clean_trigger = glue.CfnTrigger(
            self,
            id=f"{env_name}-CleanJobTrigger",
            name=f"{env_name}-CleanJobTrigger",
            workflow_name=self.workflow.name,
            type="CONDITIONAL",
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        crawler_name=glue_struct.ingest_crawler.name,
                        logical_operator="EQUALS",
                        crawl_state="SUCCEEDED"
                    )
                ],
                logical="ANY"
            ),
            actions=[glue.CfnTrigger.ActionProperty(job_name=glue_struct.clean_job.name)],
            start_on_creation=True
        )

        self.crawl_clean_trigger = glue.CfnTrigger(
            self,
            id=f"{env_name}-CleanCrawlTrigger",
            name=f"{env_name}-CleanCrawlTrigger",
            workflow_name=self.workflow.name,
            type="CONDITIONAL",
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        job_name=glue_struct.clean_job.name,
                        logical_operator="EQUALS",
                        state="SUCCEEDED"
                    )
                ],
                logical="ANY"
            ),
            actions=[glue.CfnTrigger.ActionProperty(crawler_name=glue_struct.clean_crawler.name)],
            start_on_creation=True
        )

        self.crawl_ingest_trigger.add_depends_on(glue_struct.ingest_crawler)
        self.run_clean_trigger.add_depends_on(glue_struct.clean_job)
        self.crawl_clean_trigger.add_depends_on(glue_struct.clean_crawler)
