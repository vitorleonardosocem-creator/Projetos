# models.py
from pydantic import BaseModel
from datetime import datetime

class Visitante(BaseModel):
    id: int
    nome: str
    empresa: str
    data: datetime

class CheckIn(BaseModel):
    id_visitante: int
    grupo_id: int
