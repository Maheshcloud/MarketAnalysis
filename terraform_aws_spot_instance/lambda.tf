resource "aws_lambda_function" "ec2_scheduler_lambda" {
  function_name = "ec2-scheduler-lambda"
  handler       = "main.lambda_handler"
  runtime       = "python3.9"
  role          = aws_iam_role.ec2_scheduler_lambda_role.arn
  timeout       = 300

  filename = "./ec2_scheduler_lambda.zip"
  source_code_hash = filebase64sha256("./ec2_scheduler_lambda.zip")

  environment {
    variables = {
      INSTANCE_TAG_KEY     = "ManagedBy"
      INSTANCE_TAG_VALUE   = "TerraformScheduler"
      AMI_ID               = var.ami_id
      INSTANCE_TYPE        = var.instance_type
      KEY_NAME             = var.key_name
      SECURITY_GROUP_IDS   = join(",", [aws_security_group.market_analysis_sg.id]) # Pass as comma-separated string
      SPOT_PRICE           = var.spot_price
      EIP_ALLOCATION_ID    = aws_eip.market_analysis_eip.id
    }
  }
}

resource "null_resource" "lambda_zip" {
  triggers = {
    python_code_hash = filebase64sha256("${path.module}/lambda_function.py")
  }

  provisioner "local-exec" {
    command = "zip -j ./ec2_scheduler_lambda.zip ${path.module}/lambda_function.py"
  }
}
