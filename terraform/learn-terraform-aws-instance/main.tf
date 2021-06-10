terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}

provider "aws" {
  profile = "sandbox-developer"
  region  = "us-east-1"
}

resource "aws_instance" "app_server" {
  ami           = "ami-0810a318c4b1243c5"
  instance_type = "t2.micro"
  key_name      = "tomnew"

  root_block_device {
    volume_size = "10"
  }

  vpc_security_group_ids = ["sg-086ea4a701379ead4"]
  subnet_id              = "subnet-025c297e427e44daf"

  tags = {
    Name    = "ExampleAppServerInstance"
    Project = "IBC"
  }
}
