# BaseModel to klasa która pozwala na definiowanie modeli danych w Pydantic, 
# sprawdza czy dane są poprawne i zwraca błędy jeśli nie.
# jesli ktos przsle 'sto zlotych' to Pydantic zwróci błąd.

from pydantic import BaseModel , validator
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



# Modele dla autoryzacji

class UserRegister(BaseModel):
    email: str
    password: str  # czyste hasło które przychodzi od użytkownika


    @validator("password")
    def password_length(cls, v):
        # Sprawdzamy długość hasła zanim trafi do bcrypt
        if len(v.encode("utf-8")) > 72:
            raise ValueError("Hasło nie może być dłuższe niż 72 znaki")
        if len(v) < 8:
            raise ValueError("Hasło musi mieć minimum 8 znaków")
        return v

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str  # zawsze "bearer" – to standard HTTP
