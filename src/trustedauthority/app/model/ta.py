from pydantic import BaseModel


class TrustedAuthority(BaseModel):
    name: str
    description: str
