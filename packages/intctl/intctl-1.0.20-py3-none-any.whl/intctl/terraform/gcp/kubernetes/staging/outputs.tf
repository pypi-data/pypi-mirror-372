output "cluster_name" {
  description = "The name of the created GKE Autopilot cluster."
  value       = google_container_cluster.gke_autopilot_cluster.name
}

output "cluster_endpoint" {
  description = "The endpoint of the created GKE cluster."
  value       = google_container_cluster.gke_autopilot_cluster.endpoint
}

output "cluster_location" {
  description = "The location of the created GKE Autopilot cluster."
  value       = google_container_cluster.gke_autopilot_cluster.location
}

output "bucket_name" {
  description = "Created bucket"
  value       = module.storage_bucket.bucket_name
}

output "repository_id" {
  description = "Artifact Registry repository"
  value       = module.artifact_repo.repository_id
}

output "sql_instance" {
  description = "Cloud SQL instance name"
  value       = module.cloudsql.instance_name
}
output "api_gateway_url" {
  description = "Hostname of the API Gateway"
  value       = module.api_gateway.gateway_default_hostname
}

