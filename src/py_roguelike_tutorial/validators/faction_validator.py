from pydantic import BaseModel


class FactionData(BaseModel):
    name: str


class FactionsData(BaseModel):
    factions: dict[str, FactionData]
