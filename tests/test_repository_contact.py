import datetime
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from entity.models import Contact, User
from repository.contact import (
    get_contacts,
    get_contact,
    create_contact,
    edit_contact,
    delete_contact,
    get_contact_by_name,
    get_contact_by_mail,
    get_birthday_list
)
from schemas.contact import ContactCreateSchema, ContactEditSchema
from sqlalchemy.ext.asyncio import AsyncSession


class TestContact(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(
            spec=AsyncSession
        )
        self.user = User(
            # email="test@ex.com",
            # passwd="1234qwerty",
            # salt="123qwerty",
            # is_active=True,
            # created_at=datetime.datetime.now(),
            # modified_at=datetime.datetime.now()
        )
        self.contact = Contact(
            id=1
            # first_name = "John",
            # last_name = "Doe",
            # email="test@ex.com",
            # birth_date = datetime.datetime.today(),
            # created_at=datetime.datetime.now(),
            # modified_at=datetime.datetime.now()
        )

    async def test_get_contacts(self):
        contacts = [self.contact]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_result
        result = await get_contacts(offset=0, limit=10, user_id=1, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact(self):
        contact = self.contact
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact
        self.session.execute.return_value = mock_result
        result = await get_contact(contact_id=1, user_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_create_contact(self):
        user_id = 1
        contact_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "birth_date": datetime.date.today(),
        }
        body = ContactCreateSchema(**contact_data)

        # Mock the AsyncSession
        session = MagicMock()
        async_session = AsyncMock()

        with patch.object(async_session, 'add'), patch.object(async_session, 'commit'), patch.object(async_session,
                                                                                               'refresh'):
            result = await create_contact(body=body, db=async_session, user_id=user_id)

            self.assertEqual(result.first_name, contact_data['first_name'])
            self.assertEqual(result.last_name, contact_data['last_name'])
            self.assertEqual(result.email, contact_data['email'])
            self.assertEqual(result.created_by, user_id)

    async def test_edit_contact(self):
        user_id = 1
        contact_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
            "birth_date": None,
        }
        body = ContactEditSchema(**contact_data)

        # Mock the AsyncSession
        session = MagicMock()
        async_session = AsyncMock()

        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session, 'refresh'),
            patch("repository.contact.get_contact", return_value=self.contact)
        ):
            result = await edit_contact(contact_id=1, body=body, db=async_session, user_id=user_id)

            self.assertEqual(result.first_name, contact_data['first_name'])
            self.assertEqual(result.last_name, contact_data['last_name'])
            self.assertEqual(result.email, contact_data['email'])

    async def test_delete_contact(self):
        async_session = AsyncMock()

        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session, 'refresh'),
            patch("repository.contact.get_contact", return_value=self.contact)
        ):
            result = await delete_contact(contact_id=1, db=async_session, user_id=1)
            self.assertEqual(result.id, 1)

    async def test_get_contact_by_name(self):
        contact = self.contact
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contact
        self.session.execute.return_value = mock_result
        result = await get_contact_by_name(name_query="str", user_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_by_mail(self):
        contact = self.contact
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contact
        self.session.execute.return_value = mock_result
        result = await get_contact_by_mail(mail_query="str", user_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_birthday_list(self):
        contacts = [self.contact]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mock_result
        result = await get_birthday_list(user_id=1, db=self.session)
        self.assertEqual(result, contacts)


if __name__ == '__main__':
    unittest.main()
