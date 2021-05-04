terraform {
  required_version = "~> 0.15.0"
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 2.54"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "treasure" {
  name     = "${var.app_name}-rg"
  location = var.region
}

resource "azurerm_storage_account" "treasure" {
  name                     = replace(var.app_name, "/\\W/", "")
  resource_group_name      = azurerm_resource_group.treasure.name
  location                 = azurerm_resource_group.treasure.location
  account_replication_type = "LRS"
  account_tier             = "Standard"
  min_tls_version          = "TLS1_2"
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

resource "azurerm_sql_server" "treasure" {
  name                         = "${var.app_name}-sql-server"
  resource_group_name          = azurerm_resource_group.treasure.name
  location                     = azurerm_resource_group.treasure.location
  version                      = "12.0"
  administrator_login          = "treasure"
  administrator_login_password = random_password.sql_admin_password.result
  connection_policy            = "Redirect"
}

resource "azurerm_sql_database" "treasure" {
  name                = "treasurehunt"
  resource_group_name = azurerm_resource_group.treasure.name
  location            = azurerm_resource_group.treasure.location
  server_name         = azurerm_sql_server.treasure.name
  edition             = "Basic"
}

resource "azurerm_sql_firewall_rule" "treasure" {
  name                = "azure"
  resource_group_name = azurerm_resource_group.treasure.name
  server_name         = azurerm_sql_server.treasure.name
  start_ip_address    = "0.0.0.0"
  end_ip_address      = "0.0.0.0"
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
    "AZURE_ACCOUNT_KEY"  = azurerm_storage_account.treasure.primary_access_key
    "AZURE_ACCOUNT_NAME" = azurerm_storage_account.treasure.name
    "AZURE_CONTAINER"    = azurerm_storage_container.media.name
    "DBHOST"             = azurerm_sql_server.treasure.fully_qualified_domain_name
    "DBNAME"             = azurerm_sql_database.treasure.name
    "DBPASS"             = azurerm_sql_server.treasure.administrator_login_password
    "DBUSER"             = azurerm_sql_server.treasure.administrator_login
    "DEPLOYMENT"         = "AZURE"
    "GM_API_KEY"         = var.google_maps_api_key
    "SECRET_KEY"         = random_password.secret_key.result
    "SLACK_AUTH_TOKEN"   = var.slack_auth_token
  }

  https_only = true

  site_config {
    linux_fx_version = "PYTHON|3.8"
    scm_type         = "LocalGit"
    min_tls_version  = "1.2"
    ftps_state       = "Disabled"
  }
}
