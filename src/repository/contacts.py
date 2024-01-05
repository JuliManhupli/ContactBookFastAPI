from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import or_, and_, extract, cast, Date

from src.entity.models import Contact, User
from src.schemas.contact import ContactSchema, ContactUpdate


async def get_contacts(limit: int, offset: int, name: str | None, surname: str | None, email: str | None,
                       db: AsyncSession, current_user: User):
    """
    Retrieve a list of contacts based on specified criteria.

    Args:
        limit (int): The maximum number of contacts to retrieve.
        offset (int): The number of contacts to skip before starting to return results.
        name (str): Filter contacts by name (case-insensitive) using a substring match.
        surname (str): Filter contacts by surname (case-insensitive) using a substring match.
        email (str): Filter contacts by email (case-insensitive) using a substring match.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user for whom contacts are being retrieved.

    Returns:
        List[Contact]: A list of contacts that match the specified criteria.

    Note:
        The function performs an asynchronous database query to retrieve contacts based on the provided parameters.
        It filters contacts by name, surname, and email if corresponding parameters are provided.
    """
    statement = select(Contact).filter_by(user=current_user).offset(offset).limit(limit)
    if name:
        statement = statement.filter(Contact.name.ilike(f"%{name}%"))
    if surname:
        statement = statement.filter(Contact.surname.ilike(f"%{surname}%"))
    if email:
        statement = statement.filter(Contact.email.ilike(f"%{email}%"))

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()


async def get_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    Retrieve a single contact by its unique identifier for the given user.

    Args:
        contact_id (int): The unique identifier of the contact to retrieve.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user for whom the contact is being retrieved.

    Returns:
        Contact or None: The retrieved contact if found, or None if no matching contact is found.

    Note:
        The function performs an asynchronous database query to retrieve a contact based on its unique identifier
        and the associated user. If a matching contact is found, it is returned; otherwise, None is returned.
    """
    statement = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(statement)
    await db.close()
    return contact.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, current_user: User):
    """
    Create a new contact for the given user using the provided contact data.

    Args:
        body (ContactSchema): The contact data used for creating the new contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is creating the contact.

    Returns:
        Contact: The newly created contact.

    Raises:
        HTTPException: If an error occurs during the database transaction, a 500 Internal Server Error
        with details of the error is raised.

    Note:
        The function performs an asynchronous database transaction to create a new contact with the provided data.
        It sets the contact's user to the current user, commits the transaction, refreshes the contact to get
        updated database state, and then returns the newly created contact.

    """
    try:
        contact = Contact(**body.model_dump(), user=current_user)
        db.add(contact)
        await db.commit()
        await db.refresh(contact)
        return contact
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await db.close()


async def update_contact(contact_id: int, contact: ContactUpdate, db: AsyncSession, current_user: User):
    """
    Update an existing contact for the given user with the provided contact data.

    Args:
        contact_id (int): The unique identifier of the contact to be updated.
        contact (ContactUpdate): The contact data used for updating the existing contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is updating the contact.

    Returns:
        Contact or None: The updated contact if found, or None if no matching contact is found.

    Note:
        The function performs an asynchronous database query to retrieve the existing contact based on its unique
        identifier and the associated user. If a matching contact is found, it updates the contact's attributes
        with the provided data, commits the transaction, refreshes the contact to get updated database state,
        and then returns the updated contact. If no matching contact is found, None is returned.
    """
    statement = select(Contact).filter_by(id=contact_id, user=current_user)
    existing_contact = await db.execute(statement)
    existing_contact = existing_contact.scalar_one_or_none()
    if existing_contact:
        for key, value in contact.model_dump().items():
            setattr(existing_contact, key, value)
        await db.commit()
        await db.refresh(existing_contact)
        await db.close()
    return existing_contact


async def delete_contact(contact_id: int, db: AsyncSession, current_user: User):
    """
    Delete an existing contact for the given user based on its unique identifier.

    Args:
        contact_id (int): The unique identifier of the contact to be deleted.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is deleting the contact.

    Returns:
        Contact or None: The deleted contact if found, or None if no matching contact is found.

    Note:
        The function performs an asynchronous database query to retrieve the existing contact based on its unique
        identifier and the associated user. If a matching contact is found, it is deleted, the transaction is
        committed, and the deleted contact is returned. If no matching contact is found, None is returned.
    """
    statement = select(Contact).filter_by(id=contact_id, user=current_user)
    contact = await db.execute(statement)
    contact = contact.scalar_one_or_none()
    if contact:
        await db.delete(contact)
        await db.commit()
        return contact


async def get_upcoming_birthdays(db: AsyncSession, current_user: User):
    """
    Retrieve contacts with upcoming birthdays for the given user within the next 7 days.

    Args:
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user for whom contacts with upcoming birthdays are being retrieved.

    Returns:
        List[Contact]: A list of contacts with birthdays falling within the next 7 days.

    Note:
        The function performs an asynchronous database query to retrieve contacts whose birthdays fall within
        the next 7 days for the specified user. It filters contacts based on their birthday month and day,
        considering both today and the date 7 days from today. The result is a list of contacts with upcoming
        birthdays.
    """
    today = date.today()
    next_week = today + timedelta(days=7)

    statement = select(Contact).filter(
        or_(
            and_(
                extract('month', cast(Contact.birthday, Date)) == extract('month', cast(today, Date)),
                extract('day', cast(Contact.birthday, Date)) >= extract('day', cast(today, Date))
            ),
            and_(
                extract('month', cast(Contact.birthday, Date)) == extract('month', cast(next_week, Date)),
                extract('day', cast(Contact.birthday, Date)) <= extract('day', cast(next_week, Date))
            )
        )
    ).filter_by(user=current_user)

    contacts = await db.execute(statement)
    await db.close()
    return contacts.scalars().all()
