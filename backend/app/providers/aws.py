from __future__ import annotations

from typing import Any, Mapping


class AWSAdapter:
    """
    Deployment preparation adapter for AWS targets.

    This adapter intentionally returns declarative plans/checklists instead
    of creating cloud resources directly. Runtime side effects should be done
    by dedicated IaC or deployment pipelines.
    """

    provider_name = "aws"

    def describe_targets(self) -> dict[str, str]:
        return {
            "frontend": "AWS Amplify (Next.js hosting)",
            "backend": "AWS ECS Fargate (FastAPI service)",
            "database": "Amazon RDS PostgreSQL",
            "cache": "Amazon ElastiCache Redis",
            "vector_store": "PostgreSQL pgvector extension (RDS/Aurora)",
            "storage": "Amazon S3",
            "secrets": "AWS Secrets Manager",
            "observability": "Amazon CloudWatch",
            "cicd": "AWS CodePipeline / GitHub Actions",
        }

    def required_env_vars(self) -> dict[str, tuple[str, ...]]:
        return {
            "global": (
                "AWS_REGION",
                "AWS_ACCOUNT_ID",
            ),
            "frontend": (
                "AMPLIFY_APP_NAME",
                "AMPLIFY_REPOSITORY_URL",
                "AMPLIFY_BRANCH",
            ),
            "backend": (
                "ECS_CLUSTER_NAME",
                "ECS_SERVICE_NAME",
                "ECS_TASK_FAMILY",
                "ECS_CONTAINER_PORT",
                "VPC_SUBNET_IDS",
                "VPC_SECURITY_GROUP_IDS",
            ),
            "database": (
                "RDS_INSTANCE_IDENTIFIER",
                "RDS_DB_NAME",
                "RDS_MASTER_USERNAME",
                "RDS_MASTER_PASSWORD_SECRET_ARN",
            ),
            "cache": (
                "ELASTICACHE_CLUSTER_ID",
            ),
            "storage": (
                "S3_ASSET_BUCKET",
            ),
            "secrets": (
                "SECRETS_MANAGER_PREFIX",
            ),
        }

    def deployment_order(self) -> list[str]:
        return [
            "networking",
            "database",
            "cache",
            "storage",
            "secrets",
            "backend",
            "frontend",
            "observability",
        ]

    def validate_preflight(self, env: Mapping[str, str]) -> dict[str, list[str]]:
        required = self.required_env_vars()
        missing: list[str] = []
        present: list[str] = []
        warnings: list[str] = []

        for group, names in required.items():
            for name in names:
                value = env.get(name, "").strip()
                if value:
                    present.append(name)
                else:
                    missing.append(name)

            if group == "backend" and not env.get("ECS_EXECUTION_ROLE_ARN", "").strip():
                warnings.append("ECS_EXECUTION_ROLE_ARN is recommended for Fargate task pulls/logging.")
            if group == "database" and not env.get("RDS_MULTI_AZ", "").strip():
                warnings.append("RDS_MULTI_AZ is not set; single AZ may reduce resilience for demo-day incidents.")

        return {
            "missing": sorted(missing),
            "present": sorted(present),
            "warnings": warnings,
        }

    def build_deployment_plan(self, *, env: Mapping[str, str]) -> dict[str, Any]:
        """
        Build a deterministic plan describing intended AWS resources.

        The returned object is safe to log and to use as handoff input for
        Terraform/CDK/manual runbooks.
        """
        return {
            "provider": self.provider_name,
            "targets": self.describe_targets(),
            "order": self.deployment_order(),
            "preflight": self.validate_preflight(env),
            "resources": {
                "frontend": {
                    "service": "amplify",
                    "app_name": env.get("AMPLIFY_APP_NAME", ""),
                    "repository": env.get("AMPLIFY_REPOSITORY_URL", ""),
                    "branch": env.get("AMPLIFY_BRANCH", "main"),
                },
                "backend": {
                    "service": "ecs_fargate",
                    "cluster_name": env.get("ECS_CLUSTER_NAME", ""),
                    "service_name": env.get("ECS_SERVICE_NAME", ""),
                    "task_family": env.get("ECS_TASK_FAMILY", ""),
                    "container_port": env.get("ECS_CONTAINER_PORT", "8000"),
                },
                "database": {
                    "service": "rds_postgres",
                    "identifier": env.get("RDS_INSTANCE_IDENTIFIER", ""),
                    "db_name": env.get("RDS_DB_NAME", "companionhk"),
                    "master_username": env.get("RDS_MASTER_USERNAME", ""),
                    "password_secret_arn": env.get("RDS_MASTER_PASSWORD_SECRET_ARN", ""),
                    "extensions": ["pgvector"],
                },
                "cache": {
                    "service": "elasticache_redis",
                    "cluster_id": env.get("ELASTICACHE_CLUSTER_ID", ""),
                },
                "storage": {
                    "service": "s3",
                    "bucket": env.get("S3_ASSET_BUCKET", ""),
                },
                "secrets": {
                    "service": "secrets_manager",
                    "prefix": env.get("SECRETS_MANAGER_PREFIX", "companionhk/"),
                },
            },
        }
