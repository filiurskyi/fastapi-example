from conf.db import get_db
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, contact
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(contact.router)
app.include_router(auth.router)


@app.get("/api/healthchecker")
def healthchecker():
    """
    Check if the application is running correctly

    :return: A message indicating if the application is running correctly
    """
    return {"message": "Welcome to FastAPI!"}


@app.get("/api/dbhealthchecker")
async def dbhealthchecker(db: AsyncSession = Depends(get_db)):
    """
    Check if the database is configured correctly

    :param db: AsyncSession: The database to check against
    :return: A message indicating if the database is configured correctly
    """
    try:
        result = await db.execute(text("SELECT 1"))
        if result.fetchone() is None:
            raise HTTPException(
                status_code=500, detail="Database is not configured correctly"
            )
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")
