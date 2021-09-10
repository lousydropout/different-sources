from aws_cdk import (
    aws_dynamodb as dynamodb,
    aws_s3 as s3,
    aws_lambda as lambda_,
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
        metadata_table.add_global_secondary_index(
            index_name="gsi-index",
            partition_key=dynamodb.Attribute(
                name="pk_gsi", type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="sk_gsi", type=dynamodb.AttributeType.STRING
            ),
        )

        # S3 Buckets
        storage = s3.Bucket(
            self,
            "storage",
            bucket_name=f"{prefix}-storage",
            removal_policy=cdk.RemovalPolicy.DESTROY,
        )

        # Lambda layer - FastAPI + Mangum
        fastapi_mod = lambda_.LayerVersion(
            self,
            "fastapi",
            code=lambda_.Code.from_asset("lib/fastapi/modules"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        )

        # Lambda - API
        api_handler = lambda_.Function(
            self,
            "apilambda",
            function_name=f"{prefix}-api-handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("src"),
            handler="api.handler",
            layers=[fastapi_mod],
            environment={
                "metadata_table": metadata_table.table_name,
                "storage": storage.bucket_name,
            },
            timeout=cdk.Duration.seconds(30),
        )
        # queue.grant_send_messages(api_handler)
        metadata_table.grant_full_access(api_handler)
        storage.grant_read_write(api_handler)

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

        # Lambda layer - requests
        requests_mod = lambda_.LayerVersion(
            self,
            "requests",
            code=lambda_.Code.from_asset("lib/requests/modules"),
            compatible_runtimes=[lambda_.Runtime.PYTHON_3_8],
        )

        # Lambda - Example
        api_handler = lambda_.Function(
            self,
            "example",
            function_name=f"{prefix}-example-handler",
            runtime=lambda_.Runtime.PYTHON_3_8,
            code=lambda_.Code.from_asset("src"),
            handler="example.handler",
            layers=[requests_mod],
            environment={
                "metadata_table": metadata_table.table_name,
                "storage": storage.bucket_name,
                "apigw": api_gateway.url,
            },
            timeout=cdk.Duration.minutes(15),
        )
        # queue.grant_send_messages(api_handler)
        metadata_table.grant_full_access(api_handler)
        storage.grant_read_write(api_handler)
