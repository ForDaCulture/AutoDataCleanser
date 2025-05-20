from db.supabase_client import supabase

def on_startup():
    # Optionally test Supabase connection
    try:
        supabase.table("audit_logs").select("*").limit(1).execute()
        print("Supabase connection OK")
    except Exception as e:
        print(f"Supabase connection failed: {e}") 