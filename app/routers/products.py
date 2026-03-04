#standardowy sposób zwracania błędów w FastAPI
from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import ProductCreate, ProductUpdate

# APIRouter to mini-aplikacja która potem podłączamy do głównej
# prefix znaczy że wszystkie endpointy zaczynają się od /products
# tags to tylko etykieta w dokumentacji
router = APIRouter(
    prefix="/products",
    tags=["products"]
)

# GET /products – pobierz wszystkie produkty
@router.get("/")
def get_products():
    response = supabase.table("products").select("*").execute()
    return response.data

# GET /products/{id} – pobierz jeden produkt po ID
@router.get("/{product_id}")
def get_product(product_id: str):
    response = supabase.table("products").select("*").eq("id", product_id).execute()
    
    # .eq("id", product_id) znaczy WHERE id = product_id
    # Jeśli lista jest pusta to produkt nie istnieje
    if not response.data:
        raise HTTPException(status_code=404, detail="Produkt nie istnieje")
    
    return response.data[0]  # zwracamy pierwszy (i jedyny) wynik

# POST /products – stwórz nowy produkt
@router.post("/")
def create_product(product: ProductCreate):
    # .dict() zamienia model Pydantic na słownik który Supabase rozumie
    response = supabase.table("products").insert(product.dict()).execute()
    return response.data[0]

# PATCH /products/{id} – zaktualizuj produkt
@router.patch("/{product_id}")
def update_product(product_id: str, product: ProductUpdate):
    # exclude_none=True znaczy "nie wysyłaj pól które są None"
    # dzięki temu możemy aktualizować tylko wybrane pola
    data = product.dict(exclude_none=True)
    
    if not data:
        raise HTTPException(status_code=400, detail="Brak danych do aktualizacji")
    
    response = supabase.table("products").update(data).eq("id", product_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Produkt nie istnieje")
    
    return response.data[0]

# DELETE /products/{id} – usuń produkt
@router.delete("/{product_id}")
def delete_product(product_id: str):
    response = supabase.table("products").delete().eq("id", product_id).execute()
    
    if not response.data:
        raise HTTPException(status_code=404, detail="Produkt nie istnieje")
    
    return {"message": "Produkt usunięty"}
