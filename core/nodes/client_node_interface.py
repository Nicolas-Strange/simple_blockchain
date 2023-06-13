import logging
from typing import Optional

import requests
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from jsonschema import validate
from jsonschema.exceptions import ValidationError

from valid_input import input_schema

app = Flask(__name__)


class ClientInterface:
    CERT = '../certificates/clients/client.crt'

    BLOCKCHAIN_HOST: str = "127.0.0.1"
    BLOCKCHAIN_PORT: int = 5000

    HOST: str = "127.0.0.1"
    PORT: int = 4000

    def add_transaction(self, data: dict) -> str:
        """
        Send a request to add a transaction to the blockchain.

        Args:
            data (dict): The transaction data.

        Returns:
            str: The response from the server.
        """
        try:
            validate(instance=data, schema=input_schema)
        except ValidationError as e:
            logging.error(e)
            return "error"

        response = self._send_request_to_server(
            end_point="block/add",
            data=data
        )

        return response

    def _send_request_to_server(self, end_point: str, data: Optional[dict] = None) -> str:
        """
        Send a request to the blockchain server.

        Args:
            end_point (str): The endpoint to send the request to.
            data (dict, optional): The data to send in the request payload.

        Returns:
            str: The response from the server.
        """
        url = f"https://{self.BLOCKCHAIN_HOST}:{self.BLOCKCHAIN_PORT}/{end_point}"

        try:
            response = requests.post(url, verify=self.CERT, json=data)
            return response.text

        except requests.exceptions.RequestException as e:
            return str(e)


node = ClientInterface()


@app.route('/add_transaction', methods=['POST'])
def add_transaction() -> str:
    """
    Add a transaction to the blockchain.

    Returns:
        str: The response from the server.
    """
    return node.add_transaction(request.get_json())


if __name__ == '__main__':
    http_server = WSGIServer((node.HOST, node.PORT), app)
    http_server.serve_forever()
