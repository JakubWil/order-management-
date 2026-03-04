from supabase import create_client, Client # Importujemy create_client tworzy polaczenie i Client z biblioteki supabase.
from app.config import SUPABASE_URL, SUPABASE_KEY

# Tworzymy polaczenie z bazą danych raz globalnie aby nie musiec tworzyc nowego polaczenia za kazdym razem.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_orders():
    response = supabase.table("orders").select("*").execute()
    return response.data