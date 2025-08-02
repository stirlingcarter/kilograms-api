variable "aws_region" {
  description = "The AWS region to create resources in."
  default     = "us-east-2"
}

variable "instance_type" {
  description = "The type of EC2 instance to launch."
  default     = "t2.micro"
}

variable "key_name" {
  description = "Name of the key pair to use for the EC2 instance."
  default     = "deployer-key"
}

variable "meili_url" {
  description = "The URL of the Meilisearch instance."
  sensitive   = true
}

variable "meili_api_key" {
  description = "The API key for the Meilisearch instance."
  sensitive   = true
} 