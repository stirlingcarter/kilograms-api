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
  region  = var.aws_region
  profile = var.aws_profile
}

data "aws_ssm_parameter" "ubuntu_ami" {
  name = "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp2/ami-id"
}

resource "aws_instance" "app_server" {
  ami           = data.aws_ssm_parameter.ubuntu_ami.value
  instance_type = var.instance_type
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