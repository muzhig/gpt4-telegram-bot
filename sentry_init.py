import os


if os.environ.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.aws_lambda import AwsLambdaIntegration

    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        integrations=[AwsLambdaIntegration(timeout_warning=True)]
    )
