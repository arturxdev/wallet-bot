from flask import Flask
from flask import request
from flask import Response
import requests
import os
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.environ.get("TOKEN")

app = Flask(__name__)

SUSCRIBERS = ["361114126"]
# Bitcoin address to track
BITCOIN_ADDRESS_TO_TRACK = "1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP"


def parse_message(msg):
    chat_id = msg["message"]["chat"]["id"]
    txt = msg["message"]["text"]
    print(f"User: chat_id: {chat_id} txt: {txt}")
    return chat_id, txt


def tel_send_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    r = requests.post(url, json=payload)
    return r


@app.route("/wallet/webhook", methods=["POST"])
def walletWebhook():
    print(SUSCRIBERS)
    tx_data = request.get_json()
    amount_sent = 0
    amount_received = 0
    for input_tx in tx_data.get("inputs", []):
        if (
            input_tx.get("addresses")
            and BITCOIN_ADDRESS_TO_TRACK in input_tx["addresses"]
        ):
            amount_sent += input_tx.get("output_value", 0)
    for output_tx in tx_data.get("outputs", []):
        if (
            output_tx.get("addresses")
            and BITCOIN_ADDRESS_TO_TRACK in output_tx["addresses"]
        ):
            amount_received += output_tx.get("value", 0)

    amount_sent_btc = amount_sent / 100000000
    amount_received_btc = amount_received / 100000000
    message = (
        f"💰 Transaction Alert! MR 100\n\n"
        f"Amount Sell: {amount_sent_btc:.4f} BTC\n"
        f"Amount Buy: {amount_received_btc:.8f} BTC\n\n"
        f"Timestamp: {tx_data.get('received', 'N/A')}\n"
        f"More details: https://bitinfocharts.com/bitcoin/address/1Ay8vMC7R1UbyCCZRVULMV7iQpHSAbguJP-nodusting"
    )
    for chat_id in SUSCRIBERS:
        tel_send_message(chat_id, message)
    return Response("ok", status=200)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        msg = request.get_json()
        chat_id, txt = parse_message(msg)
        if txt == "hi":
            tel_send_message(chat_id, "hello")
        else:
            tel_send_message(chat_id, "no se")
        return Response("ok", status=200)

    else:
        return "<h1>Welcome!</h1>"


if __name__ == "__main__":
    app.run(debug=True, port=3000)
