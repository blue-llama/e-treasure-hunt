variable "app_name" {
  type = string
}

variable "region" {
  type    = string
  default = "UK South"
}

variable "google_maps_api_key" {
  type      = string
  sensitive = true
  default   = null
}

variable "slack_auth_token" {
  type      = string
  sensitive = true
  default   = null
}
