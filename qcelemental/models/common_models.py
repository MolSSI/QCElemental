from pydantic import BaseModel


class Provenance(BaseModel):
    creator: str
    version: str = ""
    routine: str = ""

    class Config:
        allow_extra = True
