# 安全组：允许任何来源访问 PostgreSQL（教学目的）
resource "aws_security_group" "taskoverflow_database" {
  name        = "taskoverflow_database"
  description = "Allow inbound PostgreSQL traffic"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # 教学方便：任何 IP 都能连
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    ipv6_cidr_blocks = ["::/0"]
  }

  tags = {
    Name = "taskoverflow_database"
  }
}

# RDS 实例（PostgreSQL）
resource "aws_db_instance" "postgres" {
  identifier           = "taskoverflow-db"
  allocated_storage    = 20
  max_allocated_storage = 1000
  engine               = "postgres"
  engine_version       = "17"
  instance_class       = "db.t3.micro"
  db_name              = local.database_name
  username             = local.database_username
  password             = local.database_password
  parameter_group_name = "default.postgres17"
  skip_final_snapshot  = true
  vpc_security_group_ids = [aws_security_group.taskoverflow_database.id]
  publicly_accessible  = true  # 公开访问，便于测试

  tags = {
    Name = "taskoverflow_database"
  }
}
