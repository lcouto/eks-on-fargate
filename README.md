# eks_on_fargate

This function allows users to use terraform to update their EKS cluster to run only on Fargate during deployment

 Pre-Requisites
- Terraform EKS Module (main.tf)

This function runs commands against the EKS API to enable EKS to run on Fargate only without the kubectl commands.

This python script is executed by a lambda, but can be run directly as a null resource. The container that was being used for the terraform deployment did not have local python requirements so a lambda had to be created.