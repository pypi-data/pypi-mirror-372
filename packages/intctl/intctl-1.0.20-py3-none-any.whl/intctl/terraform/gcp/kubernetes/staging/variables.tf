variable "project_id" {
  type        = string
  description = "The project ID to deploy resources"
  default     = "intellithing"
}

variable "region" {
  type        = string
  description = "The region to deploy resources"
  default     = "europe-west2"
}

variable "cluster_name" {
  type        = string
  description = "The name of the GKE cluster"
  default     = "staging"
}

variable "network" {
  type        = string
  description = "The name of the VPC network"
  default     = "staging-vpc"
}

variable "subnetwork" {
  type        = string
  description = "The name of the subnetwork"
  default     = "staging-subnet"
}

variable "subnetwork_cidr" {
  type        = string
  description = "CIDR range for the subnetwork"
  default     = "10.1.0.0/16"
}

variable "master_authorized_networks" {
  type        = list(string)
  description = "List of CIDR blocks authorized to access the master"
  # An empty list denies public access to the control plane.
  default     = []
}

variable "master_ipv4_cidr_block" {
  type        = string
  description = "IPv4 CIDR block for the masters"
  default     = "172.16.0.0/28"
}

variable "bucket_name" {
  type        = string
  description = "GCS bucket name"
  default     = "staging-bucket"
}

variable "repository_id" {
  type        = string
  description = "Artifact Registry repository id"
  default     = "staging-repo"
}

variable "db_instance_name" {
  type        = string
  description = "Cloud SQL instance name"
  default     = "staging-sql"
}

variable "db_password" {
  type        = string
  description = "Password for postgres user"
  default     = "change-me"
}

variable "api_id" {
  type        = string
  description = "API Gateway API ID"
  default     = "staging-api"
}

variable "api_config_id" {
  type        = string
  description = "API Gateway config ID"
  default     = "staging-config"
}

variable "gateway_id" {
  type        = string
  description = "API Gateway gateway ID"
  default     = "staging-gateway"
}

variable "openapi_spec_path" {
  type        = string
  description = "Path to OpenAPI specification"
  default     = "../../../../microservices/infra-manager/terraform/openapi.yaml"
}
