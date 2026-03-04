# BaseModel to klasa która pozwala na definiowanie modeli danych w Pydantic, 
# sprawdza czy dane są poprawne i zwraca błędy jeśli nie.
# jesli ktos przsle 'sto zlotych' to Pydantic zwróci błąd.

from pydantic import BaseModel 
from typing import Optional # Optional to typ danych który może być None, czyli nie jest wymagany.

# Model do tworzenia produktu
# To jest kształt danych który musi przyjść w zapytaniu
class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None  # Optional znaczy że pole nie jest wymagane
    price: float
    stock: int

# Model do aktualizacji produktu
# Wszystkie pola Optional bo możemy aktualizować tylko część
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    stock: Optional[int] = None
