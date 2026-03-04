from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import UserRegister, Token
from app.auth import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

@router.post("/register")
def register(user: UserRegister):
    # Sprawdzamy czy email już istnieje w bazie
    existing = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if existing.data:
        raise HTTPException(status_code=400, detail="Email już zajęty")
    
    # Hashujemy hasło przed zapisem do bazy
    hashed = hash_password(user.password)
    
    response = supabase.table("users").insert({
        "email": user.email,
        "hashed_password": hashed
    }).execute()
    
    return {"message": "Konto utworzone pomyślnie"}

@router.post("/login", response_model=Token)
def login(user: UserRegister):
    # Szukamy użytkownika po emailu
    response = supabase.table("users").select("*").eq("email", user.email).execute()
    
    if not response.data:
        raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")
    
    db_user = response.data[0]
    
    # Weryfikujemy hasło
    if not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Nieprawidłowy email lub hasło")
    
    # Tworzymy token – "sub" to standardowe pole JWT dla identyfikatora użytkownika
    token = create_access_token({"sub": db_user["id"]})
    
    return {"access_token": token, "token_type": "bearer"}