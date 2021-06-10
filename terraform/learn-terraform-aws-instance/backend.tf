terraform {

  backend "remote" {
    organization = "sage-bionetworks"

    workspaces {
      name = "tyu-learn-terraform"
    }
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.27"
    }
  }

  required_version = ">= 0.14.9"
}