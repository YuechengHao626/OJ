terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    docker = {
      source  = "kreuzwerker/docker"
      version = "3.0.2"
    }
  }
}

provider "aws" {
  region                   = "us-east-1"
  shared_credentials_files = ["./credentials"]

  default_tags {
    tags = {
      Course     = "CSSE6400"
      Name       = "CoughOverflow"
      Automation = "Terraform"
    }
  }
}

# ECR Token
data "aws_ecr_authorization_token" "ecr_token" {}

provider "docker" {
  registry_auth {
    address  = data.aws_ecr_authorization_token.ecr_token.proxy_endpoint
    username = data.aws_ecr_authorization_token.ecr_token.user_name
    password = data.aws_ecr_authorization_token.ecr_token.password
  }
}

locals {
  database_username = "postgres"
  database_password = "foobarbaz2025"
  database_name     = "coughoverflow"
}

data "aws_iam_role" "lab" {
  name = "LabRole"
}

data "aws_vpc" "default" {
  default = true
}

data "aws_subnets" "private" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ALB Security Group
resource "aws_security_group" "alb_sg" {
  name        = "alb-sg"
  description = "Allow HTTP from internet"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# ECS Task Security Group
resource "aws_security_group" "ecs_sg" {
  name        = "ecs-sg"
  description = "Allow traffic from ALB"

  ingress {
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}



resource "aws_ecs_cluster" "coughoverflow" {
  name = "coughoverflow"
}

resource "aws_ecr_repository" "coughoverflow" {
  name = "coughoverflow"
}

resource "docker_image" "coughoverflow" {
  name = "${aws_ecr_repository.coughoverflow.repository_url}:latest"
  build {
    context = "."
  }
}

resource "docker_registry_image" "coughoverflow" {
  name = docker_image.coughoverflow.name
}

resource "aws_cloudwatch_log_group" "logs" {
  name              = "/ecs/coughoverflow"
  retention_in_days = 7
}

# Load Balancer
resource "aws_lb" "alb" {
  name               = "coughoverflow-alb"
  internal           = false
  load_balancer_type = "application"
  subnets            = data.aws_subnets.private.ids
  security_groups    = [aws_security_group.alb_sg.id]
}

resource "aws_lb_target_group" "tg" {
  name        = "coughoverflow-tg"
  port        = 8080
  protocol    = "HTTP"
  vpc_id      = data.aws_vpc.default.id
  target_type = "ip"

  health_check {
    path                = "/api/v1/health"
    protocol            = "HTTP"
    port                = "8080"
    interval            = 10
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

resource "aws_ecs_task_definition" "coughoverflow" {
  family                   = "coughoverflow"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = data.aws_iam_role.lab.arn
  task_role_arn      = data.aws_iam_role.lab.arn 

  container_definitions = jsonencode([
    {
      name  = "coughoverflow",
      image = docker_image.coughoverflow.name,
      portMappings = [
        {
          containerPort = 8080,
          hostPort      = 8080
        }
      ],

      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://${local.database_username}:${local.database_password}@${aws_db_instance.postgres.address}:${aws_db_instance.postgres.port}/${aws_db_instance.postgres.db_name}"
        }
      ],
      
      logConfiguration = {
        logDriver = "awslogs",
        options = {
          awslogs-group         = aws_cloudwatch_log_group.logs.name,
          awslogs-region        = "us-east-1",
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "coughoverflow" {
  name            = "coughoverflow"
  cluster         = aws_ecs_cluster.coughoverflow.id
  task_definition = aws_ecs_task_definition.coughoverflow.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.private.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = "coughoverflow"
    container_port   = 8080
  }

  depends_on = [aws_lb_listener.listener]
}

# 输出 ALB DNS 名称写入 api.txt
resource "local_file" "api_url" {
  content  = "http://${aws_lb.alb.dns_name}"
  filename = "./api.txt"
}
