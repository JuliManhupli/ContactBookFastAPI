from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactSchema, ContactUpdate, ContactResponse
from src.services.auth import auth_service
from src.conf import messages

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse])
async def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                       name: str = Query(None, title="Name filter"), surname: str = Query(None, title="Surname filter"),
                       email: str = Query(None, title="Email filter"), db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
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
        List[ContactResponse]: A list of contacts that match the specified criteria.

    Raises:
        HTTPException: If no matching contacts are found, a 404 Not Found response is raised.

    Note:
        The endpoint performs an asynchronous database query to retrieve contacts based on the provided parameters.
        It filters contacts by name, surname, and email if corresponding parameters are provided. If contacts are
        found, they are returned; otherwise, a 404 Not Found response is raised.
    """
    contacts = await repository_contacts.get_contacts(limit, offset, name, surname, email, db, current_user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail=messages.CONTACTS_NOT_FOUND)


@router.get('/{contacts_id}', response_model=ContactResponse)
async def get_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve a single contact by its unique identifier for the given user.

    Args:
        contacts_id (int): The unique identifier of the contact to retrieve.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user for whom the contact is being retrieved.

    Returns:
        ContactResponse: The details of the retrieved contact.

    Raises:
        HTTPException: If no matching contact is found, a 404 Not Found response is raised.

    Note:
        The endpoint performs an asynchronous database query to retrieve a contact based on its unique identifier
        and the associated user. If a matching contact is found, its details are returned; otherwise, a 404
        Not Found response is raised.
    """
    contact = await repository_contacts.get_contact(contacts_id, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail=messages.CONTACT_NOT_FOUND)


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Create a new contact for the given user using the provided contact data.

    Args:
        body (ContactSchema): The contact data used for creating the new contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is creating the contact.

    Returns:
        ContactResponse: The details of the newly created contact.

    Note:
        The endpoint performs an asynchronous database transaction to create a new contact with the provided data.
        It sets the contact's user to the current user, commits the transaction, refreshes the contact to get
        updated database state, and then returns the newly created contact.
    """
    contact = await repository_contacts.create_contact(body, db, current_user)
    return contact


@router.put('/{contacts_id}', response_model=ContactResponse, status_code=status.HTTP_200_OK)
async def update_contact(contacts_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Update an existing contact for the given user with the provided contact data.

    Args:
        contacts_id (int): The unique identifier of the contact to be updated.
        body (ContactUpdate): The contact data used for updating the existing contact.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is updating the contact.

    Returns:
        ContactResponse: The details of the updated contact.

    Raises:
        HTTPException: If no matching contact is found, a 404 Not Found response is raised.

    Note:
        The endpoint performs an asynchronous database query to retrieve the existing contact based on its unique
        identifier and the associated user. If a matching contact is found, it updates the contact's attributes
        with the provided data, commits the transaction, refreshes the contact to get updated database state, and
        then returns the updated contact. If no matching contact is found, a 404 Not Found response is raised.
    """
    contact = await repository_contacts.update_contact(contacts_id, body, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail=messages.CONTACT_NOT_FOUND)


@router.delete('/{contacts_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    """
    Delete an existing contact for the given user based on its unique identifier.

    Args:
        contacts_id (int): The unique identifier of the contact to be deleted.
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user who is deleting the contact.

    Returns:
        None

    Raises:
        HTTPException: If no matching contact is found, a 404 Not Found response is raised.

    Note:
        The endpoint performs an asynchronous database query to retrieve the existing contact based on its unique
        identifier and the associated user. If a matching contact is found, it is deleted, the transaction is
        committed, and a 204 No Content response is returned. If no matching contact is found, a 404 Not Found
        response is raised.
    """
    contact = await repository_contacts.delete_contact(contacts_id, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail=messages.CONTACT_NOT_FOUND)


@router.get("/birthday/", response_model=list[ContactResponse])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    """
    Retrieve contacts with upcoming birthdays for the given user within the next 7 days.

    Args:
        db (AsyncSession): The asynchronous database session.
        current_user (User): The current user for whom contacts with upcoming birthdays are being retrieved.

    Returns:
        List[ContactResponse]: A list of contacts with birthdays falling within the next 7 days.

    Raises:
        HTTPException: If no matching contacts are found, a 404 Not Found response is raised.

    Note:
        The endpoint performs an asynchronous database query to retrieve contacts whose birthdays fall within
        the next 7 days for the specified user. If contacts are found, they are returned; otherwise, a 404
        Not Found response is raised.
    """
    contacts = await repository_contacts.get_upcoming_birthdays(db, current_user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail=messages.CONTACTS_NOT_FOUND)
