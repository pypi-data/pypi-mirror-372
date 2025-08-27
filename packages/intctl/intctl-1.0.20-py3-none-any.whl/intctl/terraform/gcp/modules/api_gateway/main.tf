resource "google_api_gateway_api" "api" {
  provider = google-beta
  api_id        = var.api_id
  display_name  = var.display_name
}

resource "google_api_gateway_api_config" "config" {
  provider      = google-beta
  api           = google_api_gateway_api.api.name
  api_config_id = var.api_config_id

  openapi_documents {
    document {
      path     = var.openapi_spec_path
      contents = file(var.openapi_spec_path)
    }
  }
}

resource "google_api_gateway_gateway" "gateway" {
  provider   = google-beta
  gateway_id = var.gateway_id
  api_config = google_api_gateway_api_config.config.name
  region     = var.location
}
