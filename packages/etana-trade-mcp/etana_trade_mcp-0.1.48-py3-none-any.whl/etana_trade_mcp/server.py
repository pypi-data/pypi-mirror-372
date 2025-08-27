from typing import Any
from datetime import datetime, timedelta
import httpx
from mcp.server.fastmcp import FastMCP
import pandas as pd
from pydantic import BaseModel, Field
import base64
import hmac
import json
import os
import time
import pytz
from math import ceil
from urllib.parse import urlparse
import requests
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

# Initialize FastMCP server
mcp = FastMCP("etana-trade-mcp")

config = json.load(open("/app/data/config.json"))

PRIVATE_API_KEY = config["trader"]["api_key_private"]
KEY_ID = config["trader"]["api_key_id"]
HOST = config["trader"]["host"]
REQUEST = config["trader"]["rest_request"]
PARAMS = config["trader"]["request_params"]
nonce = 0
session = {}

def get_local_datetime(ts_string:str) -> str:
    mst_timezone = pytz.timezone('America/Denver')
    utc_dt = datetime.fromtimestamp(int(ts_string)/1000, tz=pytz.utc)
    mst_dt = utc_dt.astimezone(mst_timezone)
    dt_string = mst_dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt_string

def get_local_datetime_TTS(ts_string:str) -> str:
    mst_timezone = pytz.timezone('America/Denver')
    utc_dt = datetime.fromtimestamp(int(ts_string)/1000, tz=pytz.utc)
    mst_dt = utc_dt.astimezone(mst_timezone)
    dt_string = mst_dt.strftime("%A, %B %d, %Y at %I:%M %p")
    return dt_string

def split_concatenated_pair(pair_string):
  """
  Splits a concatenated trading pair string based on a list of known quote assets.
  
  Args:
    pair_string (str): The trading pair string (e.g., "BTCUSDT").
    
  Returns:
    tuple: A tuple containing the base and quote currency strings.
           Returns ("unknown", "unknown") if no quote asset is found.
  """
  known_quote_assets = ["USD","USDT", "BTC", "ETH", "BNB","SOL","EUR","GBP"]

  for quote in known_quote_assets:
    if pair_string.endswith(quote):
      base = pair_string[:-len(quote)]
      return base, quote
  return "unknown", "unknown"

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


