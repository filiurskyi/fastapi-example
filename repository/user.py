from datetime import datetime, timezone
from random import randint

from entity.models import User
from schemas.user import UserCreateSchema
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# async def get_users(limit: int, offset: int, db: AsyncSession):
#     """
#     The get_users function returns a list of users.

#     :param limit: int: Limit the number of results returned
#     :param offset: int: Skip the first n rows
#     :param db: AsyncSession: Pass the database connection to the function
#     :return: A list of user objects
#     :doc-author: Trelent
#     """
#     stmt = select(User).offset(offset).limit(limit)
#     users = await db.execute(stmt)
#     return users.scalars().all()


async def find_user(email: str, db: AsyncSession) -> User | None:
    """
    The find_user function takes an email and a database session,
    and returns the user with that email if it exists.
    If no such user exists, None is returned.

    :param email: str: Specify the type of the parameter
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object or none
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(email=email)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def get_user(user_id: int, db: AsyncSession):
    """
    The get_user function returns a user object from the database.

    :param user_id: int: Specify the user id of the user you want to get
    :param db: AsyncSession: Pass the database connection to the function
    :return: A user object
    :doc-author: Trelent
    """
    stmt = select(User).filter_by(id=user_id)
    user = await db.execute(stmt)
    return user.scalar_one_or_none()


async def create_user(body: dict, db: AsyncSession):
    """
    The create_user function creates a new user in the database.

    :param body: dict: Pass in the request body
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    user = User(**body)
    db.add(user)
    print(f"{user.salt=}")
    print(f"{user.passwd=}")
    await db.commit()
    await db.refresh(user)
    return user


async def update_otp(user: User, db: AsyncSession, otp: int | None = None):
    """
    The update_otp function updates the OTP for a user.

    If no OTP is provided, it will generate one randomly.


    :param user: User: Pass in the user object that is to be updated
    :param db: AsyncSession: Pass the database connection to the function
    :param otp: int | None: Set the otp to a specific value
    :return: The otp
    :doc-author: Trelent
    """
    if not otp:
        otp = randint(100000, 999999)
    setattr(user, "otp", otp)
    await db.commit()
    await db.refresh(user)
    return otp


async def user_activation(user: User, db: AsyncSession, is_active: bool):
    """
    The user_activation function is used to activate or deactivate a user.

    :param user: User: Pass the user object to the function
    :param db: AsyncSession: Pass in the database session
    :param is_active: bool: Set the user's is_active attribute to true or false
    :return: A boolean value
    :doc-author: Trelent
    """
    setattr(user, "is_active", is_active)
    await db.commit()
    await db.refresh(user)


async def edit_user(user_id: int, body: UserCreateSchema, db: AsyncSession):
    """
    The edit_user function allows you to edit a user.

    :param user_id: int: Identify the user to be edited
    :param body: UserCreateSchema: Validate the request body
    :param db: AsyncSession: Pass in the database session
    :return: The updated user object
    :doc-author: Trelent
    """
    user = await get_user(user_id, db)
    for field, value in body:
        if value is not None:
            setattr(user, field, value)

    setattr(user, "modified_at", datetime.now(timezone.utc))
    await db.commit()
    await db.refresh(user)
    return user


async def delete_user(user_id: int, db: AsyncSession):
    """
    The delete_user function deletes a user from the database.
        Args:
            user_id (int): The id of the user to delete.
            db (AsyncSession): An async session object for interacting with the database.
        Returns:
            User: The deleted User object.

    :param user_id: int: Specify the user to delete
    :param db: AsyncSession: Pass the database connection to the function
    :return: A user
    :doc-author: Trelent
    """
    user = await get_user(user_id, db)
    await db.delete(user)
    await db.commit()
    return user


async def set_image(user: User, url: str, db: AsyncSession) -> User:
    """
    The set_image function sets the image attribute of a user.

    :param user: User: Specify the user that will be updated
    :param url: str: Set the image url of a user
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    setattr(user, "image", url)
    await db.commit()
    await db.refresh(user)
    return user
