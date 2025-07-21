"""
Live test for Supabase connection and agents table
"""

from src.app.supabase_service import get_agents


def test_supabase_agents_live():
    response = get_agents()
    assert hasattr(response, "data"), "Response should have data attribute"
    assert isinstance(response.data, list), "Response data should be a list"
    print(
        f"✓ Supabase connection successful - found {len(response.data)} agents"
    )
