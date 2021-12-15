import os
from math import floor

import requests

from jinja2 import Environment, FileSystemLoader, select_autoescape
from user_agents import parse as parse_user_agent


# WEBSOCKET_ENDPOINT = os.environ["WEBSOCKET_ENDPOINT"]
DESTINATION_WALLET = os.environ["DESTINATION_WALLET"]
WELL_KNOWN_WALLET_URL = f"https://explorer.xrplf.org/{DESTINATION_WALLET}"
XUMM_APP_ID = os.environ["XUMM_APP_ID"]
XUMM_APP_SECRET = os.environ["XUMM_APP_SECRET"]

XUMM_BASE_URL = "https://xumm.app/api/v1/platform/payload"

THANK_YOU_RETURN_URL = "https://mushroom.cash/thanks"

jinja_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=select_autoescape(),
)
index_template = jinja_env.get_template("index.html")
thanks_template = jinja_env.get_template("thanks.html")
goal_met_template = jinja_env.get_template("goal_met.html")


PACKAGE_1 = {
    "amount": 125,
    "gifted_nft_amount": 1,
}

PACKAGE_2 = {
    "amount": 250,
    "gifted_nft_amount": 2,
}

# cache_raised_response = requests.post(
#     "https://testnet.xrpl-labs.com",
#     json={"command": "account_info", "account": DESTINATION_WALLET, "id": 1},
# )
# TOTAL_RAISED = 0
# try:
#     TOTAL_RAISED = floor(
#         cache_raised_response.json()["result"]["account_data"]["Balance"] / 1e6
#     )
# except KeyError:
#     pass

TOTAL_RAISED = 0


def get_payload_url(*, amount: int = 125, gifted_nft_amount: int = 1, user_agent):
    payload = {
        "txjson": {
            "TransactionType": "Payment",
            "Destination": DESTINATION_WALLET,
            "Amount": f"{amount}000000",
            "Memos": [
                {
                    "Memo": {
                        "MemoData": "🍄 I'm leveling up the XRPL with xShrooms to get a full-history node! 🍄 shroom.cash 🍄".encode(
                            "utf-8"
                        ).hex()
                    }
                }
            ],
        },
        "custom_meta": {
            "instruction": (
                f"You're sending {amount} XRP for donation and will be receiving {gifted_nft_amount}"
                f" xShrooms NFT{'s' if gifted_nft_amount > 1 else ''}"
                f" ({'1' if gifted_nft_amount > 1 else '0.5'} xShroom token, redeemable for an NFT via launch of XLS-20)"
                " as a gift for your donation."
            )
        },
        "options": {
            "return_url": {
                "web": THANK_YOU_RETURN_URL,
            }
            if user_agent.is_pc
            else {
                "app": THANK_YOU_RETURN_URL,
            }
        },
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "X-API-Key": XUMM_APP_ID,
        "X-API-Secret": XUMM_APP_SECRET,
    }
    response = requests.request("POST", XUMM_BASE_URL, json=payload, headers=headers)
    return response.json()["next"]["always"]


def handler(event, context):
    # print("EVENT")
    # print(event)
    requestPath = event["requestContext"]["http"]["path"]
    user_agent = parse_user_agent(event["requestContext"]["http"]["userAgent"])

    if requestPath.startswith("/favicon.ico"):
        return {
            "statusCode": 404,
            "body": None,
        }

    if requestPath == "/":
        body = goal_met_template.render(
            DESTINATION_WALLET=DESTINATION_WALLET,
            WELL_KNOWN_WALLET_URL=WELL_KNOWN_WALLET_URL,
            TOTAL_RAISED=TOTAL_RAISED,
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": body,
        }

    if requestPath == "/old-index":
        body = index_template.render(
            DESTINATION_WALLET=DESTINATION_WALLET,
            WELL_KNOWN_WALLET_URL=WELL_KNOWN_WALLET_URL,
            TOTAL_RAISED=TOTAL_RAISED,
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "text/html"},
            "body": body,
        }

    # if requestPath == "/donate/for/1":
    #
    #     payload_url = get_payload_url(
    #         amount=125, gifted_nft_amount=1, user_agent=user_agent
    #     )
    #     return {
    #         "statusCode": 302,
    #         "headers": {
    #             "Location": payload_url,
    #         },
    #     }
    #
    # if requestPath == "/donate/for/2":
    #     payload_url = get_payload_url(
    #         amount=250, gifted_nft_amount=2, user_agent=user_agent
    #     )
    #     return {
    #         "statusCode": 302,
    #         "headers": {
    #             "Location": payload_url,
    #         },
    #     }
    #
    if requestPath == "/thanks":
        body = thanks_template.render(
            DESTINATION_WALLET=DESTINATION_WALLET,
            WELL_KNOWN_WALLET_URL=WELL_KNOWN_WALLET_URL,
            TOTAL_RAISED=TOTAL_RAISED,
        )
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html",
            },
            "body": body,
        }

    return {
        "statusCode": 404,
        "body": None,
    }
