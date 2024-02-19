from typing import Annotated

from conf.db import get_db
from fastapi import APIRouter, Depends, File, Query, Security, UploadFile, status
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)
from schemas.auth import Token
from schemas.user import UserCreateSchema
from service import auth, emails
from service.rate_limiter import limit_allowed

# from service.avatar import get_uploader
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
security = HTTPBearer()


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    body: UserCreateSchema,
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
):
    """
    The signup function creates a new user in the database.
    It takes a UserCreateSchema as input, which is validated by FastAPI.
    The function then uses the auth module to create the user and return it.

    :param body: UserCreateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param rl: Limit the number of requests that can be made to this endpoint
    :return: A user object
    :doc-author: Trelent
    """
    user = await auth.create_user(body, db)
    return user


@router.post("/token", status_code=status.HTTP_201_CREATED)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
) -> Token:
    """
    The login_for_access_token function is used to generate a new access token for the user.
    The function takes in an OAuth2PasswordRequestForm object, which contains the username and password of the user.
    It then uses these credentials to authenticate with our database, and if successful it will return a Token object containing
    the access_token that can be used by clients to make authenticated requests.

    :param form_data: Annotated[OAuth2PasswordRequestForm: Get the data from the request body
    :param Depends()]: Pass in the form_data from the request body
    :param db: AsyncSession: Get the database connection
    :param rl: Limit the number of requests per minute
    :return: A token object, which is a pydantic model
    :doc-author: Trelent
    """
    token: Token = await auth.generate_token(db, form_data)
    return token


@router.get("/user")
async def user_path(
    token: str = Depends(oauth2_scheme),
    # current_user: auth.DefaultUser,
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
):
    """
    The secret function is a protected endpoint that returns the current user's username.

    :param token: str: Get the token from the request
    :param # current_user: auth.DefaultUser: Get the current user
    :param db: AsyncSession: Get the database session
    :param rl: Limit the number of requests per user
    :return: The user object
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    return user


@router.get("/refresh_token", response_model=Token)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Security(security),
    # token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
):
    """
    The refresh_token function is used to refresh the access token.
    The function will check if the user has a valid refresh token, and then return a new access token.


    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param # token: str: Get the token from the request header
    :param db: AsyncSession: Access the database
    :param rl: Limit the number of requests that can be made to this endpoint
    :return: A new access token, which is then used to authenticate the user and provide access to protected resources
    :doc-author: Trelent
    """
    token = credentials.credentials
    print(token)
    refresh_user_token = await auth.refresh_user_token(token, db)
    return refresh_user_token


@router.get("/mail")
async def send_mail(
    token: str = Depends(oauth2_scheme),
    # current_user: auth.DefaultUser,
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
):
    """
    The send_mail function sends an email to the user's email address.
    The function takes in a token, which is used to authenticate the user.
    It also takes in a database session and rate limit object as dependencies.

    :param token: str: Get the token from the header
    :param # current_user: auth.DefaultUser: Get the current user
    :param db: AsyncSession: Get the database session
    :param rl: Limit the number of requests a user can make
    :return: A status message
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    if user:
        subject = "Test mail"
        message = "This is a test mail"
        to_email = "yehvz@mailto.plus"
        emails.send_email(subject, message, to_email)
        return {"status": "message sent"}


@router.get("/activate")
async def activate_user(
    user_mail: str = Query(),
    otp: int = Query(),
    db: AsyncSession = Depends(get_db),
    rl=Depends(limit_allowed),
):
    """
    The activate_user function is used to activate a user account.
    It takes in the email of the user and an OTP (one time password) that was sent to their email address.
    If both are correct, it will return a success message.

    :param user_mail: str: Get the user's email address from the request body
    :param otp: int: Pass the otp to the activate_user function
    :param db: AsyncSession: Pass the database session to the function
    :param rl: Limit the number of requests per minute
    :return: A user object
    :doc-author: Trelent
    """
    user = await auth.activate_user(user_mail, otp, db)
    return user


# @router.post("/upload_image")
# async def upload(
#     token: str = Depends(oauth2_scheme),
#     file: UploadFile = File(...),
#     db: AsyncSession = Depends(get_db),
#     uploader=Depends(get_uploader),
#     rl=Depends(limit_allowed),
# ):
#     """
#     The upload function is used to upload a file.

#     :param token: str: Get the user's token
#     :param file: UploadFile: Get the file from the request
#     :param db: AsyncSession: Pass the database session to the function
#     :param uploader: Call the upload function from the uploader class
#     :param rl: Limit the number of uploads a user can make
#     :return: A dict with the image url and the id of the image
#     :doc-author: Trelent
#     """
#     image = await auth.set_user_image(token, file, db, uploader)
#     return image
