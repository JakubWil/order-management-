from fastapi import APIRouter, HTTPException, Depends
from app.database import supabase
from app.models import OrderCreate
from app.auth import get_current_user

router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

# POST /orders – złóż nowe zamówienie
@router.post("/")
def create_order(order: OrderCreate, current_user: dict = Depends(get_current_user)):
    # Krok 1 – sprawdź czy wszystkie produkty istnieją i pobierz ich ceny
    total_price = 0
    items_to_insert = []

    for item in order.items:
        # Pobieramy produkt z bazy żeby sprawdzić czy istnieje i jaka jest cena
        response = supabase.table("products").select("*").eq("id", item.product_id).execute()

        if not response.data:
            raise HTTPException(
                status_code=404,
                detail=f"Produkt o ID {item.product_id} nie istnieje"
            )

        product = response.data[0]

        # Sprawdzamy czy mamy wystarczający stan magazynowy
        if product["stock"] < item.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Niewystarczający stan magazynowy dla produktu {product['name']}. Dostępne: {product['stock']}"
            )

        # Obliczamy cenę tej pozycji i dodajemy do sumy
        item_price = product["price"] * item.quantity
        total_price += item_price

        items_to_insert.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "unit_price": product["price"]  # zapisujemy cenę z momentu zamówienia
        })

    # Krok 2 – utwórz rekord zamówienia
    # Używamy ID zalogowanego użytkownika z tokenu JWT
    order_response = supabase.table("orders").insert({
        "user_id": current_user["id"],
        "status": "pending",
        "total_price": round(total_price, 2)
    }).execute()

    new_order = order_response.data[0]

    # Krok 3 – dodaj ID zamówienia do każdej pozycji i zapisz je
    for item in items_to_insert:
        item["order_id"] = new_order["id"]

    supabase.table("order_items").insert(items_to_insert).execute()

    # Krok 4 – zaktualizuj stan magazynowy produktów
    for item in order.items:
        product = supabase.table("products").select("stock").eq("id", item.product_id).execute().data[0]
        new_stock = product["stock"] - item.quantity
        supabase.table("products").update({"stock": new_stock}).eq("id", item.product_id).execute()

    return {
        "order": new_order,
        "items": items_to_insert
    }

# GET /orders – pobierz wszystkie zamówienia zalogowanego użytkownika
@router.get("/")
def get_orders(current_user: dict = Depends(get_current_user)):
    # Każdy użytkownik widzi tylko swoje zamówienia
    response = supabase.table("orders").select("*").eq("user_id", current_user["id"]).execute()
    return response.data

# GET /orders/{id} – pobierz szczegóły jednego zamówienia
@router.get("/{order_id}")
def get_order(order_id: str, current_user: dict = Depends(get_current_user)):
    # Pobieramy zamówienie
    order_response = supabase.table("orders").select("*").eq("id", order_id).execute()

    if not order_response.data:
        raise HTTPException(status_code=404, detail="Zamówienie nie istnieje")

    order = order_response.data[0]

    # Sprawdzamy czy zamówienie należy do zalogowanego użytkownika
    # Użytkownik nie może podejrzeć zamówień innych użytkowników
    if order["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Brak dostępu do tego zamówienia")

    # Pobieramy pozycje zamówienia
    items_response = supabase.table("order_items").select("*").eq("order_id", order_id).execute()

    return {
        "order": order,
        "items": items_response.data
    }

# PATCH /orders/{id}/status – zmień status zamówienia (tylko dla admina w przyszłości)
@router.patch("/{order_id}/status")
def update_order_status(order_id: str, status: str, current_user: dict = Depends(get_current_user)):
    # Dozwolone statusy zamówienia
    allowed_statuses = ["pending", "confirmed", "shipped", "delivered", "cancelled"]

    if status not in allowed_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"Nieprawidłowy status. Dozwolone: {', '.join(allowed_statuses)}"
        )

    response = supabase.table("orders").update({"status": status}).eq("id", order_id).execute()

    if not response.data:
        raise HTTPException(status_code=404, detail="Zamówienie nie istnieje")

    return response.data[0]