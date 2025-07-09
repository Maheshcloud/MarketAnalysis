provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "market_analysis_sg" {
  name        = "market-analysis-sg"
  description = "Allow SSH and HTTP/HTTPS traffic"
  vpc_id      = var.vpc_id # Replace with your VPC ID

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # WARNING: For production, restrict this to your IP
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "market-analysis-sg"
  }
}

resource "aws_spot_instance_request" "market_analysis_spot" {
  ami                    = var.ami_id
  instance_type          = var.instance_type
  spot_price             = var.spot_price
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.market_analysis_sg.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.ec2_instance_profile.name

  user_data = <<-EOF
              #!/bin/bash
              sudo apt-get update -y
              sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common git
              curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
              sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
              sudo apt-get update -y
              sudo apt-get install -y docker-ce
              sudo usermod -aG docker ubuntu # Assuming Ubuntu AMI, change if different user
              sudo systemctl start docker
              sudo systemctl enable docker

              # Clone the repository - IMPORTANT: Replace with your actual repository URL
              git clone https://github.com/your-username/MarketAnalysis.git /home/ubuntu/MarketAnalysis
              cd /home/ubuntu/MarketAnalysis

              # Build and run Docker container
              docker build -t market-analysis-app .
              docker run -d --name market-analysis-container -p 80:80 market-analysis-app
              EOF

  tags = {
    Name        = "MarketAnalysisSpotInstance"
    ManagedBy   = "TerraformScheduler"
  }
}
