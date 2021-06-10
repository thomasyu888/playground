# Terraform Exploration

Terraform allows you to write infrastructure as code.  This is my exploration of terraform.  Follow this [getting started guide](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started) for AWS.

1. Follow instructions on [Sage jumpcloud](https://sagebionetworks.jira.com/wiki/spaces/IT/pages/405864455/Jumpcloud) to access the `aws cli`.  Must set up a profile in `~/.aws/credentials`.
1. Initialize terraform

    ```
    terraform init
    ```

1. Terraform has an auto formatter that will automatically format the code and you can validate the structure as well.

    ```
    terraform fmt
    terraform validate
    ```

1. Create instance

    ```
    cd learn-terraform-aws-instance
    terrafrom apply
    ```
