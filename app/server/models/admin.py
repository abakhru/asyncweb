from pydantic import BaseModel, EmailStr, Field


class AdminModel(BaseModel):
    fullname: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)


    class Config:
        schema_extra = {"example": {"fullname": "Amit Bakhru",
                                    "email": "bakhru@me.com",
                                    "password": "abc123"}
                        }
