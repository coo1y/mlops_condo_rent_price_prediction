resource "aws_ecr_repository" "ecr_repo_image" {
    name                 = var.ecr_repo_name
    image_tag_mutability = "MUTABLE"
    force_delete         = true

    image_scanning_configuration {
        scan_on_push = false
    }
}

# Output the repository URL so for CI/CD that can pick it up
output "ecr_repository_url" {
  description = "The URL of the ECR repository"
  value       = aws_ecr_repository.ecr_repo_image.repository_url
}
