"""Remove a client secret from a Microsoft Entra service principal."""

import argparse
import asyncio
import os

import httpx
from azure.identity import DefaultAzureCredential

GRAPH_SCOPE = "https://graph.microsoft.com/.default"
GRAPH_URL = "https://graph.microsoft.com/v1.0"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--service-principal-id",
        default=os.getenv("AZURE_SERVICE_PRINCIPAL_ID"),
        help="Service principal object ID (or AZURE_SERVICE_PRINCIPAL_ID).",
    )
    parser.add_argument(
        "--key-id",
        required=True,
        help="Key ID returned by add_sp_password.py.",
    )
    args = parser.parse_args()
    if not args.service_principal_id:
        parser.error("--service-principal-id or AZURE_SERVICE_PRINCIPAL_ID is required")
    return args


async def remove_password(args: argparse.Namespace) -> None:
    credential = DefaultAzureCredential()
    access_token = credential.get_token(GRAPH_SCOPE).token
    headers = {"Authorization": f"Bearer {access_token}"}
    service_principal_url = (
        f"{GRAPH_URL}/servicePrincipals/{args.service_principal_id}"
    )
    url = f"{service_principal_url}/removePassword"

    async with httpx.AsyncClient(timeout=30) as client:
        lookup = await client.get(
            service_principal_url,
            headers=headers,
            params={"$select": "displayName,appId,passwordCredentials"},
        )
        if lookup.status_code == httpx.codes.NOT_FOUND:
            raise RuntimeError(
                "Service principal was not found in the authenticated tenant. "
                "Use the Enterprise application service principal object ID."
            )
        lookup.raise_for_status()

        target = lookup.json()
        credential_ids = {
            credential["keyId"]
            for credential in target.get("passwordCredentials", [])
        }
        if args.key_id not in credential_ids:
            raise RuntimeError(
                f"Password credential {args.key_id} was not found on "
                f"{target.get('displayName', 'the service principal')}."
            )

        response = await client.post(url, headers=headers, json={"keyId": args.key_id})
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise RuntimeError(
                f"Microsoft Graph could not remove the password: {response.text}"
            ) from error

        for attempt in range(1, 7):
            lookup = await client.get(
                service_principal_url,
                headers=headers,
                params={"$select": "passwordCredentials"},
            )
            lookup.raise_for_status()
            remaining_ids = {
                credential["keyId"]
                for credential in lookup.json().get("passwordCredentials", [])
            }
            if args.key_id not in remaining_ids:
                print(f"Removed and verified password credential {args.key_id}.")
                return
            if attempt < 6:
                await asyncio.sleep(5)

    raise RuntimeError(
        f"Password credential {args.key_id} still appears after 6 verification attempts."
    )


def main() -> None:
    asyncio.run(remove_password(parse_args()))


if __name__ == "__main__":
    main()