@mcp.tool(name="get_trading_accounts")
async def get_trading_accounts() -> str:
    """Get all trading accounts from the Etana trading system
    Args:
        None
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/accounts")
    RPARAMS = {}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        accounts = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in accounts:
        return(accounts['status_code'])

    accounts_new = []
    for i in range(len(accounts)):
        data_dict = {  
            "currency":accounts[i]['currency_id'],
            "balance":float(accounts[i]['balance']),
            "available_for_trading":float(accounts[i]['available_for_trading']),
            "available_for_withdrawal":float(accounts[i]['available_for_withdrawal']),
            "status":accounts[i]['status'] }
        accounts_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(accounts_new)

    #For Openwebui formatting
    table = "Currency | Balance | Available for Trading | Available for Withdraw | Status" + '\n' + "| :--- | :--- | :--- | :---  | :---" + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['currency']} | {row['balance']:,.2f} | {row['available_for_trading']:,.2f} | {row['available_for_withdrawal']:,.2f} | {row['status']}") + '\n'
    
    answer = str(f"Here's your current account information from the Etana Trading system" + '\n' + table)
    return answer

@mcp.tool(name="get_order_book")
async def get_order_book(security_symbol: str = Field(default="none",description="trading symbol of the secrity that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for Euro for European Union currency as Fiat currencies. Use uppercase characters only."),
                         trading_pair : str = Field(default="none",description="trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only. ")
    ) -> str:
    """Get the order book to buy and sell crypto or fiat currencies from the Etana trading system. Accepts security symbol like BTC for bitcoin or EUR for European Union from the Etana trading system. 2 arguments are available. 
    You do not have to provide values for both, but must provide a value for at least one argument.
    Example of using the first argument - User question: Can I get the order book for bitcoin? : buy_security_symbol would be BTC
    Example of using the second argument - User question: Can I get the order book for buy BTC with USD? or Can I get the order book for BTCUSD? : trading_pair would be BTCUSD
    
    Args:
        security_symbol: trading symbol of the security that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for European Union currency as Fiat currencies. Use uppercase characters only.
        trading_pair : trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only.
    """    
    global nonce 
    nonce = 0
    global session
    session = {}
    err_msg  = str(f"trading pair could not be obtained by the our large language model. Please ask for securities that can be traded.")
    
    if security_symbol != "none":
        security_id = str(f"{security_symbol}USD")
        base = str(f"{security_symbol}")
        quote = "USD"
    elif trading_pair != "none":
        security_id = str(f"{trading_pair}")
        base, quote = split_concatenated_pair(security_id)
    else:
        security_id = str(f"EtanaAI could not figure out the trading pair")
       

    REQUEST = str(f"/api/v1/books/{security_id}")
    RPARAMS = {"limit_asks":"2","limit_bids":"2"}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        order_book = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in order_book:
        return(order_book['status_code']+ ' ' + err_msg)

    order_book_new = []
    for i in range(len(order_book)):  
        for j in range(len(order_book[i]['entries'])):
            if float(order_book[i]['entries'][j]['price']) > 0:
            
                if str(order_book[i]['entries'][j]['timestamp']).strip() == 'None':
                    dt_string = "none"
                else:
                    dt_string = get_local_datetime(order_book[i]['entries'][j]['timestamp'])
            
                data_dict = {   
                    "trading_pair":order_book[i]['security_id'],
                    "price":float(order_book[i]['entries'][j]['price']),
                    "quantity":float(order_book[i]['entries'][j]['quantity']),
                    "exchange":order_book[i]['entries'][j]['exchange_id'],
                    "datetime":dt_string}
                order_book_new.append(data_dict)  
 

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(order_book_new)

    #For Openwebui formatting
    table = "Trading Pair | Price | Quantity | Exchange | Time " + '\n' + "| :--- | :--- | :---  | :--- | :--" + '\n'

    for index, row in df.iterrows():
        table = table + str(f"{row['trading_pair']} | {row['price']:,} | {row['quantity']:,} | {row['exchange']} | {row['datetime']}") + '\n'
    
    answer = str(f"Here's your the order book for {base} from the Etana Trading system" + '\n' + table)   
    return answer

@mcp.tool(name="get_order_history")
async def get_order_history(days_back: str = Field(default="0", description="number of days from current time to start order history list. Example order list for the past week, days_back would be 7, for the past month, days_back would be 30, for the quarter, days_back would be 90, for the past year, days_back would be 365."),
                            hours_back: str = Field(default="0", description="number of hours from current time to start order history list with time less than one day. Example order list for the past hour, days_back woul be 1.")
    ) -> str:
    """Get a historical list of orders from the Etana trading system by specifying the number of past days to start the order history list. 
    Args:
        days_back: number of days from current time to start order history list. Example order list for the past week, days_back would be 7, for the past month, days_back would be 30, for the quarter, days_back would be 90, for the past year, days_back would be 365.
        hours_back: number of hours from current time to start order history list with time less than one day. Example order list for the past hour, days_back woul be 1. 
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    mst_timezone = pytz.timezone('America/Denver')

    dt = datetime.now() - timedelta(days=int(days_back),hours=int(hours_back))
    mst_dt = dt.astimezone(mst_timezone)
    dt_string = mst_dt.strftime("%Y-%m-%d %H:%M:%S")
    print(str(f"{dt_string}")+ '\n')
    print(str(f"{int(mst_dt.timestamp())}")+ '\n')

    REQUEST = str(f"/api/v1/orders/history")
    RPARAMS = {"startTime":str(int(mst_dt.timestamp()*1000))}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        order_history = get.json()
        #print(str(f"Order History Reponse: {get.json()}")+'\n')
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in order_history:
        return(order_history['status_code'])

    
    if not order_history:
        return ("No orders found time period")

    order_history_new = []
    for i in range(len(order_history)):
        data_dict = {  
            "mytime":get_local_datetime(order_history[i]['timestamp']),
            "source":order_history[i]['source'],
            "security":order_history[i]['security_id'],
            "status":order_history[i]['status'],
            "type":order_history[i]['type'],
            "side":order_history[i]['side'],
            "quantity":float(order_history[i]['quantity']),
            "average_price":float(order_history[i]['average_price']),
            "destination":order_history[i]['destination']
        }
        order_history_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(order_history_new)
    df_sorted = df.sort_values(by='mytime', ascending=False)


    #For Openwebui formatting
    table = "Date | Source | Security | Status | Type | Side | Quantity | Average Price | Destination" + '\n' + "| :--- | :--- | :--- | :---  | :--- | :---  | :--- | :--- | :---" + '\n'

    for index, row in df_sorted.iterrows():
        table = table + str(f"{row['mytime']} | {row['source']} | {row['security']} | {row['status']} | {row['type']} | {row['side']} | {row['quantity']:,.2f} | {row['average_price']:,.2f} | {row['destination']}") + '\n'
    
    answer = str(f"Here's your historical list of orders " + '\n' + table)
    return answer

