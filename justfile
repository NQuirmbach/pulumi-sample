_default:
  just --list


# Installs pulumi via homebrew
install-pulumi:
  brew install pulumi/tap/pulumi
  pulumi version

# Display the current Azure subscription
az-account:
  az account show

# Show all available Azure regions
az-regions:
  az account list-locations --output table

# Set pulumi to a different region
set-pulumi-region region:
  pulumi config set azure-native:location {{ region }}
