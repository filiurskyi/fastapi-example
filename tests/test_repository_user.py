import datetime
import unittest
from unittest.mock import MagicMock, patch, AsyncMock

from entity.models import Contact, User
from repository.user import (
    find_user,
    get_user,
    create_user,
    edit_user,
    delete_user,
    set_image,
    update_otp,
    user_activation,

)
from schemas.user import UserCreateSchema, UserViewSchema
from sqlalchemy.ext.asyncio import AsyncSession

class TestUser(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.session = MagicMock(
            spec=AsyncSession
        )
        self.user = User(
            email="jane@example.com",
            passwd="password",
            image="some_url"
        )

    async def test_find_user(self):
        user = self.user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mock_result
        result = await find_user(email="str", db=self.session)
        self.assertEqual(result, user)

    async def test_get_user(self):
        user = self.user
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = user
        self.session.execute.return_value = mock_result
        result = await get_user(user_id=1, db=self.session)
        self.assertEqual(result, user)


    async def test_create_user(self):
        user_data = {
            "email": "jane@example.com",
            "passwd": "password",
            "salt": "password",
        }
        # Mock the AsyncSession
        session = MagicMock()
        async_session = AsyncMock()

        with patch.object(async_session, 'add'), patch.object(async_session, 'commit'), patch.object(async_session,
                                                                                               'refresh'):
            result = await create_user(body=user_data, db=async_session)

            self.assertEqual(result.email, user_data['email'])
            self.assertEqual(result.passwd, user_data['passwd'])
            self.assertEqual(result.salt, user_data['salt'])

    async def test_update_otp(self):
        async_session = AsyncMock()

        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session, 'refresh'),
        ):
            result = await update_otp(user=self.user, db=async_session, otp=12345)

            self.assertEqual(result, 12345)

    async def test_user_activation(self):
        async_session = AsyncMock()

        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session, 'refresh'),
        ):
            result = await user_activation(user=self.user, db=async_session, is_active=True)

            self.assertEqual(result, None)

    async def test_edit_user(self):
        user_data = {
            "email": "jane@example.com",
            "passwd": "password",
        }
        async_session = AsyncMock()
        body = UserCreateSchema(**user_data)
        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session,'refresh'),
            patch("repository.user.get_user", return_value=self.user)

        ):
            result = await edit_user(user_id=1, body=body, db=async_session)

            self.assertEqual(result.email, user_data['email'])
            self.assertEqual(result.passwd, user_data['passwd'])


    async def test_delete_user(self):
        user_data = {
            "email": "jane@example.com",
            "passwd": "password",
        }
        async_session = AsyncMock()
        body = UserCreateSchema(**user_data)
        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session,'refresh'),
            patch("repository.user.get_user", return_value=self.user)

        ):
            result = await delete_user(user_id=1, db=async_session)

            self.assertEqual(result.email, self.user.email)
            self.assertEqual(result.passwd, self.user.passwd)

    async def test_set_image(self):
        async_session = AsyncMock()

        with (
            patch.object(async_session, 'commit'),
            patch.object(async_session, 'refresh'),
        ):
            result = await set_image(user=self.user, db=async_session, url="some_url")

            self.assertEqual(result.image, self.user.image)



if __name__ == '__main__':
    unittest.main()
