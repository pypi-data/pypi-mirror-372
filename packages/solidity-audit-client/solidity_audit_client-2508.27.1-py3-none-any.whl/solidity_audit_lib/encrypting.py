from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from substrateinterface import Keypair as SubstrateKeypair
import sr25519_ecdh


__all__ = ['encrypt', 'decrypt']


def encrypt(msg: str, signer: SubstrateKeypair, receiver: str) -> str:
    receiver_pubkey = SubstrateKeypair(ss58_address=receiver).public_key

    msg = bytes.fromhex(msg.encode().hex())

    shared_key: bytes = sr25519_ecdh.shared_secret(signer.private_key, receiver_pubkey)

    nonce = get_random_bytes(12)  # 96-bit nonce
    cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
    ciphertext, tag = cipher.encrypt_and_digest(msg)

    encrypted = nonce + ciphertext + tag  # nonce(12) + ciphertext(n) + tag(16)
    return "0x" + encrypted.hex()


def decrypt(msg: str, receiver: SubstrateKeypair, sender: str) -> str:
    sender_pubkey = SubstrateKeypair(ss58_address=sender).public_key
    msg = bytes.fromhex(msg.replace("0x", ""))

    shared_key = sr25519_ecdh.shared_secret(receiver.private_key, sender_pubkey)

    nonce = msg[:12]  # nonce(12)
    ciphertext = msg[12:-16]  # ciphertext(n)
    tag = msg[-16:]  # tag(16)

    cipher = AES.new(shared_key, AES.MODE_GCM, nonce=nonce)
    decrypted = cipher.decrypt_and_verify(ciphertext, tag)

    return decrypted.decode()
