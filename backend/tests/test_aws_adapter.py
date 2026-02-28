from app.providers.aws import AWSAdapter


def test_aws_adapter_describes_expected_targets() -> None:
    adapter = AWSAdapter()

    targets = adapter.describe_targets()

    assert targets["frontend"].startswith("AWS Amplify")
    assert targets["backend"].startswith("AWS ECS Fargate")
    assert targets["database"].startswith("Amazon RDS PostgreSQL")
    assert "CloudWatch" in targets["observability"]


def test_aws_adapter_preflight_reports_missing_and_warnings() -> None:
    adapter = AWSAdapter()

    env = {
        "AWS_REGION": "ap-east-1",
        "AWS_ACCOUNT_ID": "123456789012",
        "AMPLIFY_APP_NAME": "companionhk-web",
        "AMPLIFY_REPOSITORY_URL": "https://github.com/HaochenFa/HTE_CompanionHK",
        "AMPLIFY_BRANCH": "main",
    }

    preflight = adapter.validate_preflight(env)

    assert "ECS_CLUSTER_NAME" in preflight["missing"]
    assert "RDS_INSTANCE_IDENTIFIER" in preflight["missing"]
    assert "AWS_REGION" in preflight["present"]
    assert any("ECS_EXECUTION_ROLE_ARN" in warning for warning in preflight["warnings"])


def test_aws_adapter_builds_deployment_plan_without_side_effects() -> None:
    adapter = AWSAdapter()

    env = {
        "AWS_REGION": "ap-east-1",
        "AWS_ACCOUNT_ID": "123456789012",
        "AMPLIFY_APP_NAME": "companionhk-web",
        "AMPLIFY_REPOSITORY_URL": "https://github.com/HaochenFa/HTE_CompanionHK",
        "AMPLIFY_BRANCH": "main",
        "ECS_CLUSTER_NAME": "companionhk-cluster",
        "ECS_SERVICE_NAME": "companionhk-api",
        "ECS_TASK_FAMILY": "companionhk-api-task",
        "ECS_CONTAINER_PORT": "8000",
        "VPC_SUBNET_IDS": "subnet-1,subnet-2",
        "VPC_SECURITY_GROUP_IDS": "sg-1",
        "RDS_INSTANCE_IDENTIFIER": "companionhk-db",
        "RDS_DB_NAME": "companionhk",
        "RDS_MASTER_USERNAME": "postgres",
        "RDS_MASTER_PASSWORD_SECRET_ARN": "arn:aws:secretsmanager:ap-east-1:123456789012:secret:db",
        "ELASTICACHE_CLUSTER_ID": "companionhk-cache",
        "S3_ASSET_BUCKET": "companionhk-assets",
        "SECRETS_MANAGER_PREFIX": "companionhk/",
    }

    plan = adapter.build_deployment_plan(env=env)

    assert plan["provider"] == "aws"
    assert plan["resources"]["backend"]["service"] == "ecs_fargate"
    assert plan["resources"]["database"]["extensions"] == ["pgvector"]
    assert plan["preflight"]["missing"] == []
