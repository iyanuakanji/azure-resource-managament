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

### App Instance Property Lock

If Graph returns `CannotUpdateLockedServicePrincipalPropertyWithEnforcementScope`, the app registration has an App instance property lock that blocks updates to `passwordCredentials`. For this test application, open **Entra ID > App registrations > global_reader_sp > Authentication**, select **Configure** under **App instance property lock**, disable the lock or the credential verification lock, and save. Then rerun the workflow.

Only disable this control for a test application. Keep property locks enabled for production applications and use an approved credential-management process instead.

Run it from **Actions > Add service principal password > Run workflow**. Supply the target service principal object ID, display name, and expiry period. Keep the returned `keyId` if you need to remove the credential later.

The target ID must be the service principal's **object ID** from **Enterprise applications**, not the App registration object ID or application/client ID. These are different objects. A Graph `404 Not Found` usually means the wrong object ID was supplied, the ID belongs to another tenant, or the object is not present in the tenant used by `AZURE_TENANT_ID`.

For the `global_reader_sp` shown in the portal, first copy its **Application (client) ID** (`0e106392-b8df-4b3c-b595-a260ca68fbdc`), then resolve the Enterprise application object ID:

```bash
az ad sp show \
	--id "0e106392-b8df-4b3c-b595-a260ca68fbdc" \
	--query id \
	--output tsv
```

Use the returned value as `service_principal_id` in the workflow. Alternatively, open **Microsoft Entra ID > Enterprise applications > global_reader_sp > Properties** and copy the **Object ID** there.

This client-secret method is convenient for testing but requires secret rotation. Do not use it for production when GitHub OIDC or another secretless option is available.
