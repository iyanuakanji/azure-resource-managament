# Entra ID Resource Management

Place Entra ID resource definitions, configuration, and deployment documentation here.

Keep credentials, client secrets, and other sensitive values out of this directory and source control.

## GitHub Actions Test Workflow

The repository workflow at `.github/workflows/add-sp-password.yml` uses a service principal client secret for testing. Configure the `azure-production` GitHub environment with these secrets:

```text
AZURE_CLIENT_ID
AZURE_TENANT_ID
AZURE_SUBSCRIPTION_ID
AZURE_CLIENT_SECRET
```

The automation service principal needs Microsoft Graph application permission `Application.ReadWrite.All` with admin consent. The workflow uses `DefaultAzureCredential`, creates the password through Microsoft Graph, masks the returned secret, and deletes the temporary output file. The test workflow does not persist the generated password.

Run it from **Actions > Add service principal password > Run workflow**. Supply the target service principal object ID, display name, and expiry period. Keep the returned `keyId` if you need to remove the credential later.

This client-secret method is convenient for testing but requires secret rotation. Do not use it for production when GitHub OIDC or another secretless option is available.
