from datetime import datetime, timedelta, timezone, date

from entity.models import Contact
from schemas.contact import ContactCreateSchema, ContactEditSchema
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_contacts(limit: int, offset: int, db: AsyncSession, user_id: int):
    """
    The get_contacts function returns a list of contacts for the user.

    :param limit: int: Limit the number of contacts returned
    :param offset: int: Skip the first offset number of contacts
    :param db: AsyncSession: Pass in the database session
    :param user_id: int: Filter the contacts by user
    :return: A list of scalars
    :doc-author: Trelent
    """
    stmt = (
        select(Contact).where(Contact.created_by == user_id).offset(offset).limit(limit)
    )
    contacts = await db.execute(stmt)
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, user_id: int):
    """
    The get_contact function returns a contact object from the database.

    :param contact_id: int: Filter the results by contact id
    :param db: AsyncSession: Pass in the database session to use for querying
    :param user_id: int: Ensure that the user is only able to access contacts they have created
    :return: A contact object
    :doc-author: Trelent
    """
    stmt = select(Contact).where(Contact.created_by == user_id).filter_by(id=contact_id)
    contact = await db.execute(stmt)
    return contact.scalar_one_or_none()


async def create_contact(body: ContactCreateSchema, db: AsyncSession, user_id: int):
    """
    The create_contact function creates a new contact.

    :param body: ContactCreateSchema: Validate the request body
    :param db: AsyncSession: Access the database
    :param user_id: int: Set the created_by field in the contact table
    :return: A contact object, which is a mapped class
    :doc-author: Trelent
    """
    contact = Contact(
        # **body.model_dump(exclude_unset=True), # works too...
        **body.dict(),
    )
    setattr(contact, "created_by", user_id)
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def edit_contact(
    contact_id: int, body: ContactEditSchema, db: AsyncSession, user_id: int
):
    """
    The edit_contact function allows you to edit a contact.

    :param contact_id: int: Identify the contact to edit
    :param body: ContactEditSchema: Validate the request body
    :param db: AsyncSession: Create a database session
    :param user_id: int: Ensure that the user is only able to edit their own contacts
    :return: The contact object that was modified
    :doc-author: Trelent
    """
    contact = await get_contact(contact_id, db, user_id)
    for field, value in body:
        if value is not None:
            setattr(contact, field, value)

    setattr(contact, "modified_at", datetime.now(timezone.utc))
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete_contact(contact_id: int, db: AsyncSession, user_id: int):
    """
    The delete_contact function deletes a contact from the database.
        Args:
            contact_id (int): The id of the contact to delete.
            db (AsyncSession): An async session object for interacting with the database.
            user_id (int): The id of the user who owns this contact.

    :param contact_id: int: Specify which contact to delete
    :param db: AsyncSession: Pass in the database session
    :param user_id: int: Make sure that the user is only able to delete contacts they have created
    :return: The contact object that was deleted
    :doc-author: Trelent
    """
    contact = await get_contact(contact_id, db, user_id)
    await db.delete(contact)
    await db.commit()
    return contact


async def get_contact_by_name(name_query: str, db: AsyncSession, user_id: int):
    """
    The get_contact_by_name function returns a list of contacts that match the name query.

    :param name_query: str: Pass in the name of the contact we want to search for
    :param db: AsyncSession: Pass in the database connection to the function
    :param user_id: int: Filter the query to only return contacts created by that user
    :return: A list of dictionaries, where each dictionary is a row from the database
    :doc-author: Trelent
    """
    stmt = (
        select(Contact)
        .where(Contact.created_by == user_id)
        .where(
            or_(
                Contact.first_name.like(f"%{name_query}%"),
                Contact.last_name.like(f"%{name_query}%"),
            )
        )
    )
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def get_contact_by_mail(mail_query: str, db: AsyncSession, user_id: int):
    """
    The get_contact_by_mail function returns a list of contacts that match the mail_query string.
        The function takes in three arguments:
            - mail_query: A string containing the email address to search for.
            - db: An async database session object from SQLAlchemy.  This is used to execute queries against the database.
            - user_id: An integer representing which user created this contact.

    :param mail_query: str: Query the database for a contact with an email that contains the mail_query string
    :param db: AsyncSession: Pass the database session to the function
    :param user_id: int: Check if the user is allowed to access the contact
    :return: A list of contacts
    :doc-author: Trelent
    """
    stmt = (
        select(Contact)
        .where(Contact.created_by == user_id)
        .where(Contact.email.like(f"%{mail_query}%"))
    )
    contact = await db.execute(stmt)
    return contact.scalars().all()


async def get_birthday_list(db: AsyncSession, user_id: int):
    """
    The get_birthday_list function returns a list of contacts that have birthdays within the next 7 days.


    :param db: AsyncSession: Create a database session
    :param user_id: int: Specify the user_id of the person who created the contact
    :return: A list of contacts who have birthdays in the next 7 days
    :doc-author: Trelent
    """
    horizon = timedelta(days=7)

    stmt = (
        select(Contact)
        .where(Contact.created_by == user_id)
        .where(
            Contact.birth_date.between(
                date.today(), date.today() + horizon
            )
        )
    )
    contact = await db.execute(stmt)
    return contact.scalars().all()
