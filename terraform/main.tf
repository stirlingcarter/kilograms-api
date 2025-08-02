terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "app_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  iam_instance_profile = aws_iam_instance_profile.ec2_cloudwatch_profile.name
  user_data     = templatefile("${path.module}/scripts/setup.sh", {
    meili_url     = var.meili_url,
    meili_api_key = var.meili_api_key
  })
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name      = var.key_name

  tags = {
    Name = "KilogramsAPI"
  }
} 