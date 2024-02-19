import logging
from datetime import datetime, timedelta
from typing import Annotated

import bcrypt
import repository.user as repo_user
from conf.secret import SECRET
from entity.models import User as DBUser
from fastapi import Depends, HTTPException, UploadFile, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt
from jose.exceptions import JWTError
from passlib.context import CryptContext
from schemas.auth import Token, User
from schemas.user import UserCreateSchema
# from service.avatar import get_uploader
from service.emails import send_email
from sqlalchemy.ext.asyncio import AsyncSession

SECRET_KEY = SECRET
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRATION = 1440

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    """
    The verify_password function takes a plain-text password and the hashed version of that password,
    and returns True if they match, False otherwise. This is used to verify that the user's login attempt
    is valid.

    :param plain_password: Pass in the password that was entered by the user
    :param hashed_password: Compare the hashed password in the database to a plain text password
    :return: A boolean value, true or false
    :doc-author: Trelent
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    The get_password_hash function takes a password as input and returns the hash of that password.


    :param password: Get the password from the user
    :return: A hash of the password
    :doc-author: Trelent
    """
    return pwd_context.hash(password)


async def get_user(db: AsyncSession, email: str) -> DBUser | None:
    """
    The get_user function is used to retrieve a user from the database.


    :param db: AsyncSession: Pass the database session to the function
    :param email: str: Find the user in the database
    :return: A dbuser object or none
    :doc-author: Trelent
    """
    user = await repo_user.find_user(email, db)
    if user:
        return user


