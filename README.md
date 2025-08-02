# Kilograms API
[![CI/CD Pipeline](https://github.com/stirlingcarter/kilograms-api/actions/workflows/deploy.yml/badge.svg)](https://github.com/stirlingcarter/kilograms-api/actions/workflows/deploy.yml)

This repository contains the source code for a Python-based API that serves as a backend for the Kilograms project. It is designed to connect to a Meilisearch instance, providing a simple interface to search and retrieve data. The entire infrastructure is defined and managed using Terraform, allowing for automated and repeatable deployments on AWS.

This project is a companion to the [`@kilograms-ms`](https://github.com/your-username/kilograms-ms) repository, which handles the deployment of the Meilisearch instance itself.

## Features

-   **Python Flask API**: A lightweight and robust API built with Flask.
-   **Meilisearch Integration**: Seamlessly connects to a Meilisearch database for powerful search capabilities.
-   **Infrastructure as Code**: The entire AWS infrastructure is managed with Terraform.
-   **Automated Deployment**: The application is automatically deployed and provisioned on an AWS EC2 instance at creation time.

## Directory Structure

```
.
├── app/
│   ├── main.py          # Flask application source code
│   └── requirements.txt # Python dependencies
└── terraform/
    ├── main.tf          # Core Terraform configuration (EC2 instance)
    ├── network.tf       # Networking resources (Security Group, Key Pair)
    ├── variables.tf     # Input variables for Terraform
    ├── outputs.tf       # Outputs from our Terraform configuration
    └── scripts/
        └── setup.sh     # Provisioning script for the EC2 instance
```

## Prerequisites

Before you begin, ensure you have the following installed and configured:

1.  **Terraform**: [Download and install Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli).
2.  **AWS CLI**: [Install and configure the AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html) with your credentials.
3.  **Meilisearch Instance**: You must have a running Meilisearch instance. You can deploy one using the [`@kilograms-ms`](https://github.com/your-username/kilograms-ms) repository.
4.  **SSH Key Pair**: An SSH public key located at `~/.ssh/id_rsa.pub`. You can generate one by running `ssh-keygen`.

## Setup and Deployment

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/kilograms-api.git
    cd kilograms-api/terraform
    ```

2.  **Create a Terraform variables file:**
    Create a file named `terraform.tfvars` and add your Meilisearch instance URL and API key. This file is included in `.gitignore` to prevent you from committing sensitive credentials.

    **`terraform.tfvars`**
    ```tfvars
    meili_url     = "http://your-meilisearch-instance-ip:7700"
    meili_api_key = "your-meilisearch-api-key"
    ```

3.  **Initialize Terraform:**
    This will download the necessary providers.
    ```bash
    terraform init
    ```

4.  **Plan the deployment:**
    Review the resources that Terraform will create.
    ```bash
    terraform plan
    ```

5.  **Apply the configuration:**
    This will build and deploy the infrastructure to your AWS account.
    ```bash
    terraform apply --auto-approve
    ```
    Once the command completes, Terraform will output the public IP address of the newly created EC2 instance.

## Usage

You can interact with the deployed API using any HTTP client, such as `curl`. Replace `<INSTANCE_PUBLIC_IP>` with the IP address from the Terraform output.

*   **Root Endpoint:**
    ```bash
    curl http://<INSTANCE_PUBLIC_IP>:5000/
    ```
    *Expected Response:* `<h1>Kilograms API</h1><p>Welcome to the Kilograms Python API!</p>`

*   **Health Check:**
    Verifies the connection to the Meilisearch instance.
    ```bash
    curl http://<INSTANCE_PUBLIC_IP>:5000/health
    ```
    *Expected Response:* `{"status":"ok","meilisearch":{"status":"available"}}`

*   **Search Endpoint:**
    Performs a search against the `events` index in your Meilisearch instance.
    ```bash
    curl "http://<INSTANCE_PUBLIC_IP>:5000/search?q=techno"
    ```
    *Expected Response:* A JSON object containing the search results from Meilisearch.

## Connecting via SSH

You can connect to the EC2 instance for debugging or maintenance using SSH.

```bash
ssh -i ~/.ssh/id_rsa ubuntu@<INSTANCE_PUBLIC_IP>
```
*Note: The user is `ubuntu` because we are using an Ubuntu AMI.*

## Cleanup

To avoid ongoing charges, destroy the infrastructure when you are finished.

```bash
terraform destroy --auto-approve
``` 
