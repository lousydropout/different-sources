from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_sqs as sqs,
    aws_lambda as lambda_,
    aws_lambda_event_sources as eventsources,
    aws_apigateway as apigw,
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
            "sqsdlq",
            queue_name=f"{prefix}-sqs-dlq",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.minutes(15),
        )

        queue = sqs.Queue(
            self,
            "sqsqueue",
            queue_name=f"{prefix}-sqs-queue",
            retention_period=cdk.Duration.days(14),
            visibility_timeout=cdk.Duration.minutes(15),
            dead_letter_queue=sqs.DeadLetterQueue(
                queue=dlq, max_receive_count=5
            ),
        )

        # Lambda - API
        api_handler = lambda_.Function(
            self,
            "apilambda",
            function_name=f"{prefix}-api-handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("src"),
            handler="handler.handler",
            environment={
                "metadata_table": metadata_table.table_name,
                "storage": storage.bucket_name,
            },
        )
        queue.grant_send_messages(api_handler)
        metadata_table.grant_full_access(api_handler)
        storage.grant_read_write(api_handler)

        # Lambda - Security
        security_handler = lambda_.Function(
            self,
            "securitylambda",
            function_name=f"{prefix}-security-handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("src"),
            handler="security.handler",
            events=[eventsources.SqsEventSource(queue)],
            environment={
                "metadata_table": metadata_table.table_name,
                "storage": storage.bucket_name,
                "dlq": dlq.queue_url,
            },
        )
        dlq.grant_send_messages(security_handler)
        metadata_table.grant_full_access(security_handler)
        storage.grant_read_write(security_handler)

        # API Gateway
        api_gateway = apigw.LambdaRestApi(
            self,
            "apigateway",
            handler=api_handler,
            rest_api_name=f"{prefix}-parser-api",
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS
            ),
            endpoint_types=[apigw.EndpointType("REGIONAL")],
        )
