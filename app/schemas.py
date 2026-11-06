from pydantic import BaseModel
from typing import Dict, Any

class ProductInput(BaseModel):
    name: str
    manufacturer: str
    specs: Dict[str, Any]
    description: str