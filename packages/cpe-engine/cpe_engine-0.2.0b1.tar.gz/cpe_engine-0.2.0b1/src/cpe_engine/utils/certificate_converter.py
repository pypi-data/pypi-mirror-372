"""
Certificate conversion utilities for converting P12/PFX certificates to PEM and CER formats.
"""

import os
from pathlib import Path
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.serialization import pkcs12


def p12_to_pem(p12_path: str, password: str, output_path: str) -> None:
    """
    Convert P12/PFX certificate to PEM format.
    
    The resulting PEM file contains both the certificate and private key,
    and can be used for signing electronic documents.
    
    Args:
        p12_path: Path to the P12/PFX certificate file
        password: Password for the P12/PFX certificate
        output_path: Path where the PEM file will be saved
        
    Raises:
        FileNotFoundError: If the P12 file doesn't exist
        ValueError: If the password is incorrect or file is invalid
    """
    if not os.path.exists(p12_path):
        raise FileNotFoundError(f"Certificate file not found: {p12_path}")
    
    # Read P12/PFX file
    with open(p12_path, 'rb') as f:
        p12_data = f.read()
    
    # Load P12/PFX certificate
    password_bytes = password.encode('utf-8') if password else None
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        p12_data, password_bytes
    )
    
    # Create PEM content with certificate and private key
    pem_content = b""
    
    # Add certificate
    if certificate:
        pem_content += certificate.public_bytes(serialization.Encoding.PEM)
    
    # Add private key
    if private_key:
        pem_content += private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
    
    # Add additional certificates if any
    if additional_certificates:
        for cert in additional_certificates:
            pem_content += cert.public_bytes(serialization.Encoding.PEM)
    
    # Write PEM file
    with open(output_path, 'wb') as f:
        f.write(pem_content)


def p12_to_cer(p12_path: str, password: str, output_path: str) -> None:
    """
    Convert P12/PFX certificate to CER format.
    
    The resulting CER file contains only the public certificate (no private key)
    and can be uploaded to SUNAT.
    
    Args:
        p12_path: Path to the P12/PFX certificate file
        password: Password for the P12/PFX certificate
        output_path: Path where the CER file will be saved
        
    Raises:
        FileNotFoundError: If the P12 file doesn't exist
        ValueError: If the password is incorrect or file is invalid
    """
    if not os.path.exists(p12_path):
        raise FileNotFoundError(f"Certificate file not found: {p12_path}")
    
    # Read P12/PFX file
    with open(p12_path, 'rb') as f:
        p12_data = f.read()
    
    # Load P12/PFX certificate
    password_bytes = password.encode('utf-8') if password else None
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(
        p12_data, password_bytes
    )
    
    if not certificate:
        raise ValueError("No certificate found in P12/PFX file")
    
    # Export certificate as DER format (CER is DER encoded)
    cer_content = certificate.public_bytes(serialization.Encoding.DER)
    
    # Write CER file
    with open(output_path, 'wb') as f:
        f.write(cer_content)