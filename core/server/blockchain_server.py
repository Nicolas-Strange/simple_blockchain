import hashlib
import json
import ssl
import time
from typing import Optional

from ecdsa import VerifyingKey, SECP256k1, BadSignatureError
from flask import Flask, request
from gevent.pywsgi import WSGIServer

app = Flask(__name__)


class Blockchain:
    def __init__(self):
        self.chain = []
        self._client_public_keys = self._load_public_keys(path="patient_public_keys.json")
        self._hospital_public_keys = self._load_public_keys(path="hospital_public_keys.json")

        # genesis block
        self.add_block(data={}, previous_hash="0")  # Create the genesis block

    def add_block(self, data: dict, previous_hash: Optional[str] = None) -> dict:
        """
                append the new block to the blockchain

                Args:
                    data (dict): Transaction data.
                    previous_hash (Optional or str): hash of the previous block

                Returns:
                    dict: the last block added.
                """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time.time(),
            'data': data,
            'previous_hash': previous_hash or self._hash(self.chain[-1])
        }

        self.chain.append(block)

        return block

    def verify_ownerships(self, data: dict) -> bool:
        """
        Verify ownership of a transaction.

        Args:
            data (dict): Transaction data.

        Returns:
            bool: True if both patient and hospital ownership are verified, False otherwise.
        """
        transaction_data = {
            'patient_id': data['patient_id'],
            'hospital_id': data['hospital_id'],
            'data': data['data']
        }
        patient_signature = data["patient_signature"]
        hospital_signature = data["hospital_signature"]

        patient_ownership = self._verify_ownership(
            transaction_data=transaction_data,
            signature=patient_signature,
            public_key=self._client_public_keys[data['patient_id']]
        )
        hospital_ownership = self._verify_ownership(
            transaction_data=transaction_data,
            signature=hospital_signature,
            public_key=self._hospital_public_keys[data['hospital_id']]
        )
        return patient_ownership and hospital_ownership

    @staticmethod
    def _verify_ownership(transaction_data, signature, public_key):
        """
        Verify ownership of a transaction with a given signature and public key.

        Args:
            transaction_data (dict): Transaction data.
            signature (str): Transaction signature.
            public_key (str): Public key for signature verification.

        Returns:
            bool: True if the ownership is verified, False otherwise.
        """
        verifying_key = VerifyingKey.from_string(bytes.fromhex(public_key), curve=SECP256k1)
        try:
            verifying_key.verify(bytes.fromhex(signature), str(transaction_data).encode())
            return True
        except BadSignatureError:
            return False

    @staticmethod
    def _load_public_keys(path: str) -> dict:
        """
        Load the public keys.

        Args:
            path (str): Path to the public key file.

        Returns:
            json: The loaded public keys.
        """
        with open(path) as infile:
            return json.load(infile)

    @staticmethod
    def _hash(block):
        """
        Generate the hash of a block.

        Args:
            block: The block to be hashed.

        Returns:
            str: The hashed value of the block.
        """
        block_string = str(block).encode()

        return hashlib.sha256(block_string).hexdigest()


blockchain = Blockchain()


@app.route('/block/add', methods=['POST'])
def add_block():
    """
    Add a new block to the blockchain.

    Returns:
        dict: The response indicating the success or failure of adding a new transaction.
    """
    data = request.get_json()

    if not blockchain.verify_ownerships(data):
        return {"response": "error bad signature"}

    block = blockchain.add_block(data=data)

    return {"response": f"block added: {block}"}


if __name__ == '__main__':
    HOST = "127.0.0.1"
    PORT = 5000

    certfile = '../certificates/server/server.crt'
    keyfile = '../certificates/server/server.key'

    # Create SSL/TLS context
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile, keyfile)

    http_server = WSGIServer((HOST, PORT), app, ssl_context=ssl_context)
    http_server.serve_forever()
