import sys
import json
from websocket import WebSocketApp
import time
from secretniy import base
from queue import Queue
import threading

sys.dont_write_bytecode = True


class WebSocketRequest:
    def __init__(self):
        self.ws = None
        self.message_id = 1
        self.connected = False
        self.response_queue = Queue()
        self.dao_id = None

    def connect_websocket(self, token, dao_id):
        self.dao_id = dao_id
        self.token = token
        ws_url = "wss://ws.production.tonxdao.app/ws"
        self.ws = WebSocketApp(
            ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.wst = threading.Thread(target=self.ws.run_forever)
        self.wst.daemon = True
        self.wst.start()

    def on_open(self, ws):
        self.connected = True
        self.send_message(
            {"connect": {"token": self.token, "name": "js"}, "id": self.message_id}
        )

    def on_message(self, ws, message):
        self.response_queue.put(message)

    def on_error(self, ws, error):
        base.log(f"{base.red}WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        self.connected = False

    def send_message(self, message):
        if not self.connected:
            return

        self.ws.send(json.dumps(message))
        self.message_id += 1

    def get_response(self, timeout=10):
        try:
            response = self.response_queue.get(timeout=timeout)
            return json.loads(response)
        except Queue.Empty:
            base.log(f"{base.yellow}No response received within timeout")
            return None

    def sync_request(self):
        self.send_message(
            {"rpc": {"method": "sync", "data": {}}, "id": self.message_id}
        )
        return self.get_response()

    def publish_request(self):
        self.send_message(
            {
                "publish": {"channel": f"dao:{self.dao_id}", "data": {}},
                "id": self.message_id,
            }
        )
        return self.get_response()


def process_farm(token, dao_id):
    while True:
        ws_request = WebSocketRequest()
        ws_request.connect_websocket(token, dao_id)

        # Wait for the connection to be established
        while not ws_request.connected:
            time.sleep(0.1)

        connection_response = ws_request.get_response()

        while ws_request.connected:
            try:
                # Send farm request
                publish_response = ws_request.publish_request()

                # Get info
                sync_response = ws_request.sync_request()

                coins = sync_response["rpc"]["data"]["coins"]
                dao_coins = sync_response["rpc"]["data"]["dao_coins"]
                energy = sync_response["rpc"]["data"]["energy"]
                base.log(
                    f"{base.green}Coins: {base.white}{coins:,} - {base.green}DAO Coins: {base.white}{dao_coins:,} - {base.green}Energy: {base.white}{energy}"
                )

                if energy < 5:
                    break
            except:
                break

            time.sleep(1)

        if energy < 5:
            base.log(f"{base.yellow}Energy is too low. Stop!")
            break
