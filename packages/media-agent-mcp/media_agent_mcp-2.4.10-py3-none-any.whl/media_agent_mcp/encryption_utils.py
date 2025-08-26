#!/usr/bin/env python3
"""
Encryption utilities for secure credential transmission.

This module provides functions to encrypt and decrypt credentials using a shared password.
"""

import base64
import hashlib
from cryptography.fernet import Fernet

# Encryption password - should match the one in routes_omni.py
ENCRYPTION_PASSWORD = "media-agent-mcp!@123"


def _get_encryption_key() -> bytes:
    """
    Generate encryption key from password.
    
    Returns:
        bytes: Fernet encryption key
    """
    # Use SHA256 to create a consistent 32-byte key from password
    key_hash = hashlib.sha256(ENCRYPTION_PASSWORD.encode()).digest()
    # Fernet requires base64-encoded 32-byte key
    return base64.urlsafe_b64encode(key_hash)


def encrypt_credentials(ak: str, sk: str) -> tuple[str, str]:
    """
    Encrypt AK and SK using the encryption password.
    
    Args:
        ak: Access key to encrypt
        sk: Secret key to encrypt
    
    Returns:
        tuple: (encrypted_ak, encrypted_sk) as base64 encoded strings
    """
    key = _get_encryption_key()
    fernet = Fernet(key)
    
    # Encrypt and encode to base64 strings
    encrypted_ak = fernet.encrypt(ak.encode()).decode()
    encrypted_sk = fernet.encrypt(sk.encode()).decode()
    
    return encrypted_ak, encrypted_sk


def decrypt_credentials(encrypted_ak: str, encrypted_sk: str) -> tuple[str, str]:
    """
    Decrypt AK and SK using the encryption password.
    
    Args:
        encrypted_ak: Base64 encoded encrypted access key
        encrypted_sk: Base64 encoded encrypted secret key
    
    Returns:
        tuple: Decrypted (ak, sk) pair
    """
    key = _get_encryption_key()
    fernet = Fernet(key)
    
    # Decode and decrypt
    ak = fernet.decrypt(encrypted_ak.encode()).decode()
    sk = fernet.decrypt(encrypted_sk.encode()).decode()
    
    return ak, sk


if __name__ == "__main__":
    # Example usage
    test_ak = "test_access_key"
    test_sk = "test_secret_key"
    
    print(f"Original AK: {test_ak}")
    print(f"Original SK: {test_sk}")
    
    # Encrypt
    enc_ak, enc_sk = encrypt_credentials(test_ak, test_sk)
    print(f"Encrypted AK: {enc_ak}")
    print(f"Encrypted SK: {enc_sk}")
    
    # Decrypt
    dec_ak, dec_sk = decrypt_credentials(enc_ak, enc_sk)
    print(f"Decrypted AK: {dec_ak}")
    print(f"Decrypted SK: {dec_sk}")
    
    # Verify
    assert dec_ak == test_ak
    assert dec_sk == test_sk
    print("Encryption/Decryption test passed!")