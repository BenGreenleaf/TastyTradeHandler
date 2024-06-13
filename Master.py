from TTApi import *
from TTConfig import *
from DXLink import *
import time


apiClient = TTApi()

apiClient.login()
apiClient.validate()
apiClient.fetch_accounts()

token = apiClient.get_quote_tokens()
data = apiClient.get_equity_options("PBR")['data']['items'][0]['expirations']


for expiration in data:
    strikes = expiration['strikes']
    for strike in strikes:
        strikePrice = strike['strike-price']
        callSymbol = strike['call-streamer-symbol']
        putSymbol = strike['put-streamer-symbol']


dxClient = DXLink(apiClient.streamer_websocket_uri, apiClient.streamer_token)
while dxClient.auth_state != "AUTHORIZED":
    time.sleep(1)
    print(dxClient.auth_state)

data = {
  "type": "FEED_SETUP",
  "channel": 1,
  "acceptAggregationPeriod": 10,
  "acceptDataFormat": "COMPACT",
  "acceptEventFields": {
    "Quote": ["eventType", "eventSymbol", "bidPrice", "askPrice", "bidSize", "askSize"]
  }
}
dxClient.send(data)

time.sleep(5)

data = {
  "type": "FEED_SUBSCRIPTION",
  "channel": 1,
  "add": [{ "symbol": "AAPL", "type": "Quote" }]
}
dxClient.send(data)