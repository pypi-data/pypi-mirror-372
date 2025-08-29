from supabase import create_client, Client

url: str = "https://asthdsbkrjpthvhlxdsh.supabase.co"
key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFzdGhkc2JrcmpwdGh2aGx4ZHNoIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1NTYwODE3MSwiZXhwIjoyMDcxMTg0MTcxfQ.hqoKvUNMgn3L-i401wZ6RIOIwBQlQtQiIevnvH8Ocog"

supabase: Client = create_client(url, key)

def print_success():
    print("Connected to Supabase!")