@mcp.tool(name="create_and_execute_order")
async def create_and_execute_order(security_symbol: str = Field(default="none",description="trading symbol of the secrity that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for Euro for European Union currency as Fiat currencies. Use uppercase characters only."),
                       trading_pair : str = Field(default="none",description="trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only."),
                       side: str = Field(description="side of the order. The value can be buy or sell"),
                       quantity: str = Field(description="amount to buy or sell"),
                       )-> str:
    """To trade on the Etana trading system, you must create and execute an order on a trading pair from the order book. You must decide to use the
    security symbol that you want to buy or sell or use the trading pair you want to buy or sell. Do not use both arguements, use either security_symbol
    or trading_pair.

    Example of using the first argument - User question: I want to buy 5 bitcoin? : security_symbol = BTC, side = buy, and quantity = 5
    Example of using the second argument - User question: I want to buy 5 BTC with USD? or I want to buy 5 BTCUSD? : trading_pair = BTCUSD, side = buy, and quantity = 5

    Args:
        security_symbol: trading symbol of the security that you want to buy or sell. Examples would be BTC for Bitcoin, ETH for Ethereum as crypto currencies and USD for US Dollar, EUR for European Union currency as Fiat currencies. Use uppercase characters only.
        trading_pair : trading pair symbol that you want to buy or sell. Examples would be BTCUSD, ETHUSD for crypto trades and EURUSD, GBPUSD for Fiat trades. Use uppercase characters only.
        side: side of the order. The value can be buy or sell
        quantity: amount to buy or sell
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    err_msg  = str(f"trading pair could not be obtained by the our large language model. Please ask for securities that can be traded.")
    
    if security_symbol != "none":
        security_id = str(f"{security_symbol}USD")
        base = str(f"{security_symbol}")
        quote = "USD"
    elif trading_pair != "none":
        security_id = str(f"{trading_pair}")
        base, quote = split_concatenated_pair(security_id)
    else:
        security_id = str(f"EtanaAI could not figure out the trading pair")
       

    REQUEST = str(f"/api/v1/orders")
    RBODY = {"security_id":str(f"{security_id}"),
                 "type":"market",        #Can add limit orders later
                 "side":str(f"{side}"),
                 "time_in_force":"ioc",  #Immediate or Cancel
                 "quantity":str(f"{quantity}"),
                 "destination":"SSOR",   #Defaulting SSOR, can add destinations later
                 "source":"AIUI"}

    try:
        post = request("POST", HOST + REQUEST, body=RBODY)
        create_order = post.json()
        print(post.json())
    except requests.JSONDecodeError:
        print(post.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in create_order:
        return(create_order['status_code'])

    receipt_time_string = get_local_datetime_TTS(create_order['receipt_time'])
    answer = str(f"Your {create_order['side']} order of {create_order['quantity']} {base} was created at {receipt_time_string}. You can ask me about order history in the past hour to see details")
    return answer

@mcp.tool(name="get_trading_securities")
async def get_trading_securities() -> str:
    """Get all securities the from the Etana trading system
    Args:
        None
    """    
    global nonce 
    nonce = 0
    global session
    session = {}

    REQUEST = str(f"/api/v1/securities")
    RPARAMS = {}

    try:
        get = request("GET", HOST + REQUEST, params=RPARAMS)
        securities = get.json()
        print(get.json())
    except requests.JSONDecodeError:
        print(get.text)
    except Exception as e:
        print(f"Error processing api request: {e}")
    
    if 'status_code' in securities:
        return(securities['status_code'])

    securities_new = []
    destinations = ""
    for i in range(len(securities)):
        for j in range(len(securities[i]["available_destinations"])):
            destinations = destinations + securities[i]["available_destinations"][j] + " "
    
        data_dict = {  
            "name":securities[i]['name'],
            "type":securities[i]['type'],
            "destinations":destinations
        }
        securities_new.append(data_dict)  

    pd.set_option('max_colwidth', None)
    df = pd.DataFrame.from_dict(securities_new)

    #For Openwebui formatting
    table = "Trading Pair, Type, Destinations" + '\n' + "| :---  | :--- | :--- " + '\n'
    for index, row in df.iterrows():
        table = table + str(f"{row['name']} | {row['type']} | {row['destinations']}") + '\n'
    
    answer = str(f"The Etana Trading system supports the following trading pairs " + '\n' + table)
    return answer


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport='stdio')
