output "bucket_name" {
  description = "Created bucket name"
  value       = google_storage_bucket.bucket.name
}

output "bucket_url" {
  description = "Bucket self link"
  value       = google_storage_bucket.bucket.self_link
}
