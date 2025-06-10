# Flask (coughoverflow 服务)
resource "aws_appautoscaling_target" "flask_scaling_target" {
  max_capacity       = 4
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.coughoverflow.name}/${aws_ecs_service.coughoverflow.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.coughoverflow]
}

resource "aws_appautoscaling_policy" "flask_cpu_scale" {
  name               = "flask-cpu-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.flask_scaling_target.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 20
  }
}

# Celery Worker 服务
resource "aws_appautoscaling_target" "celery_scaling_target" {
  max_capacity       = 6
  min_capacity       = 1
  resource_id        = "service/${aws_ecs_cluster.coughoverflow.name}/${aws_ecs_service.celery_worker.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  depends_on = [aws_ecs_service.celery_worker]
}

resource "aws_appautoscaling_policy" "celery_cpu_scale" {
  name               = "celery-cpu-policy"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.celery_scaling_target.resource_id
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value = 30
  }
}
