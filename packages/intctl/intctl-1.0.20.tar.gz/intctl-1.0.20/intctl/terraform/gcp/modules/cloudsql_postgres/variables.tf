variable "instance_name" {
  type        = string
  description = "Name of the Cloud SQL instance"
}

variable "database_version" {
  type        = string
  description = "PostgreSQL version"
  default     = "POSTGRES_13"
}

variable "region" {
  type        = string
  description = "Instance region"
}

variable "tier" {
  type        = string
  description = "Machine tier"
  default     = "db-f1-micro"
}

variable "root_password" {
  type        = string
  description = "Password for postgres user"
}

variable "private_network" {
  type        = string
  description = "Self link of the VPC network for private IP connectivity"
}
