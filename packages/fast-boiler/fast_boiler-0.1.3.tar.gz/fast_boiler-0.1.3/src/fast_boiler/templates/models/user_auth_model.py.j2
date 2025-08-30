from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from sqlalchemy import Integer
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base

class User(SQLAlchemyBaseUserTable[int], Base):
    """
    The User model for authentication.

    This class inherits from SQLAlchemyBaseUserTable to get all the necessary
    authentication fields (email, hashed_password, etc.).

    We explicitly re-declare the `id` primary key here to resolve a conflict
    between the Base class used by fastapi-users and our own project's Base.
    This is the officially recommended pattern for this type of integration.
    """
    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # You can add your own custom fields here. For example:
    # first_name: Mapped[str | None]