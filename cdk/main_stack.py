from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as eventsources,
    core as cdk,
)


class DifferentSources(cdk.Stack):
    def __init__(
        self, scope: cdk.Construct, construct_id: str, prefix: str, **kwargs
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # DynamoDB Tables
        metadata_table = dynamodb.Table(
            self,
            "metadatatable",
            table_name=f"{prefix}-metadata-table",
            partition_key=dynamodb.Attribute(
                name="pk", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sk", type=dynamodb.AttributeType.STRING
            ),
            removal_policy=cdk.RemovalPolicy.DESTROY,
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        # S3 Buckets
        storage = s3.Bucket(
            self,
            "storage",
            bucket_name=f"{prefix}-storage",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # SQS Queues
        dlq = sqs.Queue(
            self,
            "datadlq",
            queue_name=f"{prefix}-dlq",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.minutes(15),
        )

        queue = sqs.Queue(
            self,
            "dataqueue",
            queue_name=f"{prefix}-queue",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.minutes(15),
            dead_letter_queue=sqs.DeadLetterQueue(
                queue=dlq, max_receive_count=5
            ),
        )

        # Lambda
        lambda_function = lambda_.Function(
            self,
            "apilambda",
            function_name=f"{prefix}-api-handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("src"),
            handler="handler.handler",
            events=[eventsources.SqsEventSource(queue)],
            environment={
                "metadata_table": metadata_table.table_name,
                "storage": storage.bucket_name,
                "dlq": dlq.queue_url,
            },
        )
        queue.grant_send_messages(lambda_function)
        dlq.grant_send_messages(lambda_function)
        metadata_table.grant_full_access(lambda_function)
        storage.grant_read_write(lambda_function)
