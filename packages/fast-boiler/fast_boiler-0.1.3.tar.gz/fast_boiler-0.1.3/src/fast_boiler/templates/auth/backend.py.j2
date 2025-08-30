import os
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Transport layer: Defines how the token is transported (e.g., cookies, headers)
cookie_transport = CookieTransport(cookie_name="fastboilerauth", cookie_max_age=3600)

# Get the secret key from the environment
# It's critical that this is kept secret
SECRET = os.environ.get("SECRET_KEY")
if SECRET is None:
    raise ValueError("SECRET_KEY environment variable not set")


def get_jwt_strategy() -> JWTStrategy:
    """
    Returns the JWT strategy instance, which is responsible for creating
    and verifying the JSON Web Tokens.
    """
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


# The main AuthenticationBackend instance
# This combines the transport and the JWT strategy
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)