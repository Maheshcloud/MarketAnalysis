variable "hosted_zone_id" {
  description = "The Route 53 Hosted Zone ID for your domain (e.g., maheshdasika.xyz)"
  type        = string
  default     = "Z0374518JWZUDUOOS763" # IMPORTANT: Replace with your Route 53 Hosted Zone ID
}

variable "instance_type" {
  description = "The EC2 instance type for the Lambda function to manage"
  type        = string
  default     = "t2.medium"
}

variable "ami_id" {
  description = "The AMI ID to use for the EC2 instance"
  type        = string
  default     = "ami-020cba7c55df1f615"
  }

variable "key_name" {
  description = "The name of the SSH key pair to use for the EC2 instance"
  type        = string
  default     = "MAnalysis"
}

variable "spot_price" {
  description = "The maximum price you are willing to pay for the spot instance"
  type        = string
}

variable aws_region {
  description = "The AWS region where the resources will be created"
  type        = string
  default     = "us-east-1" #
}

variable "vpc_id" {
  description = "The VPC ID where the resources will be created"
  type        = string
  default     = "vpc-eb288091" # IMPORTANT: Replace with your VPC ID
}
