import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, AsyncMock, Mock

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import User, Contact
from src.repository.contacts import get_contacts, get_contact, create_contact, update_contact, delete_contact, \
    get_upcoming_birthdays
from src.schemas.contact import ContactSchema, ContactUpdate


class TestAsyncContact(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.user = User(id=1, username='test_user', password="qwerty", confirmed=True)
        self.session = AsyncMock(spec=AsyncSession)

    async def test_get_contacts(self):
        limit = 10
        offset = 0
        name = 'John'
        contacts = [Contact(id=1, name='John'), Contact(id=2, name='Sava')]
        mocked_contacts = MagicMock()
        mocked_contacts.scalars.return_value.all.return_value = contacts
        self.session.execute.return_value = mocked_contacts

        result = await get_contacts(limit, offset, None, None, None, self.session, self.user)
        self.assertEqual(result, contacts)

        result = await get_contacts(limit, offset, name, None, None, self.session, self.user)
        self.assertEqual(result, contacts)

        self.session.execute.assert_called()

    async def test_get_contact(self):
        contact_id = 1
        contact = Contact(id=1, name="John")

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact

        self.session.execute.return_value = mock_result

        result = await get_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)
        self.session.execute.assert_called_once()

    async def test_create_contact(self):
        contact_data = ContactSchema(name="John", surname="Doe", email="john.doe@example.com", phone="1234567890",
                                     birthday=date(1990, 1, 1))
        new_contact = Contact(**contact_data.model_dump(), user_id=self.user.id)

        self.session.add = Mock()
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await create_contact(contact_data, self.session, self.user)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_update_contact(self):
        contact_id = 1
        contact_update = ContactUpdate(name="John", surname="Doe", email="john.doe@example.com", phone="1234567890",
                                       birthday=date(1990, 1, 1))
        existing_contact = Contact(id=1, name="Joe", surname="Eod", email="joe.email@example.com",
                                   phone="0987654321", birthday=date(1989, 12, 31), user_id=self.user.id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = existing_contact

        self.session.execute.return_value = mock_result
        self.session.commit = AsyncMock()
        self.session.refresh = AsyncMock()

        result = await update_contact(contact_id, contact_update, self.session, self.user)

        for key, value in contact_update.model_dump().items():
            self.assertEqual(getattr(existing_contact, key), value)

        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once_with(existing_contact)

    async def test_delete_contact(self):
        contact_id = 1
        contact = Contact(id=1, user_id=self.user.id)

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = contact

        self.session.execute.return_value = mock_result
        self.session.delete = AsyncMock()
        self.session.commit = AsyncMock()

        result = await delete_contact(contact_id, self.session, self.user)
        self.assertEqual(result, contact)
        self.session.delete.assert_called_once_with(contact)
        self.session.commit.assert_called_once()

    async def test_get_upcoming_birthdays(self):
        upcoming_birthdays = [Contact(birthday=date.today() + timedelta(days=3)),
                              Contact(birthday=date.today() + timedelta(days=5))]

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = upcoming_birthdays

        self.session.execute.return_value = mock_result

        result = await get_upcoming_birthdays(self.session, self.user)
        self.assertEqual(result, upcoming_birthdays)
        self.session.execute.assert_called_once()
