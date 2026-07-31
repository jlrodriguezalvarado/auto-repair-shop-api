import secrets


def generate_jwt_signing_key(length: int = 48) -> str:
    """
    Generate a secure random URL-safe string for JWT signing.

    The default length of 48 generates a key comfortably above
    the 32-byte recommendation for HS256.
    """
    return secrets.token_urlsafe(length)


def generate_secret_key(length: int = 48) -> str:
    """
    Generate a secure random URL-safe string for Django SECRET_KEY.
    """
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    jwt_key = generate_jwt_signing_key()
    secret_key = generate_secret_key()

    print("Add these lines to your .env file:")
    print()
    print(f"SECRET_KEY={secret_key}")
    print(f"JWT_SIGNING_KEY={jwt_key}")
    print()
    print("Both keys are long, random and safe for HS256 and Django.")


