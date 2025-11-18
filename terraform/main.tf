terraform {
  required_version = ">= 1.0"
  
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.0"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

# Namespace
resource "kubernetes_namespace" "adk_production" {
  metadata {
    name = "adk-production"
  }
}

# ConfigMap for application configuration
resource "kubernetes_config_map" "adk_config" {
  metadata {
    name      = "adk-config"
    namespace = kubernetes_namespace.adk_production.metadata[0].name
  }
  
  data = {
    supabase-url = var.supabase_url
    redis-url    = var.redis_url
    langfuse-host = var.langfuse_host
  }
}

# Secret for sensitive data
resource "kubernetes_secret" "adk_secrets" {
  metadata {
    name      = "adk-secrets"
    namespace = kubernetes_namespace.adk_production.metadata[0].name
  }
  
  data = {
    google-api-key        = base64encode(var.google_api_key)
    supabase-service-key  = base64encode(var.supabase_service_key)
    langfuse-public-key   = base64encode(var.langfuse_public_key)
    langfuse-secret-key   = base64encode(var.langfuse_secret_key)
  }
  
  type = "Opaque"
}

# Variables
variable "kubeconfig_path" {
  description = "Path to kubeconfig file"
  type        = string
  default     = "~/.kube/config"
}

variable "supabase_url" {
  description = "Supabase URL"
  type        = string
}

variable "redis_url" {
  description = "Redis URL"
  type        = string
}

variable "langfuse_host" {
  description = "Langfuse host URL"
  type        = string
}

variable "google_api_key" {
  description = "Google API key"
  type        = string
  sensitive   = true
}

variable "supabase_service_key" {
  description = "Supabase service key"
  type        = string
  sensitive   = true
}

variable "langfuse_public_key" {
  description = "Langfuse public key"
  type        = string
  sensitive   = true
}

variable "langfuse_secret_key" {
  description = "Langfuse secret key"
  type        = string
  sensitive   = true
}

