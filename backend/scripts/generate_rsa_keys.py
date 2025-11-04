#!/usr/bin/env python3
"""Generate RSA key pair for JWT token signing (RS256 algorithm).

This script generates a 2048-bit RSA key pair for use in JWT token signing.
In production, keys should be stored in AWS Secrets Manager.

Usage:
    python scripts/generate_rsa_keys.py

Output:
    Prints the private and public keys to stdout. You can save these to your .env file:

    JWT_PRIVATE_KEY="<generated private key in PEM format>"
    JWT_PUBLIC_KEY="<generated public key in PEM format>"
"""

from app.core.security import generate_rsa_key_pair


def main():
    """Generate and print RSA key pair."""
    print("Generating RSA key pair for JWT token signing (RS256)...")
    print("=" * 70)

    private_key, public_key = generate_rsa_key_pair()

    print("\nPrivate Key (JWT_PRIVATE_KEY):")
    print("-" * 70)
    print(private_key)
    print("-" * 70)

    print("\nPublic Key (JWT_PUBLIC_KEY):")
    print("-" * 70)
    print(public_key)
    print("-" * 70)

    print("\nTo use these keys, add them to your .env file:")
    print("\nJWT_PRIVATE_KEY=\"\"\"{}...\"\"\"".format(private_key[:50]))
    print("JWT_PUBLIC_KEY=\"\"\"{}...\"\"\"".format(public_key[:50]))
    print("\nNote: In production, these keys should be stored in AWS Secrets Manager.")
    print("=" * 70)


if __name__ == "__main__":
    main()

