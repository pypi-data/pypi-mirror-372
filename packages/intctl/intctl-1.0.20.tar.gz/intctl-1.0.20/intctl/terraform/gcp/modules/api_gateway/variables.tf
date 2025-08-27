variable "api_id" {
  type        = string
  description = "Identifier for the API"
}

variable "api_config_id" {
  type        = string
  description = "Identifier for the API config"
}

variable "gateway_id" {
  type        = string
  description = "Identifier for the Gateway"
}

variable "location" {
  type        = string
  description = "Gateway region"
  default     = "us-central1"
}

variable "openapi_spec_path" {
  type        = string
  description = "Path to the OpenAPI specification file"
}

variable "display_name" {
  type        = string
  description = "Display name for the API"
  default     = ""
}
