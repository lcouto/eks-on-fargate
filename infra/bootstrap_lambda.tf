resource "aws_security_group" "lambda" {
  name        = "lambda-sg"
  vpc_id      = module.vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

data "archive_file" "bootstrap" {

  type        = "zip"
  source_dir  = "files/lambda/"
  output_path = "files/lambda/main.zip"
 }

resource "aws_lambda_function" "bootstrap" {

  function_name    = "fargate-bootstrap"
  role             = var.lambda_role_arn
  runtime          = "python3.7"
  handler          = "main.handler"
  filename         = data.archive_file.bootstrap.output_path
  source_code_hash = data.archive_file.bootstrap.output_base64sha256
  timeout = 300

  vpc_config {
    subnet_ids         = module.vpc.private_subnets
    security_group_ids = [
      aws_security_group.lambda.id
    ]
  }
}

data "aws_lambda_invocation" "bootstrap" {

  function_name = aws_lambda_function.bootstrap.function_name
  input = <<JSON
{
  "endpoint": "${module.eks.cluster_endpoint}",
  "token": "${data.aws_eks_cluster_auth.cluster.token}"
}
JSON
  depends_on = [module.eks, aws_lambda_function.bootstrap]
}