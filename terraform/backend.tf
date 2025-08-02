terraform {
  backend "s3" {
    bucket         = "kilograms-api-tfstate"
    key            = "terraform.tfstate"
    region         = "us-east-2"
    encrypt        = true
    dynamodb_table = "kilograms-api-tfstate-lock"
  }
} 