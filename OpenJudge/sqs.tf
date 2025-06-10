resource "aws_sqs_queue" "celery_queue" {
  name = "celery"

  visibility_timeout_seconds = 90
  message_retention_seconds  = 345600
  receive_wait_time_seconds  = 10
  delay_seconds              = 0

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.celery_dlq.arn
    maxReceiveCount     = 3
  })
}

resource "aws_sqs_queue" "celery_dlq" {
  name = "celery-dead-letter"
}