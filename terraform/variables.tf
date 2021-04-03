variable "app_name" {
  type = string
}

variable "region" {
  type    = string
  default = "UK South"
}

variable "slack_auth_token" {
  type      = string
  sensitive = true
  default   = ""
}
