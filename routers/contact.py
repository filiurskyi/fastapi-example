from typing import Annotated

import repository.contact as repo_contact
from conf.db import get_db
from fastapi import APIRouter, Depends, Query, status
from fastapi.security import OAuth2PasswordBearer
from schemas.contact import ContactCreateSchema, ContactEditSchema
from schemas.user import UserViewSchema
from service import auth
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/contact", tags=["contact"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get("/")
async def list_contacts(
    # request: Request,
    limit: int = Query(10, ge=10, le=500),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The list_contacts function returns a list of contacts for the user.
        The limit and offset parameters are used to paginate the results.


    :param # request: Request: Get the request object
    :param limit: int: Limit the number of contacts returned
    :param ge: Specify the minimum value of a parameter
    :param le: Limit the number of contacts returned to 500
    :param offset: int: Get the offset of the contacts to be returned
    :param ge: Set a minimum value for the limit parameter
    :param db: AsyncSession: Pass the database session to the function
    :param token: str: Get the user id from the token
    :return: A list of contacts
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    contacts = await repo_contact.get_contacts(limit, offset, db, user.id)
    return contacts


@router.get("/birthday")
async def birthday_list(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The birthday_list function returns a list of contacts with birthdays in the current month.


    :param db: AsyncSession: Get the database connection
    :param token: str: Get the user id from the token
    :return: A list of contacts, but the schema for a contact is not defined
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    contacts = await repo_contact.get_birthday_list(db, user.id)
    return contacts


@router.get("/{id_}")
async def get_contact(
    id_: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The get_contact function returns a contact by id.
        If the contact does not exist, it will return an HTTP 303 See Other status code.

    :param id_: int: Get the contact id
    :param db: AsyncSession: Pass the database connection to the function
    :param token: str: Validate the token
    :return: A contact object, or status code if no contact is found
    :doc-author: Trelent
    """
    contact = await repo_contact.get_contact(id_, db)
    if contact is None:
        return status.HTTP_303_SEE_OTHER
    return contact


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_contact(
    body: ContactCreateSchema,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The add_contact function creates a new contact for the user.
        The function takes in a ContactCreateSchema object, which is validated by pydantic.
        It also takes in an optional database session and token string, which are used to authenticate the user.

    :param body: ContactCreateSchema: Validate the request body
    :param db: AsyncSession: Pass the database session to the function
    :param token: str: Get the user's token from the request header
    :return: A contact object
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    contact = await repo_contact.create_contact(body, db, user.id)
    return contact


@router.patch(
    "/{id_}/edit",
    response_model=ContactEditSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
async def edit_contact(
    id_: int,
    body: ContactEditSchema,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The edit_contact function allows a user to edit an existing contact.

    :param id_: int: Identify the contact to be edited
    :param body: ContactEditSchema: Validate the request body
    :param db: AsyncSession: Pass the database connection to the function
    :param token: str: Get the current user from the database
    :return: A contact object
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    contact = await repo_contact.edit_contact(id_, body, db, user.id)
    return contact


@router.delete("/{id_}/delete")
async def delete_contact(
    id_: int,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The delete_contact function deletes a contact from the database.

    :param id_: int: Get the id of the contact that is going to be deleted
    :param db: AsyncSession: Pass the database session to the function
    :param token: str: Get the token from the request header
    :return: The deleted contact
    :doc-author: Trelent
    """
    user = await auth.get_current_user(token, db)
    contact = await repo_contact.delete_contact(id_, db, user.id)
    return contact


@router.get("/search_name/{query}")
async def search_name(
    query: str | None = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The search_name function searches for contacts by name.

    :param query: str | None: Get the query parameter from the url
    :param db: AsyncSession: Get the database connection
    :param token: str: Get the current user from the database
    :return: A list of contacts
    :doc-author: Trelent
    """
    if query is None:
        return []

    user = await auth.get_current_user(token, db)
    contacts = await repo_contact.get_contact_by_name(query, db, user.id)
    return contacts


@router.get("/search_mail/{query}")
async def search_mail(
    query: str | None = None,
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
):
    """
    The search_mail function searches for contacts by email.

    :param query: str | None: Get the query string from the url
    :param db: AsyncSession: Get the database session
    :param token: str: Get the user id from the token
    :return: An array of contacts
    :doc-author: Trelent
    """
    if query is None:
        return []

    user = await auth.get_current_user(token, db)
    contacts = await repo_contact.get_contact_by_mail(query, db, user.id)
    return contacts
