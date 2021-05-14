locals {
  credential = azurerm_app_service.treasure.site_credential.0
}
output "git_remote_url" {
  value = "https://${local.credential.username}:${local.credential.password}@${var.app_name}.scm.azurewebsites.net/${var.app_name}.git"
}
