terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "REPLACE-WITH-YOUR-BUCKET-NAME"
    key    = "grafana-lab/terraform.tfstate"
    region = "us-east-1"
  }
}

variable "aws_region" {
  default = "us-east-1"
}

variable "instance_type" {
  default = "t3.medium"
}

variable "key_name" {
  description = "Name of the AWS key pair to use for SSH access"
  type        = string
}

provider "aws" {
  region = var.aws_region
}

resource "aws_security_group" "grafana_lab" {
  name        = "grafana-lab-sg"
  description = "Grafana LGTM lab access"

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "FastAPI"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "grafana-lab-sg"
  }
}

resource "aws_instance" "grafana_lab" {
  ami                    = "ami-00e801948462f718a"
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.grafana_lab.id]

  root_block_device {
    volume_size = 20
  }

  tags = {
    Name = "grafana-lab"
  }
}

output "public_ip" {
  value = aws_instance.grafana_lab.public_ip
}

output "grafana_url" {
  value = "http://${aws_instance.grafana_lab.public_ip}:3000"
}

output "prometheus_url" {
  value = "http://${aws_instance.grafana_lab.public_ip}:9090"
}

output "api_docs_url" {
  value = "http://${aws_instance.grafana_lab.public_ip}:8080/docs"
}

output "ssh_command" {
  value = "ssh -i <your-key.pem> ec2-user@${aws_instance.grafana_lab.public_ip}"
}
