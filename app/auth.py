# python-jose – biblioteka do generowania i weryfikacji tokenów JWT
#passlib + bcrypt – do hashowania haseł. 
# Nigdy nie przechowujesz hasła w czystej formie w bazie – tylko jego hash


from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import supabase



# OAuth2PasswordBearer mówi FastAPI gdzie szukać tokenu w zapytaniu
# tokenUrl to endpoint gdzie użytkownik dostaje token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_password(password: str) -> str:
    # encode("utf-8") zamienia string na bajty których bcrypt wymaga
    # gensalt() generuje losowy "sól" który sprawia że ten sam hasło
    # daje różny hash za każdym razem – to dodatkowe zabezpieczenie
    password_bytes = password.encode("utf-8")
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    # decode("utf-8") z powrotem na string żeby zapisać w bazie jako tekst
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # checkpw porównuje hasło z hashem
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8")
    )

def create_access_token(data: dict) -> str:
    # Tworzymy kopię danych żeby nie modyfikować oryginału
    to_encode = data.copy()
    
    # Ustawiamy kiedy token wygasa
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    # Kodujemy token używając SECRET_KEY i algorytmu z .env
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Depends oznacza że FastAPI automatycznie wyciągnie token z nagłówka zapytania
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Nieprawidłowy token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Dekodujemy token i wyciągamy dane
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")  # "sub" to standardowe pole JWT dla ID użytkownika
        
        if user_id is None:
            raise credentials_exception
            
    except JWTError:
        raise credentials_exception
    
    # Sprawdzamy czy użytkownik nadal istnieje w bazie
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if not response.data:
        raise credentials_exception
        
    return response.data[0]