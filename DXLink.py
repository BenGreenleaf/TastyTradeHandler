import json, threading, websocket


class DXLink:
    socket: websocket.WebSocketApp = None
    uri: str = None
    auth_token: str = None
    auth_state: str = None
    user_id: str = None
    retrieved_data: dict = {}

    def __init__(self, uri: str = None, auth_token: str = None) -> None:
        self.uri = uri
        self.auth_token = auth_token
        self.connect()

    def connect(self) -> bool:
        print("dxlink connect")
        self.socket = websocket.WebSocketApp(
            url=self.uri,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.thread = threading.Thread(target=self.socket.run_forever)
        self.thread.start()

    def disconnect(self):
        self.active = False
        self.socket.close()

    def on_message(self, ws, message):
        message = json.loads(message)
        match message["type"]:
            case "SETUP":
                self.send({"type": "AUTH", "token": self.auth_token})
            case "AUTH_STATE":
                if message["state"] == "AUTHORIZED":
                    self.auth_state = message["state"]
                    self.user_id = message["userId"]
                    self.send(
                        {
                            "type": "CHANNEL_REQUEST",
                            "channel": 1,
                            "service": "FEED",
                            "parameters": {"contract": "AUTO"},
                        }
                    )
            case "KEEPALIVE":
                self.send({"type": "KEEPALIVE"})
                print(self.retrieved_data)
            case "FEED_DATA":
                try:
                    data = message['data']
                    for d in data:
                        if type(d) == list:
                            symbol = d[1]
                            askPrice = float(d[2])
                            bidPrice = float(d[3])
                            askSize = float(d[4])
                            bidSize = float(d[5])

                            self.retrieved_data[symbol] = {'ask_price':askPrice, 'bid_price':bidPrice, 'ask_size':askSize, 'bid_size':bidSize}

                            #print(symbol, askPrice, bidPrice, askSize, bidSize)
                except Exception as e:
                    print(message, e)
            case _:
                print(message)

    def on_error(self, ws, error):
        print(f"dxlink error {error}")
        self.active = False

    def on_close(self, ws, status_code, message):
        print(f"dxlink close {status_code} {message}")
        self.active = False

    def on_open(self, ws):
        print(f"dxlink open")
        self.active = True

        self.send(
            {
                "type": "SETUP",
                "keepaliveTimeout": 60,
                "acceptKeepaliveTimeout": 60,
                "version": "0.1",
            }
        )

    def send(self, data: dict = {}):
        print(f"sending {data}")
        if (
            self.auth_state != "AUTHORIZED"
            and data["type"] != "SETUP"
            and data["type"] != "AUTH"
        ):
            print(
                f"dxlink Tried to send message of type {data['type']} but auth_state is {self.auth_state}!"
            )
            return
        if not "channel" in data:
            data["channel"] = 0
        if not "userId" in data and self.user_id is not None:
            data["userId"] = self.user_id
        self.socket.send(json.dumps(data))

    def profitFinder(self):

        for symbol in list(self.retrieved_data.keys()):
            if len(symbol) < 6:
                #Not An Option
                underlyingAsk = self.retrieved_data[symbol]['ask_price']
                underlyingBid = self.retrieved_data[symbol]['bid_price']
                for optionSymbol in list(self.retrieved_data.keys()):
                    strike = int(optionSymbol.split("P")[1]) #Potential Issue if Strike is not Integer
                    if symbol in optionSymbol and optionSymbol != symbol:
                        ask = self.retrieved_data[optionSymbol]['ask_price']

                        #loss = strike




