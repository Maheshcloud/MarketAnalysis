resource "aws_cloudwatch_event_rule" "start_instance_rule" {
  name                = "start-market-analysis-instance"
  description         = "Starts the Market Analysis EC2 instance at market open"
  schedule_expression = "cron(0 03 ? * MON-FRI *)" # Example: 14:00 UTC (2 PM UTC) Monday-Friday. Adjust to your market open time in UTC.
}

resource "aws_cloudwatch_event_target" "start_instance_target" {
  rule      = aws_cloudwatch_event_rule.start_instance_rule.name
  target_id = "start-lambda"
  arn       = aws_lambda_function.ec2_scheduler_lambda.arn
  input     = jsonencode({"action": "start"})
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_start_lambda" {
  statement_id  = "AllowExecutionFromCloudWatchStart"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_scheduler_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.start_instance_rule.arn
}

resource "aws_cloudwatch_event_rule" "terminate_instance_rule" {
  name                = "terminate-market-analysis-instance"
  description         = "Terminates the Market Analysis EC2 instance at market close"
  schedule_expression = "cron(0 10 ? * MON-FRI *)" # Example: 21:00 UTC (9 PM UTC) Monday-Friday. Adjust to your market close time in UTC.
}

resource "aws_cloudwatch_event_target" "terminate_instance_target" {
  rule      = aws_cloudwatch_event_rule.terminate_instance_rule.name
  target_id = "terminate-lambda"
  arn       = aws_lambda_function.ec2_scheduler_lambda.arn
  input     = jsonencode({"action": "terminate"})
}

resource "aws_lambda_permission" "allow_cloudwatch_to_call_terminate_lambda" {
  statement_id  = "AllowExecutionFromCloudWatchTerminate"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.ec2_scheduler_lambda.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.terminate_instance_rule.arn
}
