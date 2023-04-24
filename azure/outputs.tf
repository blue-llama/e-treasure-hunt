locals {
  credential = nonsensitive(azurerm_linux_web_app.treasure.site_credential.0)
  azuread_password = nonsensitive(azuread_user.database_admin.password)
}

output "git_remote_url" {
  value = "https://${local.credential.name}:${local.credential.password}@${var.app_name}.scm.azurewebsites.net/${var.app_name}.git"
}

# Run the following from Cloud Shell to grant the app permission in the database.
output "database_commands" {
  value = <<EOT
  sqlcmd \
    -S ${azurerm_mssql_server.treasure.name}.database.windows.net \
    -d ${azurerm_mssql_database.treasure.name} \
    -U ${azuread_user.database_admin.user_principal_name} \
    -P '${local.azuread_password}' \
    -G \
    -l 30

    CREATE USER [${azurerm_linux_web_app.treasure.name}] FROM EXTERNAL PROVIDER;
    ALTER ROLE db_owner ADD MEMBER [${azurerm_linux_web_app.treasure.name}];
    GO
EOT
}
