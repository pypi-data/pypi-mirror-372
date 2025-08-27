from typing import Any
import httpx
from mcp.server.fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel, Field
import base64
import hmac
import json
import os
import time
from math import ceil
from urllib.parse import urlparse
import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Initialize FastMCP server
mcp = FastMCP("etana-trade-mcp")

config = json.load(open("/app/data/config.json"))

PRIVATE_API_KEY = config["api_key_private"]
KEY_ID = config["api_key_id"]
HOST = config["host"]
REQUEST = config["rest_request"]
PARAMS = config["request_params"]
nonce = 0
session = {}

def numberToBytes(number):
    return number.to_bytes((ceil((number.bit_length() + 1) / 8)), "big")


def numberFromBytes(bytes):
    return int.from_bytes(bytes, byteorder="big")


def numberFromBase64(base64string):
    return numberFromBytes(base64.decodebytes(base64string.encode()))

def sign_request(method: str, url, params={}, headers={}, body=""):
    global session
    nonce = time.time_ns()
    if "id" not in session.keys():
        attempt = requests.post(HOST + "/api/v1/login/attempt", json={
            "api_key_id": KEY_ID
        }).json()

        session.update({
            "id": attempt["session_id"],
            "base": numberFromBase64(attempt["dh_base"]),
            "modulus": numberFromBase64(attempt["dh_modulus"]),
            "secret": numberFromBytes(os.urandom(512)),
        })
        print("Successfully started login attempt")

        digest = SHA256.new()
        digest.update(base64.decodebytes(attempt["challenge"].encode()))

        rsa = pkcs1_15.new(RSA.importKey(base64.decodebytes(PRIVATE_API_KEY.encode())))
        dh_public_key = pow(session["base"], session["secret"], session["modulus"])

        confirmation_body = {
            "session_id": session["id"],
            "signature": base64.encodebytes(rsa.sign(digest)).decode().replace("\n", ""),
            "dh_key": base64.encodebytes(numberToBytes(dh_public_key)).decode().replace("\n", "")
        }
        confirmation = requests.post(HOST + "/api/v1/login/confirm", json=confirmation_body).json()
        print("Successfully confirmed a session login")

        dh_server_public_key = numberFromBase64(confirmation["dh_key"])
        dh_common_secret = pow(dh_server_public_key, session["secret"], session["modulus"])
        session.update({
            "common_secret": dh_common_secret,
            "common_secret_bytes": numberToBytes(dh_common_secret),
            "server_public_key": dh_server_public_key
        })

    serialized_body = json.dumps(body) if isinstance(body, dict) else str(body)

    sorted_param_keys = sorted(params.keys())

    payload = method.upper() + \
              urlparse(url).path.lower() + \
              "&".join([key.lower() + "=" + params[key] for key in sorted_param_keys]) + \
              "X-Deltix-Nonce=" + str(nonce) + \
              "&X-Deltix-Session-Id=" + str(session["id"]) + \
              serialized_body

    print(payload)
    HMAC = hmac.new(session["common_secret_bytes"], payload.encode(), "sha384")
    digest = HMAC.digest()
    signature = base64.encodebytes(digest).decode().replace("\n", "")
    return (signature, nonce, serialized_body)


def request(method: str, url, params={}, headers={}, body=""):
    global session
    signature, nonce, serialized_body = sign_request(method, url, params, headers, body)
    headers.update({
        "X-Deltix-Signature": signature,
        "X-Deltix-Nonce": str(nonce),
        "X-Deltix-Session-Id": session["id"],
        "Content-Type": "application/json"
    })
    
    try:
        ret = requests.request(method, url, params=params, headers=headers, data=serialized_body)
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    return ret


async def get_userid_by_username(username: str = Field(description="username usually an email address")) -> str:
    """Get the userID from the user name
    Args:
        name: user's name usually their email address
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/users/by-name/{username}")
    RPARAMS = {"liviness": "true"}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        userId_record = get.json()
        print(get.json())   
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    return str(f"The userId for {username} is {userId_record["user_id"]}")

@mcp.tool()
async def get_accounts_by_username(username: str = Field(description="username usually an email address")) -> str:
    """Get all accounts given the username
    Args:
        username: user's name usually their email address
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/users/by-name/{username}")
    RPARAMS = {"liviness": "true"}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        userId_record = get.json()
        print(get.json())   

        nonce = 0
        session = {}

        answer = await get_accounts_by_userId(userId_record["user_id"])

    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    return answer


async def get_accounts_by_userId(userId: str = Field(description="userId from the Etana Trading system")) -> str:
    """Get all accounts given the userID
    Args:
        userId: userID from the Etana trading system
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/user-accounts/for-user/{userId}")
    RPARAMS = {"liviness": "true"}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        accounts = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    accounts_new = []
    for i in range(len(accounts)):
        if not accounts[i]['investment_position']['total_statistics']:
            data_dict = {"account_name":accounts[i]['account_name'],  
                    "account_currency":accounts[i]['account_currency'],
                    "account_type":accounts[i]['account_type'],
                    "total":0}
        else:
            data_dict = {"account_name":accounts[i]['account_name'],   
                    "account_currency":accounts[i]['account_currency'],
                    "account_type":accounts[i]['account_type'],
                    "total":accounts[i]['investment_position']['total_statistics'][0]['total']}
        accounts_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(accounts_new)
    
    #For Openwebui formatting
    table = "Account Name | Currency | Type | Amount" + '\n' + "| :--- | :--- | :--- | :--- " + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['account_name']} | {row['account_currency']} | {row['account_type']} | {row['total']}") + '\n'

    answer = str(f"Here's your current account information from the Etana Trading system" + '\n' + table)
    return answer

if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')

