# pipedream add-package solders
# pipedream add-package solana

import json
import math
import os
from base64 import b64encode

import requests
from solana.constants import LAMPORTS_PER_SOL
from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.compute_budget import (set_compute_unit_limit,
                                    set_compute_unit_price)
from solders.hash import Hash as Blockhash
from solders.pubkey import Pubkey
from solders.system_program import TransferParams, transfer

# TODO - Get average fee from Helius API
PRIORITY_FEE = 50_000

# Account you want donations to be sent to
RECEIVE_ACCOUNT = "82385jFFtCgYRrrmpErRYNqrM62SzN6pQguKaPhMzkQr"


BASE_URL = "https://eoyty5mupwyi9b7.m.pipedream.net"

# Image on Blink
KREECHURES_LOGO = "https://shdw-drive.genesysgo.net/333RcJZxH28iEKKhtxC5N4nZrzPqoqkpgfUbhrprbfvC/kreechures500x500.png"

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Methods": "GET,POST,PUT,OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Content-Encoding, Accept-Encoding",
    "Content-Type": "application/json",
}


INVALID_DONATION = {"transaction": "Error", "message": f"Invalid donation amount"}


def handle_get() -> dict:
    """Returns information regarding this action

    Args:
      None

    Returns:
      dict: All information to be displayed to the user regarding the action
    """

    action_response = {
        "icon": f"{KREECHURES_LOGO}",
        "title": "Donate to @daniel_charp",
        "description": "Donation to one of the 76 devs on Solana",
        "label": "Donate 0.01 SOL",
        "links": {
            "actions": [
                {"label": "Donate 0.01 SOL", "href": f"{BASE_URL}?amount=0.01"},
                {"label": "Donate 0.1 SOL", "href": f"{BASE_URL}?amount=0.1"},
                {"label": "Donate 1 SOL", "href": f"{BASE_URL}?amount=1.00"},
                {
                    "label": "Send SOL",
                    "href": f"{BASE_URL}?amount={{amount}}",
                    "parameters": [
                        {
                            "name": "amount",
                            "label": "Total SOL to send",
                            "required": True,
                        },
                    ],
                },
            ]
        },
    }

    pipedream_response = {
        "status": 200,
        "headers": CORS_HEADERS,
        "body": action_response,
    }
    return pipedream_response


def handle_post(event_used: dict) -> dict:
    """Creates transaction for action

    Args:
      event_used (dict): Contains body of POST request

    Returns:
      pipedream_response (dict): Response object containing Solana transaction
    """

    pipedream_response = {}
    donation_amount = event_used.get("query", {}).get("amount", None)
    if donation_amount:
        try:
            donation_total = float(donation_amount)
            donation_account = event_used.get("body", {}).get("account", None)
            donation_lamports = math.floor(donation_total * LAMPORTS_PER_SOL)
            http_client = Client(os.getenv("RPC_PROTECTED"))
            blockhash = http_client.get_latest_blockhash().value.blockhash
            txn = Transaction(
                fee_payer=Pubkey.from_string(donation_account),
                recent_blockhash=blockhash,
            )

            txn.add(set_compute_unit_limit(1_000_000))
            txn.add(set_compute_unit_price(PRIORITY_FEE))
            txn.add(
                transfer(
                    TransferParams(
                        from_pubkey=Pubkey.from_string(donation_account),
                        to_pubkey=Pubkey.from_string(RECEIVE_ACCOUNT),
                        lamports=donation_lamports,
                    )
                )
            )

            # TODO - b64encode followed by base64 decode seems odd. Investigate proper method of doing this.
            base64_bytes = b64encode(txn.serialize(verify_signatures=False))
            donation_payload = {
                "transaction": base64_bytes.decode("ascii"),
                "message": f"Donation in the amount of: {donation_total} SOL",
            }
            json_payload = json.dumps(donation_payload)
            pipedream_response = {
                "status": 200,
                "headers": CORS_HEADERS,
                "body": json_payload,
            }
        except Exception as e:
            json_payload = json.dumps(INVALID_DONATION)
            pipedream_response = {
                "status": 400,
                "headers": CORS_HEADERS,
                "body": json_payload,
            }
    else:
        json_payload = json.dumps(INVALID_DONATION)
        pipedream_response = {
            "status": 400,
            "headers": CORS_HEADERS,
            "body": json_payload,
        }

    return pipedream_response


def handler(pd: "pipedream"):
    event_used = pd.steps["trigger"].get("event", {})
    method_used = pd.steps["trigger"].get("event", {}).get("method", None)
    pipedream_response = {}
    match method_used:
        case "GET":
            pipedream_response = handle_get()
        case "POST":
            pipedream_response = handle_post(event_used)
        case _:
            # Will return on options method
            pipedream_response = {"status": 200, "headers": CORS_HEADERS}

    return pipedream_response
