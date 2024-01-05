from datetime import date, datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from src.schemas.user import UserResponse


class ContactSchema(BaseModel):
    """
    Schema representing the data structure for creating or updating a contact.

    Attributes:
        name (str): The name of the contact (up to 150 characters).
        surname (str): The surname of the contact (up to 150 characters).
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (date): The birthday of the contact.

    Note:
        This schema is used for validating and parsing input data when creating or updating contacts.
        It ensures that the provided data adheres to the specified format and constraints.
    """
    name: str = Field(max_length=150)
    surname: str = Field(max_length=150)
    email: EmailStr
    phone: str
    birthday: date


class ContactUpdate(BaseModel):
    """
    Schema representing the data structure for updating an existing contact.

    Attributes:
        name (str): The updated name of the contact.
        surname (str): The updated surname of the contact.
        email (EmailStr): The updated email address of the contact.
        phone (str): The updated phone number of the contact.
        birthday (date): The updated birthday of the contact.

    Note:
        This schema is used for validating and parsing input data when updating existing contacts.
        It ensures that the provided data adheres to the specified format and constraints.
    """
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date


class ContactResponse(BaseModel):
    """
    Schema representing the data structure for responding with details of a contact.

    Attributes:
        id (int): The unique identifier of the contact.
        name (str): The name of the contact.
        surname (str): The surname of the contact.
        email (EmailStr): The email address of the contact.
        phone (str): The phone number of the contact.
        birthday (date): The birthday of the contact.
        created_at (datetime | None): The timestamp indicating when the contact was created.
        updated_at (datetime | None): The timestamp indicating when the contact was last updated.
        user (UserResponse | None): Details of the user associated with the contact.

    Note:
        This schema is used for responding with details of a contact, including its attributes and related user details.
        The `Config` class attribute is set to `from_attributes = True` to allow attribute-based instantiation.
    """
    id: int = 1
    name: str
    surname: str
    email: EmailStr
    phone: str
    birthday: date
    created_at: datetime | None
    updated_at: datetime | None
    user: UserResponse | None
    model_config = ConfigDict(from_attributes=True) # noqa
