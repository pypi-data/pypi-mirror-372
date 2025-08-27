variable "project_id" {
  type        = string
  description = "GCP project ID"
}

variable "bucket_name" {
  type        = string
  description = "Name of the bucket"
}

variable "location" {
  type        = string
  description = "Bucket location"
  default     = "US"
}

variable "force_destroy" {
  type        = bool
  description = "Force destroy bucket on terraform destroy"
  default     = false
}
