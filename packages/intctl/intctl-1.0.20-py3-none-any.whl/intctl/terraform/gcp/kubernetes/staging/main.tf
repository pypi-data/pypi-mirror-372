resource "google_compute_network" "vpc" {
  name                    = var.network
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = var.subnetwork
  ip_cidr_range = var.subnetwork_cidr
  region        = var.region
  network       = google_compute_network.vpc.id
}

resource "google_container_cluster" "gke_autopilot_cluster" {
  name     = var.cluster_name
  location = var.region

  # Enable Autopilot mode
  enable_autopilot = true

  # Setting REGULAR channel
  release_channel {
    channel = "REGULAR"
  }

  # Network configuration
  network    = google_compute_network.vpc.name
  subnetwork = google_compute_subnetwork.subnet.name

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = true
    master_ipv4_cidr_block   = var.master_ipv4_cidr_block
  }

  master_authorized_networks_config {
    dynamic "cidr_blocks" {
      for_each = var.master_authorized_networks
      content {
        cidr_block   = cidr_blocks.value
        display_name = "authorized"
      }
    }
  }

  # Logging and Monitoring
  logging_service    = "logging.googleapis.com/kubernetes"
  monitoring_service = "monitoring.googleapis.com/kubernetes"
}

module "storage_bucket" {
  source       = "../../modules/storage_bucket"
  project_id   = var.project_id
  bucket_name  = var.bucket_name
  location     = var.region
  force_destroy = true
}

module "artifact_repo" {
  source        = "../../modules/artifact_registry"
  repository_id = var.repository_id
  location      = var.region
}

module "cloudsql" {
  source         = "../../modules/cloudsql_postgres"
  instance_name  = var.db_instance_name
  region         = var.region
  root_password  = var.db_password
  private_network = var.db_private_network
}

module "api_gateway" {
  source            = "../../modules/api_gateway"
  api_id            = var.api_id
  api_config_id     = var.api_config_id
  gateway_id        = var.gateway_id
  location          = var.region
  openapi_spec_path = var.openapi_spec_path
}
