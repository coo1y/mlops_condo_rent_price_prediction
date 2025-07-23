resource "aws_lambda_function" "test_function" {
  count         = var.step >= 2 ? 1 : 0
  function_name = "${var.lambda_function_prefix_name}-${var.env_name}"
  timeout       = 30 # seconds
  image_uri     = "${aws_ecr_repository.ecr_repo_image.repository_url}:${var.lambda_image_tag}"
  package_type  = "Image"
  architectures = ["arm64"]

  role = aws_iam_role.test_function_role.arn

  environment {
    variables = {
      SOME_ENV_V = var.env_name
    }
  }
}

resource "aws_iam_role" "test_function_role" {
  name = "test-${var.env_name}"

  assume_role_policy = jsonencode({
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}
