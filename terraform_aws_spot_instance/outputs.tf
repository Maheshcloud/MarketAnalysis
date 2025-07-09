output "public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_spot_instance_request.market_analysis_spot.public_ip
}
