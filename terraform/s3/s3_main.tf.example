locals {
  drEnabled = var.create_dr_bucket == 1 ? [1] : []
}

locals {
  bucket_default_kms                  = var.create_bucket == 1 && var.create_kms_key == 0 ? aws_s3_bucket.default_kms_bucket[0].bucket : "no_bucket"
  bucket_kms                          = var.create_bucket == 1 && var.create_kms_key == 1 ? aws_s3_bucket.bucket[0].bucket : "no_bucket"
  bucket                              = local.bucket_default_kms != "no_bucket" ? local.bucket_default_kms : local.bucket_kms
  bucket_dr                           = var.create_dr_bucket == 1 ? aws_s3_bucket.dr-bucket[0].bucket : "no_dr_bucket"
  noncurrent_version_expiration_local = var.noncurrent_version_expiration > -1 ? [1] : []
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

resource "aws_s3_bucket" "default_kms_bucket" {
  count         = var.create_bucket == 1 && var.create_kms_key == 0 ? 1 : 0
  request_payer = var.request_payer
  bucket        = var.bucket_name
  acl           = var.bucket_acl
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  dynamic "cors_rule" {
    for_each = var.cors_rule == null ? [] : var.cors_rule

    content {
      allowed_methods = cors_rule.value.allowed_methods
      allowed_origins = cors_rule.value.allowed_origins
      allowed_headers = lookup(cors_rule.value, "allowed_headers", null)
      expose_headers  = lookup(cors_rule.value, "expose_headers", null)
      max_age_seconds = lookup(cors_rule.value, "max_age_seconds", null)
    }
  }


  dynamic "replication_configuration" {
    for_each = local.drEnabled
    content {
      role = aws_iam_role.replication[0].arn

      rules {
        id     = "entire_bucket"
        prefix = ""
        status = "Enabled"

        destination {
          bucket        = aws_s3_bucket.dr-bucket[0].arn
          storage_class = "GLACIER"
        }
      }
    }
  }

  policy = var.bucket_policy
  versioning {
    enabled = var.bucket_versioning
  }

  dynamic "lifecycle_rule" {
    for_each = local.noncurrent_version_expiration_local
    content {
      prefix  = ""
      enabled = var.bucket_versioning
      id      = "noncurrent_version_expiration"
      noncurrent_version_expiration {
        days = var.noncurrent_version_expiration
      }
    }
  }

  # logging {
  #   target_bucket = var.target_bucket == "" ? "${var.organization}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}-${var.environment}-logging-bucket" : var.target_bucket
  #   target_prefix = "${var.bucket_name}/"
  # }
  tags = {
    Name                            = var.bucket_name
    Environment                     = var.environment
    Owner                           = var.owner
    Description                     = var.description
    Email                           = var.contact_email
    lawsonbillingcode_do_not_remove = var.billing_code
  }
}


resource "aws_s3_bucket_public_access_block" "bucket" {
  count  = var.create_kms_key == 1 && var.create_bucket == 1 ? 1 : 0
  bucket = aws_s3_bucket.bucket[0].id

  block_public_acls   = var.bucket_acl == "private" ? true : false
  block_public_policy = var.bucket_acl == "private" ? true : false
}

resource "aws_s3_bucket_public_access_block" "default_kms_bucket" {
  count  = var.create_bucket == 1 && var.create_kms_key == 0 ? 1 : 0
  bucket = aws_s3_bucket.default_kms_bucket[0].id

  block_public_acls   = var.bucket_acl == "private" ? true : false
  block_public_policy = var.bucket_acl == "private" ? true : false
}

resource "aws_s3_bucket_policy" "example" {
  bucket = aws_s3_bucket.default_kms_bucket[0].id
  policy = jsonencode({
    Id = "testBucketPolicy"
    Statement = [
      {
        Action: [ "s3:ListBucket*", "s3:GetBucketLocation" ],
        Effect = "Allow"
        Principal = {
          AWS = "325565585839"
        }
        Resource = aws_s3_bucket.default_kms_bucket[0].arn
      },
      {
        Action: [ "s3:*Object*", "s3:*MultipartUpload*" ],
        Effect = "Allow"
        Principal = {
          AWS = "325565585839"
        }
        Resource = join("", [aws_s3_bucket.default_kms_bucket[0].arn, "/*"])
      },
    ]
    Version = "2012-10-17"
  })
}

resource "aws_s3_bucket" "bucket" {
  count         = var.create_kms_key == 1 && var.create_bucket == 1 ? 1 : 0
  request_payer = var.request_payer
  bucket        = var.bucket_name
  acl           = var.bucket_acl

  dynamic "cors_rule" {
    for_each = var.cors_rule == null ? [] : var.cors_rule

    content {
      allowed_methods = cors_rule.value.allowed_methods
      allowed_origins = cors_rule.value.allowed_origins
      allowed_headers = lookup(cors_rule.value, "allowed_headers", null)
      expose_headers  = lookup(cors_rule.value, "expose_headers", null)
      max_age_seconds = lookup(cors_rule.value, "max_age_seconds", null)
    }
  }

  dynamic "lifecycle_rule" {
    for_each = local.noncurrent_version_expiration_local
    content {
      prefix  = ""
      enabled = var.bucket_versioning
      id      = "noncurrent_version_expiration"
      noncurrent_version_expiration {
        days = var.noncurrent_version_expiration
      }
    }
  }
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = aws_kms_key.kms_key[0].arn
        sse_algorithm     = "aws:kms"
      }
    }
  }
  policy = var.bucket_policy
  versioning {
    enabled = var.bucket_versioning
  }

  # logging {
  #   target_bucket = var.target_bucket == "" ? "${var.organization}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.name}-${var.environment}-logging-bucket" : var.target_bucket
  #   target_prefix = "${var.bucket_name}/"
  # }
  tags = {
    Name                            = var.bucket_name
    # Environment                     = var.environment
    Owner                           = var.owner
    Description                     = var.description
    Email                           = var.contact_email
    lawsonbillingcode_do_not_remove = var.billing_code
  }
}

resource "aws_s3_bucket" "dr-bucket" {
  provider = aws.dr
  count    = var.create_dr_bucket == 1 && var.create_bucket == 1 ? 1 : 0
  bucket   = var.dr_bucket_name
  acl      = var.bucket_acl
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }

  policy = var.bucket_policy
  versioning {
    enabled = true
  }
  tags = {
    Name                            = "${var.bucket_name}-dr"
    Environment                     = var.environment
    Owner                           = var.owner
    Description                     = var.description
    Email                           = var.contact_email
    lawsonbillingcode_do_not_remove = var.billing_code
  }
}

resource "aws_kms_key" "kms_key" {
  count                   = var.create_kms_key == 1 && var.create_bucket == 1 ? 1 : 0
  deletion_window_in_days = 10
  description             = "${var.bucket_name}-kms-key for ${var.bucket_name}"
  enable_key_rotation     = var.enable_key_rotation
  tags = {
    Name                            = "${var.bucket_name}-kms-key"
    Environment                     = var.environment
    Owner                           = var.owner
    Description                     = var.description
    Email                           = var.contact_email
    lawsonbillingcode_do_not_remove = var.billing_code
  }
}

resource "aws_kms_alias" "alias" {
  count         = var.create_kms_key == 1 && var.create_bucket == 1 ? 1 : 0
  name          = "alias/${var.bucket_name}"
  target_key_id = var.target_key_id == "" ? aws_kms_key.kms_key[0].key_id : var.target_key_id
}
