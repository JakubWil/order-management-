from fastapi import FastAPI

# Tworzysz instancję aplikacji FastAPI
# Powstaje obiekt app, którego używa serwer (np. uvicorn main:app) do uruchomienia API.
app = FastAPI(
    title="Order Management API",
    version="1.0.0",
)

# Mówisz FastAPI: „Dla żądania HTTP GET na ścieżce / wywołaj tę funkcję def root():”.
@app.get("/")
def root():
    return {"message": "Order Management API działa!"}