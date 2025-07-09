resource "aws_route53_record" "maheshdasika_xyz_a_record" {
  zone_id = var.hosted_zone_id
  name    = "maheshdasika.xyz"
  type    = "A"
  ttl     = 300
  records = [aws_eip.market_analysis_eip.public_ip]
}
