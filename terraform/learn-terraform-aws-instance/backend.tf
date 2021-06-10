terraform {
  # Comment out his backend component to
  # go with local backend.  This will create a
  # terraform.state file
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