async def authenticate_user(db, email: str, password: str) -> DBUser | None:
    """
    The authenticate_user function takes a database connection and an email address and password.
    It returns the user object if the credentials are valid, otherwise it returns None.

    :param db: Access the database
    :param email: str: Get the email of the user
    :param password: str: Get the password from the user
    :return: A dbuser object if the user is authenticated, or none otherwise
    :doc-author: Trelent
    """
    user = await get_user(db, email)
    if not user:
        return None
    if not verify_password(password, user.passwd):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    The create_access_token function creates a JWT token with the following claims:
        - exp: expiration time of the token. The default is 15 minutes after creation.
        - iat: issued at time, in UTC format.
        - scope: access_token (this is not used by our application but can be useful for other applications)

    :param data: dict: Store the data that we want to encode in our jwt
    :param expires_delta: timedelta | None: Set the expiration time of the token
    :return: A string, which is the encoded jwt
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update(
        {"exp": expire, "iat": datetime.utcnow(), "scope": "access_token"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None):
    """
    The create_refresh_token function creates a refresh token for the user.
        Args:
            data (dict): The data to be encoded in the JWT. This should include at least a username and an email address, but can also include other information such as roles or permissions.
            expires_delta (timedelta | None): The amount of time until this token expires, defaults to 1000 minutes if not specified.

    :param data: dict: Pass the user's id to the function
    :param expires_delta: timedelta | None: Set the expiration time of the token
    :return: A string
    :doc-author: Trelent
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=1000)
    to_encode.update(
        {"exp": expire, "iat": datetime.utcnow(), "scope": "refresh_token"}
    )
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession
) -> DBUser:
    """
    The get_current_user function is a dependency that will be called by the FastAPI framework to retrieve the current user.

    :param token: Annotated[str: Get the token from the request header
    :param Depends(oauth2_scheme)]: Check if the user is logged in
    :param db: AsyncSession: Connect to the database
    :return: The user object that is associated with the token
    :doc-author: Trelent
    """
    print("checking current user for token: ", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode JWT
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "access_token":
            email = payload["sub"]
            if email is None:
                raise credentials_exception
        else:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(db, email=email)
    if user is None:
        raise credentials_exception
    return user


async def decode_refresh_token(refresh_token: str):
    """
    The decode_refresh_token function decodes the refresh token and returns the email address of the user.
    If it fails to decode, it raises an HTTPException with a 401 status code.

    :param refresh_token: str: Pass the refresh token to the function
    :return: The email of the user
    :doc-author: Trelent
    """
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload["scope"] == "refresh_token":
            email = payload["sub"]
            return email
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token"
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_active_user(
        current_user: Annotated[User, Depends(get_current_user)]
):
    """
    The get_current_active_user function returns the current active user.

    :param current_user: Annotated[User: Get the current user from the database
    :param Depends(get_current_user)]: Get the current user
    :return: The current user, which is the user that has been authenticated
    :doc-author: Trelent
    """
    return current_user


async def generate_token(
        db: AsyncSession, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    The generate_token function is used to generate a new access token and refresh token.

    :param db: AsyncSession: Pass in the database session
    :param form_data: Annotated[OAuth2PasswordRequestForm: Validate the data sent in the request body
    :param Depends()]: Inject dependencies into the function
    :return: A token object
    :doc-author: Trelent
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_active:
        await repo_user.update_otp(user, db, otp=None)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRATION)

        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"sub": user.email}, expires_delta=refresh_token_expires
        )
        print("got new access token", access_token)
        print("got new refresh token", refresh_token)
        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User is not activated",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def hash_pwd(pwd: str, salt=None) -> tuple[str, str]:
    """
    The hash_pwd function takes a password and an optional salt.
    If no salt is provided, it will generate one using bcrypt's gensalt function.
    It then hashes the password with the given or generated salt using bcrypt's hashpw function.
    The hashed_pwd and the used salt are returned as a tuple of strings.

    :param pwd: str: Pass in the password that is to be hashed
    :param salt: Generate a unique hash for each password
    :return: A tuple of strings
    :doc-author: Trelent
    """
    if salt is None:
        logging.info("salting pwd")
        salt = bcrypt.gensalt()
    print(f"using salt: {salt=}")
    hashed_pwd = bcrypt.hashpw(pwd.encode(), salt)
    print(f"using hashed_pwd: {hashed_pwd=}")
    return hashed_pwd.decode("utf-8"), salt.decode("utf-8")


async def create_user(body: UserCreateSchema, db: AsyncSession):
    """
    The create_user function creates a new user in the database.
        It takes in a UserCreateSchema object, which is validated by pydantic and then converted into a dictionary.
        The function then checks if the email already exists in the database, and if it does not exist,
        hashes the password using Argon2 hashing algorithm with salt value of 16 bytes.
        Then it creates an OTP for that user and sends an email to that user's registered email address.

    :param body: UserCreateSchema: Validate the data that is being passed in
    :param db: AsyncSession: Pass the database session to the function
    :return: A user object
    :doc-author: Trelent
    """
    data = body.model_dump()
    user = await repo_user.find_user(data["email"], db)
    if not user:
        data = body.model_dump()
        data["passwd"], data["salt"] = await hash_pwd(data["passwd"])
        user = await repo_user.create_user(data, db)
        otp = await repo_user.update_otp(user, db)
        subject = "Your OTP for registration"
        message = f"Your OTP is as follows: {otp}"
        to_email = user.email
        send_email(subject, message, to_email)
        return user
    else:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def refresh_user_token(
        token: Annotated[str, Depends(oauth2_scheme)], db: AsyncSession
) -> Token:
    """
    The refresh_user_token function is used to refresh the access token.
    It takes a valid refresh token and returns a new access token.


    :param token: Annotated[str: Get the token from the request header
    :param Depends(oauth2_scheme)]: Validate the token
    :param db: AsyncSession: Pass the database session to the function
    :return: A token object
    :doc-author: Trelent
    """
    email = await decode_refresh_token(token)
    user = await repo_user.find_user(email, db)
    if user and user.is_active:
        access_token = create_access_token(data={"sub": email})
        refresh_token = create_refresh_token(data={"sub": email})

        return Token(
            access_token=access_token, refresh_token=refresh_token, token_type="bearer"
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def activate_user(user_mail: str, otp: int, db: AsyncSession):
    """
    The activate_user function is used to activate a user account.
        It takes the following parameters:
            - user_mail (str): The email of the user to be activated.
            - otp (int): The one time password sent to the users email address for activation purposes.

    :param user_mail: str: Find the user in the database
    :param otp: int: Check if the otp sent by the user is equal to the one in our database
    :param db: AsyncSession: Pass the database session to the function
    :return: The user object
    :doc-author: Trelent
    """
    user = await repo_user.find_user(user_mail, db)

    if user:
        if user.otp == otp:
            await repo_user.user_activation(user, db, True)
            return user
        else:
            HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Wrong activation password",
                headers={"WWW-Authenticate": "Bearer"},
            )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User is not found",
        headers={"WWW-Authenticate": "Bearer"},
    )


# async def set_user_image(
#         token: str,
#         file: UploadFile,
#         db: AsyncSession,
#         uploader,
# ):
#     """
#     The set_user_image function takes a token, file, db and uploader as arguments.
#     It then gets the current user from the database using get_current_user function.
#     The contents of the file are read and uploaded to cloudinary using uploader.upload method.
#     The secure url is returned by response object's get method and set in database for that user.

#     :param token: str: Get the user from the database
#     :param file: UploadFile: Get the file from the request
#     :param db: AsyncSession: Pass in the database connection
#     :param uploader: Upload the image to cloudinary
#     :param : Get the current user from the database
#     :return: A dictionary with the key &quot;message&quot; and a string value
#     """
#     user = await get_current_user(token, db)
#     contents = file.file.read()
#     response = uploader.upload(contents, public_id=file.filename)
#     response.get("secure_url")
#     await repo_user.set_image(user, response.get("secure_url"), db)

#     return {"message": f"Successfully uploaded {file.filename}"}
