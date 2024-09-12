"""An Azure RM Python Pulumi program"""

import pulumi
from pulumi_azure_native import storage, operationalinsights, resources, app, insights
from pulumi_random import RandomInteger

suffix = RandomInteger("suffix", min=100000, max=999999)
prefix = "pulsam"

resource_group_name = suffix.result.apply(lambda n: f"pulumi-sample-{n}")

# Create an Azure Resource Group
resource_group = resources.ResourceGroup(
    "resource_group", resource_group_name=resource_group_name)

test = app.DotNetComponentType.ASPIRE_DASHBOARD
# Create an Azure resource (Storage Account)
storage_account_name = suffix.result.apply(lambda n: f"{prefix}storage{n}")
account = storage.StorageAccount(
    "sa",
    resource_group_name=resource_group.name,
    account_name=storage_account_name,
    sku={
        "name": storage.SkuName.STANDARD_LRS,
    },
    kind=storage.Kind.STORAGE_V2,
)

# Create a Log Analytics Workspace for Container App Environment monitoring
log_ws = operationalinsights.Workspace(
    "log_ws",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    workspace_name=suffix.result.apply(lambda n: f"{prefix}logws{n}"),
    retention_in_days=30,
    sku=operationalinsights.WorkspaceSkuArgs(
        name="PerGB2018"
    )
)
log_ws_keys = operationalinsights.get_workspace_shared_keys(
    resource_group.name, log_ws.name)

# Create application insights
app_insights = insights.Component(
    "app_insights",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    resource_name_=suffix.result.apply(lambda n: f"{prefix}appinsights{n}"),
    kind=insights.ApplicationType.WEB,
    workspace_resource_id=log_ws.id
)

# Create an Azure Container App Environment
container_app_env = app.ManagedEnvironment(
    "container_app_env",
    resource_group_name=resource_group.name,
    location=resource_group.location,
    environment_name=suffix.result.apply(lambda n: f"{prefix}containerapp{n}"),
    # dapr_ai_connection_string=app_insights.connection_string,
    # dapr_ai_instrumentation_key=app_insights.instrumentation_key,
    app_logs_configuration=app.AppLogsConfigurationArgs(
        destination="log-analytics",
        log_analytics_configuration=app.LogAnalyticsConfigurationArgs(
            customer_id=log_ws.customer_id,
            shared_key=log_ws_keys.primary_shared_key
        )
    )
)

# Exports

pulumi.export("resource_group", resource_group.name)
pulumi.export("storage_account", account.name)
pulumi.export("log_analytics_workspace_name", log_ws.name)
pulumi.export("container_app_env_name", container_app_env.name)
