resource "aws_eip" "market_analysis_eip" {
  vpc = true

  tags = {
    Name = "MarketAnalysisEIP"
  }
}
