output "api_name" {
  description = "Full name of the created API"
  value       = google_api_gateway_api.api.name
}

output "api_config_name" {
  description = "Full name of the created API config"
  value       = google_api_gateway_api_config.config.name
}

output "gateway_name" {
  description = "Full name of the created Gateway"
  value       = google_api_gateway_gateway.gateway.name
}

output "gateway_default_hostname" {
  description = "Hostname of the Gateway"
  value       = google_api_gateway_gateway.gateway.default_hostname
}
