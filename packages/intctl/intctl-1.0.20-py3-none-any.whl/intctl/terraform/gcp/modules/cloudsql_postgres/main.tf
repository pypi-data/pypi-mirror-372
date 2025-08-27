resource "google_sql_database_instance" "instance" {
  name             = var.instance_name
  database_version = var.database_version
  region           = var.region

  settings {
    tier = var.tier

    ip_configuration {
      ipv4_enabled   = false
      private_network = var.private_network
    }
  }
}

resource "google_sql_user" "root" {
  name     = "postgres"
  instance = google_sql_database_instance.instance.name
  password = var.root_password
}
