terraform {
  required_providers {
    aws = {
      version = "~> 6.4.0"
    }
  }

  backend "s3" {
    bucket  = "condo4rent-terraform-state"
    key     = "condo4rent-prod.tfstate"
    region  = "ap-southeast-7"
    encrypt = true
  }

  required_version = "~> 1.12.2"
}

provider "aws" {
    region = var.aws_region
}
