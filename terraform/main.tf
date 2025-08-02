terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

resource "aws_instance" "app_server" {
  ami           = var.ami_id
  instance_type = var.instance_type
  user_data     = templatefile("${path.module}/scripts/setup.sh", {
    meili_url     = var.meili_url,
    meili_api_key = var.meili_api_key
  })
  vpc_security_group_ids = [aws_security_group.app_sg.id]
  key_name      = var.key_name

  provisioner "file" {
    source      = "../app/"
    destination = "/tmp/"
  }

  tags = {
    Name = "KilogramsAPI"
  }
} 