from fastapi import APIRouter, HTTPException, Depends, status, Path, Query
from fastapi_limiter.depends import RateLimiter
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.repository import contacts as repository_contacts
from src.schemas.contact import ContactSchema, ContactUpdate, ContactResponse
from src.services.auth import auth_service

router = APIRouter(prefix='/contacts', tags=['contacts'])


@router.get('/', response_model=list[ContactResponse], dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contacts(limit: int = Query(10, ge=10, le=100), offset: int = Query(0, ge=0),
                       name: str = Query(None, title="Name filter"), surname: str = Query(None, title="Surname filter"),
                       email: str = Query(None, title="Email filter"), db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_contacts(limit, offset, name, surname, email, db, current_user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail="Contacts not found")


@router.get('/{contacts_id}', response_model=ContactResponse, dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.get_contact(contacts_id, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.post('/', response_model=ContactResponse, status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def create_contact(body: ContactSchema, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.create_contact(body, db, current_user)
    return contact


@router.put('/{contacts_id}', response_model=ContactResponse, status_code=status.HTTP_200_OK,
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def update_contact(contacts_id: int, body: ContactUpdate, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.update_contact(contacts_id, body, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.delete('/{contacts_id}', status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def delete_contact(contacts_id: int, db: AsyncSession = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    contact = await repository_contacts.delete_contact(contacts_id, db, current_user)
    if contact:
        return contact
    else:
        raise HTTPException(status_code=404, detail="Contact not found")


@router.get("/birthday/", response_model=list[ContactResponse],
            dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def get_upcoming_birthdays(db: AsyncSession = Depends(get_db),
                                 current_user: User = Depends(auth_service.get_current_user)):
    contacts = await repository_contacts.get_upcoming_birthdays(db, current_user)
    if contacts:
        return contacts
    else:
        raise HTTPException(status_code=404, detail="Contacts not found")
