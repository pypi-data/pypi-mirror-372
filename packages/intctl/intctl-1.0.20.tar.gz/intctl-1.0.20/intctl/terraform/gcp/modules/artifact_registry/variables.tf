variable "repository_id" {
  type        = string
  description = "Artifact Registry repository ID"
}

variable "location" {
  type        = string
  description = "Repository region"
  default     = "us-central1"
}

variable "format" {
  type        = string
  description = "Repository format"
  default     = "DOCKER"
}

variable "description" {
  type        = string
  description = "Repository description"
  default     = ""
}
