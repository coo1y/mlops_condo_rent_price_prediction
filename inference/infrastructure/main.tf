terraform {
  required_providers {
    aws = {
      version = "~> 6.4.0"
    }
  }

  required_version = "~> 1.12.2"
}

provider "aws" {
    region = var.aws_region
}
