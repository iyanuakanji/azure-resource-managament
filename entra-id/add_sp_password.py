"""Add a client secret to an existing Microsoft Entra service principal."""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta, timezone

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
        "--display-name",
        default="Managed by automation",
        help="Display name for the new password credential.",
    )
    parser.add_argument(
        "--valid-days",
        type=int,
        default=90,
        help="Credential lifetime in days (default: 90).",
    )
    args = parser.parse_args()
    if not args.service_principal_id:
        parser.error("--service-principal-id or AZURE_SERVICE_PRINCIPAL_ID is required")
    if args.valid_days < 1:
        parser.error("--valid-days must be at least 1")
    return args


async def add_password(args: argparse.Namespace) -> None:
    credential = DefaultAzureCredential()
    access_token = credential.get_token(GRAPH_SCOPE).token
    end_date = datetime.now(timezone.utc) + timedelta(days=args.valid_days)
    payload = {
        "passwordCredential": {
            "displayName": args.display_name,
            "endDateTime": end_date.isoformat().replace("+00:00", "Z"),
        }
    }
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{GRAPH_URL}/servicePrincipals/{args.service_principal_id}/addPassword"

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()

    result = response.json()
    print("Store secretText securely now; Microsoft Graph will not return it again.", file=sys.stderr)
    print(
        json.dumps(
            {
                "keyId": result["keyId"],
                "secretText": result["secretText"],
                "endDateTime": result["endDateTime"],
            },
            indent=2,
        )
    )


def main() -> None:
    asyncio.run(add_password(parse_args()))


if __name__ == "__main__":
    main()
