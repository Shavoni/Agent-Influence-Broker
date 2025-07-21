import os

from supabase import Client, create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Example: async agent fetch
def get_agents():
    return supabase.table("agents").select("*").execute()


# Add more CRUD and analytics functions as needed for agents, negotiations, transactions, webhooks, influence_metrics
