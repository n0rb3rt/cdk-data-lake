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

        crawl_ingest_trigger = glue.CfnTrigger(
            self,
            f"{env_name}-CrawlIngestTrigger",
            workflow_name=self.workflow.name,
            type="ON_DEMAND", #TODO: scheduled
            actions=[glue.CfnTrigger.ActionProperty(crawler_name=glue_struct.ingest_crawler.name)]
        )

        run_clean_trigger = glue.CfnTrigger(
            self,
            f"{env_name}-CleanJobTrigger",
            workflow_name=self.workflow.name,
            type="CONDITIONAL",
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        crawler_name=glue_struct.ingest_crawler.name,
                        logical_operator="EQUALS",
                        crawl_state="SUCCEEDED"
                    )]
            ),
            actions=[glue.CfnTrigger.ActionProperty(job_name=glue_struct.clean_job.name)]
        )

        crawl_clean_trigger = glue.CfnTrigger(
            self,
            f"{env_name}-CleanCrawlTrigger",
            workflow_name=self.workflow.name,
            type="CONDITIONAL",
            predicate=glue.CfnTrigger.PredicateProperty(
                conditions=[
                    glue.CfnTrigger.ConditionProperty(
                        job_name=glue_struct.clean_job.name,
                        logical_operator="EQUALS",
                        state="SUCCEEDED"
                    )]
            ),
            actions=[glue.CfnTrigger.ActionProperty(crawler_name=glue_struct.clean_crawler.name)]
        )

        crawl_ingest_trigger.add_depends_on(glue_struct.ingest_crawler)
        run_clean_trigger.add_depends_on(glue_struct.clean_job)
        crawl_clean_trigger.add_depends_on(glue_struct.clean_crawler)
