from pydantic import BaseModel


class Provenance(BaseModel):
    creator: str
    version: str = None
    routine: str = None

    class Config:
        allow_extra = True
