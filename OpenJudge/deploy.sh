#!/bin/bash
set -e

echo "🔧 Initialising Terraform..."
terraform init -upgrade

echo "🚀 Applying Terraform..."
terraform apply -auto-approve

echo "✅ Deployment complete. API URL:"
cat api.txt
