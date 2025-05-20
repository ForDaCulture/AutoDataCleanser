import os
from supabase import create_client, Client
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '../.env'))

# Get Supabase configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
SUPABASE_JWT_SECRET = os.getenv('SUPABASE_JWT_SECRET')

# Validate required environment variables
if not all([SUPABASE_URL, SUPABASE_SERVICE_KEY, SUPABASE_JWT_SECRET]):
    missing = []
    if not SUPABASE_URL:
        missing.append('SUPABASE_URL')
    if not SUPABASE_SERVICE_KEY:
        missing.append('SUPABASE_SERVICE_KEY')
    if not SUPABASE_JWT_SECRET:
        missing.append('SUPABASE_JWT_SECRET')
    raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Supabase client: {str(e)}")

def get_supabase_client() -> Client:
    """
    Get the Supabase client instance.
    Returns the initialized client or raises an error if not properly configured.
    """
    if not supabase:
        raise RuntimeError("Supabase client not initialized")
    return supabase

def validate_supabase_connection() -> bool:
    """
    Validate the Supabase connection by attempting a simple query.
    Returns True if connection is valid, False otherwise.
    """
    try:
        # Try to fetch a single row from cleaning_sessions
        supabase.table('cleaning_sessions').select('id').limit(1).execute()
        return True
    except Exception as e:
        print(f"Supabase connection validation failed: {str(e)}")
        return False 