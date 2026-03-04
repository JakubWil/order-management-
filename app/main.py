from fastapi import FastAPI
from app.routers import products

# Tworzysz instancję aplikacji FastAPI
# Powstaje obiekt app, którego używa serwer (np. uvicorn main:app) do uruchomienia API.
app = FastAPI(
    title="Order Management API",
    version="1.0.0",
)


# Podłączamy router – teraz wszystkie endpointy z products.py są aktywne
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Order Management API działa!"}

# # Mówisz FastAPI: „Dla żądania HTTP GET na ścieżce / wywołaj tę funkcję def root():”.
# @app.get("/")
# def root():
#     return {"message": "Order Management API działa!"}

# # Testujemy połączenie z bazą danych, wczesniej w supabase utworzyłem tabelę products.
# @app.get("/test-db")
# def test_db():
#     response = supabase.table("products").select("*").execute()
#     return {'products': response.data}