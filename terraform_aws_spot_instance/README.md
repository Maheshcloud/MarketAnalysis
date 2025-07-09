# AWS EC2 Spot Instance for Market Analysis Application

This Terraform configuration deploys an AWS EC2 Spot Instance and automatically sets up the Market Analysis application using Docker. It also includes resources to schedule the instance to start and terminate during specified market hours (excluding weekends) using AWS Lambda and EventBridge, and securely manages application secrets using AWS Secrets Manager. Furthermore, it sets up an Elastic IP and a Route 53 A record to map a domain name to your instance.

## Prerequisites

*   **Terraform**: Install Terraform on your local machine.
*   **AWS Account**: You need an AWS account with appropriate permissions to create EC2 instances, security groups, spot instance requests, IAM roles, Lambda functions, EventBridge rules, Secrets Manager secrets, Elastic IPs, and Route 53 records.
*   **AWS CLI Configured**: Ensure your AWS CLI is configured with credentials that have the necessary permissions.
*   **EC2 Key Pair**: You need an existing EC2 Key Pair in your AWS region. Replace `your-key-pair-name` in `variables.tf` with the actual name of your key pair.
*   **Default VPC ID**: You need the ID of your **default** Virtual Private Cloud (VPC) for your chosen region. You can find this in the AWS VPC console. Replace `your-default-vpc-id` in `variables.tf` with your actual default VPC ID.
*   **AMI ID**: Find the latest suitable AMI ID for your chosen AWS region (e.g., an Ubuntu Server LTS AMI). I have provided common AMI IDs for `us-east-1` and `us-east-2` as defaults in `variables.tf`, but **it is crucial to verify these are the latest and correct AMIs for your specific use case and region.**
*   **GitHub Repository**: The `user_data` script assumes your `MarketAnalysis` project is hosted on GitHub. Update the `git clone` URL in `main.tf` to point to your actual repository.
*   **Route 53 Hosted Zone**: You must have a hosted zone for `maheshdasika.xyz` (or your desired domain) in AWS Route 53. You will need its Hosted Zone ID.

## Usage

1.  **Navigate to the directory**:
    ```bash
    cd C:\Users\mahes\Desktop\Mahesh\Project\MarketAnalysis\terraform_aws_spot_instance
    ```

2.  **Update Configuration Files**:
    *   Open `variables.tf` and update the `default` values for `ami_id`, `key_name`, `vpc_id`, and **`hosted_zone_id`** with your specific values.
    *   Open `main.tf` and update the `git clone` URL in the `user_data` script to point to your `MarketAnalysis` GitHub repository.
    *   Open `eventbridge.tf` and update the `schedule_expression` for both `start_instance_rule` and `terminate_instance_rule` to reflect your market open and close times in **UTC cron format**. The current expressions are set for Monday-Friday.
    *   **Update `secrets.tf`**: Open `secrets.tf` and **replace the placeholder values** in the `secret_string` with your actual sensitive credentials (e.g., `ZERODHA_API_KEY`, `TELEGRAM_BOT_TOKEN`, etc.) from your `.env` file. Ensure the JSON format is correct.

3.  **Prepare Lambda Deployment Package**:
    *   Ensure you have `zip` installed and available in your PATH.
    *   Run the following command in the `terraform_aws_spot_instance` directory to create the Lambda deployment package:
        ```bash
        zip -j ec2_scheduler_lambda.zip lambda_function.py
        ```

4.  **Integrate Secrets Manager Access into Your Application**:
    *   Modify your Python application (e.g., `market_analysis_app/main.py`) to retrieve secrets from AWS Secrets Manager at runtime. Here's a Python code snippet using `boto3` that demonstrates how to do this:

        ```python
        import boto3
        import json
        import os

        def get_secret(secret_name):
            """
            Retrieves a secret from AWS Secrets Manager.
            """
            region_name = os.environ.get("AWS_REGION", "us-east-1") # Or get from config

            # Create a Secrets Manager client
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=region_name
            )

            try:
                get_secret_value_response = client.get_secret_value(
                    SecretId=secret_name
                )
            except Exception as e:
                print(f"Error retrieving secret '{secret_name}': {e}")
                raise

            if 'SecretString' in get_secret_value_response:
                secret = get_secret_value_response['SecretString']
                return json.loads(secret)
            else:
                return get_secret_value_response['SecretBinary']

        # Example usage in your application:
        # secret_name = "market-analysis-app-secrets" # This should match the name in secrets.tf
        # try:
        #     secrets = get_secret(secret_name)
        #     # Now you can access your secrets like:
        #     # zerodha_api_key = secrets.get("ZERODHA_API_KEY")
        #     # telegram_bot_token = secrets.get("TELEGRAM_BOT_TOKEN")
        #     # And set them as environment variables if your app expects them that way:
        #     # for key, value in secrets.items():
        #     #     os.environ[key] = value
        # except Exception as e:
        #     print(f"Failed to load secrets: {e}")
        ```

5.  **Initialize Terraform**:
    ```bash
    terraform init
    ```

6.  **Review the plan**:
    ```bash
    terraform plan
    ```
    Review the proposed changes to ensure they align with your expectations.

7.  **Apply the changes**:
    ```bash
    terraform apply
    ```
    Type `yes` when prompted to confirm the deployment.

## Important Notes

*   **Security Group**: The security group allows inbound SSH (port 22), HTTP (port 80), and HTTPS (port 443) traffic from anywhere (`0.0.0.0/0`). **For production environments, it is highly recommended to restrict SSH access to your specific IP address range.**
*   **Spot Instance Price**: Adjust the `spot_price` in `variables.tf` based on your desired maximum bid for the spot instance. Check AWS Spot Instance pricing for your region and instance type.
*   **User Data Script**: The `user_data` script installs Docker, clones your repository, builds the Docker image, and runs the container. Ensure your `Dockerfile` is correctly configured in your `MarketAnalysis` project.
*   **Repository Access**: If your GitHub repository is private, you will need to configure SSH keys or an IAM role with appropriate permissions for the EC2 instance to clone the repository.
*   **Lambda Scheduling**: The Lambda function will launch a *new* spot instance at market open and *terminate* the existing one at market close. This means the instance ID will change daily. The Elastic IP will ensure a consistent public IP address.
*   **Secrets Management**: By using AWS Secrets Manager, your sensitive credentials are no longer hardcoded or committed to your repository. The EC2 instance will retrieve them securely at runtime.
*   **Domain Mapping**: The Elastic IP and Route 53 A record will ensure that your `maheshdasika.xyz` domain consistently points to your running spot instance during market hours.

## Destroying Resources

To destroy all resources created by this Terraform configuration, run:

```bash
terraform destroy
```
    Type `yes` when prompted to confirm the destruction.
