# Lab 2 - Broken Linux System on AWS (optional IaC)
# Usage: terraform init && terraform apply -var="key_name=your-key"

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

variable "key_name" {
  description = "EC2 key pair name for SSH access"
  type        = string
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

provider "aws" {
  region = var.region
}

data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
}

resource "aws_security_group" "lab2_sg" {
  name        = "lab2-broken-system-sg"
  description = "Allow SSH for Lab 2 training"

  ingress {
    from_port   = 22
    to_port     = 22
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
    Name    = "Lab2-Broken-System-SG"
    Purpose = "Training"
  }
}

resource "aws_instance" "lab2_broken" {
  ami                    = data.aws_ami.amazon_linux_2023.id
  instance_type          = "t2.micro"
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.lab2_sg.id]
  user_data              = file("${path.module}/../user_data.sh")

  tags = {
    Name    = "Lab2-Broken-System"
    Purpose = "Training"
  }
}

output "public_ip" {
  description = "Public IP for SSH: ssh -i key.pem ec2-user@<ip>"
  value       = aws_instance.lab2_broken.public_ip
}
