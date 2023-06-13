import json
import requests
from ecdsa import SigningKey, SECP256k1

HOST = "127.0.0.1"
PORT = 4000


class Client:
    def __init__(self):
        # For simplicity in this tutorial,
        # we load the private keys directly from a file.
        # However, it is important to consider a more secure
        # approach to obtaining the keys for enhanced security
        self._patient_private_key = self._load_private_keys("patient_private_keys.json")
        self._hospital_private_key = self._load_private_keys("hospital_private_keys.json")

    def send_transaction(self, transaction_data: dict) -> str:
        """
        Send a transaction to the client node interface.

        Args:
            transaction_data (dict): The transaction data containing patient_id, hospital_id, and data.

        Returns:
            str: The response from the server.
        """
        patient_private_key = self._patient_private_key.get(transaction_data["patient_id"])
        hospital_private_key = self._hospital_private_key.get(transaction_data["hospital_id"])

        if patient_private_key is None or hospital_private_key is None:
            return "Patient or Hospital not registered"

        # Sign the transaction with the patient's private key
        patient_signature = self._sign_transaction(transaction_data, patient_private_key)

        # Sign the transaction with the hospital's private key
        hospital_signature = self._sign_transaction(transaction_data, hospital_private_key)

        data = {
            'patient_id': transaction_data.get('patient_id'),
            'hospital_id': transaction_data.get('hospital_id'),
            'data': transaction_data.get('data'),
            'patient_signature': patient_signature,
            'hospital_signature': hospital_signature
        }

        response = requests.post(f'http://{HOST}:{PORT}/add_transaction', json=data)

        return response.text

    @staticmethod
    def _sign_transaction(transaction_data: dict, private_key: str) -> str:
        """
        Sign a transaction with the given private key.

        Args:
            transaction_data (dict): The transaction data to sign.
            private_key (str): The private key to use for signing.

        Returns:
            str: The signature of the transaction.
        """
        signing_key = SigningKey.from_string(bytes.fromhex(private_key), curve=SECP256k1)
        signature = signing_key.sign(str(transaction_data).encode()).hex()

        return signature

    @staticmethod
    def _load_private_keys(path: str) -> dict:
        """
        Load the private keys from a JSON file.

        Args:
            path (str): The path to the JSON file containing the private keys.

        Returns:
            dict: A dictionary of private keys.
        """
        with open(path) as infile:
            return json.load(infile)


def run():
    # Create a sample transaction
    data = {
        'patient_id': 'patient_id_1',
        'hospital_id': 'hospital_id_1',
        'data': "Patient data"
    }

    client = Client()
    response = client.send_transaction(data)
    print(response)


if __name__ == '__main__':
    run()
