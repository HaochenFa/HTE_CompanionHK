import boto3
import logging
from botocore.exceptions import ClientError, BotoCoreError

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more detail
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),  # Console output
        logging.FileHandler("aws_adapter.log", mode="a")  # Log file
    ]
)

logger = logging.getLogger("AWSAdapter")

class AWSAdapter:
    provider_name = "aws"

    def describe_targets(self) -> dict[str, str]:
        return {
            "frontend": "AWS Amplify (Next.js hosting)",
            "backend": "AWS ECS Fargate (FastAPI service)",
            "database": "Amazon RDS PostgreSQL",
            "cache": "Amazon ElastiCache Redis",
            "vector_store": "Amazon Aurora PostgreSQL with pgvector",
            "orchestration": "AWS Step Functions (LangGraph runtime boundary)",
            "storage": "Amazon S3 (profile memory, assets)",
            "secrets": "AWS Secrets Manager",
            "cicd": "AWS CodePipeline / GitHub Actions"
        }

    # --- Frontend ---
    def deploy_frontend(self, app_name: str, repo_url: str, branch: str = "main"):
        client = boto3.client("amplify")
        try:
            response = client.create_app(
                Name=app_name,
                Repository=repo_url,
                IamServiceRoleArn="arn:aws:iam::<account-id>:role/AmplifyServiceRole"
            )
            logger.info("Amplify app created: %s", response["App"]["AppId"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating Amplify app: %s", e)

    # --- Backend ---
    def deploy_backend(self, cluster_name: str, service_name: str, task_definition: str):
        ecs = boto3.client("ecs")
        try:
            response = ecs.create_service(
                cluster=cluster_name,
                serviceName=service_name,
                taskDefinition=task_definition,
                desiredCount=1,
                launchType="FARGATE",
                networkConfiguration={
                    "awsvpcConfiguration": {
                        "subnets": ["subnet-xxxxxx"],
                        "assignPublicIp": "ENABLED"
                    }
                }
            )
            logger.info("ECS service created: %s", response["service"]["serviceArn"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating ECS service: %s", e)

    # --- Database ---
    def setup_database(self, db_identifier: str, username: str, password: str):
        rds = boto3.client("rds")
        try:
            response = rds.create_db_instance(
                DBInstanceIdentifier=db_identifier,
                AllocatedStorage=20,
                DBInstanceClass="db.t3.micro",
                Engine="postgres",
                MasterUsername=username,
                MasterUserPassword=password,
                PubliclyAccessible=True
            )
            logger.info("RDS instance creation started: %s", response["DBInstance"]["DBInstanceIdentifier"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating RDS instance: %s", e)

    # --- Cache ---
    def setup_cache(self, cluster_name: str):
        elasticache = boto3.client("elasticache")
        try:
            response = elasticache.create_cache_cluster(
                CacheClusterId=cluster_name,
                Engine="redis",
                CacheNodeType="cache.t3.micro",
                NumCacheNodes=1
            )
            logger.info("ElastiCache cluster creation started: %s", response["CacheClusterId"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating ElastiCache cluster: %s", e)

    # --- Vector Store ---
    def setup_vector_store(self, cluster_id: str):
        rds = boto3.client("rds")
        try:
            response = rds.modify_db_cluster(
                DBClusterIdentifier=cluster_id,
                ApplyImmediately=True
            )
            logger.info("Aurora cluster modified: %s", response["DBCluster"]["DBClusterIdentifier"])
            logger.warning("Reminder: Enable pgvector manually via SQL: CREATE EXTENSION pgvector;")
        except (ClientError, BotoCoreError) as e:
            logger.error("Error modifying Aurora cluster: %s", e)

    # --- Orchestration ---
    def setup_orchestration(self, workflow_name: str, definition: str, role_arn: str):
        sf = boto3.client("stepfunctions")
        try:
            response = sf.create_state_machine(
                name=workflow_name,
                definition=definition,
                roleArn=role_arn
            )
            logger.info("Step Functions workflow created: %s", response["stateMachineArn"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating Step Functions workflow: %s", e)

    # --- Storage ---
    def setup_storage(self, bucket_name: str):
        s3 = boto3.client("s3")
        try:
            s3.create_bucket(Bucket=bucket_name)
            logger.info("S3 bucket created: %s", bucket_name)
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating S3 bucket: %s", e)

    # --- Secrets ---
    def setup_secrets(self, secret_name: str, value: str):
        sm = boto3.client("secretsmanager")
        try:
            response = sm.create_secret(
                Name=secret_name,
                SecretString=value
            )
            logger.info("Secret stored: %s", response["ARN"])
        except (ClientError, BotoCoreError) as e:
            logger.error("Error storing secret: %s", e)

    # --- CI/CD ---
    def setup_cicd(self, pipeline_name: str, role_arn: str, artifact_bucket: str):
        cp = boto3.client("codepipeline")
        try:
            response = cp.create_pipeline(
                pipeline={
                    "name": pipeline_name,
                    "roleArn": role_arn,
                    "artifactStore": {
                        "type": "S3",
                        "location": artifact_bucket
                    },
                    "stages": [
                        {"name": "Source", "actions": []},
                        {"name": "Build", "actions": []},
                        {"name": "Deploy", "actions": []}
                    ]
                }
            )
            logger.info("Pipeline created: %s", pipeline_name)
        except (ClientError, BotoCoreError) as e:
            logger.error("Error creating pipeline: %s", e)
