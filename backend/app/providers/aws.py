class AWSAdapter:
    provider_name = "aws"

    def describe_targets(self) -> dict[str, str]:
        return {
            "frontend": "AWS Amplify",
            "backend": "AWS ECS Fargate",
            "database": "AWS RDS PostgreSQL",
            "cache": "AWS ElastiCache Redis"
        }
