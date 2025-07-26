resource "aws_lambda_function" "test_function" {
  count         = var.step >= 2 ? 1 : 0
  function_name = "${var.lambda_function_prefix_name}-${var.env_name}"
  timeout       = 30 # seconds
  memory_size   = 512 # Set memory to 512 MB
  image_uri     = "${aws_ecr_repository.ecr_repo_image.repository_url}:${var.lambda_image_tag}"
  package_type  = "Image"
  role          = aws_iam_role.condo4rent_lambda_role.arn
  # architectures = ["arm64"]

  environment {
    variables = {
      MLFLOW_TRACKING_DNS = var.mlflow_tracking_dns
    }
  }
}

resource "aws_iam_role" "condo4rent_lambda_role" {
  name = "condo4rent-lambda-${var.env_name}"

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

resource "aws_iam_role_policy_attachment" "lambda_basic_execution_policy" {
  role       = aws_iam_role.condo4rent_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "s3_read_only_policy" {
  role       = aws_iam_role.condo4rent_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}
