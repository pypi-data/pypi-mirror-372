import os
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin
from dotenv import load_dotenv

from .database import get_user_db
from app.models.user_model import User

# Load environment variables from .env file
load_dotenv()

SECRET = os.environ.get("SECRET_KEY")
if SECRET is None:
    raise ValueError("SECRET_KEY environment variable not set")


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    """
    Manages user-related operations, like password hashing, token generation, etc.
    """
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """
        Hook called after a user has successfully registered.
        This is a good place to send a welcome email.
        """
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Hook called after a user has requested a password reset.
        This is where you would send the password reset email.
        """
        print(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """
        Hook called after a user has requested an email verification.
        This is where you would send the verification email.
        """
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db=Depends(get_user_db)):
    """
    FastAPI dependency that provides the UserManager instance.
    """
    yield UserManager(user_db)