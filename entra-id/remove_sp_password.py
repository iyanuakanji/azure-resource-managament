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
    url = f"{GRAPH_URL}/servicePrincipals/{args.service_principal_id}/removePassword"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json={"keyId": args.key_id})
        response.raise_for_status()

    print(f"Removed password credential {args.key_id}.")


def main() -> None:
    asyncio.run(remove_password(parse_args()))


if __name__ == "__main__":
    main()
