import json

from ecdsa import SigningKey, SECP256k1


def generate_key_pair():
    """ generate key pair for signature verification """
    signing_key = SigningKey.generate(curve=SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    private_key = signing_key.to_string().hex()
    public_key = verifying_key.to_string().hex()

    return private_key, public_key


def load(path: str) -> dict:
    """
    Load the previous keys
    """
    with open(path) as infile:
        return json.load(infile)


def save(data: dict, path: str) -> None:
    """ save the data """
    with open(path, 'w') as outfile:
        json.dump(data, outfile, indent=4)


patient_id = "patient_id_2"
hospital_id = "hospital_id_2"

# Load previous keys
patient_private_key = load("../client/patient_private_keys.json")
patient_public_key = load("../server/patient_public_keys.json")
hospital_private_key = load("../client/hospital_private_keys.json")
hospital_public_key = load("../server/hospital_public_keys.json")

# Generate key pair for the client
new_patient_private_key, new_patient_public_key = generate_key_pair()
patient_private_key[patient_id] = new_patient_private_key
patient_public_key[patient_id] = new_patient_public_key

# Generate key pair for the hospital
new_hospital_private_key, new_hospital_public_key = generate_key_pair()
hospital_private_key[hospital_id] = new_hospital_private_key
hospital_public_key[hospital_id] = new_hospital_public_key

save(data=patient_private_key, path="../client/patient_private_keys.json")
save(data=hospital_private_key, path="../client/hospital_private_keys.json")

save(data=patient_public_key, path="../server/patient_public_keys.json")
save(data=hospital_public_key, path="../server/hospital_public_keys.json")

