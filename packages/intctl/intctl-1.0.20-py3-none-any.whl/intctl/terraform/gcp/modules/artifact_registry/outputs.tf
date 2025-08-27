output "repository_id" {
  description = "Repository ID"
  value       = google_artifact_registry_repository.repo.repository_id
}

output "repository_location" {
  description = "Repository location"
  value       = google_artifact_registry_repository.repo.location
}
