terraform {
  required_version = "~> 1.0"
  required_providers {
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.74"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "azuread" {}
provider "azurerm" {
  features {}
}

resource "random_password" "azuread_password" {
  length      = 16
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
}

data "azuread_domains" "aad_domains" {
  only_default = true
}

resource "azuread_user" "database_admin" {
  user_principal_name = "${var.app_name}@${data.azuread_domains.aad_domains.domains.0.domain_name}"
  display_name        = "${var.app_name} database admin"
  password            = random_password.azuread_password.result
}

resource "azurerm_resource_group" "treasure" {
  name     = "${var.app_name}-rg"
  location = var.region
}

resource "azurerm_storage_account" "treasure" {
  name                      = replace(var.app_name, "/\\W/", "")
  resource_group_name       = azurerm_resource_group.treasure.name
  location                  = azurerm_resource_group.treasure.location
  account_replication_type  = "LRS"
  account_tier              = "Standard"
  min_tls_version           = "TLS1_2"
  enable_https_traffic_only = true

  # WIBNI to disable storage account key access: but terraform doesn't support doing this, and
  # indeed relies on it being enabled -
  # <https://github.com/terraform-providers/terraform-provider-azurerm/issues/11460>.
}

resource "azurerm_storage_container" "media" {
  name                  = "media"
  storage_account_name  = azurerm_storage_account.treasure.name
  container_access_type = "private"
}

resource "random_password" "sql_admin_password" {
  length      = 16
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
}

resource "azurerm_mssql_server" "treasure" {
  name                         = "${var.app_name}-sql-server"
  resource_group_name          = azurerm_resource_group.treasure.name
  location                     = azurerm_resource_group.treasure.location
  version                      = "12.0"
  administrator_login          = "sqladmin"
  administrator_login_password = random_password.sql_admin_password.result
  connection_policy            = "Redirect"
  azuread_administrator {
    login_username = "AzureAD Admin"
    object_id      = azuread_user.database_admin.object_id
  }
}

resource "azurerm_mssql_database" "treasure" {
  name      = "treasurehunt"
  server_id = azurerm_mssql_server.treasure.id
  sku_name  = "Basic"
}

resource "azurerm_app_service_plan" "treasure" {
  name                = "${var.app_name}-plan"
  location            = azurerm_resource_group.treasure.location
  resource_group_name = azurerm_resource_group.treasure.name
  kind                = "Linux"
  reserved            = true

  sku {
    tier = "Basic"
    size = "B1"
  }
}

resource "random_password" "secret_key" {
  length      = 16
  min_lower   = 1
  min_upper   = 1
  min_numeric = 1
}

resource "azurerm_app_service" "treasure" {
  name                = var.app_name
  resource_group_name = azurerm_resource_group.treasure.name
  location            = azurerm_resource_group.treasure.location
  app_service_plan_id = azurerm_app_service_plan.treasure.id

  app_settings = {
    "APP_URL"            = "${var.app_name}.azurewebsites.net"
    "AZURE_ACCOUNT_NAME" = azurerm_storage_account.treasure.name
    "AZURE_CONTAINER"    = azurerm_storage_container.media.name
    "DBHOST"             = azurerm_mssql_server.treasure.fully_qualified_domain_name
    "DBNAME"             = azurerm_mssql_database.treasure.name
    "DEPLOYMENT"         = "AZURE"
    "ARCGIS_API_KEY"     = var.arcgis_api_key
    "GM_API_KEY"         = var.google_maps_api_key
    "SECRET_KEY"         = random_password.secret_key.result
  }

  https_only = true

  site_config {
    linux_fx_version = "PYTHON|3.8"
    scm_type         = "LocalGit"
    min_tls_version  = "1.2"
    ftps_state       = "Disabled"
    http2_enabled    = true
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_role_assignment" "storage_contributor" {
  scope                = azurerm_storage_account.treasure.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_app_service.treasure.identity.0.principal_id
}

# Run terraform apply twice, first with the more permissive block, and then with the targeted rules.
#
# Only make this change after using Cloud Shell to grant permissions to the app service identity,
# per instructions given by the outputs.
#
# resource "azurerm_mssql_firewall_rule" "treasure" {
#   name             = "Allow Azure services"
#   server_id        = azurerm_mssql_server.treasure.id
#   start_ip_address = "0.0.0.0"
#   end_ip_address   = "0.0.0.0"
# }
resource "azurerm_mssql_firewall_rule" "treasure" {
  for_each         = toset(azurerm_app_service.treasure.possible_outbound_ip_address_list)
  name             = "app-service-${each.key}"
  server_id        = azurerm_mssql_server.treasure.id
  start_ip_address = each.key
  end_ip_address   = each.key
}
