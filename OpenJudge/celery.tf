resource "aws_ecs_task_definition" "celery_worker" {
  family                   = "celery-worker"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = data.aws_iam_role.lab.arn
  task_role_arn            = data.aws_iam_role.lab.arn

  container_definitions = jsonencode([
    {
      name      = "celery-worker",
      image     = docker_image.coughoverflow.name,
      command   = ["sh", "-c", "sleep 5 && celery -A app.tasks worker --loglevel=info"],
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
          awslogs-stream-prefix = "ecs-worker"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "celery_worker" {
  name            = "celery-worker"
  cluster         = aws_ecs_cluster.coughoverflow.id
  task_definition = aws_ecs_task_definition.celery_worker.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.private.ids
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  
}