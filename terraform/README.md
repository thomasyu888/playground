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

    Terraform stores the state either locally or remotely.  By default, it is stored locally in a file but the state can actually be stored in terraform cloud or terraform enterprise.

1. Remove instance

    ```
    terraform destroy
    ```

1. Terraform configuration can be split into different files

    - main.tf: Houses the resources to spin up
    - provider.tf: Determines what provider to use (GCP, AWS...)
    - backend.tf: Determines what backend to use (local, remote)
    - variable.tf: Resources can take variables
    - outputs.tf: Resources can have outputs

## Terraform cloud

Followed instructions [here](https://learn.hashicorp.com/tutorials/terraform/cloud-sign-up?in=terraform/cloud-get-started) to get started.

- When using terraform cloud, you can't have a local `terraform.tfstate`
- Not sure how to store amazon credentials on terraform cloud, so you can change the settings to run the applies locally, to only have workspaces save the state.