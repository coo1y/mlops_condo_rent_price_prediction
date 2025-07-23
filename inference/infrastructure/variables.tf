variable "aws_region" {
    description = "Enter your AWS region in default value"
}

variable "env_name" {
    description = "Enter your environment variable"
}

variable "ecr_repo_name" {
    description = "Enter your AWS ECR repository name"
}

variable "lambda_function_prefix_name" {
    description = "Enter your AWS Lambda function name"
}

variable "lambda_image_tag" {
    description = "Enter the tag for the Lambda image"
    default     = "latest"
}

variable "step" {
    description = "Step number to control resource creation"
    type        = number
    default     = 2
}
