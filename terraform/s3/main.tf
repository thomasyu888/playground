module "tyu-test" {
  source            = "./aws-infra-s3-bucket-module"
  bucket_name       = "tyu-test"
  create_dr_bucket  = 1
  dr_bucket_name    = "tyu-test-dr"
  environment       = var.environment
  owner             = "d3b"
  description       = "Teachey Study"
  bucket_acl        = "private"
  bucket_versioning = true
  target_bucket     = ""
  target_prefix     = "tyu-test/"
  contact_email     = "thomas.yu@sagebase.org"
  cors_rule = [
    {
      allowed_methods = ["GET", "PUT", "POST", "HEAD"]
      allowed_origins = ["*"]
      allowed_headers = ["*"]
      max_age_seconds = 3000
    }
  ]
}
