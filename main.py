import re
from typing import Callable

import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.routes import contacts, auth, users
from src.conf.config import config

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_agent_ban_list = [r"Googlebot", r"Python-urllib"]

app.include_router(auth.router, prefix='/api')
app.include_router(contacts.router, prefix='/api')
app.include_router(users.router, prefix='/api')


@app.middleware("http")
async def user_agent_ban_middleware(request: Request, call_next: Callable):
    """
    Middleware to check the user-agent header for banned patterns.

    Args:
        request (Request): The incoming HTTP request.
        call_next (Callable): The function to call to proceed with the request.

    Returns:
        JSONResponse: If a banned user-agent pattern is detected, returns a 403 Forbidden response.
                      Otherwise, proceeds with the request.

    Note:
        This middleware checks the user-agent header against a list of banned patterns.
        If a match is found, it returns a 403 Forbidden response; otherwise, it allows the request to proceed.
    """
    user_agent = request.headers.get("user-agent")
    for ban_pattern in user_agent_ban_list:
        if re.search(ban_pattern, user_agent):
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "You are banned"},
            )
    response = await call_next(request)
    return response


@app.on_event("startup")
async def startup():
    """
    Event handler for application startup.

    Note:
        This function initializes the Redis connection and sets up the FastAPILimiter.
    """
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, encoding="utf-8",
                          password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get("/")
def index():
    """
    Endpoint for testing purposes.

    Returns:
        dict: A simple message indicating the success of the endpoint.
    """
    return {"message": "Test"}


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
   Endpoint to check the health of the application and database connection.

   Args:
       db (AsyncSession): The asynchronous database session.

   Returns:
       dict: A message indicating the health status of the application and database.

   Raises:
       HTTPException: If an error occurs while connecting to the database, a 500 Internal Server Error is raised.
   """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
