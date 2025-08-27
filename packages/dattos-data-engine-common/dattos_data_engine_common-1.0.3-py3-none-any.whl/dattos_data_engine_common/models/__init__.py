from pydantic import BaseModel


class Column(BaseModel):
    name: str
    data_type: str
