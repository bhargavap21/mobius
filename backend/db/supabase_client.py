"""
Supabase client configuration and initialization
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Validate configuration
if not SUPABASE_URL or not SUPABASE_KEY:
    logger.warning("⚠️  Supabase configuration missing. Please set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
    supabase_client = None
    supabase_admin_client = None
else:
    try:
        # Create Supabase client (with anon key for normal operations)
        supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info(f"✅ Supabase client initialized for project: {SUPABASE_URL}")

        # Create admin client (with service role key for bypassing RLS)
        if SUPABASE_SERVICE_KEY:
            supabase_admin_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
            logger.info(f"✅ Supabase admin client initialized")
        else:
            supabase_admin_client = None
            logger.warning("⚠️  SUPABASE_SERVICE_ROLE_KEY not set. Admin operations may fail.")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        supabase_client = None
        supabase_admin_client = None


def get_supabase() -> Client:
    """
    Get the Supabase client instance.

    Returns:
        Client: Supabase client instance

    Raises:
        RuntimeError: If Supabase client is not initialized
    """
    if supabase_client is None:
        raise RuntimeError(
            "Supabase client not initialized. "
            "Please check your SUPABASE_URL and SUPABASE_ANON_KEY environment variables."
        )
    return supabase_client


def get_supabase_admin() -> Client:
    """
    Get the Supabase admin client instance (bypasses RLS).
    Use only for server-side operations that need to bypass Row Level Security.

    Returns:
        Client: Supabase admin client instance

    Raises:
        RuntimeError: If Supabase admin client is not initialized
    """
    if supabase_admin_client is None:
        raise RuntimeError(
            "Supabase admin client not initialized. "
            "Please check your SUPABASE_SERVICE_ROLE_KEY environment variable."
        )
    return supabase_admin_client


def check_connection() -> bool:
    """
    Check if Supabase connection is working.

    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        client = get_supabase()
        # Try a simple query to verify connection
        client.table('users').select('id').limit(1).execute()
        logger.info("✅ Supabase connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Supabase connection test failed: {e}")
        return False
